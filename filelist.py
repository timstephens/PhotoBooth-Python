#! /opt/local/bin/python2.7

import glob
import os

size = width, height = 320, 240
picWidth = 128
picHeight = 90

black = 0,0,0
numImagesInGrid = 16

imageRoot = "/Users/timini/Documents/Code/PhotoBooth/"

myFiles = []
imageList = []
myDirs = []

def readDirs():
	#Get a list of the image subdirectories that have already been created.
	os.chdir(imageRoot)
	for item in os.listdir(imageRoot):    
		if os.path.isdir(os.path.join(imageRoot, 'imagesFolder/' ,item)):
			print "Directory : ",item
			if not item.startswith('.'):
				myDirs.append(item)
	return myDirs[]
	
def loadFiles(directory):
	#Read in files from the directory containing images from the last run
	
	os.chdir(os.path.join(imageRoot, directory))
	dirList = os.listdir('.')
	
	#Now lets build the list of images into tbe image list
	for item in dirList[len(dirList)-16:len(dirList)]:
		image=pygame.image.load(item)
		imageList.append(image)
	num = 1
	while len(imageList) < numImagesInGrid:
		#Need to load images from the special place...
		filename = str(num) + '.jpg'
		path = os.path.join('/Users/timini/Documents/Code/Photobooth/famousFaces/', filename)
		image = pygame.image.load(path)
		imageList.append(image)
		if num > 16:
			num = 0 #We're going to loop through these 16 until the list is full

readDirs()
print "Directory Listing\n===========================\n"
print myDirs

lastDirectory = myDirs[len(myDirs)-1]
print "Last Directory Name =" + lastDirectory
readFiles(lastDirectory)

