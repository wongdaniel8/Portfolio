import csv
from sklearn.feature_extraction import DictVectorizer
from scipy import io
import numpy as np
import random
import math
import sys
import pickle



spamData = io.loadmat("spam-dataset/spam_data")
SPAMTRAIN = spamData["training_data"]
print("spam train shape ", SPAMTRAIN.shape)
SPAMLABELS = spamData["training_labels"][0] #1500 ones i.e. spam, 3672 zeros i.e. ham
SPAMTEST = spamData["test_data"]
ham = []
spam =[]
for i in range(0, len(SPAMLABELS)):
    if SPAMLABELS[i] == 1:
        spam.append(SPAMTRAIN[i])
    else:
        ham.append(SPAMTRAIN[i])
ham = np.asarray(ham)
spam = np.asarray(spam)
hamMeans = np.mean(ham, axis=0)
hamStds = np.std(ham, axis=0)
spamStds = np.std(spam, axis=0)
spamMeans = np.mean(spam, axis=0)
rand = []
tIndices = [] #indices to train with 
for i in range(0, len(SPAMLABELS)):
    rand.append(i)
random.shuffle(rand)
SUBTRAIN = []
SUBLABELS = [] #3879 emails
SUBVALIDATIONLABELS = [] #1293 emails    #5172 total set
SUBVALIDATION = []
count = 0
for index in rand:           
    if count < 500:
        SUBVALIDATION.append(SPAMTRAIN[index])
        SUBVALIDATIONLABELS.append(SPAMLABELS[index])
    else:
        tIndices.append(index)
        SUBTRAIN.append(SPAMTRAIN[index])
        SUBLABELS.append(SPAMLABELS[index])
    count += 1
print(len(SUBVALIDATIONLABELS), len(SUBVALIDATION))
print(len(SUBTRAIN), len(SUBLABELS))


#////////////////////////////////////////////////////////

def getSplit(indices, labels):
    ones = 0
    zeros = 0
    for i in range(0, len(indices)):
        if labels[i] == 1:
            ones += 1
        else:
            zeros += 1
    return (zeros, ones)

def allSame(l):
    for i in range(0, len(l)):
        if l[i] != l[0]:
            return False
    return True

def containsDups(l):
    s = set()
    for i in range(0, len(l)):
        s.add(l[i])
    if len(s) != len(l):
        return True
    return False


def entropy(s, labels): 
    """
    s will be a list of indices
    """
    ones = 0 
    zeros = 0
    cardinality = len(s)
    for i in range(0, len(s)):
        if labels[s[i]] == 0:
            zeros += 1
        else: 
            ones += 1
    onesR = ones / float(cardinality)
    zerosR = 1 - float(onesR)
    if onesR == 1 or zerosR == 1: #eeeh if one class only return -# to indicate good split???
        return -10

    return (-1 * onesR * float(math.log(onesR, 2))) - (zerosR * float(math.log(zerosR, 2)))

def HSpecial(sl, sr, onesRLeft, onesRRight):
    if onesRLeft == 0 or onesRRight == 0:
        return 1000000
    if onesRLeft == 1 or onesRRight == 1:
        return -1000000
    zerosRLeft = 1 - float(onesRLeft) 
    zerosRRight = 1 - float(onesRRight)

    slCard = len(sl)
    srCard = len(sr)
    num = slCard * float((-1 * onesRLeft * float(math.log(onesRLeft, 2))) - (zerosRLeft * float(math.log(zerosRLeft, 2)))) 
    + srCard * float((-1 * onesRRight * float(math.log(onesRRight, 2))) - (zerosRRight * float(math.log(zerosRRight, 2))))
    denom = slCard + float(srCard)
    return num / float(denom)


def H(sl, sr, labels):
    """
    weighted avg entropy after a split that yield left set of indices (sl) and right set (sr)
    """
    slCard = len(sl)
    srCard = len(sr)

    num = slCard * float(entropy(sl, labels)) + srCard * float(entropy(sr, labels))
    denom = slCard + float(srCard)
    return num / float(denom)

class Node:
    def __init__(self, split_rule, lNode, rNode, lab):
        self.splitRule = split_rule
        self.left = lNode
        self.right = rNode
        self.label = lab

    def display(self):
        print("label: ", self.label, "splitRule: ", self.splitRule)#, "left: ", self.left, "right: ", self.right)

