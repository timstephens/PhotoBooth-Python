#! /usr/bin/python2.7
'''
Tim Stephens http://www.tjstephens.com
03May2014

This is the photobooth application. 

The app starts with a photo gallery that loads some images from a previously used storage directory, and then displays them in a nice grid.
Next, it'll wait for input from the pushbutton - using a callback function to throw an event rather than calling the function directly. This way, the button presses can be queued and then flushed if there are lots.
Activate the camera in preview mode, and then overlay a countdown timer
Turn off preview mode 
flash the screen white
Grab an image
Pixellate and display the image large
Add to the gallery
Save the image to the repository
Return to the gallery

'''
import Image #Image manipulation
import picamera
import pygame, sys #For UI display and stuff
from pygame.locals import *
from time import sleep #delays and resting the processor
import io #For capturing images to a stream
import cv #for face detection
import os
import pigpio #For the IO interrupts
from random import shuffle #for suffling the images loaded from disk

## Global settings and initialisation.

windowSize = width, height = 1000, 800 #The size of the gallery display grid.
black = 0,0,0
white = 255,255,255
grey = 220,220,220
backgroundColor = black
camBrightness = 50


imageRoot = "/mnt/storage" #location of the directory containing all the images.

labelPos =(350,90) #position of the numbers when capturing the image.
textPos = (90,600) #position of text that will appear during processing
textContent = 'Preparing your portrait' #Explanation for whilst the system is doing face detection.

numImagesInGrid = 12 #This is a hack to make sure that the correct number of images are preloaded at the beginning. The 'normal' image display keeps track of whether the screen is full, but the preload doesn't. 

cameraResolution = (350, 350) #TODO: Will probably need to change for installation!
pixelSize = 6 #The size of the pixels in the pixellated images.
picWidth = 240 #Width of the image in pixels.
picPadding = 3 #Padding between images in the display grid.

## Definitions

global imageList
imageList=[]
myDirs = []
scriptPath = "/home/pi/mos" #os.getcwd() #This might be a way to break things if the script is started with an odd working directory
#camera = picamera.PiCamera()
screen = pygame.display.set_mode(windowSize, FULLSCREEN)
pygame.init()
pygame.mouse.set_visible(False) #Hide the mouse cursor
BUTTON_PRESSED = USEREVENT+1
global listFull
listFull = 0 #Store whether the image list is full or not. If it's full, we'll stop it growing beyond the end of the screen.



## Functions

def cbf(g, L, t):
	#Generate an event for every button press. NB: This will queue up a load if the button's pressed repeatedly whilst capture is underway
	#Flush the event queue at the end of the image capture sequence.
	pygame.event.clear() #Flush the queue here to kill of switch bounce.
	try: 
		pygame.event.post(pygame.event.Event(BUTTON_PRESSED))
		#print "Event Posted"
	except:
		#This is only likely to error if the event queue is full, so clear it here too
		pygame.event.clear() 
		print "Event queue cleared"

def readDirs():
	#Get a list of the image subdirectories that have already been created.
	mypath = os.path.join(imageRoot, 'imagesFolder/')
	os.chdir(mypath)
	for item in os.listdir(mypath):    
		if os.path.isdir(os.path.join(mypath ,item)):
			#print "Directory : ",item
			if not item.startswith('.'):
				myDirs.append(item)
	return myDirs
	
def loadFiles(directory):
	#Read in files from the directory containing images from the last run
	print "Input directory: " + str(directory)
	try:
		os.chdir(os.path.join(imageRoot, 'imagesFolder/', str(directory)))
		dirList = os.listdir('.')
		#Now lets build the list of images into tbe image list
		for item in dirList[len(dirList)-16:len(dirList)]:
			image=pygame.image.load(item)
			print "Loaded " + item
			imageList.append(image)
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
	except OSError as e:
		print 'No files, or perhaps no folder found'.format(e.errno, e.strerror)
	except:
		print 'There was an error loading the image from this location:' + str(directory)	
		print 'I am going to show just the famous faces this time'
		
	n = 1
	while len(imageList) < numImagesInGrid:
		#Need to load images from the special place...
		filename = str(n) + '.jpg'
		path = os.path.join(imageRoot, 'famousFaces/', filename)
		image = pygame.image.load(path)
		imageList.append(image)
		n+=1
		if n > 16:
			n = 1 #We're going to loop through these 16 until the list is full
	shuffle(imageList) #Mix up the order a bit	

