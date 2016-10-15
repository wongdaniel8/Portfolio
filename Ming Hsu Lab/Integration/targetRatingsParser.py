"""
@author Daniel Wong
Parser for the individual target ratings file, targetting warmth and competence in particular,
saves two dictionary objects:
	1) warmth dictionary, key: group, value: rating 0-100 scale
	2) competence dictionary, key: group, value: rating 0-100 scale
All null values such as an empty response are omitted.
"""

raw = open("mindperc_econgames_targetratings_all_forR.csv")
linesList = raw.readlines()

warmthMapping = dict()
header = linesList[0].split(",")
for i in range(0, len(header)):
	string = header[i]
	if "warmth_" in string:
		warmthMapping[string] = []
		for j in range(2, len(linesList)):
			rating = linesList[j].split(",")[i]
			if rating != "": 
				warmthMapping[string].append(rating)
print(warmthMapping)

compMapping = dict()
header = linesList[0].split(",")
for i in range(0, len(header)):
	string = header[i]
	if "competence_" in string:
		compMapping[string] = []
		for j in range(2, len(linesList)):
			rating = linesList[j].split(",")[i]
			if rating != "": 
				compMapping[string].append(rating)
print(compMapping)








