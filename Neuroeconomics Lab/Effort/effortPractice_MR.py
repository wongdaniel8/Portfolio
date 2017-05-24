"""
@author Daniel Wong
Version 3 of the effort task
"""
import pygame
import time
import random
import numpy as np
import math


#uncomment this part for scanner
pygame.joystick.init()
pygame.joystick.Joystick(0).init()
# Prints the joystick's name
JoyName = pygame.joystick.Joystick(0).get_name()
print ("Name of the joystick:",JoyName)
# Gets the number of axes
JoyAx = pygame.joystick.Joystick(0).get_numaxes()
print( "Number of axis:",JoyAx)
joystick = pygame.joystick.Joystick(0)
# Prints the values for axis0
##while True:
##    pygame.event.pump()
##    print pygame.joystick.Joystick(0).get_axis(0)

    
#parse parameter file
raw = open("V3params-6-practice.txt")
lines = []
paramsList = []
for line in raw:
    lines.append(line)
for i in range(1, len(lines)):
    params = lines[i]
    params = params.split(",")
    paramsList.append(params)

choiceOutputs = []
trialOutput = [] #to record various values we wish to measure for each trial, list is cleared after each trial
totalTrials = len(paramsList)
timeToChoose = -1
totalWinnings = 0

subjectID = raw_input("Enter ID: ")
#user can either set the mvc value manually, or use the one that was recorded in the file calibrationV3_(SID).txt
calibrationPrompt = ""
while calibrationPrompt not in ["Y", "N"]:
    calibrationPrompt = raw_input("Would you like to manually set the mvc? The default mvc will be the one associated with the subject ID \'" + subjectID + "\'. Enter either Y or N:")

useRecordedMVC = True
maxEffort = ""
if calibrationPrompt == "N":
    useRecordedMVC = True
else:
    maxEffortPrompt = raw_input("Enter max effort: (To tester: 3 is a good starting point for average person) ")
    maxEffort = float(maxEffortPrompt)
    useRecordedMVC = False
startTime = time.time()

##uncomment this part for scanner
class fakeMP:
    def sample(self):
            global fakeDataPoint
            pygame.event.pump()
            print("joystick raw: ",joystick.get_axis(0))
            absoluteForce = joystick.get_axis(0) - -.81 -.245
            return [absoluteForce,0,0]
    def start_recording(self):
            return 0
    def stop_recording(self):
            return 0
    def close(self):
            return 0
# class fakeMP:
#     def sample(self):
#             global fakeDataPoint          
#             return [random.uniform(0,2),0,0]
#     def start_recording(self):
#             return 0
#     def stop_recording(self):
#             return 0
#     def close(self):
#             return 0


def recordChoiceOutput(trialNumber):
    global trialOutput
    trialOutput.insert(0, str(trialNumber))
    choiceOutputs.append(trialOutput)
    filename = "effort_MR1_practice_" + str(subjectID) + ".txt"
    file = open(filename, "w")
    # file.write("trial,choice,outcome,timeToChoose,averageForce")
    file.write("trialNumber,trialOnset,decisionTime,choice,squeezeStart,squeezeFinish,outcomeOnset,result,avgSqueeze,maxForce")

    file.write("\n")    
    for entry in choiceOutputs:
        for i in range(0, len(entry)):
            if i != (len(entry) - 1):
                file.write(str(entry[i]) + ",")
            else:
                file.write(str(entry[i]))
        file.write("\n")
    trialOutput = []
    file.close()

