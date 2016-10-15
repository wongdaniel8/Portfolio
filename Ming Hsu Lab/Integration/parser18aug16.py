"""
@author Daniel Wong
Parser for the integration and targeted values ratings 
"""
import numpy as np
import math

def getMappings(normalized):
	"""
	If normalized == True, we independently normalize all of an individual's ratings for warmth, competence, and confidence
	Parser for the integration and targeted values ratings, 
	saves two dictionary objects:
		1) warmth integration dictionary, key: group1 + " _" + group2, value: list of tuples (rating 0-100 scale, confidence 0-100 scale)
		2) competence integration dictionary, key: key: group1 + " _" + group2, value: list of tuples (rating 0-100 scale, confidence 0-100 scale)
	Also note that non-integrated paramters were also measured, 
	these are in the dictionaries as well with key: group, and value: list of tuples(rating 0-100 scale, confidence 0-100 scale)
	Raw file must have tab delimeter that separates each line.
	"""
	if normalized == True:
		userMapMeans, userMapStandardDevs = getNormalizedStats()

	raw = open("mindperc_econgames_INTEGRATION_ratings_confidence_18aug16.csv")
	linesList = raw.readlines()
	lines = linesList[0].split("\t")
	for i in range(0, len(lines)):
		lines[i] = lines[i].split(",")
	lines.pop(0) #first was empty

	warmthMapping = dict()
	compMapping = dict()

	for i in range(15, len(lines[1]) - 6):
		if lines[2][i] == "warmth_rating":
			string = lines[0][i].lower()
			if lines[1][i] != "":
				string += "_"
			string += lines[1][i]
			if string not in warmthMapping.keys():
				warmthMapping[string] = []
			for j in range(3, len(lines)): #change start index to 0 to discern which rater gave what instead of conglomerationg values
				if lines[j][i] != "":
					if normalized == False:
						if lines[j][i + 1] != "":
							warmthMapping[string].append((int(lines[j][i]), int(lines[j][i + 1])))
						else:
							warmthMapping[string].append((int(lines[j][i]), lines[j][i + 1]))
					else: 

						if lines[j][i + 1] != "":
							userMean = userMapMeans[j][0]
							userWarmthConfidenceMean = userMapMeans[j][2]
							userStdDev = userMapStandardDevs[j][0]
							userStdDevConfidence = userMapStandardDevs[j][2]

							warmthRating = int(lines[j][i])
							confidenceRating = int(lines[j][i + 1])
							if userStdDev == 0:
								stdDevUnits = 0
							else:
								stdDevUnits = (warmthRating - userMean) / float(userStdDev)
							if userStdDevConfidence == 0:
								stdDevUnitsWarmthConfidence = 0
							else:
								stdDevUnitsWarmthConfidence = (confidenceRating - userWarmthConfidenceMean) / float(userStdDevConfidence)
							
							warmthMapping[string].append((50 + stdDevUnits * userStdDev, 50 + stdDevUnitsWarmthConfidence * userStdDevConfidence))
						else:
							warmthMapping[string].append((50 + stdDevUnits * userStdDev, ""))


		if lines[2][i] == "competence_rating":
			string = lines[0][i].lower()
			if lines[1][i] != "":
				string += "_"
			string += lines[1][i]
			if string not in compMapping.keys():
				compMapping[string] = []
			for j in range(3, len(lines)):
				if lines[j][i] != "":
					if normalized == False:
						if lines[j][i + 1] != "":
							compMapping[string].append((int(lines[j][i]), int(lines[j][i + 1])))
						else:
							compMapping[string].append((int(lines[j][i]), lines[j][i + 1]))
					else:
						if lines[j][i + 1] != "":
							userMean = userMapMeans[j][1]
							userCompConfidenceMean = userMapMeans[j][3]
							userStdDev = userMapStandardDevs[j][1]
							userStdDevConfidence = userMapStandardDevs[j][3]
							compRating = int(lines[j][i])
							confidenceRating = int(lines[j][i + 1])
							if userStdDev == 0:
								stdDevUnits = 0
							else:
								stdDevUnits = (compRating - userMean) / float(userStdDev)
							if userStdDevConfidence == 0:
								stdDevUnitsCompConfidence = 0
							else:
								stdDevUnitsCompConfidence = (confidenceRating - userCompConfidenceMean) / float(userStdDevConfidence)
							
							compMapping[string].append((50 + stdDevUnits * userStdDev, 50 + stdDevUnitsCompConfidence * userStdDevConfidence))
						else:
							compMapping[string].append((50 + stdDevUnits * userStdDev, ""))



	return (warmthMapping, compMapping)


