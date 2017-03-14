"""
@author Daniel Wong
Version 3 of the effort task
"""
import pygame
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from libmpdev import MP150

#parse parameter file
raw = open("V3params.txt")
lines = []
paramsList = []
for line in raw:
    lines.append(line)
for i in range(1, len(lines)):
    params = lines[i]
    params = params.split(",")
    paramsList.append(params)

choiceOutputs = []
totalTrials = len(paramsList)
timeToChoose = -1
totalWinnings = 0

subjectID = raw_input("Enter ID: ")
calibrationPrompt = ""
while calibrationPrompt not in ["Y", "N"]:
    calibrationPrompt = raw_input("Is calibration necessary? Enter Y or N: ")
calibrationBool = True
maxEffort = ""
if calibrationPrompt == "Y":
    calibrationBool = True
else:
    maxEffortPrompt = raw_input("Enter max effort: (To tester: 3 is a good starting point for average person) ")
    maxEffort = float(maxEffortPrompt)
    calibrationBool = False


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

def recordChoiceOutput():
    filename = "choiceOutputV3_SID:" + subjectID + ".txt"
    file = open(filename, "w")
    file.write("trial,choice,outcome,timeToChoose,averageForce")
    file.write("\n")
    for entry in choiceOutputs:
        for i in range(0, len(entry)):
            if i != (len(entry) - 1):
                file.write(str(entry[i]) + ",")
            else:
                file.write(str(entry[i]))
        file.write("\n")
    file.close()

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
            plt.show()
            plt.pause(6)
            text0.remove()
            if goodTrials != 1:
                text.remove()
            if goodTrials == 1:
                text01.remove()
            if goodTrials > 1:
                text3.remove()

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
        text = ax.text(1.2, 180, 'READY...', \
                fontsize = 24, color = 'red')
        while not quitted:
            if timer > 1.5 and ticker == 1:
                text.remove()
                text1 = ax.text(1, 180, 'SQUEEZE! ', \
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
        
        print("MVC for this trial: ", max(candidates))
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
    text1 = ax.text(.2, 1.3, "Remember! Squeeze the device harder to play a higer lottery,", \
            fontsize = 18, color = 'black')
    text4 = ax.text(.2, 1.2, "and less for a lower lottery.", \
            fontsize = 18, color = 'black')
    text2 = ax.text(.2, 1.1, "The game should take about 30 minutes.", \
            fontsize = 18, color = 'black')
    text3 = ax.text(.2, 1.0, "Good luck!", \
            fontsize = 18, color = 'black')
    plt.show()
    plt.pause(6)

    print(acceptedMVCs, "acceptedMVCs")
    filename = "calibrationV3_SID:" + subjectID + ".txt" 
    file = open(filename, "w")
    file.write("calibration average forces: " + str([x / float(100) for x in acceptedMVCs]))
    file.write("\n")
    plt.close()

    return float(np.mean(acceptedMVCs) / 100) #to reaccomodate for squeeze game force being measured directly as oppossed to multiplying force by 100



def drawChooseScreen(disp, trialNumber):
    def drawLeft():
        font = pygame.font.Font(pygame.font.get_default_font(), 22)  
        #draw text for lottery
        prob = int(paramsList[trialNumber - 1][5])  
        textsurf = font.render(str(prob) + "%" + " chance of ", False, (255,255,255))
        disp.blit(textsurf,(50,130))
        font = pygame.font.Font(pygame.font.get_default_font(), 26)         
        moneysurf = font.render("$" + str(paramsList[trialNumber - 1][1]), False, (0,255,0))
        disp.blit(moneysurf, (50, 170))
        #draw blue 0% line
        pygame.draw.rect(disp, (0,0,255), (170 + 2, 170 + height - 8, width - 4, 5), 0)
        percentsurf = font.render("0%", False, (255, 255, 255))
        disp.blit(percentsurf, (170 - 50, 170 + height - 20))
        pygame.display.flip()
    def drawRight():
        font = pygame.font.Font(pygame.font.get_default_font(), 22)  
        #draw text for lottery   
        prob = int(paramsList[trialNumber - 1][5])  
        textsurf = font.render(str(prob) + "%" + " chance of ", False, (255,255,255)) 
        disp.blit(textsurf,(610,130))
        font = pygame.font.Font(pygame.font.get_default_font(), 26)         
        moneysurf = font.render("$" + str(paramsList[trialNumber - 1][2]), False, (0,255,0))
        disp.blit(moneysurf, (610, 170))
        #draw blue %mvc line
        percentage = float(paramsList[trialNumber - 1][3])/float(100)
        converse = 1 - percentage
        pygame.draw.rect(disp, (0,0,255), (730 + 2, 170 + (converse * height) - 6, width -4, 5), 0)
        #fill up until %mvc line
        pygame.draw.rect(disp, (255,0,0), (730 + 3, 170 + height - height * percentage, width - 6, height * percentage - 3), 0)
        percentsurf = font.render(str(paramsList[trialNumber - 1][3]) + "%", False, (255, 255, 255))
        disp.blit(percentsurf, (730 - 70, 170 + converse * height - 20))
        pygame.display.flip()
    
        

    global timeToChoose
    chooseDuration = float(paramsList[trialNumber - 1][4])
    endTime = time.time() + chooseDuration
    initTime = time.time()
    while time.time() < endTime:
        width = 80
        height = 300
        timeWidth = 500

        #draw timebar
        pygame.draw.rect(disp, (255,255,255), (350, 65, timeWidth, 30), 3) 
        timePercentage = (time.time() - initTime) / float(chooseDuration)
        #fill timebar proportional to time
        pygame.draw.rect(disp, (255,255,255), (350, 65, int(timeWidth * timePercentage), 30), 0)

        font = pygame.font.Font(pygame.font.get_default_font(), 26)         
        chooseText = font.render("CHOOSE", False, (255,255,255))
        disp.blit(chooseText, (500, 30))
                                                        #w    h
        pygame.draw.rect(disp, (255,255,255), (40, 120, 300, 400), 3) #left outer rectangle
        pygame.draw.rect(disp, (255,255,255), (170, 170, 80, 300), 3)
        drawLeft()

        pygame.draw.rect(disp, (255,255,255), (600, 120, 300, 400), 3) #right outer rectangle
        pygame.draw.rect(disp, (255,255,255), (730, 170, 80, 300), 3) 
        drawRight()

        arrows = pygame.image.load("arrows.png")
        disp.blit(arrows, (400, 600))

        pygame.display.flip()

        timeToChoose = time.time() - initTime

        for event in pygame.event.get():                               
            if event.type == pygame.KEYUP and event.key == 50:
                print("2 pressed")
                disp.fill((0,0,0))
                pygame.draw.rect(disp, (255, 255, 0), (600, 120, 300, 400), 3)
                pygame.draw.rect(disp, (255,255,255), (40, 120, 300, 400), 3) #left outer rectangle
                pygame.draw.rect(disp, (255,255,255), (170, 170, 80, 300), 3) 
                pygame.draw.rect(disp, (255,255,255), (730, 170, 80, 300), 3) 
                drawLeft()
                drawRight()
                pygame.display.flip()
                pygame.time.wait(2000)
                return 2

            if event.type == pygame.KEYDOWN and event.key == 49:
                print("1 pressed")
                disp.fill((0,0,0))
                pygame.draw.rect(disp, (255,255,0), (40, 120, 300, 400), 3) #left outer rectangle
                pygame.draw.rect(disp, (255,255,255), (170, 170, 80, 300), 3) 
                pygame.draw.rect(disp, (255,255,255), (600, 120, 300, 400), 3) #right outer rectangle
                pygame.draw.rect(disp, (255,255,255), (730, 170, 80, 300), 3) 
                pygame.display.flip()
                drawLeft()
                drawRight()
                pygame.time.wait(2000)
                return 1
    return -1

def displayFailureToChoose(disp):
    global totalWinnings
    disp.fill((0,0,0))
    font = pygame.font.Font(pygame.font.get_default_font(), 26)         
    endtext = font.render("You've failed to choose a lottery in time ", False, (255,255,255))
    disp.blit(endtext, (375, 270))
    endtext = font.render("and have lost $1. ", False, (255,255,255))
    disp.blit(endtext, (375, 370))
    pygame.display.flip()
    pygame.time.wait(3000)
    totalWinnings = max(0, totalWinnings - 1)

def displayFixation(disp, choice):
    disp.fill((0,0,0))
    fix = pygame.image.load("fixation.png")
    disp.blit(fix,(0,0))
    font = pygame.font.Font(pygame.font.get_default_font(), 35) 
    if choice == 2:
        textsurf = font.render("PREPARE TO SQUEEZE...", False, (255,255,255))
        disp.blit(textsurf, (400, 230))
    else:
        textsurf = font.render("DO NOT SQUEEZE!", False, (255,255,255))
        disp.blit(textsurf, (430, 230))
    pygame.display.flip()
    pygame.time.wait(3000)


    
def squeezeGame(disp, MP, trialNumber, choice, mvc):
    
    displayFixation(disp, choice)

    disp.fill((0,0,0))
    if choice == 1:
        font = pygame.font.Font(pygame.font.get_default_font(), 26) 
        noSqueezeText = font.render("DO NOT SQUEEZE" , False, (255,255,255))
        disp.blit(noSqueezeText, (480, 30))
    initTime = time.time()
    endTime = time.time() + 10
    width = 130
    height = 340
    timeWidth = 500
    hoveredTime = 0

    def displaySqueezeSuccess():
        pygame.draw.rect(disp, (0,0,0), (477, 25, 310, 50), 0)
        pygame.display.flip()
        successText = font.render("SUCCESS", False, (255,255,255))
        disp.blit(successText, (550, 30))
        pygame.draw.rect(disp, (0,255,0), (350, 130, timeWidth, 30), 0)
        pygame.display.flip()
        pygame.time.wait(5000)
        outcome = random.random()
        print("outcome", outcome, "target", float(paramsList[trialNumber - 1][5]) / 100)
        # if outcome == 0:
        if outcome < float(paramsList[trialNumber - 1][5]) / 100:
            displayOutcome(disp, trialNumber, choice, converse, "win")
            choiceOutputs.append([trialNumber,choice, "win", timeToChoose,np.mean(forces)])
            recordChoiceOutput()
        else:
            displayOutcome(disp, trialNumber, choice, converse, "lose")
            choiceOutputs.append([trialNumber,choice, "lose", timeToChoose,np.mean(forces)])
            recordChoiceOutput()
        return
    def displaySqueezeFailure():
        failureText = font.render("Squeeze Failure", False, (255,255,255))
        disp.blit(failureText, (510, 30))
        pygame.draw.rect(disp, (255,0,0), (350, 130, timeWidth, 30), 0)
        pygame.display.flip()
        pygame.time.wait(5000)
        displayOutcome(disp, trialNumber, choice, converse, "lose")
        choiceOutputs.append([trialNumber,choice, "lose", timeToChoose, np.mean(forces)])
        recordChoiceOutput()
    
    forces = []
    while time.time() < endTime:
        pygame.draw.rect(disp, (255,255,255), (300, 100, 600, 500), 3) #outer container rectangle
        pygame.draw.rect(disp, (255,255,255), (610, 190, width, height), 3) #inner rectangle
        pygame.draw.rect(disp, (255,255,255), (350, 130, timeWidth, 30), 3) #time bar
        timePercentage = (time.time() - initTime) / float(10)
        print(timePercentage)
        #fill timebar proportional to time
        pygame.draw.rect(disp, (255,255,255), (350, 130, int(timeWidth * timePercentage), 30), 0)
        
        force = MP.sample()[0] + .245 #real force value to use
        forces.append(force)
        # force = timePercentage * 3 #fake increasing force value for testing

        #mask with black rectangle 
        pygame.draw.rect(disp, (0,0,0), (613, 193, width - 6, height - 6), 0)
        #if pulsing adjust to: 
        # pygame.draw.rect(disp, (0,0,0), (613, 195, width - 6, height - 6), 0)
        
        #draw force bar (filled to top)
        #constants added so fill bar doesn't overlap with outer white rectangle
        k = abs(force / float(mvc)) #to prevent red bar from falling below 0% line
        pygame.draw.rect(disp, (255,0,0), (613, 190 + height - height * k, width - 6, height * k - 3), 0)
        
        
        #draw percentage text
        font = pygame.font.Font(pygame.font.get_default_font(), 26) 
        if choice == 2:
            percentage = float(paramsList[trialNumber - 1][3])/float(100)
            converse = 1 - percentage
            percentsurf = font.render(str(paramsList[trialNumber - 1][3]) + "%", False, (255,255,255))
        else: 
            percentage = 0
            converse = 1 - percentage
            percentsurf = font.render(str(0) + "%", False, (255,255,255))
        disp.blit(percentsurf, (610 - 100, 190 + (converse * height) - 6))

        #draw %mvc blue line
        if choice != 1:
            pygame.draw.rect(disp, (0,0,255), (612, 190 + (converse * height) - 6, width - 4, 10), 0)
        
        # #==========================================
        # #edits to enforce 3s hover for squeeze success
        if force >= mvc * percentage:
             initHoverTime = time.time()

        while force >= mvc * percentage:
             if time.time() >= endTime: #in case time expires while user is hovering above threshold, we should still exit because time is up
                 displaySqueezeFailure()
                 return 
             force = MP.sample()[0] + .245
             print("force: ", force)
             forces.append(force)
             #mask with black rectangle 
             pygame.draw.rect(disp, (0,0,0), (613, 193, width - 6, height - 6), 0)
             
             k = min(abs(force) / float(mvc), 1) #to prevent red bar from falling below 0% line, and from exceeding topline
             pygame.draw.rect(disp, (255,0,0), (613, 190 + height - height * k, width - 6, height * k - 3), 0)
             #draw %mvc blue line
             if choice != 1:
                 pygame.draw.rect(disp, (0,0,255), (612, 190 + (converse * height) - 6, width - 4, 10), 0)
             #fill timebar proportional to time
             timePercentage = (time.time() - initTime) / float(10)
             pygame.draw.rect(disp, (255,255,255), (350, 130, int(timeWidth * timePercentage), 30), 0)
             pygame.display.flip()
             hoveredTime = time.time() - initHoverTime
             if hoveredTime > 3 and time.time() - initTime >= 5: #enforce at least 5 seconds of squeeze time
                 displaySqueezeSuccess()
                 return
        # #==========================================
        #print(force, mvc * percentage, "AAA")

        if choice == 1 and time.time() - initTime >= 5:
            displaySqueezeSuccess()
            return
            
        pygame.display.flip()

    displaySqueezeFailure()



def displayOutcome(disp, trialNumber, choice, converse, outcome):
    global totalWinnings
    percentage = 1 - converse
    disp.fill((0,0,0))
    width = 130
    height = 340
    pygame.draw.rect(disp, (255,255,0), (300, 100, 600, 500), 3) #outer container rectangle
    pygame.draw.rect(disp, (255,255,255), (610, 190, width, height), 3) #inner rectangle

    #draw %mvc blue line
    pygame.draw.rect(disp, (0,0,255), (612, 190 + (converse * height) - 6, width - 4, 10), 0) #blue %mvc line

    #fill up until blue %mvc line
    if percentage != 0:
        pygame.draw.rect(disp, (255,0,0), (613, 190 + height - height * (percentage) + 4, width - 6, height * percentage - 6), 0)

    moneyAmount = ""
    #draw percentage text
    font = pygame.font.Font(pygame.font.get_default_font(), 26) 
    if choice == 2:
        moneyAmount = paramsList[trialNumber - 1][2]
        percentsurf = font.render(str(paramsList[trialNumber - 1][3]) + "%", False, (255,255,255))
    else: 
        moneyAmount = paramsList[trialNumber - 1][1]
        percentsurf = font.render(str(0) + "%", False, (255,255,255))
    disp.blit(percentsurf, (610 - 80, 190 + (converse * height) - 6))

    #draw probability and money texts
    prob = int(paramsList[trialNumber - 1][5])  
    textsurf = font.render(str(prob) + "%" + " chance of ", False, (255,255,255))
    disp.blit(textsurf, (350, 150))
    moneysurf = font.render("$" + str(moneyAmount), False, (0,255,0))
    disp.blit(moneysurf, (350, 200))
    
    if outcome == "win":
        totalWinnings += float(moneyAmount)
        #draw green check mark
        greenCheck = pygame.image.load("greenCheck2.png")
        disp.blit(greenCheck, (920, 260))

        #draw "YOU WIN!" text
        wintext = font.render("YOU WIN!", False, (255,255,255))
        disp.blit(wintext, (550, 30))

        pygame.display.flip()
        pygame.time.wait(5000)
    else: #if outcome == "lose"
        #draw red cross
        redCross = pygame.image.load("redCross2.png")
        disp.blit(redCross, (920, 260))

        #draw "YOU LOSE" text
        wintext = font.render("YOU LOSE", False, (255,255,255))
        disp.blit(wintext, (550, 30))

        pygame.display.flip()
        pygame.time.wait(5000)

def displayFinish(disp):
    global totalWinnings
    disp.fill((0,0,0))
    font = pygame.font.Font(pygame.font.get_default_font(), 26)         
    endtext = font.render("You've finished the experiment. ", False, (255,255,255))
    disp.blit(endtext, (375, 270))

    totalWinnings = totalWinnings * .2

    if totalWinnings == 0:
         endtext = font.render("You won $0.00.", False, (255,255,255))
    else:
        totalWinnings = str(totalWinnings)
        if totalWinnings < 1 and len(totalWinnings) == 2:
            totalWinnings += "0"
        elif "." not in totalWinnings:
            totalWinnings += ".00"
        elif len(totalWinnings) == 3:
            totalWinnings += "0"
        endtext = font.render("You won $" + str(totalWinnings) + ".", False, (255,255,255))
    disp.blit(endtext, (375, 370))
    endtext = font.render("Please get the experimenter.", False, (255,255,255))
    disp.blit(endtext, (375, 470))
    pygame.display.flip()
    pygame.time.wait(10000)

def runGame():
    pygame.init()
    RES = (1200,700)    # Screen resolution for PyGame
    disp = pygame.display.set_mode(RES, pygame.RESIZABLE)

    try:
        MP = MP150()               
        print("MP150 live")
    except:                                 
        print("no MP; using random values")
        MP = fakeMP()
    if calibrationBool:
        mvc = calibrate(MP)
    else:
        mvc = maxEffort
    # mvc = 3 #.7
    pygame.display.set_caption("Effort Game")
    pygame.time.wait(1000)
    trialNumber = 1

    


    while trialNumber <= totalTrials:
        disp.fill((0,0,0))
        pygame.display.flip()
        choice = drawChooseScreen(disp, trialNumber)
        if choice == -1: #failed to pick lottery
            displayFailureToChoose(disp)
            trialNumber += 1
            continue
        squeezeGame(disp, MP, trialNumber, choice, mvc)
        trialNumber += 1
        #for pause screen and update participant that preliminary rounds are over
        if trialNumber == 6:
            disp.fill((0,0,0))
            while True:
                escaped = False
                for event in pygame.event.get(): 
                    if event.type == pygame.KEYUP and event.key == 32:
                        print("space pressed")
                        escaped = True
                        break
                    font = pygame.font.Font(pygame.font.get_default_font(), 32)  
                    text = font.render("Now you will also play the 50/50 lotteries.", False, (255,255,255))
                    text2 = font.render(" Some trials will have a 100% chance of winning, but most will be 50/50.", False, (255,255,255))
                    text3 = font.render("When you're ready to start, press SPACE.", False, (255,255,255))
                    disp.blit(text, (270, 220))
                    disp.blit(text2, (20, 300)) 
                    disp.blit(text3, (280, 370)) 
                    pygame.display.flip()
                if escaped:
                    break 

    displayFinish(disp)


runGame()


#to change blue bar to be %mvc = top of blue line (probably will need to change red fill to adjust slightly): 
#pygame.draw.rect(disp, (0,0,255), (612, 190 + (converse * height) + 6, width - 4, 10), 0)
#rectangles start at top left 

#To do: 
#
