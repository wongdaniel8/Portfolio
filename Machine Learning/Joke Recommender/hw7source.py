import numpy as np
import math
import random
from scipy import io
from sklearn import preprocessing
import sys
from matplotlib import pyplot as plt
import pickle 
from heapq import heapreplace, heappop, heappush, heappushpop, nsmallest

X = io.loadmat("data/mnist_data/images")
images = X["images"]
images = images.T
images = np.reshape(images, (60000, 784))

testFile = open("data/joke_data/query.txt", "r") #1-indexed
test = [] #list of lists, [person, joke]
for line in testFile.readlines():
    l = line.strip().split(",")
    for i in range(0, len(l)):
        l[i] = int(l[i]) - 1 #to account for 1 indexing
    test.append([l[1], l[2], -1])
    # print(test)

data = io.loadmat("data/joke_data/joke_train")
R = data["train"] #0 indexed
validationFile = open("data/joke_data/validation.txt", "r") #1-indexed

validation = [] #list of lists, [person, joke, rating(0 or 1)]
for line in validationFile.readlines():
    l = line.strip().split(",")
    for i in range(0, len(l)):
        if i == 2:
            l[i] = int(l[i])
        else:
            l[i] = int(l[i]) - 1 #to account for 1 indexing
    validation.append(l)
LABELS = []
for i in range(0, len(validation)):
    LABELS.append(validation[i][2])
sumRatings = np.zeros(len(R[0]))
countsForColumn = np.zeros(len(R[0]))

S = [] #list of valid user, joke pairs that are not NaN

for i in range(0, len(R)):
    for j in range(0, len(R[0])):
        if math.isnan(R[i][j]) == False: 
            S.append((i, j))
            sumRatings[j] += R[i][j]
            countsForColumn[j] += 1
meanRatings = np.zeros(len(R[0]))
for i in range(0, len(meanRatings)):
    meanRatings[i] = sumRatings[i] / float(countsForColumn[i])

# print(validation)

#////////////////////////////////////////////////////////////////////////////

def basicAveragePredictions():
    predictions = []
    errors = 0
    for i in range(0, len(validation)):
        if meanRatings[validation[i][1]] > 0:
            predictions.append(1)
        else:
            predictions.append(0)
    for i in range(0, len(predictions)):
        if predictions[i] != LABELS[i]:
            errors += 1
    print("error rate: ", errors / float(len(predictions)))
    return predictions

#////////////////////////////////////////////////////////////////////////////

for i in range(0, len(R)):
    for j in range(0, len(R[0])):
        if math.isnan(R[i][j]) == True:
            R[i][j] = 0

def kMeans(k, dtype):
    if dtype == "images":
        print("images", images.shape)
        matrix = images
    else:
        matrix = R
    centers = []
    clusters = {} #maps center vector to set of participants
    personToCluster = {} #maps person to cluster
    notDone = True

    #initialize clusters (cardinality = k) to be random points of R 
    for i in range(0, k):
        randomIndex = random.randint(0, len(matrix[0]) - 1)
        clusters[tuple(matrix[randomIndex])] = set()

    #assign points to closest center
    for i in range(0, len(matrix)):
        centers = clusters.keys()
        closestCenter = centers[0]
        minDistance = np.float('inf')
        for j in range(0, len(centers)):
            distance = np.linalg.norm(matrix[i] - np.asarray(centers[j])) 
            if distance < minDistance:
                minDistance = distance
                closestCenter = centers[j]
        clusters[closestCenter].add(i)
        personToCluster[i] = closestCenter

    iters = 0    
    while iters < 50:
        print(iters)
        #update cluster centers
        keys = clusters.keys()
        for key in keys:
            mean = np.zeros(len(matrix[0]))
            for person in clusters[key]:
                mean = mean + matrix[person]
            mean = mean / float(len(clusters[key]))
            clusters[tuple(mean)] = clusters.pop(key)
            for person in clusters[tuple(mean)]:
                personToCluster[person] = tuple(mean)

        #assign points to centers
        notDone = False 
        centers = clusters.keys()
        for i in range(0, len(matrix)):
            closestCenter = tuple(centers[0])
            minDistance = np.float('inf')
            for j in range(0, len(centers)):
                distance = np.linalg.norm(matrix[i] - np.asarray(centers[j])) 
                if distance < minDistance:
                    minDistance = distance
                    closestCenter = tuple(centers[j])
            if closestCenter != personToCluster[i]:
                notDone = True
                clusters[tuple(personToCluster[i])].remove(i) #remove from old cluster
                personToCluster[i] = closestCenter #update 
                clusters[tuple(closestCenter)].add(i) #add to new cluster
        iters += 1

    for key in clusters.keys():
        center = key
        summation = 0
        for point in clusters[key]:
            summation += (np.subtract(matrix[point], center)**2)
    # print("total k means loss: ", summation)
    print("norm: ", np.linalg.norm(summation))

    return clusters, personToCluster


