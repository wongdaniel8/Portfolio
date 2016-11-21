# @author Daniel Wong
# arch -32 python newgame3.py
# CONSTANTS
RES             = (1200,700)	# Screen resolution for PyGame
TOTALSQUEEZE    = 100;		
MAXTIME         = 10;

# IMPORTS
import pygame
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
# from libmpdev import MP150
# import winsound

#READ IN .csv FILE to use as parameters
raw = open("params.txt")
lines = []
paramsList = []
for line in raw:
    lines.append(line)
for i in range(1, len(lines)):
    params = lines[i]
    params = params.split(",")
    for i in range(0, len(params)):
        params[i] = float(params[i])
    paramsList.append(params)
global totalTrials
totalTrials = 100

totalTrials += 1

delayRewardOnset = 1.5
durationDisplayReward = 3
timeUntilBeep = 1
beepDuration = 5000 #measured in milliseconds
squeezeNextTrial = 7

subjectID = raw_input("Enter ID: ")
calibrationPrompt = ""
while calibrationPrompt not in ["Y", "N"]:
    calibrationPrompt = raw_input("Is calibration necessary? Enter Y or N: ")
calibrationBool = True
maxEffort = ""
if calibrationPrompt == "Y":
    calibrationBool = True
else:
    maxEffortPrompt = raw_input("Enter max effort: (To tester 3 is a good starting point for average person) ")
    maxEffort = float(maxEffortPrompt)
    calibrationBool = False

fullscreen = False
fullscreenPrompt = ""
while fullscreenPrompt not in ["Y", "N"]:
    print("Full screen is a PC compatible only tool.")
    fullscreenPrompt = raw_input("Would you like the game full screen? Enter Y or N:")
   
if fullscreenPrompt == "Y":
    fullscreen = True
else:
    fullsreen = False

    
def recordChoiceOutput():
    file = open(subjectID + "choiceOutput.txt", "w")
    file.write("Trial,LR_TARGETL,LR_TARGETH,HR_TARGETL,HR_TARGETH,L_EFFORT_PROB,L_EFFORT_MAG,H_EFFORT_PROB,H_EFFORT_MAG,Subject Choice,Result,AvgForce")
    file.write("\n")
    for entry in choiceOutputs:
        for i in range(0, len(entry)):
            if i != (len(entry) - 1):
                file.write(str(entry[i]) + ",")
            else:
                file.write(str(entry[i]))
        file.write("\n")
    file.close()

    file = open("forceOutput.txt", "w")
    file.write("Time,Force,Event\n")
    for entry in forceOutputs:
        for i in range(0, len(entry)):
            if i != (len(entry) - 1):
                file.write(str(entry[i]) + ",")
            else:
                file.write(str(entry[i]))
        file.write("\n")
    file.close()


############### Class to mimic the squeeze system if the BioPac is not available.
##  if the BioPac is not plugged in, this class creates random numbers to feed to
##    the rest of the program.
##    The member functions mimic those of the BioPac interface
global fakeDataPoint
fakeDataPoint = -.0279
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

############### Class to draw Progress Bar
###  Used for a variety of progress bars

class pb:
		def __init__(self,d,sx,sy,l,h,c):
				self.disp = d
				self.x=sx
				self.y=sy
				self.length=l
				self.height=h
				self.color=c
				self.width=3
				
		def drawLine(self):
				pygame.draw.polygon(self.disp,self.color,  \
				       [[self.x,self.y],  \
				        [self.x+self.length,self.y],   \
				        [self.x+self.length,self.y+self.height],   \
				        [self.x,self.y+self.height]],self.width)               
		
		def drawFill(self,pc):
				pygame.draw.rect(self.disp,self.color,   \
						[[self.x+self.width,self.y+self.width],   \
						[((self.length-2*self.width)*pc),self.height-2*self.width]])
				self.drawLine()

