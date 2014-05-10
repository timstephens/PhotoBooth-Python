#! /usr/bin/python2.7
'''
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

# Global settings and initialisation.

windowSize = width, height = 1000, 800 #The size of the gallery display grid.
black = 0,0,0
white = 255,255,255
grey = 220,220,220
backgroundColor = black
camBrightness = 60


imageRoot = "/home/pi/mos/imageRoot" #location of the directory containing all the images.

labelPos =(350,90) #position of the numbers when capturing the image.

numImagesInGrid = 12 #This is a hack to make sure that the correct number of images are preloaded at the beginning. The 'normal' image display keeps track of whether the screen is full, but the preload doesn't. 

cameraResolution = (300, 350) #TODO: Will probably need to change for installation!
pixelSize = 6 #The size of the pixels in the pixellated images.
picWidth = 240 #Width of the image in pixels.
picPadding = 3 #Padding between images in the display grid.

## Definitions

global imageList
imageList=[]
myDirs = []
scriptPath = os.getcwd() #This might be a way to break things if the script is started with an odd working directory
#camera = picamera.PiCamera()
screen = pygame.display.set_mode(windowSize, FULLSCREEN)
pygame.init()
pygame.mouse.set_visible(False) #Hide the mouse cursor
BUTTON_PRESSED = USEREVENT+1
global listFull
listFull = 0 #Store whether the image list is full or not. If it's full, we'll stop it growing beyond the end of the screen.



## Functions
def cbf(g, L, t):
	#Generate an event for every button press. This will queue up a load if the button's pressed repeatedly whilst capture is underway
	#Flush the event queue at the end of the image capture sequence. 
	pygame.event.post(pygame.event.Event(BUTTON_PRESSED))
	print "Event Posted"

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

		

def updateDisplay(imageList):
	#Write the images to the screen buffer in a grid with the correct spacing and then show the result
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
    min_size = (20,20)
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
        
def imgCrop(image, cropBox, boxScale=1):
    # Crop a PIL image with the provided box [x(left), y(upper), w(width), h(height)]
    print "CropBox =" + str(cropBox)
    # Calculate scale factors
    # Should give something that's a bit wider/taller than the facial recognition box
    # The image is going to be square, so make that happen here. 
    delta=int(max(cropBox[2]*(boxScale-1),0))
    # yDelta=max(cropBox[3]*(boxScale-1),0)
    # Convert cv box to PIL box [left, upper, right, lower]
    # PIL_box=[cropBox[0]-xDelta, cropBox[1]-yDelta, cropBox[0]+cropBox[2]+xDelta, cropBox[1]+cropBox[3]+yDelta]
    # Return a square image...
    #TODO: Can probably be cleverer here about how this is calculated to prevent multiple resize operations.
    PIL_box=[cropBox[0]-delta, cropBox[1]-delta, cropBox[0]+cropBox[2]+delta, cropBox[1]+cropBox[2]+delta]
    image.crop(PIL_box)
    return image.resize((picWidth, picWidth), Image.NEAREST) 
    #Making sure that the image is square and a constant size

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
			croppedImage=imgCrop(pil_im, face[0],boxScale)
			imageArray.append(croppedImage)
	else:
		print 'No faces found:'
		#TODO: Make sure that the returned image is central in the camera image, and the same size!!
		croppedImage = imgCrop(pil_im, [int((cameraResolution[0]-picWidth)/2),int((cameraResolution[1]-picWidth)/2),picWidth,picWidth], boxScale)
		imageArray.append(croppedImage)
		#return croppedImage
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
	# render text
	for x in range (5,0,-1):
		screen.fill(black)
		#print "We're at %i", x
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
	return image
	
	
	pygame.event.clear() #Flush the event queue so that we don't capture multiple images if the button is mashed on by someone.

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
	capturedImage.save('/tmp/ncrop.png')
	#Let's update the display so that it doesn't display black whilst the images are being processed.
	listFull = updateDisplay(imageList)
	#Carry out the face detection and pixellation here
	imageArray = faceCrop(capturedImage, 1.1) #Do a loose crop around the face...
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
	listFull = updateDisplay(imageList)
	

	
	pygame.event.clear()
	
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
	sleep(0.05)

	
