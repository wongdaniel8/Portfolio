"""
    Author: Daniel Wong, email: wongdaniel8@berkeley.edu
    Phylogenetic Tree Generator 
"""


def UPGMA(d, mutableD):
	"""
    Recursive constructor that takes an ultramteric dissimilary mapping d (as dictionary). 
    """
	if len(mutableD.keys()) == 1: return 
	deltaC = {}
	deltaKeyDict = {} #dictionary mapping which two nodes made the delta key, used for deletion later
	for key1 in mutableD.keys():
		for key2 in mutableD.keys():
			summation = 0
			if key1 != key2:
				for char1 in key1:
					for char2 in key2:
						if char1 == char2:
							continue
						summation += d[char1][char2]
				deltaKey = key1 + key2
				deltaKeyDict[deltaKey] = (key1, key2)
				deltaC[deltaKey] = (1/(len(key1) * len(key2))) * summation
	minimum = 10000000000000000000000
	minDelta = ""
	for key in deltaC.keys():
		if deltaC[key] < minimum:
			minimum = deltaC[key]
			minDelta = key
	print("deltaC is ", deltaC)
	print("minDelta "+minDelta+", value: " + str(minimum))
	dCopy = mutableD.copy()
	dCopy[minDelta] = {}
	del dCopy[deltaKeyDict[minDelta][0]]
	del dCopy[deltaKeyDict[minDelta][1]]
	return UPGMA(d, dCopy)

def neighborJoin2(d):
	"""
    Recursive constructor that takes a dissimilary mapping d
    and constructs a neighbor joining phylogenetic tree.
    
    """

	if len(d.keys()) == 2: return 
	r = {}
	for key1 in d.keys():
		summation = 0
		for key2 in d[key1].keys(): 
			summation += d[key1][key2]
		r[key1] = summation / (len(d.keys()) - 2)
	minTuple = ("","", 100000000000000)
	for key1 in d.keys():
		for key2 in d[key1].keys():
			if d[key1][key2] - r[key1] - r[key2] < minTuple[2]:
				minTuple = (key1, key2, d[key1][key2] - r[key1] - r[key2])
	dCopy = d
	newKey = minTuple[0]+minTuple[1]
	dCopy[newKey] = {}
	for key1 in d.keys():
		if key1 != minTuple[0] and key1 != minTuple[1] and key1 != newKey:
			dCopy[newKey][key1] = (d[minTuple[0]][key1] + d[minTuple[1]][key1] - d[minTuple[0]][minTuple[1]]) / 2
			dCopy[key1][newKey] = (d[minTuple[0]][key1] + d[minTuple[1]][key1] - d[minTuple[0]][minTuple[1]]) / 2
	for key1 in dCopy.keys():
		if minTuple[0] in dCopy[key1].keys():	
			del dCopy[key1][minTuple[0]]
		if minTuple[1] in dCopy[key1].keys():	
			del dCopy[key1][minTuple[1]]
	del dCopy[minTuple[0]]
	del dCopy[minTuple[1]]
	print(dCopy)
	return neighborJoin2(dCopy)
