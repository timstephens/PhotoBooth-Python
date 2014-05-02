#! /opt/local/bin/python2.7
'''
This is a stab at the actual photobooth application. 

The app will start with a photo gallery that loads some images from the storage directory, and then displays them in a nice grid (this already exists in the mos.py script)
Next, it'll wait for input from the pushbutton - use the callback function to throw an event rather than calling the function directly. This way, the button presses can be queued and then flushed if there are multiple ones.
Activate the camera in preview mode, and then overlay a countdown timer
Turn off preview mode, 
flash the screen white
Grab an image
Pixellate and display the image large
Add to the gallery
Save the image to the repository
Return to the gallery

'''
import Image 
import pygame, sys
from pygame.locals import *
from time import sleep

size = width, height = 320, 240
black = 0,0,0
white = 255,255,255
global imageList
imageList=[]


screen = pygame.display.set_mode(size)
	
pygame.init()

def readFiles():
	os.chdir("/Users/timini/Pictures/iPhone3G")
	for file in glob.glob("*.JPG"):
		print file
		myFiles.append(file)
	numberOfImages = len(myFiles)
	print numberOfImages
	print myFiles[(numberOfImages-4):numberOfImages]
	for file in myFiles[(numberOfImages-4):numberOfImages]:
		print file
		image = pygame.image.load(file)
		imageList.append(image)
		

def updateDisplay():
	for i in imageList:
		print i
		screen.blit(i, (x, y))
		x += (picWidth + 40)
		if x > (width - picWidth):
			x = 0
			y += (picHeight + 40)
		if y > (height- picHeight):
			y=0
			listFull = 1 #Next time we capure an image, delete the first in the list
		#Need to handle the case where the list gets too many images in it and starts to overflow
	pygame.display.flip()


def showCountdown():
	#Display numbers on screen, real big
	myfont = pygame.font.Font(None, 150)

	#TODO: Turn on camera preview and enable some sort of overlay
	# render text
	for x in range (3,0,-1):
		screen.fill(black)
		#print "We're at %i", x
		label = myfont.render(str(x), 1, white)
		screen.blit(label, (100, 100))
		pygame.display.flip()
		sleep(1)
	screen.fill(white)
	pygame.display.flip()
	sleep(1)
	#TODO: turn off preview and capture image here...
	screen.fill(black)
	pygame.display.flip()
	updateDisplay()
	#TODO Pixellate and display the image
	#TODO Add the image to the gallery
	
	
	pygame.event.clear() #Flush the event queue so that we don't capture multiple images if the button is mashed on by someone.
	

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			cb.cancel() 
			pigpio.stop()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit()
			if event.key == K_SPACE:
				print "Space Pressed"
				showCountdown()
	

	
	x=0
	y=0
	
	
	pygame.display.flip()
	
