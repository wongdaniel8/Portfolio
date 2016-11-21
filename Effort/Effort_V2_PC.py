# CONSTANTS
RES             = (1200,900)	# Screen resolution for PyGame
TOTALSQUEEZE    = 100;		# How much force, total, to end the game
MAXTIME         = 10;

# IMPORTS
import pygame
import time, random, os, sys
import numpy as np
#from libmpdev import MP150 commented out for editing purposes


##images
# fixation=pygame.image.load(os.path.join('fixation.png'))
# readyscreen=pygame.image.load(os.path.join('readyscreen.png'))
# win_high=pygame.image.load(os.path.join('win_high.png'))
# win_low=pygame.image.load(os.path.join('win_low.png'))
# lose=pygame.image.load(os.path.join('lose.png'))
#
#
# ##use these modules to change between screens
# pygame.display.flip()
# pygame.time.wait()

############### Class to mimic the squeeze system if the BioPac is not available.
##  if the BioPac is not plugged in, this class creates random numbers to feed to
##    the rest of the program.
##    The member functions mimic those of the BioPac interface
class fakeMP:          
        def sample(self):
                return [random.uniform(0,2),0,0]
        def start_recording(self):
                return 0
        def stop_recording(self):
                return 0
        def close(self):
                return 0

############### Class to draw Progress Bar
###  Used for a variety of progress bars

class pb: #CLASS NOT NEEDED -DAN
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
		#   (the time allows us to plot it properly, between 0 and maxt		                    
		def addpoint(self,point,time):
				self.points.append((point,time))
                
				print ("Pointy", point)
				
				
		def draw(self):
			
				for (p,t) in self.points:
										 
					# Calculate the pixel for the top of the data point.
					#  This will be the height the progress bar is at, minus the bounding rectangle (top and bottom, so 2*width)
					#    and then the size of the point itself, p.  
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
                def drawLine(self):
                                pygame.draw.polygon(self.disp,self.color,  \
                                       [[self.x,self.y],  \
                                        [self.x+self.length,self.y],   \
                                        [self.x+self.length,self.y+self.height],   \
                                        [self.x,self.y+self.height]],0) 

                                # Draw 15-20% line
                                pygame.draw.polygon(self.disp,self.rangeColor,  \
                                        [[self.x,self.y+self.height*0.85], \
                                        [self.x+self.length,self.y+self.height*0.85], \
                                        [self.x+self.length,self.y+self.height*0.80], \
                                        [self.x,self.y+self.height*0.80]],0)

                                # Draw 55-60% line
                                pygame.draw.polygon(self.disp,self.rangeColor,  \
                                        [[self.x,self.y+self.height*0.45], \
                                        [self.x+self.length,self.y+self.height*0.45], \
                                        [self.x+self.length,self.y+self.height*0.40], \
                                        [self.x,self.y+self.height*0.40]],0)


                                              
                # Add a new data point along with the time it was added
                #   (the time allows us to plot it properly, between 0 and maxt                             
                def addpoint(self,point,time):
                                self.point = point
                                print ("Point", point)
                                
                def drawForceLine(self):
                        prob = 1 - self.point/2.0
                        print("PROB", prob)
                        pygame.draw.polygon(self.disp,self.forceColor, \
                                [[self.x,self.y+self.height*prob], \
                                [self.x+self.length,self.y+self.height*prob], \
                                [self.x+self.length,self.y+self.height*(prob-0.010)], \
                                [self.x,self.y+self.height*(prob-0.010)]],0)
                                
                def draw(self):            
                                if self.flag:
                                        self.drawLine()
                                        self.drawForceLine()
				
				
