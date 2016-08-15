from scipy import io
import numpy as np
import random
import math
from matplotlib import pyplot as plt
import sys
def Q1():
    housing = io.loadmat("housing_dataset/housing_data")
    training = housing["Xtrain"]
    tlabels = housing["Ytrain"]
    testing = housing["Xvalidate"]
    vlabels = housing["Yvalidate"]
    #set up cross validation sets
    indices = []
    for i in range(0, 19440):
        indices.append(i)
    random.shuffle(indices)
    sets = []
    temp = []
    for i in range(0, 19440):
        temp.append(indices[i])
        if len(temp) == 1944:
            sets.append(temp)
            temp = []

    #tune to find value of lambda
    riskSum = 0
    for i in range(0, 10):
        train = []
        tl = []
        validation = []
        vlabs = []
        for j in range(0, 10):
            if j == i: 
                for k in sets[i]:
                    validation.append(training[k])
                    vlabs.append(tlabels[k])
            else: 
                for k in range(0, 1944):
                    train.append(training[sets[j][k]])
                    tl.append(tlabels[sets[j][k]])
        train = np.asarray(train)

        X = train
        lambda1 = .001

        I1 = np.identity(len(X))
        w = np.dot(np.transpose(X), tl)
        left = np.dot(np.transpose(X), X)
        left = np.add(left, lambda1 * np.identity(len(left)))
        w = np.dot(np.linalg.inv(left), w)
        predictions = np.dot(validation, w)
        RSS = 0
        for i in range(0, len(vlabs)):
            RSS += math.pow((predictions[i] - vlabs[i]), 2)
            
        alpha = np.mean(vlabs)
        risk = np.dot(validation, w)
        risk = np.add(risk, alpha * np.reshape(np.ones(len(validation)), (1944, 1)))
        risk = np.subtract(risk, vlabs)
        risk = np.dot(np.transpose(risk), risk)
        risk = risk + lambda1 * np.dot(np.transpose(w), w)
        riskSum += risk

        print("RSS", RSS)
    print("risk sum", riskSum)


    #apply to validation set 
    X = training
    lambda1 = .001 #LAMBDA VALUE DOESNT CHANGE RSS WHY? (UP TO CERTAIN ORDERS OF MAGNITUDE)
    I1 = np.identity(len(X))
    w = np.dot(np.transpose(X), tlabels)
    left = np.dot(np.transpose(X), X)
    left = np.add(left, lambda1 * np.identity(len(left)))
    w = np.dot(np.linalg.inv(left), w)

    predictions = np.dot(testing, w)
    RSS = 0
    for i in range(0, len(vlabels)):
        RSS += math.pow((predictions[i] - vlabels[i]), 2)
    print("RSS validation: ", RSS)
    print(RSS)
    print("w: ", w)  

        
    indices = []
    for i in range(0, len(w)):
        indices.append(i)
    indices = np.asarray(indices)
    plt.xlabel("index")
    plt.ylabel("w value")
    plt.plot(indices, w[0:len(w)], 'ro')
    plt.show()



 #////////////////////////////////////////////////////////
def sigmoid(gamma):
    return 1 / float((1 + math.exp(-1 * gamma)))

def empiricalRisk(w, X, y, n):
    R = 0 
    for i in range(0, n):
        R += float(y[i]) * math.log(sigmoid(np.dot(np.transpose(w), X[i])))
        R += float((1 - y[i])) * math.log(1 - float(sigmoid(np.dot(np.transpose(w), X[i]))))
    R = R * -1
    return R

