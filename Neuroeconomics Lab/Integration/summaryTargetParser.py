def getMappings():
	"""
	returns dictionary with key: individual target group, value: tuple(competence value, warmth value)
	"""
	raw = open("warmth-competence-ratings.csv")
	linesList = raw.readlines()

	lines = linesList[0].split("\t")
	for i in range(0, len(lines)):
		lines[i] = lines[i].split(",")
	lines.pop(0)

	valueMappings = dict()
	for i in range(1, len(lines)):
		warmth = lines[i][2]
		if "\r" in warmth:
			newString = ""
			for j in range(0, len(warmth)):
				if warmth[j] != "\r":
					newString += warmth[j]
			warmth = newString

		competence = lines[i][1]
		if "\r" in competence:
			newString = ""
			for j in range(0, len(competence)):
				if competence[j] != "\r":
					newString += competence[j]
			competence = newString
		valueMappings[lines[i][0]] = (competence, warmth)

	return valueMappings