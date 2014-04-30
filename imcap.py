#! /usr/bin/python

import pygame, sys, array, Image
import pigpio
from array import *
from time import sleep
from pygame.locals import *
import pygame.camera

## Initialisation

pigpio.start()
pygame.init()
pygame.camera.init()
size= width, height = 640, 480
speed = [128,0]
picWidth = 128
picHeight = 90

black = 0,0,0

screen = pygame.display.set_mode(size) #, pygame.FULLSCREEN)

global imageList
imageList = []
global previousT
previousT = 0


## Function Definitions

## captureImage grabs an image from the webcam that's connected and then applies some transforms to it from PIL

def captureImage():
	backgroundColor = (0,)*3
	pixelSize = 9
	cam = pygame.camera.Camera("/dev/video0",(picWidth,picHeight))
	cam.start()
	im= cam.get_image()
	pygame.image.save(im,'/tmp/102.bmp')
	cam.stop()
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
				print "List Length = " + str(len(imageList))
	screen.fill(black)
		
	ballrect = image.get_rect()
	x=0
	y=0
	for i in imageList:
		screen.blit(i, (x, y))
		x += picWidth
		if x > (width - picWidth):
			x = 0
			y += picHeight
		if y > (height - picHeight):
			y=0
			del imageList[0]
		#Need to handle the case where the list gets too many images in it and starts to overflow

		
	pygame.display.flip()

