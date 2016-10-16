import numpy as np
import numpy
from matplotlib import pyplot as plt
import math
from scipy import io
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib
import random
import sys
from sklearn import preprocessing
import matplotlib.mlab as mlab
from scipy.stats import multivariate_normal

def q2Plot():
    delta = 0.025
    x = np.arange(-6.0, 6.0, delta)
    y = np.arange(-6.0, 6.0, delta)
    X, Y = np.meshgrid(x, y)

    a = mlab.bivariate_normal(X, Y, 2, 1.0, 1.0, 1.0, 0.0)
    b = mlab.bivariate_normal(X, Y, 3, 2, -1.0, 2.0, 1.0)
    
    Z1c = mlab.bivariate_normal(X, Y, 1, 2, 0, 2, 1)  
    Z2c = mlab.bivariate_normal(X, Y, 1, 2, 2, 0, 1)

    Z1d = mlab.bivariate_normal(X, Y, 1, 2, 0, 2, 1)  
    Z2d = mlab.bivariate_normal(X, Y, 3, 2, 2, 0, 1)  

    Z1e = mlab.bivariate_normal(X, Y, 1, 2, 1, 1, 0)  
    Z2e = mlab.bivariate_normal(X, Y, 2, 2, -1 , -1, 1)  

    c = Z1c - Z2c
    d = Z1d - Z2d
    e = Z1e - Z2e

    CS = plt.contour(X, Y, a)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()

    CS = plt.contour(X, Y, b)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()

    CS = plt.contour(X, Y, c)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()

    CS = plt.contour(X, Y, d)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()

    CS = plt.contour(X, Y, e)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()




def Q3():
    mu = 3
    sigma = 9
    X1 = np.random.normal(mu, sigma, 100)
    X2 = []
    for element in X1:
        newElement = .5 * element + np.random.normal(4, 4, 1)[0]
        X2.append(newElement)
    X2 = np.asarray(X2)
    summationX1 = 0
    summationX2 = 0
    for i in range(0, 100):
        summationX1 += X1[i]
        summationX2 += X2[i]
    X1avg = summationX1 / len(X1)
    X2avg = summationX2 / len(X2)
    print("X1 avg: ", X1avg)
    print("X2 avg: ", X2avg)
    covarianceMatrix = np.cov([X1, X2])
    print("covariance matrix: ", covarianceMatrix)
    print("eigenvalues: ",np.linalg.eigvals(covarianceMatrix))
    eigs = np.linalg.eig(covarianceMatrix)
    print("eigs: ", eigs)
    print("legnths", len(X1), len(X2))
    plt.axis([-15, 15, -15, 15])
    plt.xlabel("X1")
    plt.ylabel("X2")

    plt.plot(X1, X2, 'ro')
    plt.show()

    vector1 = eigs[1][0] 
    eigenval1 = eigs[0][0]
    vector2 = eigs [1][1]
    eigenval2 = eigs[0][1]
    theta1 = math.atan(vector1[1]/vector1[0])
    theta2 = math.atan(vector2[1]/vector2[0])
    a = eigenval1*math.cos(theta1)
    b = eigenval1*math.sin(theta1)
    c = eigenval2*math.cos(theta2)
    d = eigenval2*math.sin(theta2)
    print(a,b,c,d)
    soa = np.array([[X1avg, X2avg, a, b], [X1avg, X2avg, c, d]])
    X,Y,U,V = zip(*soa)
    plt.figure()
    ax = plt.gca()
    ax.quiver(X,Y,U,V,angles='xy',scale_units='xy',scale=1)
    ax.set_xlim([-100,100])
    ax.set_ylim([-75,100])
    plt.draw()
    plt.show()

    U = []
    if eigenval1 > eigenval2:
        r1 = [vector1[0], vector2[0]]
        r2 = [vector1[1], vector2[1]]
    else:
        r1 = [vector2[0], vector1[0]]
        r2 = [vector2[1], vector1[1]] 
    U.append(r1)
    U.append(r2)

    U = np.asarray(U, dtype = np.float64)
    print(U)

    U = np.transpose(U)
    print(X1)
    for i in range(0, len(X1)):
        if X1[i] > 0:
            X1[i] = X1[i] - X1avg
        else:
            X1[i] = X1[i] + X1avg
    for i in range(0, len(X1)):
        if X2[i] > 0:
            X2[i] = X2[i] - X2avg
        else:
            X2[i] = X2[i] + X2avg
    # X1 = np.subtract(X1, X1mean)
    # X2 = np.subtract(X2, X2mean)
    newX1 = []
    newX2 = []
    newPoints = []
    for i in range(0, len(X1)):
        p1 = X1[i]
        p2 = X2[i]
        pair = [p1, p2]
        newPoint = np.asarray(pair)
        newPoints.append(newPoint)
    rotatedNewPoints = []
    for i in range(0, len(X1)):
        rotatedNewPoints.append(np.dot(newPoints[i], U))
    for i in range(0, len(rotatedNewPoints)):
        newX1.append(rotatedNewPoints[i][0])
        newX2.append(rotatedNewPoints[i][1])
    plt.axis([-15, 15, -15, 15])
    plt.plot(newX1,newX2, 'ro')
    plt.show()




