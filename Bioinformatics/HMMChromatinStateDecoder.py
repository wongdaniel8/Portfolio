#!/usr/bin/env python
import math

def posterior_decoding(observed_states1):
    """
    Return a matrix of hidden state probabilities.

    Use the posterior decoding algorithm to decode the hidden states of the HMM.

    :observed_states: two lists of observed states (of the same length), one for 
    each histone modification (e.g. [1, 2, 3, 4, 3, 2, 2] [2, 1, 3, 6, 6, 6, 2])
    
    :return: matrix of hidden states and probabilities(as list of lists), 
    where each row reprsents a time point and each column corresponds to one of the hidden states.
    (e.g. [ [0.0659,0.07,0.003,0.8611], [0.6342,0.12,0.11,0.1358], ... ]  
        where the two inside lists are the first two rows of the matrix, and the first position 
        corresponds to the probability of being in the Coding state at the first position in the 
        genomic data (0.0659).
   

    """
    L = len(observed_states1[0])
    solution = [[] for i in range(0, L)]
    forwardMatrix = forward(observed_states1)
    backwardMatrix = backward(observed_states1)
    
    likelihood = 0
    for i in range(0, 4):
        likelihood += forwardMatrix[L - 1][i]
    print("likelihood forward", likelihood)

    for i in range(0, L):
        for j in range(0, 4):
            if forwardMatrix[i][j] == 0 or backwardMatrix[i][j] == 0 or likelihood == 0: 
                product = 0
            else:
                product = math.log10(forwardMatrix[i][j]) + math.log10(backwardMatrix[i][j]) - math.log10(likelihood)
                product = math.pow(10, product)
            solution[i].insert(j, product)

    printMatrix(solution)
    return solution


# Transition probabilities
A = {
    'coding': {
        'coding': 0.8,
        'regulatory': 0.04,
        'hetero': 0.02,
        'other': 0.14,
    },
    'regulatory': {
        'coding': 0.1,
        'regulatory': 0.9,
        'hetero': 0.0,
        'other': 0.0,
    },
    'hetero': {
        'coding': 0.0,
        'regulatory': 0.05,
        'hetero': 0.75,
        'other': 0.2,
    },
    'other': {
        'coding': 0.01,
        'regulatory': 0.05,
        'hetero': 0.24,
        'other': 0.7,
    },
}


# Emission probabilities
E1 = {
    'coding': {
        1: 0.03,
        2: 0.07,
        3: 0.1,
        4: 0.8,
    },
    'regulatory': {
        1: 0.4,
        2: 0.2,
        3: 0.3,
        4: 0.1,
    },
    'hetero': {
        1: 0.9,
        2: 0.06,
        3: 0.03,
        4: 0.01,
    },
    'other': {
        1: 0.4,
        2: 0.4,
        3: 0.1,
        4: 0.1,
    },
}


E2 = {
    'coding': {
        1: 0.3,
        2: 0.3,
        3: 0.3,
        4: 0.1,
    },
    'regulatory': {
        1: 0.01,
        2: 0.19,
        3: 0.2,
        4: 0.6,
    },
    'hetero': {
        1: 0.8,
        2: 0.1,
        3: 0.05,
        4: 0.05,
    },
    'other': {
        1: 0.4,
        2: 0.4,
        3: 0.15,
        4: 0.05,
    },
}


# Initial probabilities
P = {
    'coding': 0.001,
    'regulatory': 0.1,
    'hetero': 0.4,
    'other': 0.499,
}

