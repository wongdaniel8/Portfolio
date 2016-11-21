#return mvc

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time
from PIL import Image      
import random

class fakeMP:
        
    def sample(self):
            global fakeDataPoint          
            return [random.uniform(0,2),0,0]
            # fakeDataPoint += .02
            # return [fakeDataPoint, 0, 0] 
    def start_recording(self):
            return 0
    def stop_recording(self):
            return 0
    def close(self):
            return 0



try:
    MP = MP150()               
    print("MP150 live")
except:                                 
    print("no MP; using random values")
    MP = fakeMP()

quitted = False
timer = 0.0
waittime = .005
nump = 0
quitted = False
mvc = -1
candidatemvc = -1
candidates = []
plt.ion()
goodTrials = 0
clicked = False
counter = 0
acceptedMVCs = []
accepted = False
lastMVC = -1

def accept(event):
    global goodTrials
    global clicked 
    global acceptedMVCs
    global accepted
    clicked = True
    goodTrials += 1
    accepted = True

    # quitted = True
def reject(event):
    counter = counter 

plt.axis([0, 10, 0, 5])


global clicked
while goodTrials < 3:
    plt.clf()
    plt.axis([0, 10, 0, 5])
    quitted = False
    timer = 0.0
    clicked = False
    accepted = False

    while not quitted:
        if counter > 0: 
            x = [1,2,3,4,5,6]
            y = [lastMVC, lastMVC, lastMVC, lastMVC, lastMVC, lastMVC]
            plt.plot(x, y, color="black", linewidth = 2.0, dashes = [1,2,3,4])
            plt.show()
        candidate = MP.sample()[0]
        print("candidate", candidate)
        candidates.append(candidate)
        plt.scatter(timer, candidate)
        # plt.plot(timer, candidate, '-o')

        candidates.append(candidate)
        plt.pause(.05)
        plt.show()
        
        time.sleep(waittime)
        timer = timer + waittime * 5
        if timer > .5: #8.0:
            quitted = True
    axReject = plt.axes([0.4, 0.9, 0.5, 0.075])
    axAccept = plt.axes([0.81, 0.05, 0.1, 0.075])
    while clicked == False:
        bAccept = Button(axAccept, 'Accept')
        button1 = bAccept.on_clicked(accept)
        bReject = Button(axReject, 'Previous')
        button2 = bReject.on_clicked(reject)
        plt.pause(1)
        plt.show()
        if accepted == True:
            averageMVC = np.mean(candidates)
            acceptedMVCs.append(averageMVC)
            lastMVC = averageMVC
            counter += 1
print(acceptedMVCs, "acceptedMVCs")


#change axis of trials after the first to adjust for mvc, add dashed line