def kMeansPredict(k, dtype):
    clusters, personToCluster = kMeans(k, dtype)
    predictions = []
    errors = 0
    for i in range(0, len(validation)):
        center = personToCluster[validation[i][0]]
        others = list(clusters[center])
        summat = 0
        for person in others:
            summat += R[person][validation[i][1]]
        summat = summat / float(len(others))
        if summat > 0:
            predictions.append(1)
        else:
            predictions.append(0)

    for i in range(0, len(predictions)):
        if predictions[i] != LABELS[i]:
            errors += 1
    print("error rate: ", errors / float(len(predictions)))
    return predictions

def kMeansVisualize(k, dtype):
    clusters, personToCluster = kMeans(k, dtype)
    # clusters = pickle.load(open( "1numberClustersk20.p", "rb"))
    
    # filetype = "1numberClustersk"
    # filetype += str(k) + ".p"
    # print(filetype)
    # pickle.dump(clusters, open(filetype, "wb"))

    for cluster in clusters.keys():
        cluster = np.asarray(cluster)
        cluster = np.reshape(cluster, (28,28))
        plt.imshow(cluster, interpolation='nearest')
        plt.show()

def kNearestNeighborsPredict(k):
    personToHeap = {}
    for i in range(0, 100):
        heap = []
        for j in range(0, k):
            heap.append((float('-inf'), -1))
        personToHeap[i] = heap
    for i in range(0, 100):
        vector = R[i]
        for j in range(0, len(R)):
            if j != i:
                heappushpop(personToHeap[i], (-1 * np.linalg.norm(vector - R[j]), j))
    knearest = {}
    for i in range(0, 100):
        smallest = []
        for j in range(0, k):
            smallest.append(heappop(personToHeap[i]))
        knearest[i] = smallest


    # personToHeap = {}

    # for i in range(0, len(R)):
    #     heap = []
    #     personToHeap[i] = heap

    # for i in range(0, len(R)):
    #     vector = R[i]
    #     for j in range(0, len(R)):
    #         if j != i:
    #             personToHeap[i].append((np.linalg.norm(vector - R[j]), j))
    # knearest = {}
    # for i in range(0, len(R)):
    #     smallest = nsmallest(k, personToHeap[i], key=lambda e:e[0])
    #     knearest[i] = smallest




    predictions = []
    for i in range(0, len(validation)):
        neighbors = knearest[validation[i][0]]
        # print(neighbors)
        summation = 0
        for neighbor in neighbors:
            summation += R[neighbor[1]][validation[i][1]]
        summation = summation / float(len(neighbors))
        if summation < 0:
            predictions.append(0)
        else:
            predictions.append(1)

    errors = 0
    for i in range(0, len(predictions)):
        if predictions[i] != LABELS[i]:
            errors += 1
    print("error rate: ", errors / float(len(predictions)))

            






#////////////////////////////////////////////////////////////////////////////