def updateDisplay(imageList, textLabel=False):
	#Write the images to the screen buffer in a grid with the correct spacing and then show the result
	# If there's text in the textLabel parameter, draw that over the image gallery
	screen.fill(black) # Make sure that any text or old images showing on the screen are hidden before writing new ones.

	x=y=0
	listFull = 0 #How we track whether the screen buffer is full
	for i in imageList:
		#print i
		screen.blit(i, (x, y))
		x += (picWidth + picPadding)
		if x > (width - picWidth):
			x = 0
			y += (picWidth + picPadding)
		if y > (height- picWidth):
			y=0
			listFull = 1 #Next time we capure an image, we'll delete the first in the list
	if textLabel:
		myfont = pygame.font.Font(None, 90)
		label = myfont.render(textContent, 1, grey)
		screen.blit(label, textPos)
	pygame.display.flip() #Display the grid on-screen
	pygame.event.clear() #Flush the event queue so that we don't capture multiple images if the button is mashed on by someone.
	return listFull
	
def pil2cvGrey(pil_im):
    # Convert a PIL image to a greyscale cv image
    # from: http://pythonpath.wordpress.com/2012/05/08/pil-to-opencv-image/
    pil_im = pil_im.convert('L')
    cv_im = cv.CreateImageHeader(pil_im.size, cv.IPL_DEPTH_8U, 1)
    cv.SetData(cv_im, pil_im.tostring(), pil_im.size[0]  )
    return cv_im

def cv2pil(cv_im):
    # Convert the cv image to a PIL image
    return Image.fromstring("L", cv.GetSize(cv_im), cv_im.tostring())

def DetectFace(image, faceCascade, returnImage=False):
    # This function takes a grey scale cv image and finds
    # the patterns defined in the haarcascade function
    # modified from: http://www.lucaamore.com/?p=638

    #variables    
    min_size = (10,10)
    haar_scale = 1.1
    min_neighbors = 3
    haar_flags = 0

    # Equalize the histogram
    cv.EqualizeHist(image, image)

    # Detect the faces
    faces = cv.HaarDetectObjects(
            image, faceCascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size
        )
    # If faces are found
    if faces and returnImage:
        for ((x, y, w, h), n) in faces:
            # Convert bounding box to two CvPoints
            pt1 = (int(x), int(y))
            pt2 = (int(x + w), int(y + h))
            cv.Rectangle(image, pt1, pt2, cv.RGB(255, 0, 0), 5, 8, 0)

    if returnImage:
        return image
    else:
        return faces
        
def imgCrop(image, cropBox, boxScale):
    # Crop a PIL image with the provided box [x(left), y(upper), w(width), h(height)]
    # Calculate scale factors
    # Should give something that's a bit wider/taller than the facial recognition box
    # The image is going to be square, so make that happen here. 
    delta=int(max(cropBox[2]*(boxScale-1),0))
    # Convert cv box to PIL box [left, upper, right, lower]
    # Return a square image...
    #TODO: Can probably be cleverer here about how this is calculated to prevent multiple resize operations.
    #Make sure that the edges of the crop box never extend beyond the edge of the image
    PIL_box=[max(cropBox[0]-delta,0), max(cropBox[1]-delta,0), min(cropBox[0]+cropBox[2]+delta, cameraResolution[0]), min(cropBox[1]+cropBox[2]+delta, cameraResolution[1])]
    print PIL_box
    print " and delta is " + str(delta)
    image=image.crop(PIL_box)
    return image.resize((picWidth, picWidth), Image.NEAREST) 

def faceCrop(pil_im,boxScale):
	#This returns an array of PIL images cropped to contain each face.
	
	imageArray = []
	# Select one of the haarcascade files:
	#   haarcascade_frontalface_alt.xml  <-- Best one
	#   haarcascade_frontalface_alt2.xml
	#   haarcascade_frontalface_alt_tree.xml
	#   haarcascade_frontalface_default.xml
	#   haarcascade_profileface.xml
	loadpath = os.path.join(scriptPath, 'haarcascade_frontalface_alt.xml')
	faceCascade = cv.Load(loadpath) 
	cv_im=pil2cvGrey(pil_im)
	faces=DetectFace(cv_im,faceCascade)
	if faces:
		print str(len(faces)) + " faces found"
		for face in faces:
			print face
			croppedImage=imgCrop(pil_im, face[0],boxScale)
			imageArray.append(croppedImage)
	else:
		print 'No faces found:'
		#TODO: Make sure that the returned image is central in the camera image, and the same size!!
		croppedImage = imgCrop(pil_im, [int((cameraResolution[0]-picWidth)/2),int((cameraResolution[1]-picWidth)/2),picWidth,picWidth], boxScale)
		imageArray.append(croppedImage)
	return imageArray

