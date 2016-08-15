import numpy as np
import math
import random
from scipy import io
from sklearn import preprocessing
import sys
from matplotlib import pyplot as plt

def convertLabel(lab):
    ar = np.zeros(10)
    ar[lab] = 1
    return ar

def convertVector(v):
    for i in range(0, len(v)):
        if v[i] == 1:
            return i

data = io.loadmat("dataset/train")
X = data["train_images"]
print("original images shape 1", X.shape)
intLabs = data["train_labels"]
LABELS = []
for i in range(0, len(intLabs)):
    LABELS.append(convertLabel(intLabs[i]))
LABELS = np.asarray(LABELS)
images = []
cardinality = 60000

#get the data
n = len(X)
X =  X.reshape(( n * n, -1 ))
images = X.T #was this here during training? yes
print("images shape 1", images.shape) #60k x 784

#visualize an image!
# one = np.reshape(images[20000],(28,28))
# plt.imshow(one, interpolation='nearest')
# plt.show()
# print(LABELS[20000])

#add L2 norm
images = preprocessing.normalize(images, norm='l2')

#center data
# means = np.mean(images, 0)
# for i in range(0, len(images)):
#     for j in range(0, len(images[0])):
#         images[i][j] = images[i][j] - means[j]


#fictitious dimension for data
xFict = np.ones((len(images), 785))
xFict[:,:-1] = images
images = np.copy(xFict)

#shuffle images and labels
rand = []
newImages = []
newLabels = []
for i in range(0, len(images)):
    rand.append(i)
random.shuffle(rand)
for j in range(0, len(rand)):
    newImages.append(images[rand[j]])
    newLabels.append(LABELS[rand[j]])
newImages = np.asarray(newImages)
newLabels = np.asarray(newLabels)
images = newImages
LABELS = newLabels

np.save("images.npy", images)




TEST = io.loadmat("dataset/test")
TESTIMAGES = TEST["test_images"]
TESTIMAGES = np.reshape(TESTIMAGES, (10000, 784))

# #add L2 norm
TESTIMAGES = preprocessing.normalize(TESTIMAGES, norm='l2')
#center data
# testMeans = np.mean(TESTIMAGES, 0)
# for i in range(0, len(TESTIMAGES)):
#     for j in range(0, len(TESTIMAGES[0])):
#         TESTIMAGES[i][j] = TESTIMAGES[i][j] - testMeans[j]
#fict dimension
xFict = np.ones((len(TESTIMAGES), 785))
xFict[:,:-1] = TESTIMAGES
TESTIMAGES = np.copy(xFict)
print("test images final shape", TESTIMAGES.shape)