def Q2(): 
    R = 0 
    w0 = np.asarray([-2, 1, 0])
    y = [1, 1, 0, 0]
    X = np.asarray([[0, 3, 1], [1, 3, 1], [0, 1, 1], [1, 1, 1]])
    w = w0
    
    batchSum = 0
    innerSum = 0
    print("risk w0: ", empiricalRisk(w0, X, y, 4))

    mu = []
    dots = np.dot(w, np.transpose(X))
    for element in dots:
        mean = sigmoid(element)
        mu.append(mean)
    print("mu0: ", mu)

    for i in range(0, 4):
        innerSum = y[i] - sigmoid(np.dot(np.transpose(X[i]), w))
        innerSum = np.dot(innerSum, X[i])
        batchSum += innerSum
    w1 = np.add(w0, batchSum)

    print("w1: ", w1)

    print("risk w1: ", empiricalRisk(w1, X, y, 4))

    mu = []
    dots = np.dot(w, np.transpose(X))
    for element in dots:
        mean = sigmoid(element)
        mu.append(mean)
    print("mu1: ", mu)

    batchSum = 0
    innerSum = 0
    for i in range(0, 4):
        innerSum = y[i] - sigmoid(np.dot(np.transpose(X[i]), w1))
        innerSum = np.dot(innerSum, X[i])
        batchSum += innerSum
    w2 = np.add(w1, batchSum)
    print("w2: ", w2)
    print("risk w2: ", empiricalRisk(w2, X, y, 4))



#////////////////////////////////////////////////////////

def Q3():
    data = io.loadmat("spam_dataset/spam_data")
    print(data)
    X = data["training_data"]
    Y = data["training_labels"][0]
    validation = data["test_data"]

    standardized = np.copy(X)
    standardized = np.asarray(X, dtype=np.float64)
    columnAvgs = {}
    columnStds = {}
    for i in range(0, 32):
        summat = 0
        elements = []
        for j in range(0, 5172):
            summat += X[j][i]
            elements.append(X[j][i])
        columnStds[i] = np.std(elements)
        columnAvgs[i] = summat
    for key in columnAvgs.keys():
        columnAvgs[key] = columnAvgs[key] / float(5172)
    for i in range(0, 5172):
        for k in range(0, 32):
            standardized[i][k] -= float(columnAvgs[k])
            standardized[i][k] = standardized[i][k] / float(columnStds[k])

    logarized = np.copy(X)
    logarized = np.asarray(logarized, dtype = np.float64)
    for i in range(0, 5172):
        for j in range(0, 32):
            logarized[i][j] = math.log(logarized[i][j] + .1, 10)

    binarized = np.copy(X)
    binarized = np.asarray(X, dtype = np.float64)
    for i in range(0, 5172):
        for j in range(0, 32):
            if binarized[i][j] > 0:
                binarized[i][j] = 1
            else: 
                binarized[i][j] = 0

    #/////////////////////////////////////////////////////////////////
    #BATCH///////////////////////////
    for v in range(0, 3):
    # for v in range(1, 2):
        w = np.zeros(32)
        pX = np.copy(X)
        title = ""
        risks = []
        if v == 0: 
            title = "Standardized Preprocess"
            pX = standardized
            epsilon = .000001
        if v == 1:
            title = "Logarithmic Preprocess"
            pX = logarized
            epsilon = .00001
        if v == 2:
            title = "Binarized Preprocess"
            pX = binarized
            epsilon = .000001


        count = 0
        # iterations = 1500
        iterations = 3000
        print("reached2")


        for i in range(0, iterations):
            summation = 0
            for j in range(0, 5172):
                innerSum = Y[j] - sigmoid(np.dot(np.transpose(pX[j]), w))
                innerSum = np.dot(innerSum, pX[j])
                summation += innerSum
            w = np.add(w, epsilon * summation)
        
        print("reached3")

        #graph results
            count += 1
            if count % 10 == 0:
                risks.append(empiricalRisk(w, pX, Y, 5172))
        print("final risk: ", risks[len(risks) - 1])
        indices = []
        for z in range(0, len(risks)):
            indices.append(z)
        plt.xlabel("iteration")
        plt.ylabel("risk")
        plt.title(title)
        plt.plot(indices, risks, 'ro')
        plt.show()

        #for kaggle
        # if v == 1:
        #     sys.stdout = open("dummy2.txt", "w")
        #     print("Id, Category")
        #     predictions = []
        #     for f in range(0, len(validation)):
        #         value = sigmoid(np.dot(w, validation[f]))
        #         if value > .5:
        #             prediction = 1
        #         else: 
        #             prediction = 0
        #         print(str(f + 1) + ", " + str(prediction))
        #         predictions.append(prediction)

