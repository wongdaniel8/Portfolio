"""
@author Daniel Wong 
Phase 2 of social Bayesian Integration study, 80% fixed confidence elicitation
"""
import re
import numpy as np

raw = open("rawDataPhase2 (1).csv")
linesList = raw.readlines()
lines = linesList[0].split("\t")
for i in range(0, len(lines)):
	lines[i] = lines[i].split(",")
lines.pop(0)

integratedGroups = ['ARAB FARMER', 'ARAB LAWYER', 'ARAB NURSE', 'ARAB OLYMPIC ATHLETE', 'ARAB PRISON INMATE', 'BRITISH FARMER', 'BRITISH LAWYER', 'BRITISH NURSE', 'BRITISH OLYMPIC ATHLETE', 'BRITISH PRISON INMATE', 'GREEK FARMER', 'GREEK LAWYER', 'GREEK NURSE', 'GREEK OLYMPIC ATHLETE', 'GREEK PRISON INMATE', 'JAPANESE FARMER', 'JAPANESE LAWYER', 'JAPANESE NURSE', 'JAPANESE OLYMPIC ATHLETE', 'JAPANESE PRISON INMATE', 'JEWISH FARMER', 'JEWISH LAWYER', 'JEWISH NURSE', 'JEWISH OLYMPIC ATHLETE', 'JEWISH PRISON INMATE']
singletonsRace = ["ARAB", "BRITISH", "GREEK", "JAPANESE", "JEWISH"]
singletonsOccupation = ["FARMER", "PRISON INMATE", "NURSE", "LAWYER", "OLYMPIC ATHLETE"]

validUsers = range(6, 107) #only these participants gave complete answers

def getTargetGroup(targString):
	"""
	TARGSTRING is an arbitrary string containing the desired target group, 
	returns target group as a String
	"""
	ind = targString.index
	m = re.search('[A-Z]{2,} [A-Z]{2,} [A-Z]{2,}|[A-Z]{2,} [A-Z]{2,}|[A-Z]{2,}', targString)
	if m == None:
		return ""
	return m.group(0)

def getMappings():
	"""
	Returns dictionary of key: user_id, value: dictionary {key: target group, value: tuple(rating, low, high)}
	"""
	user_hash = {}
	for i in range(6, len(lines)): #loop through each row of users
		user_hash[i] = {}
		for j in range(15, len(lines[i]) - 3, 3): #loop through columns, final index is wrong
			target = getTargetGroup(lines[1][j])
			if target != "":
				if lines[i][j] != "" and target not in user_hash[i].keys():
					user_hash[i][target] = (int(lines[i][j]), int(lines[i][j + 1]), int(lines[i][j + 2]))
		if len(user_hash[i]) != 25: #delete entries that did not have all 25 responses
			del user_hash[i]
	return user_hash

def initialRangeAnalysis():
	"""
	function to test how confident people are in integrated target groups vs single target groups
	"""
	user_hash = getMappings()
	belowZero = 0
	aboveZero = 0
	totalR = 0
	for user in validUsers:
		R = 0
		for target in integratedGroups:
			if target not in user_hash[user].keys() or user_hash[user][target][0] == "":
				continue
			t1, t2 = getTargets(target)
			t1High = int(user_hash[user][t1][2])
			t1Low = int(user_hash[user][t1][1])
			t2High = int(user_hash[user][t2][2])
			t2Low = int(user_hash[user][t2][1])
			low = int(user_hash[user][target][1])
			high = int(user_hash[user][target][2])
			d = high - low
			d1 = t1High - t1Low
			d2 = t2High - t2Low
			R += d - (d1 + d2) / 2
		if R < 0:
			belowZero += 1
		else:
			aboveZero += 1
		totalR += R
	print("below zero: ", belowZero / float(100), "above zero: ", aboveZero / float(100))
	print("average C value: ", totalR / float(100))


def getTargets(target):
	"""
	Given an integrated TARGET, returns the two corresponding individual targets
	that make up the integrated target as a list
	"""
	if "OLYMPIC ATHLETE" in target and len(target) > 16:
		index = target.index("OLYMPIC")
		return [target[0 : index - 1], "OLYMPIC ATHLETE"]
	if "PRISON INMATE" in target and len(target) > 14:
		index = target.index("PRISON")
		return [target[0 : index - 1], "PRISON INMATE"]
	else:
		return target.split(" ")