def forward(observed_states):
    """
    Run forward algorithm and returns matrix

    """
    L = len(observed_states[0])
    matrix = [[] for i in range (0, L)]
    for i in range (0, L):
        for j in range(0, 4):
            if j == 0: state = "coding"
            if j == 1: state = "regulatory"
            if j == 2: state = "hetero"
            if j == 3: state = "other"
            emission = math.log10(E1[state][observed_states[0][i]]) + math.log10(E2[state][observed_states[1][i]])
            # emission = math.pow(10,emission)
            if i == 0:
                ## matrix[i][j] = P[state]
                # matrix[i].insert(j, emission * P[state])
                init = emission + math.log10(P[state])
                init = math.pow(10, init)
                matrix[i].insert(j, init)
            else:
                # print("first, ", E1[state][observed_states[0][i]], "second, ", E2[state][observed_states[1][i]])
                summation = 0
                prevState = ""
                for k in range(0, 4):
                    if k == 0: prevState = "coding"
                    if k == 1: prevState = "regulatory"
                    if k == 2: prevState = "hetero"
                    if k == 3: prevState = "other"

                    # summation += matrix[i - 1][k] * A[prevState][state]
                    if matrix[i - 1][k] == 0 or A[prevState][state] == 0:
                        summation += 0
                    else:
                        product = math.log10(matrix[i - 1][k]) + math.log10(A[prevState][state])
                        product = math.pow(10, product)
                        summation += product

                # matrix[i].insert(j, emission * summation)
                if summation == 0:
                    entry = 0
                else:
                    entry = emission + math.log10(summation)
                    entry = math.pow(10, entry)
                matrix[i].insert(j, entry)

    likelihood = 0
    for i in range(0, 4):
        likelihood += matrix[L - 1][i]
    print("likelihood forward", likelihood)

    return matrix

def backward(observed_states):
    """
    Run backward algorithm and returns matrix
    """
    L = len(observed_states[0])
    matrix = [[] for i in range (0, L)]
    for i in range (L - 1, -1, -1):
        for j in range(0, 4):
            if j == 0: state = "coding"
            if j == 1: state = "regulatory"
            if j == 2: state = "hetero"
            if j == 3: state = "other"
            if i == L - 1:
                matrix[i].insert(j, 1)
            else: 
                summation = 0
                prevState = ""
                for k in range(0, 4):
                    if k == 0: forstate = "coding"
                    if k == 1: forstate = "regulatory"
                    if k == 2: forstate = "hetero"
                    if k == 3: forstate = "other"

                    # emission = E1[forstate][observed_states[0][i + 1]] * E2[forstate][observed_states[1][i + 1]]
                    emission = math.log10(E1[forstate][observed_states[0][i + 1]]) + math.log10(E2[forstate][observed_states[1][i + 1]])
                    # summation +=  A[state][forstate] * emission * matrix[i + 1][k] 
                    if (A[state][forstate] == 0 or emission == 0 or matrix[i+1][k] == 0):
                        summation += 0
                    else: 
                        product = math.log10(A[state][forstate]) + emission + math.log10(matrix[i+1][k])
                        product = math.pow(10, product)
                        summation += product
                matrix[i].insert(j, summation)
    return matrix

def getBackwardLikelihood(matrix, observed_states):
    likelihood = 0 
    for i in range(0, 4):
        if i == 0: state = "coding"
        if i == 1: state = "regulatory"
        if i == 2: state = "hetero"
        if i == 3: state = "other"
        emission = math.log10(E1[state][observed_states[0][0]]) + math.log10(E2[state][observed_states[1][0]])
        # emission = math.pow(10, emission)

        product = emission + math.log10(matrix[0][i]) + math.log10(P[state])
        product = math.pow(10, product)
        likelihood += product
        # likelihood += emission * matrix[0][i] * P[state]
    return(likelihood)

def printMatrix(nestedList):
    print("matrix:")
    for l in nestedList:
        print(l)

if __name__ == "__main__":
    import doctest
    doctest.testmod()


# observed = [[1, 2, 3, 4, 3, 2, 2], [2, 1, 3, 4, 4, 3, 2]]
# f = forward(observed)
# print("F")
# printMatrix(f)
# print()
# b= backward(observed)
# print("B")
# printMatrix(b)
# print("likelihood backward", getBackwardLikelihood(b, observed))
# posterior_decoding(observed)



observed = [[1, 1, 1], [1, 1, 1]]
f = forward(observed)
print("F")
printMatrix(f)
print()
b= backward(observed)
print("B")
print("likelihood backward", getBackwardLikelihood(b, observed))
printMatrix(b)
print()
posterior_decoding(observed)

def parser(inp):
    e1 = []
    e2 = []
    f = open(inp)
    matrix = []
    row = []
    for lines in f:
        item = lines.split("\n")
        for el in item:
            subitem = el.split("\t")
            if len(subitem) > 1:
                e1.append(int(subitem[1]))
                e2.append(int(subitem[2]))
    return([e1, e2])

# observed = (parser("test1"))
# f = forward(observed)
# print("F")
# printMatrix(f)
# print()
# b= backward(observed)
# print("B")
# printMatrix(b)
# observed = [[4,1,3], [4,1,4]]
# posterior_decoding(observed)