#/////////////////////////////////////////////////////////////////
#STOCHASTIC
    # for v in range(2, 3):
    for v in range(0, 3):
        w = np.zeros(32)
        pX = np.copy(X)
        title = ""
        risks = []
        if v == 0: 
            title = "Standardized Preprocess"
            pX = standardized
        if v == 1:
            title = "Logarithmic Preprocess"
            pX = logarized
        if v == 2:
            title = "Binarized Preprocess"
            pX = binarized

        #values geq .1 yielded math overflow error
        epsilon = .001 
        originalEps = .01
        iterations = 2000
        count = 0
        for i in range(0, iterations):
            # epsilon = originalEps / float(i + 1) ######UNCOMMENT TO DECAY LEARNING
            summation = 0
            j = random.randint(0, 5171)
            innerSum = Y[j] - sigmoid(np.dot(np.transpose(pX[j]), w))
            innerSum = np.dot(innerSum, pX[j])
            summation += innerSum
            w = np.add(w, epsilon * summation)
            count += 1

        #graph results
            if count % 10 == 0:
                risk = empiricalRisk(w, pX, Y, 5172)
                risks.append(risk)
        
        print("last", risks[len(risks) - 1])
        indices = []
        for z in range(0, len(risks)):
            indices.append(z)
        plt.xlabel("iteration (/10)")
        plt.ylabel("risk")
        plt.title(title)
        plt.plot(indices, risks, 'ro')
        plt.show()


#/////////////////////////////////////////////////////////////////
#POLY AND LINEAR KERNEL



def linearKernel(x, z, rho):
    res = np.dot(np.transpose(x), z)
    res += rho
    return res

def kernel(x, z, rho):
    res = np.dot(np.transpose(x), z)
    res += rho
    return math.pow(res, 2)

def kernelSigmoid(a, size, X, Xi, kernelMat, index, rho):
    summation = 0
    for i in range(0, size):
        summation += a[i] * kernelMat[i][index] 
    return sigmoid(summation)

def kernelRisk(a, X, y, n, kernelMat, rho):
    R = 0 
    for i in range(0, n):
        summation = 0
        for j in range(0, n):
            summation += a[j] * kernelMat[j][i] 
        kernSig = sigmoid(summation)
        R += y[i] * float(math.log(kernSig))
        R += (1 - y[i]) * math.log(1 - float(kernSig))
    R = R * -1
    return R


data = io.loadmat("spam_dataset/spam_data")
TRAININGDATA = data["training_data"]
TRAININGLABELS = data["training_labels"][0]
VALIDATION = data["test_data"]