############### Class to draw Graph Bar
class gb:
		def __init__(self,d,sx,sy,l,h,c,mt,f):
				self.disp = d			# PyGame display handle
				self.x=sx			# (x,y) coordinate of upper left hand side of progress bar
				self.y=sy
				self.length=l			# size (length, height) of progress bar
				self.height=h
				self.color=c
				self.width=3			# width of the bounding rectangle, so we can offset our data point plots
				self.points=[]			# data points (might be time, force, average, etc.)
				self.maxt=mt			# Maximum value, so that we can calculate how far apart to space points 
				self.flag=f
				
		# Draw outer rectangle		
		def drawLine(self):
				pygame.draw.polygon(self.disp,self.color,  \
				       [[self.x,self.y],  \
				        [self.x+self.length,self.y],   \
				        [self.x+self.length,self.y+self.height],   \
				        [self.x,self.y+self.height]],self.width)   
				              
		# Add a new data point along with the time it was added
		# The time allows us to plot it properly, between 0 and maxt		                    
		def addpoint(self,point,time):
				self.points.append((point,time))
			    
		def draw(self):
			
				for (p,t) in self.points:
										 
					# Calculate the pixel for the top of the data point.
					# This will be the height the progress bar is at, minus the bounding rectangle (top and bottom, so 2*width)
					# and then the size of the point itself, p.  
					bh = (self.height-(2*self.width))*(p/2)
					bar=bh
					if not self.flag:
						bar=2
					# the x axis offset is the x coordinate for plotting.
					#  This is based on the current time as a percentage of maximum time...offset by the bounding rectangle
					xo = self.x+t/self.maxt*(self.length-2*self.width)
					
					# draw a rectangle for the point.
					pygame.draw.rect(self.disp,self.color,  \
						[[xo,self.y+self.width+(self.height-bh)],  \
						[2,bar]])
						  
				if self.flag:
					self.drawLine()

class wb: # NEW - Class to draw our white bar
                def __init__(self,d,sx,sy,l,h,c,mt,f,rc=(128,128,128),fc=(255,0,0)):
                                self.disp = d                   # PyGame display handle
                                self.x=sx                       # (x,y) coordinate of upper left hand side of progress bar
                                self.y=sy
                                self.length=l                   # size (length, height) of progress bar
                                self.height=h
                                self.color=c
                                self.width=3                    # width of the bounding rectangle, so we can offset our data point plots
                                self.point = 0                  # data points (might be time, force, average, etc.)
                                self.maxt=mt                    # Maximum value, so that we can calculate how far apart to space points 
                                self.flag=f
                                self.rangeColor=rc              # NEW - RGB values for the two grey rectangles
                                self.forceColor=fc              # NEW - RGB values for the long white background rectangle
                                
                # Draw outer rectangle          
                def drawLine(self, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH):
                                pygame.draw.polygon(self.disp,self.color,  \
                                       [[self.x,self.y],  \
                                        [self.x+self.length,self.y],   \
                                        [self.x+self.length,self.y+self.height],   \
                                        [self.x,self.y+self.height]],0) 
                              
                                #Draw LR lines
                                pygame.draw.polygon(self.disp, (173, 168, 169),  \
                                        [[self.x,self.y+self.height*(1-LR_TARGETL)], \
                                        [self.x+self.length,self.y+self.height*(1-LR_TARGETL)], \
                                        [self.x+self.length,self.y+self.height*(1-LR_TARGETH)], \
                                        [self.x,self.y+self.height*(1-LR_TARGETH)]],0)

                                # Draw HR lines
                                pygame.draw.polygon(self.disp,(173, 168, 169),  \
                                        [[self.x,self.y+self.height*(1-HR_TARGETL)], \
                                        [self.x+self.length,self.y+self.height*(1-HR_TARGETL)], \
                                        [self.x+self.length,self.y+self.height*(1-HR_TARGETH)], \
                                        [self.x,self.y+self.height*(1-HR_TARGETH)]],0)


                                              
                # Add a new data point along with the time it was added
                # The time allows us to plot it properly, between 0 and maxt                             
                def addpoint(self,point,time):
                                self.point = point
                                if point < 0:
                                    self.point = 0
                                print("current force: ", point)

                #forceline for MVC
                def drawForceLine(self, MVC):
                        ratio = self.point /float(mvc) 
                        h = 600 - (500 * ratio)
                        pygame.draw.polygon(self.disp,self.forceColor, \
                                [[self.x, h], \
                                [self.x+self.length, h], \
                                [self.x+self.length,h - 5], \
                                [self.x, h - 5]],0)
           
                def draw(self, mvc, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH):            
                                if self.flag:
                                        self.drawLine(LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH)
                                        self.drawForceLine(mvc)
				
				