class Neural_Network(object):
    def __init__(self):        
        #Define Hyperparameters
        self.inputLayerSize = 784 + 1
        self.outputLayerSize = 10
        self.hiddenLayerSize = 200 + 1

        #define layers and activations
        self.x = [] #input layer
        self.h = [] #post-tanh values in hidden layer
        self.z = [] #post sigmoid function values in output layer
        self.u = [] #pre-tanh function values in hidden layer
        self.uPrime = [] #pre-sigmoid function values in ouput layer

        #Weights (parameters)
        self.V = np.random.normal(0, .01, (785, 200))
        self.W = np.random.normal(0, .01, (201, 10))
        # self.V = np.load("V3.npy")
        # self.W = np.load("W3.npy")

    def sigmoid(self, z):
        #Apply sigmoid activation function to scalar, vector, or matrix
        return 1 / (1 + np.exp(-z))

    def sigmoidPrime(self, z):
    #Derivative of sigmoid function
        return np.exp(-z) / ((1 + np.exp(-z))**2)

    # def sigmoid(self, z):
    #     return np.log(1 + np.exp(z))

    # def sigmoidPrime(self, z):
    #     return 1 / (1 + np.exp(-z))
    
    def tanh(self, z):
        return np.tanh(z)

    def tanhPrime(self, z):
        return 1 - (self.tanh(z))**2
        
    def forward(self, X, batch):
        """
        batch will be true if we pass in a batch of images for X to compute y hat
        """
        #Propagate inputs though network
        self.u = np.dot(X, self.V)
        self.h = self.tanh(self.u)
        # self.uPrime = np.dot(hDim, self.W)
        hcopy = np.copy(self.h)
        if batch == True:
            hFict = np.ones((len(self.h), 201))
            hFict[:, :-1] = hcopy
            self.uPrime = np.dot(hFict, self.W)
        else:
            self.uPrime = np.dot(np.append(hcopy, [1]), self.W)
        # self.uPrime = np.dot(self.h, self.W)
        yHat = self.sigmoid(self.uPrime) 
        return yHat

    def costFunction(self, X, y):
        #Compute squared error cost for given X, y, use weights already stored in class.
        self.yHat = self.forward(X, True)
        J = 0.5 * np.sum(np.square(y - self.yHat))
        return J

    def costFunctionPrime(self, X, y, batch):
        """
        Compute derivative with respect to V and W for a given sample X and label y
        implement batch functionality later for batch gradient descent
        """
        # dJdW = 201x10  # dJdV = 785x201  # delta2 = 1x201 but want 1x200???
         # dJdV = want 785x200 
        if batch == False:
            self.yHat = self.forward(X, batch)
            delta3 = np.multiply(- (y - self.yHat), self.sigmoidPrime(self.uPrime))
            dJdW = np.dot(np.reshape(np.append(self.h, [1]), (1, 201)).T, np.reshape(delta3, (1, 10)))

            delta2 = np.dot(delta3, np.delete(self.W.T, np.s_[-1:], 1)) * (1 - (self.tanh(self.h))**2)####self.h does not have fict dimension
            dJdV = np.dot(np.reshape(X, (1, 785)).T, np.reshape(delta2, (1, 200)))####
            return dJdV, dJdW #dV is mostly 0s

    def crossEntropyCost(self, X, y):
        self.yHat = self.forward(X, True)
        J = -1 * np.sum(y * np.log(self.yHat) + ((1 - y) * np.log(1 - self.yHat)))
        return J

    def crossEntropyCostPrime(self, X, y, batch):
        self.yHat = self.forward(X, batch)
        delta3 = -1 * np.multiply((y/self.yHat) - ((1-y)/(1-self.yHat)), self.sigmoidPrime(self.uPrime))
        dJdW = np.dot(np.reshape(np.append(self.h, [1]), (1, 201)).T, np.reshape(delta3, (1, 10)))
        delta2 = np.dot(delta3, np.delete(self.W.T, np.s_[-1:], 1)) * (1 - (self.tanh(self.h))**2)####self.h does not have fict dimension
        dJdV = np.dot(np.reshape(X, (1, 785)).T, np.reshape(delta2, (1, 200)))####
        return dJdV, dJdW #dV is mostly 0s


    def trainNeuralNetwork(self, images, labels, validation, validationLabels, costType):
        print("V: ", self.V)
        print("W: ", self.W)
        errorRate = 1
        decayStart = -1
        DONE = False
        iters = 0
        epsilon =  0.1
        trainingErrors = []
        itersList = []
        validationAccuracies = []
        costs = []
        while iters < 820000: #820k full cycle
            #STOCHASTIC SINGLE IMAGE
            sample = images[iters % len(images)] 
            y = labels[iters % len(images)] 
            if costType == "squared":
                dv, dw = self.costFunctionPrime(sample, y, False) 
            else:
                dv, dw = self.crossEntropyCostPrime(sample, y, False)
            self.V = self.V - float(epsilon) * dv #subtract every element in vector v by dv
            self.W = self.W - float(epsilon) * dw #subtract every element in vector w by dw
            iters += 1
            decayStart += 1
            
            if DONE == False and errorRate < .08:
                epsilon = epsilon * .6
                DONE = True
                decayStart = 1
            if DONE == True and (decayStart % (5 * cardinality) == 0):
                epsilon = epsilon * .6
            
            if costType == "entropy" and errorRate < .11:
                epsilon = .01
           
            if iters % 40000 == 0:
                if costType == "squared":
                    cost = self.costFunction(images, labels)
                    costs.append(cost)
                else:
                    cost = self.crossEntropyCost(images, labels) #PASSING IN ALL IMAGES TO COMPUTE COST
                    costs.append(cost)
                print("COST", cost) 
            
            if iters % 40000 == 0:
                preds = self.predict("", validation)
                mistakes = 0
                trueLabelsDigits = []
                for l in validationLabels:
                    trueLabelsDigits.append(convertVector(l))
                for i in range(0, len(preds)):
                    if preds[i] != trueLabelsDigits[i]:
                        mistakes += 1
                errorRate = mistakes / float(len(preds))
                print("iteration: ", iters, "epsilon: ", epsilon, " val error rate: ", mistakes / float(len(preds)))
                validationAccuracies.append(1 - errorRate)
            
            if iters % 40000 == 0:
                preds = self.predict("", images)
                mistakes = 0
                trueLabelsDigits = []
                for l in labels:
                    trueLabelsDigits.append(convertVector(l))
                for i in range(0, len(preds)):
                    if preds[i] != trueLabelsDigits[i]:
                        mistakes += 1
                errorRate = mistakes / float(len(preds))
                print("iteration: ", iters, "epsilon: ", epsilon, " training error rate: ", mistakes / float(len(preds)))
                trainingErrors.append(errorRate)
                itersList.append(iters)
        
        # np.save("V3.npy", self.V)
        # np.save("W3.npy", self.W)

        plt.xlabel("iteration")
        plt.ylabel("cost")
        plt.plot(itersList, costs, 'ro')
        plt.show()

        plt.xlabel("iteration")
        plt.ylabel("training error")
        plt.plot(itersList, trainingErrors, 'ro')
        plt.show()

        plt.xlabel("iteration")
        plt.ylabel("validation accuracy")
        plt.plot(itersList, validationAccuracies, 'ro')
        plt.show()

        
        return self.V, self.W

    def predict(self, weights, images):
        """
        returns predictions as integers
        """
        predictions = []
        for image in images:
            pred = self.forward(image, False)
            maxi = float('-inf')
            digit = -1
            for i in range(0, len(pred)):
                if pred[i] > maxi:
                    maxi = pred[i]
                    digit = i
            predictions.append(digit)
        return predictions

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def validate(costType):
    
    # validation = np.load("validation.npy")
    # validationLabels = np.load("validationLabels.npy")
    # training = np.load("training.npy")
    # trainingLabels = np.load("trainingLabels.npy")
    
    rand = []
    for i in range(0, cardinality):
        rand.append(i)
    random.shuffle(rand)
    training = []
    trainingLabels = []
    validation = []
    validationLabels = []
    for r in range(0, len(rand)):
        if r < 10000: #original 1000
            validation.append(images[rand[r]])
            validationLabels.append(LABELS[rand[r]])#[0])
        else:
            training.append(images[rand[r]])
            trainingLabels.append(LABELS[rand[r]])#[0])
    validation = np.asarray(validation)
    validationLabels = np.asarray(validationLabels)
    training = np.asarray(training)
    trainingLabels = np.asarray(trainingLabels)


    np.save("validation.npy", validation)
    np.save("validationLabels.npy", validationLabels)
    np.save("training.npy", training)
    np.save("trainingLabels.npy", trainingLabels)

    if costType == "squared":
        NN = Neural_Network()
        NN.trainNeuralNetwork(training, trainingLabels, validation, validationLabels, "squared")
    else:
        NN = Neural_Network()
        NN.trainNeuralNetwork(training, trainingLabels, validation, validationLabels, "entropy")

    predictions = NN.predict("", validation)
    mistakes = 0
    trueLabelsDigits = []
    for l in validationLabels:
        trueLabelsDigits.append(convertVector(l))
    print("true labels as digits", trueLabelsDigits)
    for i in range(0, len(predictions)):
        if predictions[i] != trueLabelsDigits[i]:
            mistakes += 1
    print("error rate: ", mistakes / float(len(predictions)))
    return NN