def printUserHash():
	user_hash = getMappings()
	for key in user_hash:
		print("user: ", key, "row: ", key + 1)
		print("length of hash for user: ", len(user_hash[key]))
		print(user_hash[key])
		print("+++++++++++++")

def plotSubjectVsTarget():
	"""
	generates plots for x-axis: subject id, y-axis: target value (3 points: low, rating, high)
	"""
	import matplotlib.pyplot as plt

	user_hash = getMappings()
	for integrated in integratedGroups:
		xAxis = []
		yLow = []
		yAverage = []
		yHigh = []
		for user in getValidUsers(integrated):
			xAxis.append(user)
			yLow.append(user_hash[user][integrated][1])
			yAverage.append(user_hash[user][integrated][0])
			yHigh.append(user_hash[user][integrated][2])

		fig, ax = plt.subplots()
		plt.xlabel("User")
		plt.ylabel(integrated)
		plt.title(integrated + " Distribution of Low, Average, and High per User")
		ax.scatter(xAxis, yLow, color='blue')
		ax.scatter(xAxis, yAverage, color='black')
		ax.scatter(xAxis, yHigh, color = 'red')
		plt.show()

def getValidUsers(integratedTarget):
	"""
	returns list of users that gave a response for the integratedTarget
	"""
	valids = []
	user_hash = getMappings()
	for user in user_hash.keys():
		if integratedTarget in user_hash[user].keys():
			valids.append(user)
	return valids

def plotTargetRangePermutations(dtype):
	"""
	Generates various bar plots of a singleton target's range, and the ranges of 
	all combinations including that singleton target
	dtype indicates either "race" or "occupation"
	"""
	import matplotlib.pyplot as plt
	user_hash = getMappings()
	if dtype == "race":
		outerLoop = singletonsRace
		innerLoop = singletonsOccupation
	else:
		outerLoop= singletonsOccupation
		innerLoop = singletonsRace

	for target in outerLoop:
		ranges = []
		for user in validUsers:
			ranges.append(user_hash[user][target][2] - user_hash[user][target][1])
		avgRange = np.mean(ranges)
		integratedRanges = [] #ranges of all permutations of ethicity + occupation
		xLabels = []
		for complement in innerLoop:
			ranges = []
			if dtype == "race":
				integrated = target + " " + complement
			else:
				integrated = complement + " " + target
			users = getValidUsers(integrated)
			for user in users:
				ranges.append(user_hash[user][integrated][2] - user_hash[user][integrated][1])
			xLabels.append(integrated)
			integratedRanges.append(np.mean(ranges))

		integratedRanges.insert(0, avgRange)
		xLabels.insert(0, target)
		N = len(xLabels)
		ind = np.arange(N)
		width = .35
		fig, ax = plt.subplots()
		rects1 = ax.bar(ind, integratedRanges, width, color='g')

		# add text for labels, title and axes ticks
		ax.set_ylabel('Warmth Range')
		ax.set_title('Ranges of Integrated Groups: ' + target)
		ax.set_xticks(ind + width)
		xtickNames = ax.set_xticklabels(xLabels)
		plt.setp(xtickNames, rotation= -20, fontsize=8)

		if dtype == "race":
			plt.savefig("EthnicityRangeFigures/" + target + '.png')
		else:
			plt.savefig("OccupationalRangeFigures/" + target + '.png')
		# plt.show()







##Some tests to check if user_hash is parsed properly:
# user_hash = getMappings()
# print(user_hash[6]["BRITISH NURSE"]) #42,29,61
# print(user_hash[6]["BRITISH LAWYER"]) #57,50,74
# print(user_hash[6]["GREEK NURSE"]) #69,63,77
# print(user_hash[6]["NURSE"]) #52,48,64
# print(user_hash[132]["JAPANESE OLYMPIC ATHLETE"]) #55,16,83
# print(user_hash[11]["OLYMPIC ATHLETE"]) #('53', '51', '81')

##Functional Calls:
# user_hash = getMappings()
# printUserHash()
# initialRangeAnalysis()
# plotSubjectVsTarget()
plotTargetRangePermutations("race")
plotTargetRangePermutations("occupation")