############### An instance of a SqueezeGame
class SqueezeGame:
        
        def __init__(self,fs,d,f, MP):
                self.fullSqueeze = fs                # total points in game
                self.disp = d                        # pygame display
                self.font = f                        # pygame font
                #  The game involves squeezing until you get to TOTALSQUEEZE
                #     this progressbar shows the % of TOTALSQUEEZE reached
                self.progressbar = pb(d,150,100,600,40,(255,0,0)) #red
                #  Progress bar for time
                self.timebar = pb(d,150,50,600,40,(0,255,0))
                #  Progress bar for current force
                self.forcebar = gb(d,150,150,600,100,(0,0,255),MAXTIME,True)
                # Progress bar for average force from start to now
                self.averagebar=gb(d,150,150,600,100,(255,255,255),MAXTIME,False)
               
                #outer white box
                self.forcebar2 = wb(d,350,100,500,500,(255,255,255),MAXTIME,True) # NEW - coordinates, color for the white/grey bar
                self.mp = MP

        def runGame(self, mvc, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH, L_EFFORT_PROB, L_EFFORT_MAG, H_EFFORT_PROB, H_EFFORT_MAG):
                timeDur = time.time()
                total = 0.0								
                quited = False          				
                self.mp.start_recording()               
                timer = 0.0                    
                waittime = 0.005                    # delay between samples
                nump=0				    # number of samples taken
                allSamples = [] #list of all samples
                avgSample = "null"
                
                #display effort game for user to view before playing
                self.disp.fill((0,0,0))
                textsurf = self.font.render("Time: " + str(int(timer)) + "s", False, (255,255,255))
                pygame.draw.rect(self.disp, (0,0,0), (5, 35, 200, 200), 0)
                self.disp.blit(textsurf,(10,50))    # display the current time
                font = pygame.font.Font(pygame.font.get_default_font(), 42)
                self.forcebar2.draw(mvc,LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH) # NEW - drawing the line
                heightLower = float(self.forcebar2.height*(LR_TARGETH) - self.forcebar2.height*(LR_TARGETL))
                heightUpper = float(self.forcebar2.height*(HR_TARGETH) - self.forcebar2.height*(HR_TARGETL))
               #text for low lottery probability and magnitude
                textsurf = font.render(str(int(100 * L_EFFORT_PROB)) + "%", False, (0,0,255))
                self.disp.blit(textsurf,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower))) #35
                textsurf1 = font.render("$0." + str(int(L_EFFORT_MAG)), False, (37,115,38))
                self.disp.blit(textsurf1,(self.forcebar2.x + 205 ,self.forcebar2.y+self.forcebar2.height*(1-LR_TARGETH)+ (.60 * heightLower)))
                font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                textsurf1 = font1.render("chance of", False, (0,0,255))
                self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.30 * heightLower)))
                #text for high lottery probability and magnitude
                textsurf2 = font.render(str(int(100 * H_EFFORT_PROB)) + "%", False, (0,0,255))
                self.disp.blit(textsurf2,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH) + (.22 * heightUpper))) #35
                textsurf3 = font.render("$0." + str(int(H_EFFORT_MAG)), False, (37,115,38))
                self.disp.blit(textsurf3,(self.forcebar2.x + 205 ,self.forcebar2.y + self.forcebar2.height*(1-HR_TARGETH) + (.60 * heightUpper)))
                textsurf1 = font1.render("chance of", False, (0,0,255))
                self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH)+ (.30 * heightUpper)))
                pygame.display.flip()
                
                endTime = time.time() + timeUntilBeep
                # to give user a chance to see lottery for 6 seconds before interacting with it
                while time.time() < endTime:
                    pass
                # Freq = 1000 # Set Frequency To 2500 Hertz
                # Dur = beepDuration # Set Duration To 1000 ms == 1 second
                # winsound.Beep(Freq,3000)

                timeCounter = 0
                timer = 0.0
                initTime = time.time()
                while not quited:
                        timeCounter += 1
                        sample = self.mp.sample()       
                        if timeCounter % 50 == 0:
                            forceOutputs.append((time.time() - initialTime, self.mp.sample()[0] + .245, ""))
                        nump = nump+1
                        if sample[0] > 0:					
                                total = total + sample[0];	
                        self.disp.fill((0,0,0))     # paint screen black
                        textsurf = self.font.render("Time: " + str(int(timer)) + "s", False, (255,255,255))
                        pygame.draw.rect(self.disp, (0,0,0), (5, 35, 200, 200), 0)
                        self.disp.blit(textsurf,(10,50))   
                        samp = .245 + sample[0]
                        if fullscreen == False:
                                  pygame.draw.rect(self.disp, (0,0,0), (1000, 50, 200, 200), 0)
                                  fontForce = pygame.font.Font(pygame.font.get_default_font(), 22)
                                  forceText = fontForce.render("Force x100: "+str(int(samp * 100)), False, (255,255,255))
                                  self.disp.blit(forceText, (1000, 50))
                        
                        self.forcebar2.addpoint(samp, timer) # displaying force as the red line
                        allSamples.append(samp)
                        self.forcebar2.draw(mvc,LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH) 
                        self.averagebar.addpoint(total/nump,timer)  
                        font = pygame.font.Font(pygame.font.get_default_font(), 42)
                        heightLower = float(self.forcebar2.height*(LR_TARGETH) - self.forcebar2.height*(LR_TARGETL))
                        heightUpper = float(self.forcebar2.height*(HR_TARGETH) - self.forcebar2.height*(HR_TARGETL))

                       #text for low lottery probability and magnitude
                        textsurf = font.render(str(int(100 * L_EFFORT_PROB)) + "%", False, (0,0,255))
                        self.disp.blit(textsurf,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower))) #35
                        textsurf1 = font.render("$0." + str(int(L_EFFORT_MAG)), False, (37,115,38))
                        self.disp.blit(textsurf1,(self.forcebar2.x + 205 ,self.forcebar2.y+self.forcebar2.height*(1-LR_TARGETH)+ (.60 * heightLower)))
                        font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                        textsurf1 = font1.render("chance of", False, (0,0,255))
                        self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.30 * heightLower)))
                        
                        
                        #text for high lottery probability and magnitude
                        textsurf2 = font.render(str(int(100 * H_EFFORT_PROB)) + "%", False, (0,0,255))
                        self.disp.blit(textsurf2,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH) + (.22 * heightUpper))) #35
                        textsurf3 = font.render("$0." + str(int(H_EFFORT_MAG)), False, (37,115,38))
                        self.disp.blit(textsurf3,(self.forcebar2.x + 205 ,self.forcebar2.y + self.forcebar2.height*(1-HR_TARGETH) + (.60 * heightUpper)))
                        textsurf1 = font1.render("chance of", False, (0,0,255))
                        self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH)+ (.30 * heightUpper)))
              
                        #logic to exit after hovering 3 seconds while in a lottery
                        while (samp > LR_TARGETL * float(mvc)) and (samp < LR_TARGETH * float(mvc))  and not quited:
                              timeCounter += 1
                              if timeCounter % 50 == 0:
                                  forceOutputs.append((time.time() - initialTime, self.mp.sample()[0] + .245, ""))
                              nump = nump+1
                              textsurf = self.font.render("Time: " + str(int(timer)) + "s", False, (255,255,255))
                              time.sleep(waittime)
                              timer = timer + waittime * 5

                              if timer > 7.05: 
                                  quited = True
                                  break
                              pygame.draw.rect(self.disp, (0,0,0), (5, 35, 200, 200), 0)
                              self.disp.blit(textsurf,(10,50))  

                              samp = self.mp.sample()[0] + .245
                              if fullscreen == False:
                                  pygame.draw.rect(self.disp, (0,0,0), (1000, 50, 200, 200), 0)
                                  fontForce = pygame.font.Font(pygame.font.get_default_font(), 22)
                                  forceText = fontForce.render("Force x100: "+str(int(samp * 100)), False, (255,255,255))
                                  self.disp.blit(forceText, (1000, 50))
                              
                              self.forcebar2.addpoint(samp, timer) # displaying force as the red line
                              self.forcebar2.draw(mvc,LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH)
                              allSamples.append(samp)       
                              self.averagebar.addpoint(total/nump,timer)	# add new force point, and display average
                              font = pygame.font.Font(pygame.font.get_default_font(), 42)
                              heightLower = float(self.forcebar2.height*(LR_TARGETH) - self.forcebar2.height*(LR_TARGETL))
                              heightUpper = float(self.forcebar2.height*(HR_TARGETH) - self.forcebar2.height*(HR_TARGETL))

                              #text for low lottery probability and magnitude
                              textsurf = font.render(str(int(100 * L_EFFORT_PROB)) + "%", False, (0,0,255))
                              self.disp.blit(textsurf,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower))) #35
                              textsurf1 = font.render("$0." + str(int(L_EFFORT_MAG)), False, (37,115,38))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 205 ,self.forcebar2.y+self.forcebar2.height*(1-LR_TARGETH)+ (.60 * heightLower)))
                              font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                              textsurf1 = font1.render("chance of", False, (0,0,255))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.30 * heightLower)))
                                
                                
                              #text for high lottery probability and magnitude
                              textsurf2 = font.render(str(int(100 * H_EFFORT_PROB)) + "%", False, (0,0,255))
                              self.disp.blit(textsurf2,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH) + (.22 * heightUpper))) #35
                              textsurf3 = font.render("$0." + str(int(H_EFFORT_MAG)), False, (37,115,38))
                              self.disp.blit(textsurf3,(self.forcebar2.x + 205 ,self.forcebar2.y + self.forcebar2.height*(1-HR_TARGETH) + (.60 * heightUpper)))
                              textsurf1 = font1.render("chance of", False, (0,0,255))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH)+ (.30 * heightUpper)))
                      

                              pygame.display.flip()
                              
                              timeDur = time.time()
                              if timeDur - initTime > 3: #return average squeeze as the midpoint between low range low and low range high
                                  return timer, ((LR_TARGETL * mvc) + (LR_TARGETH * mvc)) / float(2)
                                  print("quitted in low hover")
                                  
                        while (samp > HR_TARGETL * float(mvc)) and (samp < HR_TARGETH * float(mvc)) and not quited:
                              timeCounter += 1
                              if timeCounter % 50 == 0:
                                  forceOutputs.append((time.time() - initialTime, self.mp.sample()[0] + .245, ""))
                              nump = nump+1
                              textsurf = self.font.render("Time: " + str(int(timer)) + "s", False, (255,255,255))
                              time.sleep(waittime)
                              timer = timer + waittime * 5

                              if timer > 7.05:
                                  quited = True
                                  
                                  break
                              pygame.draw.rect(self.disp, (0,0,0), (5, 35, 200, 200), 0)
                              self.disp.blit(textsurf,(10,50))  

                              samp = self.mp.sample()[0] + .245

                              if fullscreen == False:
                                  pygame.draw.rect(self.disp, (0,0,0), (1000, 50, 200, 200), 0)
                                  fontForce = pygame.font.Font(pygame.font.get_default_font(), 22)
                                  forceText = fontForce.render("Force x100: "+str(int(samp * 100)), False, (255,255,255))
                                  self.disp.blit(forceText, (1000, 50))
                              
                              self.forcebar2.addpoint(samp, timer) # displaying force as the red line
                              self.forcebar2.draw(mvc,LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH)
                              allSamples.append(samp)
                             
                              self.averagebar.addpoint(total/nump,timer)	# add new force point, and display average
                              font = pygame.font.Font(pygame.font.get_default_font(), 42)
                              heightLower = float(self.forcebar2.height*(LR_TARGETH) - self.forcebar2.height*(LR_TARGETL))
                              heightUpper = float(self.forcebar2.height*(HR_TARGETH) - self.forcebar2.height*(HR_TARGETL))

                              #text for low lottery probability and magnitude
                              textsurf = font.render(str(int(100 * L_EFFORT_PROB)) + "%", False, (0,0,255))
                              self.disp.blit(textsurf,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower))) #35
                              textsurf1 = font.render("$0." + str(int(L_EFFORT_MAG)), False, (37,115,38))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 205 ,self.forcebar2.y+self.forcebar2.height*(1-LR_TARGETH)+ (.60 * heightLower)))
                              font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                              textsurf1 = font1.render("chance of", False, (0,0,255))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-LR_TARGETH)+ (.30 * heightLower)))
                                
                              #text for high lottery probability and magnitude
                              textsurf2 = font.render(str(int(100 * H_EFFORT_PROB)) + "%", False, (0,0,255))
                              self.disp.blit(textsurf2,(self.forcebar2.x + 153, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH) + (.22 * heightUpper))) #35
                              textsurf3 = font.render("$0." + str(int(H_EFFORT_MAG)), False, (37,115,38))
                              self.disp.blit(textsurf3,(self.forcebar2.x + 205 ,self.forcebar2.y + self.forcebar2.height*(1-HR_TARGETH) + (.60 * heightUpper)))
                              textsurf1 = font1.render("chance of", False, (0,0,255))
                              self.disp.blit(textsurf1,(self.forcebar2.x + 253, self.forcebar2.y + self.forcebar2.height * (1-HR_TARGETH)+ (.30 * heightUpper)))
                      

                              pygame.display.flip()
                              timeDur = time.time()
                              if timeDur - initTime > 3:
                                  return timer, ((HR_TARGETL * mvc) + (HR_TARGETH * mvc)) / float(2)


                        initTime = time.time()
                        timeDur = initTime



                        pygame.display.flip() # force screen to update
                        
                        # if 'esc' is hit, quit
                        for event in pygame.event.get(pygame.KEYDOWN):
                                print ("Some key was hit")
                                if pygame.key.name(event.key) == 'escape':
                                        print("Escape key hit")
                                        quited = True
					
                        # We need to sleep each time through the loop, or things progress too quickly. 
                        time.sleep(waittime)
                        timer = timer + waittime * 5

                        if timer > 7.05:
                            quited = True

                forceOutputs.append((time.time() - initialTime, self.mp.sample()[0] + .245, ""))
                
                summ = 0
                for i in range(200, len(allSamples)):
                    summ += allSamples[i]
                # When the game is finished, we return how long it took, and the average adjusted squeeze value.
                return timer, summ / float(len(allSamples) - 200)

        def stopGame(self):
                self.mp.stop_recording()                    
                self.mp.close()                            


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

            while not quitted:
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
        file = open(subjectID + "calibration.txt", "w")
        file.write("calibration average forces: " + str([x / float(100) for x in acceptedMVCs]))
        file.write("\n")
        plt.close()

        return float(np.mean(acceptedMVCs) / 100) #to reaccomodate for squeeze game force being measured directly as oppossed to multiplying force by 100


