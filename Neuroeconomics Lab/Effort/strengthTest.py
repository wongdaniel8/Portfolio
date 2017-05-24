"""
@author Daniel Wong
Calibration file to be used for the effort task. Records the user's MVC and writes this value to a file 
called calibrationV3_(SID).txt to be extracted in EffortV3.py
"""
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from libmpdev import MP150



subjectID = raw_input("Enter ID: ")

class fakeMP:
    def sample(self):
        global fakeDataPoint          
        return [random.uniform(0,2),0,0]
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

def calibrate(MP):
    global goodTrials
    global clicked 
    global acceptedMVCs
    global accepted
    global counter
    global clicked
    global lastValidAverage
    global highestMVC 
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
    maxHeight = 150
    lastValidAverage = -2
    highestMVC = -1

    def accept(event):
        global goodTrials
        global clicked 
        global acceptedMVCs
        global accepted
        clicked = True
        goodTrials += 1
        accepted = True
        
    def reject(event):
        global counter
        global clicked
        clicked = True
        counter = counter 

    plt.axis([0, 7, 0, maxHeight])
    fig=plt.figure(1)
    fig.set_size_inches(12, 10, forward = True)
    ax=fig.add_subplot(111)
    ax.set_xlim(0,7)
    text = ax.text(.1, 90, 'Calibration Phase: prepare to squeeze as hard as you can for 7 seconds', \
                    fontsize = 18, color = 'black')
    plt.show()
    plt.pause(5)
                  
    while goodTrials < 3:
        plt.clf()    
        plt.axis([0, 7, 0, maxHeight])
        quitted = False
        timer = 0.0
        clicked = False
        
        x=0
        y=0 
        fig=plt.figure(1)
        ax=fig.add_subplot(111)
        ax.set_xlim(0,7)
        line,=ax.plot(x,y,'ko-', color = "black")
        fig.set_size_inches(12, 10, forward = True)
        temp = highestMVC
        if lastValidAverage > highestMVC:
            highestMVC = lastValidAverage

        if goodTrials > 0 and accepted == True:
            plt.axis([0, 7, 0, 150])
            if goodTrials == 1:
                 text0 = ax.text(.2, 100, 'Average force on current trial: ' + str(int(lastValidAverage)), \
                    fontsize = 18, color = 'black')
                 text01 =  ax.text(.2, 90, 'Exert a force greater than ' + str(int(lastValidAverage)) + " to receive an extra $1.00", \
                    fontsize = 18, color = 'black')
            else:
                
                text = ax.text(.2, 120, 'Bonus target: ' + str(int(temp)), \
                    fontsize = 18, color = 'black')
                text0 = ax.text(.2, 110,  'Average force on current trial: ' + str(int(lastValidAverage)), \
                    fontsize = 18, color = 'black')
            if goodTrials > 1 and lastValidAverage > lastMVC:
                text3 = ax.text(.2, 100, 'Congratulations! Average force is greater than target: You earned $1.00', \
                        fontsize = 18, color = 'black')
            if goodTrials > 1 and lastValidAverage <= lastMVC:
                text3 = ax.text(.2, 100, 'You did not exceed your maximum and did not receive the extra $1.00', \
                        fontsize = 18, color = 'black')
            if goodTrials == 2:
                text4 = ax.text(.2, 80, 'try one more time!', \
                        fontsize = 18, color = 'black')
                text5 = ax.text(.2, 70, 'Exert a force greater than ' + str(int(lastValidAverage)) + " to receive an extra $1.00", \
                    fontsize = 18, color = 'black')
            plt.show()
            plt.pause(6)
            text0.remove()
            if goodTrials != 1:
                text.remove()
            if goodTrials == 1:
                text01.remove()
            if goodTrials > 1:
                text3.remove()
                text4.remove()
                text5.remove()

        accepted = False
    
        if goodTrials > 0:
                if lastValidAverage > lastMVC:
                    lastMVC = lastValidAverage
                plt.axis([0, 7, 0, lastMVC + 50])
                maxHeight = lastMVC + .5
                x = [0,1,2,3,4,5,6,7,8,9]
                y = [highestMVC,highestMVC, highestMVC, highestMVC, highestMVC, highestMVC, highestMVC,highestMVC,highestMVC,highestMVC]
                plt.plot(x, y, color="black", linewidth = 1.0, dashes = [1,2,3,4])
                
                plt.show()

        
        ticker = 1 #used so that first if statement in while loop is executed only once
        text = ax.text(1.2, 100, 'READY...', \
                fontsize = 24, color = 'red')
        while not quitted:
            if timer > 1.5 and ticker == 1:
                text.remove()
                text1 = ax.text(1, 100, 'SQUEEZE! ', \
                fontsize = 24, color = 'green')
                ticker += 1
                


            x = [2, 2, 2, 2, 2, 2, 2, 2]
            y = [0, 20, 40, 60, 80, 100, 120, 140]
            plt.plot(x, y, color="black", linewidth = 1.0, dashes = [1,2,3,4])
            x = [5, 5, 5, 5, 5, 5, 5, 5]
            y = [0, 20, 40, 60, 80, 100, 120, 140]
            plt.plot(x, y, color="black", linewidth = 1.0, dashes = [1,2,3,4])

            candidate = (MP.sample()[0] + .245) * 100
            # dynamically adjust y axis if max value exceeded
            if goodTrials == 0 and candidate > maxHeight:
                plt.axis([0, 7, 0, maxHeight * 2])
            if goodTrials > 0 and candidate > maxHeight:
                plt.axis([0, 7, 0, maxHeight * 2])
                maxHeight = maxHeight * 2
            if candidate < 0:
                candidate = 0
           
            x = np.concatenate((line.get_xdata(), [(timer)]))
            y = np.concatenate((line.get_ydata(), [(candidate)]))
            line.set_data(x, y)

            if timer > 2 and timer < 5:
                candidates.append(candidate)
            plt.pause(.05)
           
            time.sleep(waittime)
            timer = timer + waittime * 65 
            if timer > 7: #8.0:
                quitted = True
        
        print("max MVC for this trial: ", max(candidates))
        print("average MVC for this trial: ", np.mean(candidates))

        axReject = plt.axes([0.61, 0.9, 0.15, 0.08])
        axAccept = plt.axes([0.28, 0.9, 0.15, 0.08])
        while clicked == False:
            bAccept = Button(axAccept, 'Accept')
            button1 = bAccept.on_clicked(accept)
            bReject = Button(axReject, 'Reject')
            button2 = bReject.on_clicked(reject)
            plt.pause(1)
            plt.show()
            if accepted == True:
                averageMVC = np.mean(candidates)
                lastValidAverage = averageMVC
                acceptedMVCs.append(averageMVC)
                counter += 1
        candidates = []
                
    #to display final reward updates for calibration
    plt.clf()            
    plt.axis([0, 7, 0, 150])
    fig=plt.figure(1)
    ax=fig.add_subplot(111)
    ax.set_xlim(0,7)
    text01 = ax.text(.2, 110,'Bonus target: ' +  str(int(highestMVC)), \
            fontsize = 18, color = 'black')
    text0 = ax.text(.2, 100,'Average force on current trial: ' + str(int(lastValidAverage)), \
            fontsize = 18, color = 'black')
    if goodTrials > 1 and lastValidAverage > lastMVC:
        text3 = ax.text(.2, 90, 'Congratulations! Average force is greater than target: You earned $1.00', \
                fontsize = 18, color = 'black')
    if goodTrials > 1 and lastValidAverage <= lastMVC:
        text3 = ax.text(.2, 90, 'You did not exceed your maximum and did not receive the extra $1.00', \
                fontsize = 18, color = 'black')
    plt.show()
    plt.pause(6)

    #instructions for squeeze game
    plt.clf()            
    plt.axis([0, 7, 0, 1.5])
    fig=plt.figure(1)
    ax=fig.add_subplot(111)
    ax.set_xlim(0,7)
    text = ax.text(.2, 1.4, "You will now start the game.", \
            fontsize = 18, color = 'black')
    text1 = ax.text(.2, 1.3, "Remember! The lotteries will always be 50/50,", \
            fontsize = 18, color = 'black')
    text4 = ax.text(.2, 1.2, "regardless of whether you choose effort or no-effort.", \
            fontsize = 18, color = 'black')
    text2 = ax.text(.2, 1.1, "The game should take about 35 minutes.", \
            fontsize = 18, color = 'black')
    text3 = ax.text(.2, 1.0, "Good luck!", \
            fontsize = 18, color = 'black')
    plt.show()
    plt.pause(6)

    print(acceptedMVCs, "acceptedMVCs")
    filename = "calibrationV3_" + subjectID + ".txt" 
    file = open(filename, "w")
    file.write(str(float(np.mean(acceptedMVCs) / 100)))
    plt.close()

calibrate(MP)