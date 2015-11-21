"""
    Author: Daniel Wong, email: wongdaniel8@berkeley.edu
    Phylogenetic Tree Generator 
"""


def UPGMA(d, mutableD):
	"""
    Recursive constructor that takes an ultramteric dissimilary mapping d. 
    Caller should also pass in a copy of d for manipulation.
    
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

#Testing Code Below
#====================================
# d = {}
# d["d"] = {"b": 32, "r": 48, "w":51}
# d["b"] = {"d": 32, "r": 26, "w":34}
# d["r"] = {"d": 48, "b":26, "w":42}
# d["w"] = {"d": 51, "b":34, "r": 42}

d = {}
d["d"] = {"b": 32, "r": 48, "w":51, "s": 50, "l": 48, "c":98, "m": 148}
d["b"] = {"d": 32, "r": 26, "w":34, "s": 29 , "l":33 , "c":84 , "m":136}
d["r"] = {"d": 48, "b":26, "w":42, "s": 44 , "l": 44 , "c": 92 , "m":152}
d["w"] = {"d": 51, "b":34, "r": 42, "s": 44 , "l": 38 , "c":86 , "m":142}
d["s"] = {"d" :50 , "b": 29 , "r": 44 , "w": 44, "l": 24, "c":89 , "m":142}
d["l"] = {"d" :48 , "b": 33 , "r": 44 , "w": 38 , "s": 24 , "c":90 , "m": 142}
d["c"] = {"d" : 98, "b": 84 , "r":92 , "w":86 , "s":89 , "l": 90, "m": 148}
d["m"] = {"d" :148 , "b": 136 , "r": 152 , "w":142 , "s":142 , "l":142 , "c":148}
# print(neighborJoin2(d))

print("============================")
# b = {}
# b["a"] = {"b":5, "c": 7,"d":13}
# b["b"] = {"a": 5 ,"c": 4,"d": 10}
# b["c"] = {"a":7 , "b": 4, "d":8}
# b["d"] = {"a": 13,  "b": 10 , "c":8}
# print(neighborJoin2(b))

print("============================")
copyD = d.copy()
print(UPGMA(d, copyD))

print("============================")
b = {}
b["a"] = {"b":2, "c": 4,"d":6}
b["b"] = {"a": 2 ,"c": 4,"d": 6}
b["c"] = {"a":4, "b": 4, "d":6}
b["d"] = {"a": 6,  "b": 6 , "c":6}
bCopy = b.copy()
print(UPGMA(b, bCopy))