def SVD(d, testType):
    print("blah")
    # R = np.random.normal(0, .01, (10, 10))
    U, s, V = np.linalg.svd(R, full_matrices=False)
    print(U.shape, s.shape, V.shape, "SHAPES")

    newU = []
    newV = []
    for i in range(0, len(U)):
        newU.append(U[i][0:d])
    for i in range(0, d):
        newV.append(V[i])
    newU = np.asarray(newU)
    newV = np.asarray(newV)
    error = meanSquaredError(newU, newV, testType)
    return error #actually predictions right now


def meanSquaredError(u, v, testType):
    if testType == "validation":
        data = validation
    else:
        data = test
    summation = 0
    predictions = []
    estimR = np.zeros((24983, 100))
    for i in range(0, len(u)):
        for j in range(0, len(v[0])):
            # print(u[i], v.T[j], "vector shapes")
            dot = np.dot(u[i], v.T[j])
            # print(dot)
            summation = summation + (dot - R[i][j])**2
            estimR [i][j] = dot
    print("mean squared error: ", summation)
    predictions = []
    errors = 0
    for i in range(0, len(data)):
        if estimR[data[i][0]][data[i][1]] > 0:
            predictions.append(1)
        else:
            predictions.append(0)
    if testType == "validation":
        for i in range(0, len(predictions)):
            if predictions[i] != LABELS[i]:
                errors += 1
        print("SVD/meanSquared error rate: ", errors / float(len(predictions)))
    return predictions


#////////////////////////////////////////////////////////////////////////////


def minimizeRated(d, testType):
    U = np.random.normal(0, .01, (24983, 100))
    V = np.random.normal(0, .01, (100, 100))
    iters = 2000
    lambda1 = .1
    epsilon = .0002
    #     loss = 0 
    #     for pair in S:
    #         loss += (np.dot(U[pair[0]], V.T[pair[1]]) - R[pair[0]][pair[1]])**2
    #         for pair1 in S:
    #             loss += lambda1 * np.linalg.norm(U[pair1[0]])
    #         for pair1 in S:
    #             loss += lambda1 * np.linalg.norm(V.T[pair1[1]])
    #     print(loss)

    for i in range(0, iters):
        print(i)
        if i % 2 == 0:
            dLdV = np.dot(U.T, 2*(np.dot(U, V) - R)) + (2 * lambda1 * V)
            V = V - epsilon * dLdV
        else:
            dLdU = np.dot(2*(np.dot(U, V) - R), V.T) + (2 * lambda1 * U) 
            U = U - epsilon * dLdU

    summation = 0
    predictions = []
    estimR = np.zeros((24983, 100))
    for i in range(0, len(U)):
        for j in range(0, len(V[0])):
            dot = np.dot(U[i], V.T[j])
            summation = summation + (dot - R[i][j])**2
            estimR [i][j] = dot

    predictions = []

    if testType == "validation":
        errors = 0
        for i in range(0, len(validation)):
            if estimR[validation[i][0]][validation[i][1]] > 0:
                predictions.append(1)
            else:
                predictions.append(0)
        for i in range(0, len(predictions)):
            if predictions[i] != LABELS[i]:
                errors += 1
        print("error rate: ", errors / float(len(predictions)))

    else:
        predictions = []
        for i in range(0, len(test)):
            if estimR[test[i][0]][test[i][1]] > 0:
                predictions.append(1)
            else:
                predictions.append(0)
        print(predictions, len(predictions))
        return predictions



def getKaggle():
    # predictions = SVD(2, "test")
    predictions = minimizeRated(2, "test")
    sys.stdout = open("kaggle_submission1.txt", "w")
    print("Id,Category")
    for i in range(0, len(predictions)):
        print(str(i + 1) + str(",") + str(predictions[i]))



#MAIN RUNS

basicAveragePredictions() 

kMeansVisualize(5, "images")
kMeansVisualize(10, "images")
kMeansVisualize(20, "images")

SVD(2, "validation")
SVD(5, "validation")
SVD(10, "validation")
SVD(20, "validation")

kNearestNeighborsPredict(10)
kNearestNeighborsPredict(100)
kNearestNeighborsPredict(1000)

minimizeRated(2, "test")
getKaggle()