training = io.loadmat("data/digit_dataset/train")
images = []
for i in range(0, 60000):
    image = []
    for j in range(0, 28):
        for k in range(0, 28):
            image.append(training["train_images"][j][k][i])
    image = np.asarray(image, dtype=np.float64)
    images.append(image)
images = np.asarray(images, dtype=np.float64)
images = preprocessing.normalize(images, norm='l2')

possibleTrainingIndices = []
for i in range(0, 60000):
    possibleTrainingIndices.append(i)
validationIndices = []

num = random.randint(0, 59999)
for i in range(0, 10000):
    while num in validationIndices:
        num = random.randint(0, 59999)
    validationIndices.append(num)
    possibleTrainingIndices.remove(num)
validationLabels = []
for i in range(0, 10000):
    validationLabels.append(training["train_labels"][validationIndices[i]][0])

def getPriors():
    """
    for q5b, get prior distributions of digits
    """
    priors = np.zeros(10)
    for i in range(0, 60000):
        label = training["train_labels"][i][0]
        priors[label] += 1
    print(priors)
    for i in range(0, 10):
        priors[i] = priors[i] / float(60000)
    print(priors)

def getKagglePredictionsDigits():
    testing = io.loadmat("data/digit_dataset/test")
    testImages = testing["test_images"]
    for i in range (0, 10000):
        newImage = np.reshape(np.asarray(testImages[i]), (28, 28))
        newImage = np.transpose(newImage)
        temp = np.reshape(newImage, (1, 784))
        testImages[i] = temp
    testImages = preprocessing.normalize(testImages, norm='l2')

    trainingImageIndices = []
    for i in range(0, 60000): #train with all images
        trainingImageIndices.append(i)
   
    meanVectors = computeMeanMatrices(trainingImageIndices)
    covariances = computeCovMatrices(trainingImageIndices)
    shape = (784, 784)
    
    inverses = []
    for i in range(0, 10):
        inverses.append(np.linalg.inv(np.add(covariances[i], .001 * np.identity(784))))
    determinants = []
    for i in range(0, 10):
        det = abs( np.linalg.slogdet(np.add(covariances[i], .001 * np.identity(784)))[1] )#* np.linalg.slogdet(np.add(covariances[i], .001 * np.identity(784)))[0]
        determinants.append(det)
    coefficients = []
    for i in range(0, 10):
        coefficients.append((-784/float(2))*math.log(2*math.pi) - (.5 * math.log(determinants[i])))
    guesses = []
    labels = []

    for i in range(0, 10000):
        maximum = float("-inf")
        guess = -1
        image = testImages[i]
        for z in range(0, 10):
            diff = np.subtract(image, meanVectors[z])
            exponent = -.5 * np.transpose(diff)
            exponent = np.dot(exponent, inverses[z])
            exponent = np.dot(exponent, diff)
            prob = exponent 
            prob += coefficients[z]
            if prob > maximum:
                maximum = prob
                guess = z
        guesses.append(guess)
    print("Id,Category")
    for i in range(0, len(guesses)):
        print(str(i + 1) +","+str(guesses[i]))

