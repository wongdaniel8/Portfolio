"""
@Author Daniel Wong
Integration study of warmth, competence, and stereotyping
"""

import math
import random
import numpy as np
from scipy import stats 
import parser18aug16 as parser
import summaryTargetParser as targetParser
import matplotlib.pyplot as plt

global allL2Norms
allL2Norms = 0
count = 0 
global normalized 
normalized = True

alphas = [1, 10, 100, 1000]
betas = [.001, .01, .1, 1, 10, 100]
gammas = [.001, .01, .1, 1, 10]
global alpha, beta, gamma
alpha, beta, gamma = 0, 1, 1
alpha, beta, gamma = 1, .0001, .001

def getCombination(mu1, mu2, sig1, sig2, confidence1, confidence2):
	"""
	Takes as parameters, mu1 and mu2, which are the two averages of the independent random variables for
	warmth and competence respectively, and also sig1 and sig2, which are the standard deviations of the warmth
	and competence distributions, respectively. Returns the new combined average and new standard deviation of
	the new random variable, warmth + competence.
	"""
	global alpha, beta, gamma

	#Standard Bayesian
	# sigNew = math.sqrt(math.pow(sig1, 2) + math.pow(sig2, 2))
	# muNew = u1 + u2
	# return muNew, sigNew 

	##In accordance with the nature papers:
	sigNew = (math.pow(sig1,2) * math.pow(sig2, 2)) \
	/ float((math.pow(sig1,2) + math.pow(sig2, 2)))
	inv1 = 1 / float((math.pow(sig1, 2)))
	inv2 = 1 / float((math.pow(sig2, 2)))
	sumInverses = inv1 + inv2

	##inverse standard deviations squared
	# w1 = inv1 / float(sumInverses)
	# w2 = inv2 / float(sumInverses)

	## equal weighting
	# w1 = .5
	# w2 = .5

	## weightings based off of confidence
	# summation = confidence1 + confidence2
	# w1 = confidence1 / float(summation)
	# w2 = confidence2 / float(summation)

	##weightings with exponentials
	# w1 = w1**.001
	# w2 = w2**.001
	# newSummation = w1 + w2
	# w1 = w1 / float(newSummation)
	# w2 = w2 / float(newSummation)

	##weightings with polynomial factors
	w1 = (beta * confidence1 + alpha)**gamma  
	w2 = (beta * confidence2 + alpha)**gamma 
	newSummation = w1 + w2
	w1 = w1 / float(newSummation)
	w2 = w2 / float(newSummation)

	muNew = w1 * mu1 + w2 * mu2
	return muNew, sigNew