class DecisionTree:
    def __init__(self, root):
        self.root = root
        self.maxIters = 30
        self.ERRORS = 0
        self.TOTAL = 0

    def segmenter(self, dtype, indices, X, labels, bagging):
        """
        returns a tuple (feature, threshold, slFinal, srFinal) such that feature is the feature to split on,
        threshold is the value to split on, slFinal (srFinal) is the list of indices of samples to be partitioned to 
        the left (right), X must be the ENTIRE training set. indices serves to selectively select which samples to use.
        bagging = True if we're using attribute bagging, False otherwise
        """
        lowestEntropy = float('inf')
        feature = -1
        threshold = .5
        slFinal = []
        srFinal = []
        iterate = []
        if bagging == True:
            randomFeatures = []
            for i in range(0, len(X[0])):
                randomFeatures.append(i)
            random.shuffle(randomFeatures)
            randomFeatures = randomFeatures[0: int(round(math.sqrt(len(randomFeatures))))]#len(randomFeatures) / 3] #hyperparam /3 pretty good
            iterate = randomFeatures
        else:
            iterate = range(0, len(X[0]))

        for d in iterate: #iterate through all features if no bagging
            if dtype == "spam":
                hmean = hamMeans[d]
                smean = spamMeans[d]
                hstd = hamStds[d]
                sstd = spamStds[d]
                candidates = np.arange(hmean - (2 * float(hstd)), hmean + (2 * float(hstd)), hstd / float(4))
            else:
                hmean = poorMeans[d]
                hstd = poorStds[d]
                smean = richMeans[d]
                sstd = richStds[d]
                candidates = np.arange(hmean - (2 * float(hstd)), hmean + (2 * float(hstd)), hstd / float(4)) #better performance but slower

            for thresholdCandidate in candidates:
                if thresholdCandidate <= 0:
                    continue
                sl = []
                sr = []
                #suggested partition into sl and sr 
                for i in indices: 
                    if X[i][d] > thresholdCandidate: #using mean of feature for ham set as candidate for final threshold, i.e. if greater than avg implies spam, sr
                        sr.append(i)
                    else: 
                        sl.append(i) 
                if len(sl) == 0 or len(sr) == 0: #useless threshold then
                    continue

                entropy = H(sl, sr, labels)
                if entropy < lowestEntropy:
                    lowestEntrpy = entropy
                    feature = d
                    threshold = thresholdCandidate
                    slFinal = sl
                    srFinal = sr
        return feature, threshold, slFinal, srFinal

    def train(self, dtype, node, indices, X, labels, iteration, bagging): #FINAL SPAM TRAIN
        """
        returns node, build tree recursively
        X is the entire training set (must be complete),
        labels are corresponding labels
        indices are indices of sample data to train with
        """
        print("iteration", iteration)
        
        if len(indices) == 0:
            print("ERROR")
        
        leftStat ="not done"
        rightStat = "not done"
        DONE = False
        mult = 10 

        segment = self.segmenter(dtype, indices, X, labels, bagging) #
        splitRule = (segment[0], segment[1])
        sl = segment[2]
        sr = segment[3]

        if len(sl) == 0 and len(sr) == 0:
            print("empty!")
            sl = indices[0: len(indices) / 2]
            sr = indices[len(indices) / 2 : len(indices)]
        node.splitRule = splitRule
        print("lengths", len(sl), len(sr))
       
        if not DONE and len(sl) <= 1000: #1000 good for census, 500 spam
            # print("left handling")
            numOnes = 0
            numZeros = 0
            for ind in sl:
                if labels[ind] == 1:
                    numOnes += 1
                else:
                    numZeros += 1
            if numOnes == numZeros:
                print("EQUALITY")

            if numOnes > numZeros:
                maxi = 1
                mini = 0
                minor = numZeros
                major = numOnes
            else: 
                maxi = 0
                mini = 1
                minor = numOnes
                major = numZeros

            if major > mult * float(minor):
                print("mult partition")
            
            if iteration > self.maxIters:
                print("max reached")
                leftStat = "done"
                rightStat = "done"
                DONE = True
                leafNode = Node(splitRule, None, None, maxi)
                node.left = leafNode
                node.right = leafNode

            if numOnes != numZeros and (len(sl) < 15 or major > mult * float(minor)): #65 best majority vote
                print("ones, zeros ", numOnes, numZeros)
                self.ERRORS += min(numOnes, numZeros)
                self.TOTAL += numZeros + numOnes
                leafNode = Node(splitRule, None, None, maxi)
                node.left = leafNode
                leftStat = "done"

        if not DONE and len(sr) <= 1000: #best is 500 so far
            numOnes = 0
            numZeros = 0
            for ind in sr:
                if labels[ind] == 1:
                    numOnes += 1
                else:
                    numZeros += 1

            if numOnes > numZeros:
                maxi = 1
                mini = 0
                minor = numZeros
                major = numOnes
            else: 
                maxi = 0
                mini = 1
                minor = numOnes
                major = numZeros
            if major > mult * float(minor):
                print("mult partition")

            if iteration > self.maxIters:
                print("max reached")
                leftStat = "done"
                rightStat = "done"
                DONE = True
                leafNode = Node(splitRule, None, None, maxi)
                node.left = leafNode
                node.right = leafNode

            if numOnes != numZeros and (len(sr) < 15 or major > mult * float(minor)):
                print("ones, zeros ", numOnes, numZeros)
                self.ERRORS += min(numOnes, numZeros)
                self.TOTAL += numZeros + numOnes
                leafNode = Node(splitRule, None, None, maxi)
                node.right = leafNode
                rightStat = "done"


        if not DONE and leftStat == "not done":
            node.left = Node(splitRule, None, None, "internal")
            self.train(dtype, node.left, sl, X, labels, iteration + 1, bagging)

        if not DONE and rightStat == "not done":
            node.right = Node(splitRule, None, None, "internal")
            self.train(dtype, node.right, sr, X, labels, iteration + 1, bagging)
        return 

    def predict(self, data):
        """
        data is a 2D array of data entries
        returns a list of predictions
        """
        predictions = []
        for entry in data:
            p = self.root
            while(True):
                splitRule = p.splitRule
                feature = splitRule[0]
                thresh = splitRule[1]
                if entry[feature] < thresh:
                    p = p.left
                else:
                    p = p.right
                if p.left == None and p.right == None:
                        predictions.append(p.label)
                        break
        return predictions