choiceOutputs = []
forceOutputs = []
def main(trial, mvc, MP):
        """
        params trial and mvc, if trial is first, calibrate to find mvc,
        else if trial is not first, use the mvc value passed in as the true mvc
        """
        global totalTrials
        HR_TARGETL = 0
        HR_TARGETH = 0
        LR_TARGETL = 0
        LR_TARGETH = 0
        L_EFFORT_PROB = 0
        L_EFFORT_MAG = 0
        H_EFFORT_PROB = 0
        H_EFFORT_MAG = 0
        if trial != 0: 
            HR_TARGETL = paramsList[trial - 1][2]
            HR_TARGETH = paramsList[trial - 1][3]
            LR_TARGETL = paramsList[trial - 1][0]
            LR_TARGETH = paramsList[trial - 1][1]
            L_EFFORT_PROB = paramsList[trial - 1][4]
            L_EFFORT_MAG = paramsList[trial - 1][5]
            H_EFFORT_PROB = paramsList[trial - 1][6]
            H_EFFORT_MAG = paramsList[trial - 1][7]

         #CAPTURE MAXIMAL SQUEEZE====================
        if trial == 0:
##            sg = SqueezeGame(TOTALSQUEEZE,"","", MP)
            if calibrationBool == True:
                mvc = calibrate(MP)
                return "calibration", mvc
            else:
                return "calibration", maxEffort 
        #==========================================================
        
        # Setup the screen and font using PyGame
        pygame.init()

        if fullscreen == True:
            disp = pygame.display.set_mode(RES, pygame.FULLSCREEN)  # create a new display
        else:
            disp = pygame.display.set_mode(RES, pygame.RESIZABLE)
        font = pygame.font.Font(pygame.font.get_default_font(), 24)
        pygame.display.set_caption("Effort Game")

        # Run a SqueezeGame
        #   Create an instance of SqueezeGame and run it.
        sg = SqueezeGame(TOTALSQUEEZE,disp,font, MP)

        if trial > 0:
            forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, "trial onset"))
            t, avgSample = sg.runGame(mvc, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH, L_EFFORT_PROB, L_EFFORT_MAG, H_EFFORT_PROB, H_EFFORT_MAG)
            print ("Finished the game in %f seconds" % t)
            time.sleep(delayRewardOnset)
            percentage = avgSample / float(mvc)
            result = "null"
            heightLower = float(sg.forcebar2.height*(LR_TARGETH) - sg.forcebar2.height*(LR_TARGETL))
            heightUpper = float(sg.forcebar2.height*(HR_TARGETH) - sg.forcebar2.height*(HR_TARGETL))
            greenCheck = pygame.image.load("greenCheck2.png")
            redCross = pygame.image.load("redCross2.png")
            returnVal = ""
            if HR_TARGETL <= avgSample / float(mvc) <= HR_TARGETH: 
                print("High lottery")
                rand = random.uniform(0,1)
                color = (25, 25, 255)
                #outline upper box
                pygame.draw.polygon(sg.disp, (252, 230, 232),  \
                                                 [[sg.forcebar2.x,sg.forcebar2.y+sg.forcebar2.height*(1-HR_TARGETL)], \
                                                 [sg.forcebar2.x+sg.forcebar2.length,sg.forcebar2.y+sg.forcebar2.height*(1-HR_TARGETL)], \
                                                 [sg.forcebar2.x+sg.forcebar2.length,sg.forcebar2.y+sg.forcebar2.height*(1-HR_TARGETH)], \
                                                 [sg.forcebar2.x,sg.forcebar2.y+sg.forcebar2.height*(1-HR_TARGETH)]],0)
                #text for high lottery probability and magnitude
                font = pygame.font.Font(pygame.font.get_default_font(), 42)
                heightLower = float(sg.forcebar2.height*(LR_TARGETH) - sg.forcebar2.height*(LR_TARGETL))
                heightUpper = float(sg.forcebar2.height*(HR_TARGETH) - sg.forcebar2.height*(HR_TARGETL))
             
                #text for high lottery probability and magnitude
                textsurf2 = font.render(str(int(100 * H_EFFORT_PROB)) + "%", False, (0,0,255))
                disp.blit(textsurf2,(sg.forcebar2.x + 153, sg.forcebar2.y + sg.forcebar2.height * (1-HR_TARGETH) + (.22 * heightUpper))) 
                textsurf3 = font.render( "$0." + str(int(H_EFFORT_MAG)), False, (37,115,38))
                disp.blit(textsurf3,(sg.forcebar2.x + 205 ,sg.forcebar2.y + sg.forcebar2.height*(1-HR_TARGETH) + (.60 * heightUpper)))
                font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                textsurf1 = font1.render("chance of", False, (0,0,255))
                disp.blit(textsurf1,(sg.forcebar2.x + 253, sg.forcebar2.y + sg.forcebar2.height * (1-HR_TARGETH)+ (.30 * heightUpper)))
      
                pygame.display.flip()
                time.sleep(2)
                
                if rand <= H_EFFORT_PROB:
                    result = "win"
                    disp.blit(greenCheck,(sg.forcebar2.x + sg.forcebar2.length + 30, sg.forcebar2.y + sg.forcebar2.height * (1-HR_TARGETH)+ (.22 * heightUpper)))
                    color = (0, 255, 0)    #green
                else:
                    result = "lose"

                    disp.blit(redCross,(sg.forcebar2.x + sg.forcebar2.length + 30, sg.forcebar2.y + sg.forcebar2.height * (1-HR_TARGETH)+ (.22 * heightUpper)))
                    color = (152, 56, 176) #dark purple 

                forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, "outcome"))
                
                
               
                pygame.display.flip()      # force screen to update
                time.sleep(durationDisplayReward)
                choiceOutputs.append((trial, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH, L_EFFORT_PROB, L_EFFORT_MAG, H_EFFORT_PROB, H_EFFORT_MAG, "high effort", result, avgSample))
                returnVal = ("HR", mvc)

            elif LR_TARGETL <= avgSample / float(mvc) <= LR_TARGETH:
                print("LOW LOTTERY")
                rand = random.uniform(0,1)
                color = (25, 25, 255)
                #outline lower box
                pygame.draw.polygon(sg.disp, (252, 230, 232) ,  \
                                                 [[sg.forcebar2.x,sg.forcebar2.y+sg.forcebar2.height*(1-LR_TARGETL)], \
                                                 [sg.forcebar2.x+sg.forcebar2.length,sg.forcebar2.y+sg.forcebar2.height*(1-LR_TARGETL)], \
                                                 [sg.forcebar2.x+sg.forcebar2.length,sg.forcebar2.y+sg.forcebar2.height*(1-LR_TARGETH)], \
                                                 [sg.forcebar2.x,sg.forcebar2.y+sg.forcebar2.height*(1-LR_TARGETH)]],0)           
                #text for low lottery probability and magnitude
                font = pygame.font.Font(pygame.font.get_default_font(), 42)
                heightLower = float(sg.forcebar2.height*(LR_TARGETH) - sg.forcebar2.height*(LR_TARGETL))
                heightUpper = float(sg.forcebar2.height*(HR_TARGETH) - sg.forcebar2.height*(HR_TARGETL))

                 #text for low lottery probability and magnitude
                textsurf = font.render(str(int(100 * L_EFFORT_PROB)) + "%", False, (0,0,255))
                disp.blit(textsurf,(sg.forcebar2.x + 153, sg.forcebar2.y + sg.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower)))
                textsurf1 = font.render("$0." + str(int(L_EFFORT_MAG)), False, (37,115,38))
                disp.blit(textsurf1,(sg.forcebar2.x + 205 ,sg.forcebar2.y+sg.forcebar2.height*(1-LR_TARGETH)+ (.60 * heightLower)))
                font1 = pygame.font.Font(pygame.font.get_default_font(), 24)
                textsurf1 = font1.render("chance of", False, (0,0,255))
                disp.blit(textsurf1,(sg.forcebar2.x + 253, sg.forcebar2.y + sg.forcebar2.height * (1-LR_TARGETH)+ (.30 * heightLower)))
                                 
                if rand <= L_EFFORT_PROB:
                    result = "win" 
                    disp.blit(greenCheck,(sg.forcebar2.x + sg.forcebar2.length + 30, sg.forcebar2.y + sg.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower)))
                    
                    color = (0, 255, 0)    #green
                else:
                    result = "lose"
                    disp.blit(redCross,(sg.forcebar2.x + sg.forcebar2.length + 30, sg.forcebar2.y + sg.forcebar2.height * (1-LR_TARGETH)+ (.22 * heightLower)))
                    color = (152, 56, 176) #dark purple 

                forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, "outcome"))

                

                pygame.display.flip()      #force screen to update
                time.sleep(durationDisplayReward)

                choiceOutputs.append((trial, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH, L_EFFORT_PROB, L_EFFORT_MAG, H_EFFORT_PROB, H_EFFORT_MAG, "low effort", result, avgSample))
                returnVal = ("LR", mvc)
            
            else:
                redCrossLarge = pygame.image.load("redCrossLarge.png")
                disp.blit(redCrossLarge,(sg.forcebar2.x + 35, sg.forcebar2.y + 35))
                pygame.display.flip()           # force screen to update
                time.sleep(durationDisplayReward)