def extractInformation(warmthMapping, compMapping):
	"""
	returns warmth and competence dictionaries of key: integrated group / single group, value: 
	tuple(mean, standard deviation of values, average confidence, standard deviation of confidence values)
	"""
	warmthNumericalMapping = dict()
	for key in warmthMapping.keys():
		valuesList = []
		confidenceList = []
		for tup in warmthMapping[key]:
			valuesList.append(int(tup[0]))
			if tup[1] != "":
				confidenceList.append(int(tup[1]))
		warmthNumericalMapping[key] = (np.mean(valuesList), np.std(valuesList), np.mean(confidenceList), np.std(confidenceList))

	compNumericalMapping = dict()
	for key in compMapping.keys():
		valuesList = []
		confidenceList = []
		for tup in compMapping[key]:
			valuesList.append(int(tup[0]))
			if tup[1] != "":
				confidenceList.append(int(tup[1]))
		compNumericalMapping[key] = (np.mean(valuesList), np.std(valuesList), np.mean(confidenceList), np.std(confidenceList))


	return warmthNumericalMapping, compNumericalMapping



def getNormalizedStats():
	"""
	Returns two dictionaries containting statistical information for each user, key: user number 
		1) userMapMeans: maps user number to list of [average for warmth ratings, average for competence ratings, average for confidence_warmth ratings, average for confidence_competence ratings]
		2) userMapStandardDevs: maps user number to list of [standard deviation of warmth ratings, standard deviation of competence ratings, ... same mapping as above
	
	"""
	raw = open("mindperc_econgames_INTEGRATION_ratings_confidence_18aug16.csv")
	linesList = raw.readlines()
	lines = linesList[0].split("\t")
	for i in range(0, len(lines)):
		lines[i] = lines[i].split(",")
	lines.pop(0) #first was empty
	unNormalizedWarmth, unNormalizedComp = extractInformation(getMappings(False)[0], getMappings(False)[1])
	
	userMap = dict() #maps user number to list of list of warmth ratings, list of competence ratings, list of confidence_warmth ratings, list of confidence_competence ratings
	for i in range(3, len(lines) - 1):
		warmth = []
		competence = []
		confidenceWarmth = []
		confidenceCompetence = []
		userMap[i] = [warmth, competence, confidenceWarmth, confidenceCompetence]
		for j in range(15, len(lines[0])):
			if lines[i][j] == "":
				continue
			ratingType = lines[2][j]
			if ratingType == "warmth_rating":
				userMap[i][0].append(int(lines[i][j]))
			elif ratingType == "competence_rating":
				userMap[i][1].append(int(lines[i][j]))
			elif ratingType == "warmth_confidence":
				userMap[i][2].append(int(lines[i][j]))
			elif ratingType == "competence_confidence":
				userMap[i][3].append(int(lines[i][j]))
	userMapMeans = dict() #maps user number to list of [average for warmth ratings, average for competence ratings, average for confidence_warmth ratings, average for confidence_competence ratings]
	userMapStandardDevs = dict() #maps user number to list of standard deviation of warmth ratings, standard deviation of competence ratings, ...
	for key in userMap.keys():
		userMapMeans[key] = []
		userMapStandardDevs[key] = []
		for i in range(0, 4):
			if userMap[key][i] == []:
				userMapMeans[key].append("")
				userMapStandardDevs[key].append("")
			else:
				userMapMeans[key].append(np.mean(userMap[key][i]))
				userMapStandardDevs[key].append(np.std(userMap[key][i]))
	return userMapMeans, userMapStandardDevs