def visualize(tree, sample):
    """
    returns the path that a sample takes on tree
    """ 
    p = tree.root
    direction = "null"
    while p.left != None and p.right != None:
        splitRule = p.splitRule
        feature = splitRule[0]
        thresh = splitRule[1]
        if sample[feature] < thresh:
            direction = "left"
            p = p.left
        else:
            direction = "right"
            p = p.right
        print("splitRule: ",feature, "thresh: ", thresh, " direction: ", direction)
    print(p.label)

#///////////////////////////////////////////////////
#RANDOM FORESTS

class randomForests:
    def __init__(self, numTrees, X, y):
        """
        trees will be a list of DecisionTree objects, X will be the entire training set,
        y will be the corresponding labels
        """
        self.numTrees = numTrees
        self.trees = []
        self.X = X
        self.y = y


    def populate(self, dtype, numSamples, indices1):
        """
        initialize self.trees with self.numTrees trees trained on numSamples
        trained on a random sampling from indices1
        """
        for i in range(0, self.numTrees):
            root = Node(None, None, None, "root")
            tree = DecisionTree(root)
            indices = []
            for j in range(0, len(indices1)):
                rand = random.randint(0, len(indices1) - 1) #random index to find random sample from index1
                rand = indices1[rand]
                indices.append(rand)
            tree.train(dtype, root, indices, self.X, self.y, 0, True) #we use bagging in this case
            print("tree, ", i)
            self.trees.append(tree)
    
    def predict(self, data):
        """
        data is a 2D array of data entries
        returns a list of predictions, based off of majority vote
        """
        predictions = []
        for entry in data:
            numOnes = 0
            numZeros = 0
            for tree in self.trees:
                p = tree.root
                while p.left != None and p.right != None:
                    splitRule = p.splitRule
                    feature = splitRule[0]
                    thresh = splitRule[1]
                    if entry[feature] < thresh:
                        p = p.left
                    else:
                        p = p.right
                if p.label == 1:
                    numOnes += 1
                else:
                    numZeros += 1
            if numOnes > numZeros:
                predictions.append(1)
            else: 
                predictions.append(0)
        return predictions


def findCommonSplits(forest):
    """
    finds the most common splits for the roots of the trees in the forest,
    mapping will be a dictionary of key(feature) mapped to a list of the different threshold split criteria
    """
    mapping = {}
    for tree in forest.trees:
        split = tree.root.splitRule
        if split[0] not in mapping.keys():
            mapping[split[0]] = []
        mapping[split[0]].append(split[1])
    print(mapping)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#MAIN RUNS FOR SPAM