##                time.sleep(1.0)
##                forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, ""))
##                time.sleep(1.0)
##                forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, ""))
##                time.sleep(1.0)
##                forceOutputs.append((time.time() - initialTime, sg.mp.sample()[0] + .245, ""))
                choiceOutputs.append((trial, LR_TARGETL, LR_TARGETH, HR_TARGETL, HR_TARGETH, L_EFFORT_PROB, L_EFFORT_MAG, H_EFFORT_PROB, H_EFFORT_MAG, "failure", "lose", avgSample))
                returnVal = ("none", mvc)

            
        #if not last trial, display countdown time to squeeze for next trial
            if trial != totalTrials - 1:
                squeezed = False
                pygame.draw.rect(disp, (0,0,0), (5, 35, 200, 200), 0)
                font = pygame.font.Font(pygame.font.get_default_font(), 20)
                textsurf = font.render("Squeeze to progress to next trial ", False, (255,255,255))
                disp.blit(textsurf,(450,20))
                pygame.display.flip()
                exitTime = time.time() + squeezeNextTrial + 1
                while time.time() < exitTime:
                    timeRemaining = exitTime - time.time()
                    pygame.draw.rect(disp, (0,0,0), (500, 50, 200, 30), 0)
                    textsurf = font.render("Squeeze to progress to next trial ", False, (255,255,255))
                    disp.blit(textsurf,(450,20))
                    if timeRemaining < squeezeNextTrial:
                        textsurf = font.render("time remaining: " + str(int(exitTime - time.time())), False, (255,255,255))
                        disp.blit(textsurf,(515,50)) #10, 190 
                        pygame.display.flip()
                    force = sg.mp.sample()[0] + .245
                    if force > .2 and timeRemaining < squeezeNextTrial:
                        squeezed = True
                        break
                if squeezed == False:
                    returnVal = ("failed", mvc)
                    disp.fill((0,0,0))
                    font1 = pygame.font.Font(pygame.font.get_default_font(), 48)
                    textsurf = font1.render("Failed to squeeze", False, (255,255,255))
                    textsurf2 = font1.render("Timeout for this trial ", False, (255,255,255))
                    disp.blit(textsurf,(320,200))
                    disp.blit(textsurf2,(290,280))
                    pygame.display.flip()
                    time.sleep(7)
            recordChoiceOutput()
            return returnVal