############### An instance of a SqueezeGame
class SqueezeGame:
        
        def __init__(self,fs,d,f):
                self.fullSqueeze = fs                # total points in game
                self.disp = d                        # pygame display
                self.font = f                        # pygame font
                #  The game involves squeezing until you get to TOTALSQUEEZE
                #     this progressbar shows the % of TOTALSQUEEZE reached
                self.progressbar = pb(d,150,100,600,40,(255,0,0))
                #  Progress bar for time
                self.timebar = pb(d,150,50,600,40,(0,255,0))
                #  Progress bar for current force
                self.forcebar = gb(d,150,150,600,100,(0,0,255),MAXTIME,True)
                # Progress bar for average force from start to now
                self.averagebar=gb(d,150,150,600,100,(255,255,255),MAXTIME,False)
                # Here is where we test if there is a BioPac installed.  If so MP150 will return
                #   a good value.  If not, we use the fakeMP instead.
                self.forcebar2 = wb(d,550,100,100,500,(255,255,255),MAXTIME,True) # NEW - coordinates, color for the white/grey bar
                try:
                        self.mp = MP150()               # start communication with the squeezer
                        print("MP150 live")
                except:                                 # if no squeezer, use a fakeMP
                        print("no MP; using random values")
                        self.mp = fakeMP()

        def runGame(self):
                total = 0.0								# keep track of total squeeze
                quited = False          				# manage the loop
                self.mp.start_recording()               # start recording
                timer = 0.0                             # total time for this game
                waittime = 0.005  #NEEDS TWEEKING, ARBITRARILY SET                  # delay between samples
                nump=0									# number of samples taken
                while not quited:
                		
                        sample = self.mp.sample()       # get new squeezie sample
                        nump = nump+1
                        if sample[0] > 0: #MIGHT NEED TWEEKING, perhaps adjust so that 0 value is resting grip hold, run new trial for each patient    # add current sample to total
                                total = total + sample[0];	# sometimes MP150 returns <0, which we consider errors and ignore
                        self.disp.fill((0,0,0))             # paint screen black
                        textsurf = self.font.render("Time: " + str(timer) + "s", False, (255,255,255))
                        self.disp.blit(textsurf,(10,50))    # display the current time
                        
                        #textsurf = self.font.render("Instantaneous Force: %.3f" % (sample[0]), False, (255,255,255))
                        #self.disp.blit(textsurf,(10,110))
                        
                        # textsurf = self.font.render("Work:", False, (255,255,255))
                        # self.disp.blit(textsurf,(10,100))    # display the total work so far
                        
                        # textsurf = self.font.render("Force(0-2):", False, (255,255,255))
                        # self.disp.blit(textsurf,(10,150))    # display the current force sample
                        
                        # textsurf = self.font.render("Avg: %.3f" % (total/nump), False, (255,255,255))
                        # self.disp.blit(textsurf,(10,200))    # display the average force so far
                    
                        # self.timebar.drawFill(timer/MAXTIME)		# display time 
                        #  self.forcebar.addpoint(sample[0],timer)		# display force with new point
                        # self.forcebar.draw()
                    
                    

                    
                    
# PHIL's EDIT
#==============================================================================
                        #sample2 = random.uniform(0,2)
                        sample2 = 0
                        for x in xrange(1000):
                             sample2 =  random.uniform(-0.05,0.05) + np.log(timer/2) + 1
                             if sample2 > 2: #Setting Upper Limits
                                 sample2 = 2
                             if sample2 < 0: #Setting Lower Limits
                                 sample2 = 0                                                   
                             print sample2
#==============================================================================
                        
                        
                        self.forcebar2.addpoint(sample2,timer) # NEW - displaying force as the red line                       
                        self.forcebar2.draw() # NEW - drawing the line
                        # self.progressbar.drawFill(total/TOTALSQUEEZE)  # progress to date
                        self.averagebar.addpoint(total/nump,timer)	# add new force point, and display average
                        
                        # self.averagebar.draw()
                        pygame.display.flip()           # force screen to update
                        
                        # if 'esc' is hit, quit
                        for event in pygame.event.get(pygame.KEYDOWN):
                                print ("Some key was hit")
                                if pygame.key.name(event.key) == 'escape':
                                        print("Escape key hit")
                                        quited = True
						# # Game ends when TOTALSQUEEZE is reached
      #                   if total > self.fullSqueeze:
      #                           quited = True
                    
                        # We need to sleep each time through the loop, or things progress too quickly.  Computers are fast.
                        time.sleep(waittime)
                        timer = timer + waittime*20

                        if timer > 5.0:
                            quited = True
                # When the game is finished, we return how long it took.
                # The faster the game finishes, the higher the average force was
                return timer

        def stopGame(self):
                self.mp.stop_recording()                     # stop recording
                self.mp.close()                              # and close 


def main():
        # Setup the screen and font using PyGame
        pygame.init()
        disp = pygame.display.set_mode(RES)   # create a new display
        font = pygame.font.Font(pygame.font.get_default_font(), 24)
        pygame.display.set_caption("Effort Game")



        # Run a SqueezeGame
        #   Create an instance of SqueezeGame and run it.
        sg = SqueezeGame(TOTALSQUEEZE,disp,font)
        t = sg.runGame()
        print ("Finished the game in %f seconds" % t)
        sg.stopGame()

        # wait for 'escape' to be hit
                
        # Clean up and shutdown
        #pygame.display.quit()

#main()