##train on subtraining set
def validateSpam():
    classifier = DecisionTree(None)
    classifier.root = Node("", None, None, "root")
    classifier.train("spam", classifier.root, tIndices, SPAMTRAIN, SPAMLABELS, 0, False) #performs better with bagging???
   
    ##visualize traversal
    visualize(classifier, SPAMTRAIN[0])
    print("actual label: ", SPAMLABELS[0])
    print("root split: ",classifier.root.splitRule)
    #test classifier on validation set, ~21% error rate
    predictions = classifier.predict(SUBVALIDATION)
    print(predictions)
    mistakes = 0
    for i in range(0, len(SUBVALIDATIONLABELS)):
        if predictions[i] != SUBVALIDATIONLABELS[i]:
            mistakes += 1
    print("VALIDATION ERROR RATE: ", mistakes / float(len(SUBVALIDATIONLABELS)))

    predictions = classifier.predict(SUBTRAIN)
    mistakes = 0
    for i in range(0, len(SUBTRAIN)):
        if predictions[i] != SUBLABELS[i]:
            mistakes += 1
    print("TEST ERROR RATE: ", mistakes / float(len(SUBLABELS)))

def validateSpamForest():
    forest = randomForests(20, SPAMTRAIN, SPAMLABELS)
    forest.populate("spam", len(SUBTRAIN), tIndices)#[0: len(tIndices) / 2 : 2])  #hyperparam #SUBTRAIN = 3879 #data bagging  n' = n performed well
    pickle.dump(forest, open( "save.p", "wb" ))
    
    for tree in forest.trees:
        mistakes = 0
        preds = tree.predict(SUBVALIDATION)
        for i in range(0, len(SUBVALIDATIONLABELS)):
            if preds[i] != SUBVALIDATIONLABELS[i]:
                mistakes += 1
        print("INDIVIDUAL TREE ERROR RATE SPAM FOREST: ", mistakes / float(len(SUBVALIDATIONLABELS)))
    

    predictions = forest.predict(SUBVALIDATION)
    print(predictions)
    mistakes = 0

    #takes about 2 mins, aggregate bagging = 1/3 size of feature space 15.9% with 20 trees
    for i in range(0, len(SUBVALIDATIONLABELS)):
        if predictions[i] != SUBVALIDATIONLABELS[i]:
            mistakes += 1
    print("VALIDATION ERROR RATE SPAM FOREST: ", mistakes / float(len(SUBVALIDATIONLABELS)))

    predictions = forest.predict(SUBTRAIN)
    mistakes = 0
    for i in range(0, len(SUBTRAIN)):
        if predictions[i] != SUBLABELS[i]:
            mistakes += 1
    print("test error rate spam forest: ", mistakes / float(len(SUBLABELS)))

    findCommonSplits(forest)

