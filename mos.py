#! /usr/bin/python

import pygame, sys, array, Image
import pigpio
import ImageEnhance
from array import *
from time import sleep
from pygame.locals import *
import pygame.camera

## Initialisation

pygame.camera.init()
size = width, height = 320, 240
picWidth = 128
picHeight = 90

black = 0,0,0

screen = pygame.display.set_mode(size, FULLSCREEN)

global imageList
imageList = []
global previousT
previousT = 0


## Function Definitions

## captureImage grabs an image from the webcam that's connected and then applies some transforms to it from PIL

def captureImage():
	backgroundColor = (0,)*3
	pixelSize = 4
	
	cam = pygame.camera.Camera("/dev/video0",(picWidth,picHeight))
	cam.start()
	im= cam.get_image()
	pygame.image.save(im, '/tmp/img101.png')
	cam.stop()
	#This is a horrible, horrible hack to get everything playing nice. It really ought to not be necessary to go via apair of temp files to use an image in two parts of the same script!
	#It would be nice to save a few captured images so that we can have some sort of display board or something and so that the exhibit has something to display on it when it's first switched on.

	image = Image.open('/tmp/img101.png')
	image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
	image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
	pixel = image.load()
	
	enh = ImageEnhance.Brightness(image)
	enh.enhance(1.3) 
	for i in range(0,image.size[0],pixelSize):
	  for j in range(0,image.size[1],pixelSize):
	    for r in range(pixelSize):
	      pixel[i+r,j] = backgroundColor
	      pixel[i,j+r] = backgroundColor
	 
	image.save('/tmp/img102.png')
	image.save('/home/pi/mos/img101.png')
	im = pygame.image.load('/tmp/img102.png')
	return im

##cb captures the button-press and handles it

def cbf(g, L, t):
	global previousT
	s = "gpio=" + str(g) + " level=" + str(L) + " at " + str(t) + "previousT=" + str(previousT)
	print(s)
	if t > (previousT + 100000):
		image = captureImage()
		imageList.append(image)
		print "List Length = " + str(len(imageList))
		previousT = t

#Setup the GPIO stuff

pigpio.start()
pigpio.set_pull_up_down(24, pigpio.PUD_UP)
cb = pigpio.callback(24, pigpio.FALLING_EDGE, cbf)


## Begin the main loop

image = captureImage()
imageList.append(image)

listFull = 0 #Store whether the list is full up or not.

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
				image = captureImage()
				imageList.append(image)
				if listFull > 0:
					del imageList[0]
				print "List Length = " + str(len(imageList))
	screen.fill(black)

	ballrect = image.get_rect()
	x=0
	y=0
	for i in imageList:
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
	
