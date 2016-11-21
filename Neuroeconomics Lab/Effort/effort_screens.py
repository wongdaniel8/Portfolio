import pygame
import time
import newgame2
import random

pygame.init()
RES = (1200,900)
w = 1200
h = 900
size=(w,h)
screen = pygame.display.set_mode((w, h))
c = pygame.time.Clock() # create a clock object for timing
count = 0 #keep track of number of game iterations

#load all the images into variables
fix=pygame.image.load("fixation.png")
ready=pygame.image.load("readyscreen.png") 
high=pygame.image.load("win_high.png")
low=pygame.image.load("win_low.png")
lose=pygame.image.load("lose.png")
mvc = -1

while count != 15:
        
        #show fixation cross for 2 seconds
        # screen.blit(fix,(0,0))
        # pygame.display.flip() # update the display
        # pygame.time.wait(1000)

        #show ready screen for 2 seconds
       
        # screen.blit(ready,(0,0))
        # pygame.display.flip() 
        # pygame.time.wait(1000)

        #start game
        if count == 0:
                decisionRange, mvc = newgame2.main(count, 0)
        else:
                decisionRange = newgame2.main(count, mvc)[0]
            
        #if only calibrate once, feed in count as a param to main, if count = 1
        #calibrate and return decisionRange, mvc in main
        #else dont calibrate and return decisionRange, null in main, adjust and call
        #newgame2.main with paramter of mvc returned in first trial
        print("decisionRange", decisionRange)
        print("mvc", mvc)
        rand = random.uniform(0, 1)
        print("rand", rand)

      
        #display rewards
        if decisionRange == "LR":
                if rand <= .5:
                        screen.blit(low,(0,0))
                        pygame.display.flip() 
                        pygame.time.wait(2000)
                else:
                        screen.blit(lose,(0,0))
                        pygame.display.flip() 
                        pygame.time.wait(2000)
        elif decisionRange == "HR":
                 if rand <= .5:
                        screen.blit(high,(0,0))
                        pygame.display.flip() 
                        pygame.time.wait(2000)
                 else:
                        screen.blit(lose,(0,0))
                        pygame.display.flip() 
                        pygame.time.wait(2000)
        elif decisionRange == "calibration":
                count += 1
                continue
        else:
                screen.blit(lose,(0,0))
                pygame.display.flip() 
                pygame.time.wait(2000)

        count+=1

pygame.display.quit()


        
