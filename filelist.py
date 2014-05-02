#! /opt/local/bin/python2.7

import glob
import os
import array
import pygame
from time import sleep
from pygame.locals import *

size = width, height = 320, 240
picWidth = 128
picHeight = 90

black = 0,0,0


screen = pygame.display.set_mode(size)


myFiles = []
imageList = []


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

readFiles()
x = y = 0

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
				updateDisplay()
	screen.fill(black)
	
	