def getKaggleSpam():
    forest = randomForests(10, SPAMTRAIN, SPAMLABELS)
    forest.populate("spam", len(SUBTRAIN), tIndices) 
    predictions = forest.predict(SPAMTEST)
    sys.stdout = open("spamPredictions.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + "," + str(predictions[i]))

def getPickleKaggleSpam():
    classifier = pickle.load(open("save.p", "rb" ))
    predictions = classifier.predict(SPAMTEST)
    sys.stdout = open("spamPredictions.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + "," + str(predictions[i]))

#//////////////////////////////////////////////////////////////////////////////////////
#CENSUS DATA

def isNumber(string):
    nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] 
    for i in range(0, len(string)):
        if string[i] not in nums:
            return False
    return True

raw = open("census_data/train_data.csv")
raw2 = open("census_data/test_data.csv")
reader = csv.DictReader(raw) #reader is an object containing dictionaries
reader2 = csv.DictReader(raw2)
LABELS = []   
CSUBTRAIN = []
cIndices = []
CSUBLABELS = []
CSUBVALIDATION = []
CSUBVALIDATIONLABELS = []

#establish labels and D list
D = []
for row in reader:
    D.append(row)
    LABELS.append(int(row['label']))
D2 = []
for row in reader2:
    D2.append(row)

#remove labels feature from set
if "label" in D[0].keys():
    for d in D:
        d.pop("label", None)
print(D[0].keys())


#map categorical vars to counts 
catMap = {} #{workclass: {val1: count, val2: count, ...},  education: {val3: count, val4: count}, ...}
for key in D[0].keys():
    if not isNumber(D[0][key]):
        catMap[key] = {}
        for d in D:
            if d[key] not in catMap[key]:
                catMap[key][d[key]] = 1
            else:
                catMap[key][d[key]] += 1

maxMaps = {} #maps each category to the highest occuring string value
for key in catMap:
    d = catMap[key]
    maximum = 0
    maxValue = ''
    for key2 in d.keys():
        if d[key2] > maximum:
            maximum = d[key2]
            maxValue = key2
    maxMaps[key] = maxValue

for d in D:
    if d["native-country"] == "Holand-Netherlands":
        d["native-country"] = maxMaps["native-country"]

#replace ? unknowns with modes of categorical vars
for d in D:
    for key in d.keys():
        if d[key] == '?':
            d[key] = maxMaps[key]
        if isNumber(d[key]):
            d[key] = int(d[key])
for d in D2:
    for key in d.keys():
        if d[key] == '?':
            d[key] = maxMaps[key]
        if isNumber(d[key]):
            d[key] = int(d[key])

v = DictVectorizer(sparse=False)
CENSUSTRAIN = v.fit_transform(D) #returns 2d array bunch of 0s and 1s
CENSUSTEST = v.fit_transform(D2)
featNames =  ['age', 'capital-gain', 'capital-loss', 'education-num', 'education=10th', 'education=11th', 'education=12th', 'education=1st-4th', 'education=5th-6th', 'education=7th-8th', 'education=9th', 'education=Assoc-acdm', 'education=Assoc-voc', 'education=Bachelors', 'education=Doctorate', 'education=HS-grad', 'education=Masters', 'education=Preschool', 'education=Prof-school', 'education=Some-college', 'fnlwgt', 'hours-per-week', 'marital-status=Divorced', 'marital-status=Married-AF-spouse', 'marital-status=Married-civ-spouse', 'marital-status=Married-spouse-absent', 'marital-status=Never-married', 'marital-status=Separated', 'marital-status=Widowed', 'native-country=Cambodia', 'native-country=Canada', 'native-country=China', 'native-country=Columbia', 'native-country=Cuba', 'native-country=Dominican-Republic', 'native-country=Ecuador', 'native-country=El-Salvador', 'native-country=England', 'native-country=France', 'native-country=Germany', 'native-country=Greece', 'native-country=Guatemala', 'native-country=Haiti', 'native-country=Honduras', 'native-country=Hong', 'native-country=Hungary', 'native-country=India', 'native-country=Iran', 'native-country=Ireland', 'native-country=Italy', 'native-country=Jamaica', 'native-country=Japan', 'native-country=Laos', 'native-country=Mexico', 'native-country=Nicaragua', 'native-country=Outlying-US(Guam-USVI-etc)', 'native-country=Peru', 'native-country=Philippines', 'native-country=Poland', 'native-country=Portugal', 'native-country=Puerto-Rico', 'native-country=Scotland', 'native-country=South', 'native-country=Taiwan', 'native-country=Thailand', 'native-country=Trinadad&Tobago', 'native-country=United-States', 'native-country=Vietnam', 'native-country=Yugoslavia', 'occupation=Adm-clerical', 'occupation=Armed-Forces', 'occupation=Craft-repair', 'occupation=Exec-managerial', 'occupation=Farming-fishing', 'occupation=Handlers-cleaners', 'occupation=Machine-op-inspct', 'occupation=Other-service', 'occupation=Priv-house-serv', 'occupation=Prof-specialty', 'occupation=Protective-serv', 'occupation=Sales', 'occupation=Tech-support', 'occupation=Transport-moving', 'race=Amer-Indian-Eskimo', 'race=Asian-Pac-Islander', 'race=Black', 'race=Other', 'race=White', 'relationship=Husband', 'relationship=Not-in-family', 'relationship=Other-relative', 'relationship=Own-child', 'relationship=Unmarried', 'relationship=Wife', 'sex=Female', 'sex=Male', 'workclass=Federal-gov', 'workclass=Local-gov', 'workclass=Never-worked', 'workclass=Private', 'workclass=Self-emp-inc', 'workclass=Self-emp-not-inc', 'workclass=State-gov', 'workclass=Without-pay']
z = 0
for name in featNames:
    print(str(z) + name)
    z += 1
poorMeans = []
poorStds = []
richMeans = []
richStds = []
RICH = []
POOR = []
for i in range(0, len(CENSUSTRAIN)):
    if LABELS[i] == 1:
        RICH.append(CENSUSTRAIN[i])
    else:
        POOR.append(CENSUSTRAIN[i])
RICH = np.asarray(RICH)
POOR = np.asarray(POOR)
richMeans = np.mean(RICH,axis=0)
poorMeans = np.mean(POOR, axis=0)
poorStds = np.std(POOR, axis=0)
richStds = np.std(RICH, axis=0)

# # #3/4 1/4 split test validation
rand = []
for i in range(0, len(D)):
    rand.append(i)
random.shuffle(rand)
for i in rand: #32724 samples in whole data set
    if i < 3272:
        CSUBVALIDATION.append(CENSUSTRAIN[i])
        CSUBVALIDATIONLABELS.append(LABELS[i])
    else:
        cIndices.append(i)
        CSUBTRAIN.append(CENSUSTRAIN[i])
        CSUBLABELS.append(LABELS[i])

def validateCensus():
    classifier = DecisionTree(None)
    classifier.root = Node("", None, None, "root")
    classifier.train("census", classifier.root, cIndices, CENSUSTRAIN, LABELS, 0, False) #change back to false later
    
    ##visualize traversal
    visualize(classifier, CENSUSTRAIN[0])
    print("actual label: ", LABELS[0])
    print("root split: ",classifier.root.splitRule)
    

    predictions = classifier.predict(CSUBVALIDATION)
    mistakes = 0
    ones = 0
    zeros = 0
    for i in range(0, len(CSUBVALIDATIONLABELS)):
        if predictions[i] != CSUBVALIDATIONLABELS[i]:
            if predictions[i] == 1:
                ones +=1
            mistakes += 1
    # print(predictions)
    print("ones", ones)
    print("out of ", len(CSUBVALIDATIONLABELS))
    print("validation error rate census: ", mistakes / float(len(CSUBVALIDATIONLABELS)))

    predictions = classifier.predict(CSUBTRAIN)
    mistakes = 0
    for i in range(0, len(CSUBLABELS)):
        if predictions[i] != CSUBLABELS[i]:
            mistakes += 1
    print("out of ", len(CSUBLABELS))
    print("training error rate census: ", mistakes / float(len(CSUBLABELS)))
    print("ERRORS, ", classifier.ERRORS)
    print("TOTAL, ", classifier.TOTAL)
    print(classifier.ERRORS / float(classifier.TOTAL))


def validateCensusForest():
    forest = randomForests(20, CENSUSTRAIN, LABELS)
    forest.populate("census", len(CSUBTRAIN), cIndices)
    pickle.dump(forest, open( "save.p", "wb" ))

    predictions = forest.predict(CSUBVALIDATION)
    for tree in forest.trees:
        mistakes = 0
        preds = tree.predict(CSUBVALIDATION)
        for i in range(0, len(CSUBVALIDATIONLABELS)):
            if preds[i] != CSUBVALIDATIONLABELS[i]:
                mistakes += 1
        print("INDIVIDUAL TREE ERROR RATE SPAM FOREST: ", mistakes / float(len(CSUBVALIDATIONLABELS)))
    mistakes = 0
    for i in range(0, len(CSUBVALIDATIONLABELS)):
        if predictions[i] != CSUBVALIDATIONLABELS[i]:
            mistakes += 1
    print("validation error rate: ", mistakes / float(len(CSUBVALIDATIONLABELS)))
    findCommonSplits(forest)

    mistakes = 0
    predictions = forest.predict(CSUBTRAIN)
    for i in range(0, len(CSUBLABELS)):
        if predictions[i] != CSUBLABELS[i]:
            mistakes += 1
    print("training error rate: ", mistakes / float(len(CSUBLABELS)))



def getKaggleCensus():
    classifier = DecisionTree(None)
    classifier.root = Node("", None, None, "root")
    classifier.train("census", classifier.root, cIndices, CENSUSTRAIN, LABELS, 0, False)
    predictions = classifier.predict(CENSUSTEST)
    sys.stdout = open("censusPredictions.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + "," + str(predictions[i]))

def getKaggleCensusPickled():
    classifier = pickle.load(open("save.p", "rb" ))
    predictions = classifier.predict(CENSUSTEST)
    sys.stdout = open("censusPredictions.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + "," + str(predictions[i]))

# validateCensus()
# validateCensusForest() 
# getKaggleCensusPickled()


# validateSpam()
# validateSpamForest()
# getPickleKaggleSpam()