def computeMeanMatrices(imageIndices):
    labelCounts = np.zeros(10) #vector 1 x 10 with label counts
    shape = (10, 784)
    meanVectors = np.zeros(shape, dtype = np.float64)
    for i in range(0, len(imageIndices)):
        label = training["train_labels"][imageIndices[i]][0]
        labelCounts[label] += 1
        imageIndex = imageIndices[i]
        # image = images[i] #####################changed
        image = images[imageIndices[i]]
        for j in range(0, 784):
            meanVectors[label][j] = meanVectors[label][j] + image[j]
    
    for i in range(0, 10):
        for j in range(0, 784):
            meanVectors[i][j] = meanVectors[i][j] / float(labelCounts[i])
    return meanVectors


def computeCovMatrices(imageIndices):
    """
    Returns list of covariance matrices such that 0th element is cov0, 1st element is cov1
    Computed using only images from imageIndices
    """
    imageMatrix = []
    a0 = []
    a1 = []
    a2 = []
    a3 = []
    a4 = []
    a5 = []
    a6 = []
    a7 = []
    a8 = []
    a9 = []
    imageMatrix.append(a0)
    imageMatrix.append(a1)
    imageMatrix.append(a2)
    imageMatrix.append(a3)
    imageMatrix.append(a4)
    imageMatrix.append(a5)
    imageMatrix.append(a6)
    imageMatrix.append(a7)
    imageMatrix.append(a8)
    imageMatrix.append(a9)
    for i in range(0, len(imageIndices)):
        label = training["train_labels"][imageIndices[i]][0]
        imageMatrix[label].append(images[imageIndices[i]])
    covariances = []

    for i in range(0, len(imageMatrix)):
        cov = np.cov(np.asarray(imageMatrix[i]), rowvar = False)
        print("shape,", cov.shape)
        covariances.append(cov)
    return covariances

def Q5d(sampleSize):
    """
    LDA decision boundary
    given sample size, trains with SAMPLESIZE number of images, and returns
    a tuple of (samplesize, error rate) based on the predefined validation set above
    """
    trainingImageIndices = []
    shuffled = list(possibleTrainingIndices)
    random.shuffle(shuffled) 
    for i in range(0, sampleSize):
        trainingImageIndices.append(shuffled[i])
#======================================================================
    meanVectors = computeMeanMatrices(trainingImageIndices)
    covariances = computeCovMatrices(trainingImageIndices)
    shape = (784, 784)
    sigmaOverall = np.zeros(shape, dtype = np.float64)
    for cov in covariances:
        sigmaOverall = np.add(sigmaOverall, cov)
    sigmaOverall = .1 * sigmaOverall 
    sigmaOverall = np.add(sigmaOverall, .001  * np.identity(784))
    inverse = np.linalg.inv(sigmaOverall)
    
    guesses = []
    labels = []
    for i in range(0, len(validationIndices)):
        maximum = float("-inf")
        mini = float("inf")
        guess = -1
        image = images[validationIndices[i]]
        for z in range(0, 10):
            diff = np.subtract(image, meanVectors[z])
            exponent = -.5 * np.transpose(diff)
            exponent = np.dot(exponent, inverse)
            exponent = np.dot(exponent, diff)
            prob = exponent 
            if prob > maximum:
                maximum = prob
                guess = z
        guesses.append(guess)
    errors = 0
    for i in range(0, len(guesses)):
        if guesses[i] != validationLabels[i]:
            errors += 1
    errorRate = errors / float(len(guesses))
    print("errors:" , errors, "guesses: ", len(guesses), "rate ", errorRate)
    return(sampleSize, errorRate)

def plotQ5d(decision):
    """
    decision = 0 for LDA, 1 for QDA
    """
    sets = [100, 200, 500, 1000, 2000, 5000, 10000, 30000, 50000]
    Y = []
    for i in range(0, len(sets)):
        if decision == 0:
            tup = Q5d(sets[i])
        else:
            tup = Q5dii(sets[i])
        print("tup ", tup)
        Y.append(tup[1])
    plt.plot(sets, Y,  'ro' )
    plt.xlabel("Sample Size")
    plt.ylabel("Error Rate")
    plt.show()