def drawChooseScreen(disp, trialNumber):
    def drawLeft():
        font = pygame.font.Font(pygame.font.get_default_font(), 22)  
        #draw text for lottery
        prob = int(paramsList[trialNumber - 1][5])  
        textsurf = font.render(str(50) + "%" + " chance of ", False, (255,255,255))
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
        textsurf = font.render(str(50) + "%" + " chance of ", False, (255,255,255)) 
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
    trialOutput.append(str(time.time() - startTime))
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
                trialOutput.append(str(time.time() - startTime))
                trialOutput.append("2")
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
                trialOutput.append(str(time.time() - startTime))
                trialOutput.append("1")
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
    endTime = time.time() + 6
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
        pygame.time.wait(500)
        outcome = random.random()
        print("outcome", outcome, "target", float(paramsList[trialNumber - 1][5]) / 100)
        if outcome < float(paramsList[trialNumber - 1][5]) / 100:
            displayOutcome(disp, trialNumber, choice, converse, "win")
        else:
            displayOutcome(disp, trialNumber, choice, converse, "lose")
        trialOutput.append(str((np.mean(forces) / float(mvc)) * 100) + "%" )
        trialOutput.append(str((np.max(forces) / float(mvc)) *100) +  "%")
        recordChoiceOutput(trialNumber)
        return
    def displaySqueezeFailure():
        failureText = font.render("Squeeze Failure", False, (255,255,255))
        disp.blit(failureText, (510, 30))
        pygame.draw.rect(disp, (255,0,0), (350, 130, timeWidth, 30), 0)
        pygame.display.flip()
        pygame.time.wait(500)
        displayOutcome(disp, trialNumber, choice, converse, "lose")
        # choiceOutputs.append([trialNumber,choice, "lose", timeToChoose, np.mean(forces)])
        trialOutput.append(str((np.mean(forces) / float(mvc)) * 100) + "%" )
        trialOutput.append(str((np.max(forces) / float(mvc)) *100) +  "%")
        recordChoiceOutput(trialNumber)
    
                
    trialOutput.append(str(time.time() - startTime))
    forces = []
    while time.time() < endTime:
        pygame.draw.rect(disp, (255,255,255), (300, 100, 600, 500), 3) #outer container rectangle
        pygame.draw.rect(disp, (255,255,255), (610, 190, width, height), 3) #inner rectangle
        pygame.draw.rect(disp, (255,255,255), (350, 130, timeWidth, 30), 3) #time bar
        timePercentage = (time.time() - initTime) / float(6)
        #fill timebar proportional to time
        pygame.draw.rect(disp, (255,255,255), (350, 130, int(timeWidth * timePercentage), 30), 0)
        
        force = MP.sample()[0] + .245 #real force value to use
        print("force", force)
        forces.append(force)
        # force = timePercentage * 3 #for faking increasing force value for testing

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
                     trialOutput.append(str(time.time() - startTime))
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
                 timePercentage = (time.time() - initTime) / float(6)
                 pygame.draw.rect(disp, (255,255,255), (350, 130, int(timeWidth * timePercentage), 30), 0)
                 pygame.display.flip()
                 hoveredTime = time.time() - initHoverTime
                 if hoveredTime > 3:# and time.time() - initTime >= 5: #enforce at least 5 seconds of squeeze time
                     trialOutput.append(str(time.time() - startTime))
                     displaySqueezeSuccess()
                     return
            # #==========================================
        #display success squeeze
        if choice == 1 and time.time() - initTime >= 4:
            trialOutput.append(str(time.time() - startTime))
            displaySqueezeSuccess()
            return
        pygame.display.flip()
    
    trialOutput.append(str(time.time() - startTime))
    #display failure to squeeze
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
    textsurf = font.render(str(50) + "%" + " chance of ", False, (255,255,255))
    disp.blit(textsurf, (350, 150))
    moneysurf = font.render("$" + str(moneyAmount), False, (0,255,0))
    disp.blit(moneysurf, (350, 200))
    
            
    trialOutput.append(str(time.time() - startTime))
    if outcome == "win":
        trialOutput.append("win")

        totalWinnings += float(moneyAmount)
        #draw green check mark
        greenCheck = pygame.image.load("greenCheck2.png")
        disp.blit(greenCheck, (920, 260))

        #draw "YOU WIN!" text
        wintext = font.render("YOU WIN!", False, (255,255,255))
        disp.blit(wintext, (550, 30))

        pygame.display.flip()
        pygame.time.wait(int(paramsList[trialNumber - 1][6]))
    else: #if outcome == "lose"
        trialOutput.append("lose")
        #draw red cross
        redCross = pygame.image.load("redCross2.png")
        disp.blit(redCross, (920, 260))

        #draw "YOU LOSE" text
        wintext = font.render("YOU LOSE", False, (255,255,255))
        disp.blit(wintext, (550, 30))

        pygame.display.flip()
        pygame.time.wait(int(paramsList[trialNumber - 1][6]))
    disp.fill((0,0,0))
    fixation = pygame.image.load("fixation.png")
    disp.blit(fixation,(0,0))
    pygame.display.flip()
    pygame.time.wait(int(paramsList[trialNumber - 1][7]))

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

def showExample(disp):
    example = pygame.image.load("practice_preview.png")
    disp.blit(example, (0,0))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():                               
            if event.type == pygame.KEYUP and (event.key == 50 or event.key == 49):
                return 



def runGame():
    global trialOutput
    pygame.init()
    RES = (1200,700)    # Screen resolution for PyGame
    disp = pygame.display.set_mode(RES, pygame.RESIZABLE)

    try:
        MP = MP150()               
        print("MP150 live")
    except:                                 
        print("no MP; using random values")
        MP = fakeMP()
  
    if useRecordedMVC:
        raw = open("calibrationV3_" + subjectID + ".txt")
        print("raw", raw)
        for line in raw:
            print(line)
            mvc = float(line)
        print("MVC = ", mvc)
    else:
        mvc = maxEffort

    pygame.display.set_caption("Effort Game")
    pygame.time.wait(1000)
    showExample(disp)
    # pygame.time.wait(1000)

    trialNumber = 1
    while trialNumber <= totalTrials:
        disp.fill((0,0,0))
        pygame.display.flip()
        choice = drawChooseScreen(disp, trialNumber)
        if choice == -1: #failed to pick lottery
            trialOutput = []
            displayFailureToChoose(disp)
            trialNumber += 1
            continue
        squeezeGame(disp, MP, trialNumber, choice, mvc)
        trialNumber += 1
    displayFinish(disp)

runGame()


#to change blue bar to be %mvc = top of blue line (probably will need to change red fill to adjust slightly): 
#pygame.draw.rect(disp, (0,0,255), (612, 190 + (converse * height) + 6, width - 4, 10), 0)
#rectangles start at top left 