def visualizeTargets():
	"""
	generates graph of individual target ratings, based off of Ming's csv file for averaged warmth and competence values 
	"""
	global normalized
	intWarmthMap, intCompMap = parser.extractInformation(parser.getMappings(normalized)[0], parser.getMappings(normalized)[1])
	targetMap = targetParser.getMappings()
	allCategories = set()
	compAxis = []
	warmthAxis = []
	fig, ax = plt.subplots()
	for key in intWarmthMap.keys():
		integrated = key
		g1 = integrated.split("_")[0]
		g2 = integrated.split("_")[1]
		if g1 != "":
			allCategories.add(g1)
		if g2 != "":
			allCategories.add(g2)

	#adjusts label positions for annotation
	catLabelMap = dict()
	for category in allCategories:
		if category == "jewish":
			catLabelMap[category] = (-30, -30)
		elif category == "farmer": 
			catLabelMap[category] = (0, 20)
		elif category == "greek" or category == "nurse":
		 	catLabelMap[category] = (20, -20)
		elif category == "british": 
			catLabelMap[category] = (-30, -30)
		else:
			catLabelMap[category] = (-20, 20)
		catLabelMap["japanese"] =(-40, 20)

	for category in allCategories:
		x = targetMap[category][1]
		y = targetMap[category][0]
		compAxis.append(x)
		warmthAxis.append(y)


		ax.annotate(category, (x,y), xytext = catLabelMap[category],
        textcoords = 'offset points', 
        bbox = dict(boxstyle = 'round,pad=0.2', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

	plt.xlabel("warmth")
	plt.ylabel("competence")
	plt.title("Individual Ratings")
	ax.scatter(compAxis, warmthAxis)
	plt.show()

def getPlotData(integrated):
	"""
	integrated = g1 + "_" + g2
	returns two lists, warmthAxis and compAxis, for which axis[0] = g1 value, axis[1] = g2 value, 
	axis[2] = observed integrated value, axis[3] = predicted integrated value
	"""
	global normalized
	g1 = integrated.split("_")[0]
	g2 = integrated.split("_")[1] 
	compAxis = []
	warmthAxis = []
	getMappingsWarmth = parser.getMappings(normalized)[0]
	getMappingsComp = parser.getMappings(normalized)[1]
	intWarmthMap, intCompMap = parser.extractInformation(getMappingsWarmth, getMappingsComp)

	#using mean and standard deviation computed from 18aug16 data: 
	compAxis.append(intCompMap[g1][0]) #group 1
	compAxis.append(intCompMap[g2][0]) #group 2

	compAxis.append(intCompMap[integrated][0]) #combined observed
	
	#using mean and standard deviation computed from 18aug16 data: 
	compPrediction = getCombination(float(intCompMap[g1][0]), float(intCompMap[g2][0]), float(intCompMap[g1][1]), float(intCompMap[g2][1]), float(intCompMap[g1][2]), float(intCompMap[g2][2]))
	
	compAxis.append(compPrediction[0]) #combined predicted
	
	#using mean and standard deviation computed from 18aug16 data: 
	warmthAxis.append(intWarmthMap[g1][0])
	warmthAxis.append(intWarmthMap[g2][0])
	
	warmthAxis.append(intWarmthMap[integrated][0])
	
	#using mean and standard deviation computed from 18aug16 data: 
	warmthPrediction = getCombination(float(intWarmthMap[g1][0]), float(intWarmthMap[g2][0]), float(intWarmthMap[g1][1]), float(intWarmthMap[g2][1]), float(intWarmthMap[g1][2]), float(intWarmthMap[g2][2]))
	
	warmthAxis.append(warmthPrediction[0])
	return warmthAxis, compAxis


def visualizeIntegrated(integrated):
	"""
	integrated takes form group1 + "_" + group2,
	visualizes a graph with four points, one for each individual group, one for the observed integrated group
	(computed by taking average of 18aug16 data), 
	and one for the predicted integrated group
	"""
	global allL2Norms

	g1 = integrated.split("_")[0]
	g2 = integrated.split("_")[1] 
	fig, ax = plt.subplots()

	warmthAxis, compAxis = getPlotData(integrated)

	for i in range(0, len(compAxis)):
		label = ""
		if i == 0:
			label = g1
		elif i == 1:
			label = g2
		elif i == 2:
			label = "observed integrated"
		else:
			label = "predicted integrated"

		ax.annotate(label, (compAxis[i],warmthAxis[i]), xytext = (-20, 20),
	        textcoords = 'offset points', 
	        bbox = dict(boxstyle = 'round,pad=0.2', fc = 'yellow', alpha = 0.5),
	        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

	observed = np.asarray([compAxis[2], warmthAxis[2]])
	predicted = np.asarray([compAxis[3], warmthAxis[3]])
	l2norm = np.linalg.norm(observed - predicted)
	print("l2 norm: ", l2norm)
	allL2Norms += l2norm

	plt.ylabel("warmth")
	plt.xlabel("competence")
	plt.title("Integrated Ratings")
	plt.scatter(compAxis, warmthAxis)
	plt.savefig("Confidence/" + integrated + '.png')
	plt.show()
	return warmthAxis, compAxis
	

def plotPredictedError():
	"""
	generates two plots of predicted vs observed, one for warmth and one for competence,
	also calculates R^2$ values for both plots
	"""
	global normalized

	warmthPred = []
	warmthObserved = []
	compPred = []
	compObserved = []
	SStotalWarmth = 0
	SSresWarmth = 0
	SStotalComp = 0
	SSresComp = 0
	keys = parser.getMappings(normalized)[0].keys()
	for key in keys:

		if "_" in key:
			warmthAxis, compAxis = getPlotData(key)
			warmthPred.append(warmthAxis[3])
			warmthObserved.append(warmthAxis[2])
			compPred.append(compAxis[3])
			compObserved.append(compAxis[2])

	meanObservedWarmth = np.mean(warmthObserved)
	meanObservedComp =  np.mean(compObserved)
	for i in range(0, len(warmthObserved)):
		SStotalWarmth += (warmthObserved[i] - meanObservedWarmth)**2
		SSresWarmth += (warmthObserved[i] - warmthPred[i])**2
		SStotalComp += (compObserved[i] - meanObservedComp)**2
		SSresComp += (compObserved[i] - compPred[i])**2


	plt.axis([0, 100, 0, 100])
	fig = plt.figure(1)
	ax = fig.add_subplot(111)
	slope, intercept, r_value, p_value, std_err = stats.linregress(warmthObserved, warmthPred)
	print(r_value**2)
	text = ax.text(60, 20, "R^2 value: " + str(r_value**2) , \
                        fontsize = 12, color = 'black')
	plt.title("Observed vs Predicted Warmth")
	plt.ylabel("Predicted Value")
	plt.xlabel("Observed Value")
	plt.scatter(warmthObserved, warmthPred)
	plt.plot([0,100], [0,100])
	plt.show()

	fig = plt.figure(1)
	ax = fig.add_subplot(111)
	slope, intercept, r_value, p_value, std_err = stats.linregress(compObserved, compPred)
	print(r_value**2)
	text = ax.text(60, 20, "R^2 value: " + str(r_value**2) , \
                        fontsize = 12, color = 'black')
	plt.axis([0, 100, 0, 100])
	plt.title("Observed vs Predicted Competence")
	plt.ylabel("Predicted Value")
	plt.xlabel("Observed Value")
	plt.scatter(compObserved, compPred)
	plt.plot([0,100], [0,100])
	plt.show()

def plotConfidence(tar, measure):
	"""
	takes parameters tar, which indicates if either "integrated" certainty or "target" certainty should be plotted,
	and measure, which takes either the value of "warmth" or "competence"
	"""
	global normalized
	integrated = ""
	if tar == "integrated":
		integrated = True
	if tar == "target":
		integrated = False
	intWarmthMap, intCompMap = parser.getMappings(normalized)
	if measure == "warmth":
		mapping = intWarmthMap
	else:
		mapping = intCompMap
	labels = []
	values = []
	for key in mapping.keys():
		count = 0
		if ("_" in key and integrated) or ("_" not in key and not integrated):
			avgCertainty = 0
			for i in range(0, len(mapping[key])):
				if mapping[key][i][1] != "":
					avgCertainty += int(mapping[key][i][1])
					count += 1
			avgCertainty = avgCertainty / float(count)
			labels.append(key)
			values.append(int(avgCertainty))

	fig = plt.figure()
	ax = fig.add_subplot(111)

	N = len(values)
	
	ind = np.arange(N)                # the x locations for the groups
	width = 0.35                      # the width of the bars

	rects1 = ax.bar(ind, values, width,
	                color='blue',
	                error_kw=dict(elinewidth=2,ecolor='red'))

	# axes and labels
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,100)
	ax.set_ylabel('Certainty')
	if tar == "integrated":
		ax.set_title('Integrated Certainty Measures for ' + measure)
	else:
		ax.set_title('Target Certainty Measures for ' + measure)
	xTickMarks = labels
	if tar == "target":
		k = .3 
	else:
		k = 1 
	ax.set_xticks(ind+width - k)
	xtickNames = ax.set_xticklabels(xTickMarks)
	plt.setp(xtickNames, rotation=45, fontsize=10)

	print("values", values, len(values))
	print("labels", labels, len(labels))
	plt.show()

def predictIntegratedConfidence(measure):
	"""
	generates a plot of predicted confidence by integrating two individual target group confidences, with
	weightings based off of inverse standard deviation squared.
	Measure takes either value "warmth" or "competence"
	"""
	global normalized
	intWarmthMap, intCompMap = parser.extractInformation(parser.getMappings(normalized)[0], parser.getMappings(normalized)[1])
	print(intWarmthMap)
	predictedList = []
	observedList = []
	labels = []
	if measure == "warmth":
		mapping = intWarmthMap
	if measure == "competence":
		mapping = intCompMap
	for key in mapping.keys():
		if "_" in key:
			g1 = key.split("_")[0]
			g2 = key.split("_")[1]
			confidence1 = mapping[g1][2]
			sig1 = mapping[g1][3]
			confidence2 = mapping[g2][2]
			sig2 = mapping[g2][3]
			sigNew = (math.pow(sig1,2) * math.pow(sig2, 2)) \
			/ float((math.pow(sig1,2) + math.pow(sig2, 2)))
			inv1 = 1 / float((math.pow(sig1, 2)))
			inv2 = 1 / float((math.pow(sig2, 2)))
			sumInverses = inv1 + inv2
			##inverse standard deviations squared
			w1 = inv1 / float(sumInverses)
			w2 = inv2 / float(sumInverses)
			predValue = confidence1 * w1 + confidence2 * w2
			predictedList.append(predValue)
			observedList.append(mapping[key][2])
			labels.append(key)

	
	fig = plt.figure(1)
	ax = fig.add_subplot(111)
	plt.axis([50, 100, 50, 100])
	if normalized == True:
		plt.axis([0, 100, 0, 100])
	plt.scatter(observedList, predictedList)
	plt.plot([0,100], [0,100])

	slope, intercept, r_value, p_value, std_err = stats.linregress(observedList, predictedList)
	text = ax.text(70, 60, "R^2 value: " + str(r_value**2) , \
                        fontsize = 12, color = 'black')
	plt.title("Observed vs Predicted " + measure.title() + " Confidence")
	plt.xlabel("Observed")
	plt.ylabel("Predicted")
	plt.savefig("Confidence/predicted" + measure + 'Integrated.png')
	plt.show()


##==================================================
##Main runs of program
##==================================================

##visualizeTargets
# for key in parser.getMappings(normalized)[0].keys():
# 	if "_" in key:
# 		count += 1
# 		visualizeIntegrated(key)
# print("average l2 norm", allL2Norms / float(count))

# plotPredictedError()

# plotConfidence("target", "warmth")
# plotConfidence("target", "competence")
# plotConfidence("integrated", "competence")
# plotConfidence("integrated", "warmth")

# visualizeIntegrated("japanese_nurse")
# visualizeIntegrated("arab_athlete")

# predictIntegratedConfidence("warmth")
# predictIntegratedConfidence("competence")

##hypertuning of parameters
# for a in alphas: 
# 	for b in betas:
# 		for g in gammas:
# 			print(a, b, g)
# 			alpha = a
# 			beta = b
# 			gamma = g
# 			plotPredictedError()

