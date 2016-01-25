"""
    Author: Daniel Wong, email: wongdaniel8@berkeley.edu
    Bowtie Genomic Aligner. 
"""

import sys

def get_suffix_array(s):
    """
    Implementation of suffix array generation
    """
    SA = [] 
    suffixDictionary = {} #map suffix to its index
    for i in range(0, len(s)):
        suffixDictionary[ s[i : len(s)] ] = i
    sortedSuffixes = sorted(suffixDictionary) #sort suffixes    
    for key in sortedSuffixes:
        SA.append(suffixDictionary[key])
    return SA



def getM(F):
    """
    Returns the helper data structure M (using the notation from class)
    """
    #1-indexed
    M = {} #maps character in alphabet to first occurrence in F
    for i in range(0, len(F)): 
        if F[i] not in M:
            M[F[i]] = i + 1
    return M 


def getOCC(L):
    """
    Returns the OCC data structure such that OCC[c][k] is the number of times char c appeared in L[1], ..., L[k]
    """
    #implemented to be 1-indexed
    occ = {}
    for i in range(0, len(L)):
        char = L[i]
        if char not in occ:
            occ[char] = {}
            for z in range(0, i + 1):
                occ[char][z] = 0
            for k in range(i + 1, len(L) + 1):
                occ[char][k] = 1
        else: 
            for j in range (i + 1, len(L) + 1):
                occ[char][j] = 1 + occ[char][i]
    return occ
    

def bwt(s, SA):
    """
    Input:
        s = a string text
        SA = the suffix array of s

    Output:
        BWT of s as a string

    """
    transform = ""
    for i in range(0, len(SA)):
        if SA[i] == 0:
            transform += "$"
        else:
            transform += s[SA[i] - 1]
    return transform

def getF(L):
    """
    Input:
        L = bwt(s)

    Output:
        F column of bwt (sorted string of L)
    """
    return sorted(L)



def exact_match(p, SA, L, F, M, occ):
    """
    Input:
        p = the pattern string
        SA = suffix array of some reference string s
        L = bwt(s)
        F = sorted(bwt(s))
        M, occ = buckets and repeats information used by sp, ep

    Output:
        The first aligned starting position of p in s (0-indexed)
    """
    charList = []
    for char in p:
        charList.append(char)
    if charList[-1] not in M.keys():
        return False 
    lastChar = charList.pop()
    sp = M[lastChar]
    ep = M[lastChar] + occ[lastChar][len(L)] - 1 #next char in M structure
    while (len(charList) != 0):
        c = charList.pop()
        if c not in M.keys():
            return False 
        sp = M[c] + occ[c][sp - 1] 
        ep = M[c] + occ[c][ep] - 1
        if ep < sp: return False
    return SA[ep - 1]


def bowtie(SA, L, F, M, occ, p, q, k):
    """
    Input:
        SA = suffix array of some reference string s
        L = bwt(s)
        F = sorted(bwt(s))
        M, occ = buckets and repeats information used by sp, ep
        p = a string pattern
        q = a quality score array for p
        k = maximum number of backtracks

    Output:
        The first aligned starting position of p in s

    Notes:
        Only allow A<->T and G<->C mismatches
        Output should be 0-indexed
        If multiple matches are found, return the first

    Example:
        > S = 'GATTACA'
        > SA = get_suffix_array(S)
        > L = bwt(S)
        > F = getF(L)
        > M = getM(F)
        > occ = getOCC(L)
        > bowtie(SA, L, F, M, occ, 'AGA', [40, 15, 35], 2)
        4

    """
    openPositions = []
    for z in range(0, len(q)):
        openPositions.append(True)
    backtracks = 0 
    pList = []
    copyOfP = []
    for char in p:
        if char not in ['A', 'T', 'C', 'G', '$']: return False
        pList.append(char)
        copyOfP.append(char)
    lastSubstituted = -1
        

    while backtracks < k: 
        match = exact_match(p, SA, L, F, M, occ)
        if isinstance(match, bool) == False: 
            return match
        else:
            if openPositions.count(False) == len(q):
                return False 
            openPos = -1
            bestScore = 10000000000000000
            for d in range(len(q) - 1, -1, -1):
                if openPositions[d] == True and q[d] <= bestScore:
                    openPos = d
                    bestScore = q[d]
            c = pList[openPos]
            substitution = None #the character to substitute in for c
            if c == 'A': substitution = 'T'
            if c == 'T': substitution = 'A'
            if c == 'C': substitution = 'G'
            if c == 'G': substitution = 'C'
            pList[openPos] = substitution
            openPositions[openPos] = False
            if openPos > lastSubstituted:
                for s in range (0, openPos):
                    pList[s] = copyOfP[s]
                    openPositions[s] = True
            lastSubstituted = openPos
            p = ''.join(pList)
            backtracks += 1
    return False 

def myLocate(p, SA, L, F, M, occ): 
    """
    Returns index of suffix of mismatch 
    if mismatch, returns the tuple (-1, index of suffix of mismatch, character that was a mismatch)
    
    """ 
    charList = []
    for char in p:
        charList.append(char)
    if charList[-1] not in M.keys():
        return (-1, len(charList) - 1, charList[-1])
    lastChar = charList.pop()
    sp = M[lastChar]
    ep = M[lastChar] + occ[lastChar][len(L)] - 1 #next char in M structure
    while (len(charList) != 0):
        c = charList.pop()
        if c not in M.keys():
            return (-1, len(charList), c) 
        sp = M[c] + occ[c][sp - 1]
        ep = M[c] + occ[c][ep] - 1
        if ep < sp and len(charList) == 0: 
            if len(charList) == 0: return (-1, 0, c)
            else: return (-1, len(charList) - 1, charList[-1])
    return sp - 1 # -1 to bring back to 0-indexed