def Q5dii(sampleSize):
    """
    QDA decision boundary
    """
    trainingImageIndices = []
    shuffled = list(possibleTrainingIndices)
    random.shuffle(shuffled) 
    for i in range(0, sampleSize):
        trainingImageIndices.append(shuffled[i])
#======================================================================
    meanVectors = computeMeanMatrices(trainingImageIndices)
    covariances = computeCovMatrices(trainingImageIndices)
    shape = (784, 784)
    
    inverses = []
    for i in range(0, 10):
        inverses.append(np.linalg.inv(np.add(covariances[i], .001 * np.identity(784))))
    determinants = []
    for i in range(0, 10):
        det = abs( np.linalg.slogdet(np.add(covariances[i], .001 * np.identity(784)))[1] )#* np.linalg.slogdet(np.add(covariances[i], .001 * np.identity(784)))[0]
        determinants.append(det)
    coefficients = []
    for i in range(0, 10):
        coefficients.append((-784/float(2))*math.log(2*math.pi) - (.5 * math.log(determinants[i])))
    print("coeff", coefficients)
    print("determs", determinants)
    guesses = []
    labels = []

    for i in range(0, len(validationIndices)):
        maximum = float("-inf")
        guess = -1
        image = images[validationIndices[i]]
        for z in range(0, 10):
            diff = np.subtract(image, meanVectors[z])
            exponent = -.5 * np.transpose(diff)
            exponent = np.dot(exponent, inverses[z])
            exponent = np.dot(exponent, diff)
            prob = exponent 
            prob += coefficients[z]
            if prob > maximum:
                maximum = prob
                guess = z
        guesses.append(guess)

    errors = 0
    for i in range(0, len(guesses)):
        if guesses[i] != validationLabels[i]:
            errors += 1
    errorRate = errors / float(len(guesses))
    print("errors:" , errors, "guesses: ", len(guesses), "rate ", errorRate)
    return(sampleSize, errorRate)

def spamClassifier():
    spamData = io.loadmat("data/spam_dataset/spam_data")
    emails = spamData["training_data"]
   
    emails = preprocessing.normalize(emails, norm='l2')

    labels = spamData["training_labels"][0]
    ones = 0
    zeros = 0
    hams = []
    spams = []
    for i in range(0, len(labels)):
        if labels[i] == 1:
            ones += 1
            spams.append(emails[i])
        else:
            zeros += 1
            hams.append(emails[i])
    hams = np.asarray(hams)
    spams = np.asarray(spams)
    print(labels[0])
    print(spamData["training_data"].shape)
    meanHam = np.zeros((1, 32))
    meanSpam = np.zeros((1, 32))
    for i in range(0, 5172):
        if labels[i] == 0:
            meanHam = np.add(emails[i], meanHam)
        else:
            meanSpam = np.add(emails[i], meanHam)
    meanHam = (1/float(zeros)) * meanHam
    meanSpam = (1/float(ones)) * meanSpam
    # print(meanHam)

    covHam = np.cov(hams, rowvar = False)
    detHam =  abs(np.linalg.slogdet(np.add(covHam, .001 * np.identity(32)))[1])
    invHam = np.linalg.inv(np.add(covHam, .001 * np.identity(32)))
    covSpam= np.cov(spams, rowvar = False)
    detSpam =  abs(np.linalg.slogdet(np.add(covSpam, .001 * np.identity(32)))[1])
    invSpam = np.linalg.inv(np.add(covSpam, .001 * np.identity(32)))

    guesses = []
    testData = spamData["test_data"]

    covHam = np.add(covHam, .001 * np.identity(32))
    covSpam = np.add(covSpam, .001 * np.identity(32))
    hamClass = multivariate_normal(meanHam[0], covHam).logpdf
    spamClass = multivariate_normal(meanSpam[0], covSpam).logpdf
    for x in testData:
        prob = [hamClass(x), spamClass(x)]
        if prob[0] > prob[1]:
            guesses.append(0)
        else:
            guesses.append(1)

    # coefficientHam = (float(-16) * math.log(2 * math.pi)) - .5*math.log(detHam)
    # coefficientSpam = (float(-16) * math.log(2 * math.pi)) - .5*math.log(detSpam)
    # for i in range(0, len(testData)):
    #     maxi = float("-inf")
    #     guess = -1
    #     email = testData[i]
        
    #     diff = np.subtract(email, meanHam)
    #     diff = np.transpose(diff)
    #     exp = np.transpose(diff) * float(-.5)
    #     exp = np.dot(exp, invHam)
    #     exp = np.dot(exp, diff)
    #     exp = exp + coefficientHam
    #     maxi = max(maxi, exp)
    #     guess = 0

    #     diff = np.subtract(email, meanSpam)
    #     diff = np.transpose(diff)
    #     exp = np.transpose(diff) * float(-.5)
    #     exp = np.dot(exp, invSpam)
    #     exp = np.dot(exp, diff)
    #     exp = exp + coefficientSpam
    #     if exp > maxi:
    #         guess = 1
    #     guesses.append(guess)
    # sys.stdout = open("spamPredictions.txt", "w")
    print("Id,Category")
    for i in range(0, len(guesses)):
        print(str(i + 1) + "," + str(guesses[i]))