def captureImage():
	#Capture an image from the RPi camera, look for faces in it, and then pixellate and return the result.
	stream = io.BytesIO() #So that we can directly import an OpenCV image for face detection
	cam = picamera.PiCamera()
	cam.rotation = 90 
	cam.hflip = True
	cam.resolution = cameraResolution
	cam.brightness = camBrightness
	#Display numbers on screen, real big
	myfont = pygame.font.Font(None, 1000)
	cam.preview_alpha = 128 #Opacity of the preview image.
	cam.start_preview()
	# render a countdown, with the screen flashing white for illumination when the photo is taken
	for x in range (5,0,-1):
		screen.fill(black)
		label = myfont.render(str(x), 1, white)
		screen.blit(label, labelPos)
		pygame.display.flip()
		sleep(1)
	cam.stop_preview()
	cam.hflip = False
	screen.fill(white)
	label = myfont.render(str(0), 1, grey)
	screen.blit(label, labelPos)
	pygame.display.flip()
	cam.capture(stream, format = 'jpeg')
	cam.close()
	
	screen.fill(black)
	pygame.display.flip()
	stream.seek(0)
	image = Image.open(stream)
	pygame.event.clear() #Flush the event queue so that we don't capture multiple images if the button is mashed on by someone.
	return image

def pixellate(image):
	image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
	image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
	pixel = image.load()
	for i in range(0,image.size[0],pixelSize):
	  for j in range(0,image.size[1],pixelSize):
	    for r in range(pixelSize):
	      pixel[i+r,j] = backgroundColor
	      pixel[i,j+r] = backgroundColor
	return image

def respondToEvent():
	imageArray = []
	global listFull #Yes, it's a hack
	global fileNumber
	capturedImage=captureImage()
	#Let's update the display so that it doesn't display black whilst the images are being processed.
	listFull = updateDisplay(imageList, textContent)
	#Carry out the face detection and pixellation here
	imageArray = faceCrop(capturedImage, 1.3) #Do a loose crop around the face...
	for image in imageArray:
		image = pixellate(image)
		image.save('/tmp/img102.png')
		filename = str(fileNumber) + '.jpg'
		fileNumber +=1
		image.save(os.path.join(currentDir, filename))
		im=pygame.image.load('/tmp/img102.png') #The returned image from the capture is a PIL image. Read this into pygame via the filesystem since using streams directly results in some sort of garbled image.
		#This is an abominable hack. TODO: Find a way to read directly from stream rather than going via a file
		imageList.append(im)
		if listFull > 0:
			del imageList[0]
		print "List Length = " + str(len(imageList))
	listFull = updateDisplay(imageList, False)
	pygame.event.clear(BUTTON_PRESSED)

# ########################################################################
#
# Main Program
#
# ########################################################################
#Setup the GPIO stuff

pigpio.start()
pigpio.set_pull_up_down(24, pigpio.PUD_UP)
cb = pigpio.callback(24, pigpio.FALLING_EDGE, cbf)

myDirs = readDirs()
print myDirs
if myDirs:
	lastDirectory = len(myDirs)-1 #List is zero-referenced, first directory begins with 1
else:
	lastDirectory = 1

loadFiles(lastDirectory) # This should populate the list of images with something...
listFull = updateDisplay(imageList) #Make sure that the faces are displayed onscreen
print "Length of myDirs is " + str(len(myDirs))
#create a directory for this run's worth of files
currentDir = os.path.join(imageRoot, 'imagesFolder/', str(len(myDirs)+1))
print currentDir
if not os.path.isdir(currentDir):
	os.mkdir(currentDir)

fileNumber = 1

pygame.event.clear() #Make sure there's nothing waiting for us.
while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			cb.cancel() 
			pigpio.stop()
			camera.close()
			sys.exit()
		if event.type == BUTTON_PRESSED:
			#This is a horrible hack since there are now 2 places to enter all this stuff and there's a real likelihood of stuff going wrong..
			print "Button Pressed"
			respondToEvent()
			
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit()
			if event.key == K_SPACE:
				print "Space Pressed"
				respondToEvent()
	pygame.event.clear()
	sleep(0.05)

	