def kernelLogisticRidge(X, y, validX, validY, ktype, n):
    a = np.zeros(n)
    kernelMatrix = np.zeros((n, n))
    risks = []
    valRisks = []
    rho = .1
    # rho = 10
    alpha = .0001
    lambda1 = .001
    # epsilon = .0001 #gave bad val poly
    epsilon = .00001 #good poly and linear, risks train 2206 with 2500 iters (poly)

    iterations = 3000

    for i in range (0, n):
        for j in range(0, n):
            if ktype == "linear":
                kernelMatrix[i][j] = linearKernel(X[i], X[j], rho)
            else:
                kernelMatrix[i][j] = kernel(X[i], X[j], rho)

    print("reached2")
    count = 0
    for q in range(0, iterations):
        count += 1
        i = random.randint(0, n - 1)
        for z in range(0, n):
            if z == i:
                a[i] = a[i] - epsilon * float(lambda1) * a[i] + epsilon * (y[i] - sigmoid(np.dot(kernelMatrix, a)[i]))
            else: 
                a[z] = a[z] - epsilon * float(lambda1) * a[z]
    
     
    # sys.stdout = open("dummyKernel.txt", "w")
    # for f in range(0, len(VALIDATION)):
    #     hsum = 0
    #     for g in range(0, len(a)):
    #         hsum += a[g] * float(kernelMatrix[g][f])
    #     h = sigmoid(hsum)
    #     if h > .5:
    #         prediction = 1
    #     else:
    #         prediction = 0
    #     print(str(f + 1) + "," + str(prediction))

        
    #primal/////////////////////////////////////
    # w = np.dot(np.transpose(X), a)
    # sys.stdout = open("dummyKernel.txt", "w")
    # print("Id,Category")
    # predictions = []
    # for f in range(0, len(VALIDATION)):
    #     value = sigmoid(np.dot(w, VALIDATION[f]))
    #     if value > .5:
    #         prediction = 1
    #     else: 
    #         prediction = 0
    #     print(str(f + 1) + "," + str(prediction))
    #/////////////////////////////////////////////


        if count % 150 == 0:
            risk = kernelRisk(a, X, y, n, kernelMatrix, rho)
            risks.append(risk)
            print(risk)

            valRisk = kernelRisk(a, validX, validY, 1724, kernelMatrix, rho)
            valRisks.append(valRisk)
            print(valRisk)

    # plot training risk
    print("final risk: ", risks[len(risks) - 1])
    indices = []
    for z in range(0, len(risks)):
        indices.append(z)
    plt.xlabel("iteration")
    plt.ylabel("risk")
    if ktype == "poly":
        plt.title("poly kernel training risk")
    else:
        plt.title("linear kernel training risk")
    plt.plot(indices, risks, 'ro')
    plt.show()

    #plot validation risk
    print("final val risk: ", valRisks[len(valRisks) - 1])
    indices = []
    for z in range(0, len(valRisks)):
        indices.append(z)
    plt.xlabel("iteration")
    plt.ylabel("validation risk")
    if ktype == "poly":
        plt.title("poly kernel validation risk")
    else:
        plt.title("linear kernel validation risk")
    plt.plot(indices, valRisks, 'ro')
    plt.show()

    return risks



def crossValidateLogisticRidge():
    #crossValidation 
    indices = []
    for i in range(0, 5172):
        indices.append(i)
    random.shuffle(indices)
    sets = []
    temp = []
    for i in range(0, 5172):
        temp.append(indices[i])
        if len(temp) == 1724:
            sets.append(temp)
            temp = []

    for m in range(0, 3):
        #set up X, y, and validations
        X = []
        y = []
        validX = []
        validY = [] 
        for t in range(0, 3):
            if t == m:
                for index in sets[t]:
                    validY.append(TRAININGLABELS[index])
                    validX.append(TRAININGDATA[index])
            else:
                for index in sets[t]:
                    X.append(TRAININGDATA[index])
                    y.append(TRAININGLABELS[index])

        # preprocess
        X = np.asarray(X)
        logarized = np.copy(X)
        logarized = np.asarray(logarized, dtype = np.float64)
        for i in range(0, 3448):
            for j in range(0, 32):
                logarized[i][j] = math.log(logarized[i][j] + .1, 10)
        X = logarized

        validLog = np.copy(validX)
        validLog = np.asarray(validLog, dtype = np.float64)
        for i in range(0, 1724):
            for j in range(0, 32):
                validLog[i][j] = math.log(validLog[i][j] + .1, 10)
        validX = validLog

        # polyRiskVal = kernelLogisticRidge(validX, validY, validX, validY, "poly", 1724) #to compute poly val risk
        polyRisks = kernelLogisticRidge(X, y, validX, validY, "poly", 3448) #1724???
        linearRisks = kernelLogisticRidge(X, y, validX, validY, "linear", 3448)
        



# Q1()
# Q2()
# Q3()
# crossValidateLogisticRidge() #all of kernel parts for q3