count = 0
initialTime = time.time()
pygame.init()
##if fullscreen == True:
##    disp = pygame.display.set_mode(RES, pygame.FULLSCREEN)
##else:
##    disp = pygame.display.set_mode(RES, pygame.RESIZABLE)
fix=pygame.image.load("fixation.png")

#create mp to measure force during fixation
try:
        MP = MP150()               
        print("MP150 live")
except:                                 
        print("no MP; using random values")
        MP = fakeMP()

while count != totalTrials: #6#count is number of trials + 1 for calibration
    
        if count == 0:
                decisionRange, mvc = main(count, 0, MP)
                if decisionRange == "failed":
                    count += 1
        else:
                #show fixation cross for 2 seconds
                if fullscreen == True:
                    disp = pygame.display.set_mode(RES, pygame.FULLSCREEN)
                else:
                    disp = pygame.display.set_mode(RES, pygame.RESIZABLE)
                disp.blit(fix,(0,0))
                forceOutputs.append((time.time() - initialTime, MP.sample()[0] + .245, "fixation onset"))
                pygame.display.flip() # update the display
                pygame.time.wait(1000)
               

                decisionRange = main(count, mvc, MP)[0]
                if decisionRange == "failed":
                    count += 1
        count+=1
        if count >= totalTrials:
            break

print("outputs", choiceOutputs)
print("forceOutputs", forceOutputs)





            


       
#main()
#DAN'S EDITS====================================================
#squeeze points are added to the constant .245 to account for initial negative readouts (starts at about .245 at rest
#on a table, increases/becomes more positive with increasing squeeze strength)


#source takes file in same directory labeled "params.txt" and takes the params as the regions of the
#grey boxes (modifications in class wb)
#writes total average squeeze to file named "averageSqueeze.txt" in same directory

#squeeze values of first 2 seconds of game are ignored, time given for participant to make decision, only values
# from t > 2 are used for derivation of average

#====================================================
#Post meeting notes version 3.0
#adjust so only calibration values taken within time window t = 2 through t = 5
#change lottery text