def Q6():
    housing = io.loadmat("data/housing_dataset/housing_data")
    Xtrain = housing["Xtrain"]
    Ytrain = housing["Ytrain"]
    Xval = housing["Xvalidate"]
    Yval = housing["Yvalidate"]

    ones = np.zeros((19440, 1), dtype= np.float64)
    for i in range(0, 19440):
        ones[i] += 1
    Xtrain = np.append(Xtrain, ones, axis = 1)
    onesVal = np.zeros((1200, 1), dtype= np.float64)
    for i in range(0, 1200):
        onesVal[i] += 1
    Xval = np.append(Xval, onesVal, axis = 1)
    
    w = np.zeros((19440, 1), dtype= np.float64)
    w = np.dot(np.transpose(Xtrain), Xtrain)
    w = np.linalg.inv(w)
    w = np.dot(w, np.transpose(Xtrain))
    w = np.dot(w, Ytrain)
    print(w)

    predictions = np.zeros((1200, 1), dtype = np.float64)
    maxi = float("-inf")
    mini = float("inf")
    for i in range(0, len(Xval)):
        prediction = np.dot(Xval[i], w)
        maxi = max(maxi, prediction)
        mini = min(mini, prediction)
        predictions[i] = prediction
    print("maximum prediction: ", maxi, "minimum predicition: ", mini)
    
    RSS = 0
    for i in range(0, len(Yval)):
        difference = predictions[i] - Yval[i]
        difference = math.pow(difference, 2)
        RSS += difference 
    print("RSS value: ", RSS)
    print("average error: ", math.sqrt(RSS/float(19440)))

    indices = []
    for i in range(0, len(w) - 1):
        indices.append(i)
    indices = np.asarray(indices)
    plt.xlabel("index")
    plt.ylabel("w value")
    plt.plot(indices, w[0:len(w) - 1], 'ro')
    plt.show()

    trainingResiduals = []
    maxi = float("-inf")
    mini = float("inf")
    buckets = [0] * 10
    summation = 0
    for i in range(0, len(Xtrain)):
        difference = np.dot(Xtrain[i], w) - Ytrain[i]
        trainingResiduals.append(difference)
        summation += difference
        maxi = max(maxi, difference)
        mini = min(mini, difference)
    totalSpan = abs(maxi - mini)
    print("avg of residual: ", summation /float(len(Xtrain)))
    for i in range(0, len(Xtrain)):
        difference = np.dot(Xtrain[i], w) - Ytrain[i]
        dist = abs(difference - mini)
        width = totalSpan/float(10)
        bucket = int(dist / width)
        buckets[bucket - 1] += 1
    print("width",width)
    print(buckets)
    print("max", maxi, "min", mini)
    scatter = []
    for i in range(0, 10):
        for j in range(0, buckets[i]):
            scatter.append(i)
    plt.hist(scatter, bins = 9)
    plt.show()

#==============================================
#MAIN RUNS
# q2Plot()
# Q3()
# getPriors()
# plotQ5d(0)
# plotQ5d(1)
# getKagglePredictionsDigits()
# spamClassifier()
# Q6()