def computeGradient(NN):
    """
    for computing gradient of V
    """
    a = images[1]
    W = np.copy(NN.W)
    V = np.copy(NN.V)
    grads = []
    for i in range(0, len(a)):
        aCopy = np.copy(a)
        aCopy[i] = aCopy[i] + .00001
        el1 = costFunction1(NN, V, W, a, LABELS[1])
        aCopy[i] = aCopy[i] - .00002
        el2 = costFunction1(NN, V, W, a, LABELS[1])
        numerator = el1 - el2
        # print(numerator)
        # if numerator != 0:
        #     print("nonzero")
        grads.append(numerator / float(2 * .00001))
    return np.asarray(grads)

def forward1(NN, V, W, X, batch):
        #Propagate inputs though network
        u = np.dot(X, V)
        h = NN.tanh(u)
        # print("h shape", self.h.shape)
        
        # self.uPrime = np.dot(hDim, self.W)
        copy = np.copy(h)
        # print(batch)
        if batch == True:
            hFict = np.ones((len(h), 201))
            hFict[:, :-1] = copy
            uPrime = np.dot(hFict, W)
        else:
            uPrime = np.dot(np.append(copy, [1]), W)
        # self.uPrime = np.dot(self.h, self.W)
        yHat = NN.sigmoid(uPrime) 
        return yHat

def costFunction1(NN, V, W, X, y):
    #Compute squared error cost for given X, y, use weights already stored in class.
    yHat = forward1(NN, V, W, X, False)
    J = 0.5 * np.sum(np.square(y-yHat))
    return J

def getKaggle(NN, images):
    predictions = NN.predict("",images)
    sys.stdout = open("digitPredictions2.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + "," + str(predictions[i]))


# getKaggle(Neural_Network(), TESTIMAGES)

NN = validate("entropy")
NN = validate("squared")

