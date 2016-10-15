"""
@author Daniel Wong
Parser for the integration ratings, 
saves two dictionary objects:
	1) warmth integration dictionary, key: group1 + " _" + group2, value: list of all ratings 0-100 scale
	2) competence integration dictionary, key: key: group1 + " _" + group2, value: list of all ratings 0-100 scale
It is important to note that the subject i gave a warmth rating of warmthMapping[integrated_group][i] 
and a competence rating of compMapping[integrated_group][i] (index is consistent with each participant in warmth and comp mapping)
Although subject i could also be subject j for i != j in cases of redundant categories in study, like label "Arab_athlete",
index consistency among the two mappings still holds however. 
Raw file must have tab delimeter that separates each line.
"""

raw = open("mindperc_econgames_INTEGRATION_ratings_17aug16.csv")
linesList = raw.readlines()
lines = linesList[0].split("\t")
for i in range(0, len(lines)):
	lines[i] = lines[i].split(",")
lines.pop(0) 

warmthMapping = dict()
compMapping = dict()
for i in range(15, len(lines[1]) - 6):
	if lines[2][i] == "warmth":
		string = lines[0][i]
		string += "_"
		string += lines[1][i]
		if string not in warmthMapping.keys():
			warmthMapping[string] = []
		for j in range(3, len(lines)): #change start index to 0 to discern which rater gave what instead of conglomerationg values
			warmthMapping[string].append(lines[j][i])

	if lines[2][i] == "competence":
		string = lines[0][i]
		string += "_"
		string += lines[1][i]
		if string not in compMapping.keys():
			compMapping[string] = []
		for j in range(3, len(lines)):
			compMapping[string].append(lines[j][i])

#to check all values were collected
count = 0
for key in warmthMapping.keys():
	count += len(warmthMapping[key]) 
print(count, 25*200)

# print(warmthMapping)

# print(warmthMapping["Arab_athlete"])
# print(compMapping["Arab_athlete"])

#print(warmthMapping["Jewish_farmer"])
#print(compMapping["Jewish_farmer"])
