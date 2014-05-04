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
import Image #Image manipulation
import picamera
import pygame, sys #For UI display and stuff
from pygame.locals import *
from time import sleep #delays
import io #For capturing images to a stream
import cv #for face detection
# import numpy as np #for opencv face detection

# Global settings and initialisation.
size = width, height = 380, 260
black = 0,0,0
white = 255,255,255
global imageList
imageList=[]
picWidth = 90
picHeight = 120

#camera = picamera.PiCamera()
screen = pygame.display.set_mode(size, FULLSCREEN)
pygame.init()


## Functions

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
		

def updateDisplay(imageList):
	x=y=0
	listFull = 0
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
    min_size = (15,15)
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

    # Calculate scale factors
    # Should give something that's a bit wider/taller than the facial recognition box
    # The image is going to be square, so make that happen here. 
    delta=int(max(cropBox[2]*(boxScale-1),0))
    # yDelta=max(cropBox[3]*(boxScale-1),0)
    # Convert cv box to PIL box [left, upper, right, lower]
    # PIL_box=[cropBox[0]-xDelta, cropBox[1]-yDelta, cropBox[0]+cropBox[2]+xDelta, cropBox[1]+cropBox[3]+yDelta]
    # Return a square image...
    PIL_box=[cropBox[0]-delta, cropBox[1]-delta, cropBox[0]+cropBox[2]+delta, cropBox[1]+cropBox[2]+delta]
    return image.crop(PIL_box)

def faceCrop(pil_im,boxScale=1):
	# Select one of the haarcascade files:
	#   haarcascade_frontalface_alt.xml  <-- Best one
	#   haarcascade_frontalface_alt2.xml
	#   haarcascade_frontalface_alt_tree.xml
	#   haarcascade_frontalface_default.xml
	#   haarcascade_profileface.xml
	faceCascade = cv.Load('haarcascade_frontalface_alt.xml')
	cv_im=pil2cvGrey(pil_im)
	faces=DetectFace(cv_im,faceCascade)
	if faces:
		#n=1
		#TODO: This will return the first face in the image, and not anything else.
		# Will need an array or something of the various images to be able to return >1 face 
		for face in faces:
			croppedImage=imgCrop(pil_im, face[0],boxScale=boxScale)
			#fname,ext=os.path.splitext(img)
			#croppedImage.save(fname+'_crop'+str(n)+ext)
			#n+=1
			return croppedImage
	else:
		print 'No faces found:'
		croppedImage = imgCrop(pil_im, [0,10,90,90], boxScale = 1)
		return croppedImage


def captureImage():
	#Capture an image from the RPi camera, look for faces in it, and then pixellate and return the result.
	imageResolution = (90, 120) #TODO: Will probably need to change for installation!
	backgroundColor = (0,)*3
	pixelSize = 4
	stream = io.BytesIO() #So that we can directly import an OpenCV image for face detection
	cam = picamera.PiCamera()
	cam.rotation = 90 
	cam.resolution = imageResolution
	#Display numbers on screen, real big
	myfont = pygame.font.Font(None, 150)
	cam.preview_alpha = 128 #Opacity of the preview image.
	cam.start_preview()
	# render text
	for x in range (3,0,-1):
		screen.fill(black)
		#print "We're at %i", x
		label = myfont.render(str(x), 1, white)
		screen.blit(label, (100, 100))
		pygame.display.flip()
		sleep(1)
	cam.stop_preview()
	screen.fill(white)
	pygame.display.flip()
	cam.capture(stream, format = 'jpeg')
	cam.close()
	sleep(1)
	
	screen.fill(black)
	pygame.display.flip()
	
	stream.seek(0)
	image = Image.open(stream)
	image = faceCrop(image, 1.5) #Do a loose crop around the face...

	image = pixellate(image)
	return image
	
	
	pygame.event.clear() #Flush the event queue so that we don't capture multiple images if the button is mashed on by someone.

def pixellate(image):
	imageResolution = (90, 120) #TODO: Will probably need to change for installation!
	backgroundColor = (0,)*3
	pixelSize = 4
	image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
	image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
	pixel = image.load()
	
	#TODO: May need to enhance the brightness of the image in here, but leave it for now
	#enh = ImageEnhance.Brightness(image)
	#enh.enhance(1.3) 
	for i in range(0,image.size[0],pixelSize):
	  for j in range(0,image.size[1],pixelSize):
	    for r in range(pixelSize):
	      pixel[i+r,j] = backgroundColor
	      pixel[i,j+r] = backgroundColor
	 
	#image.save('/tmp/img102.png')
	#image.save('/home/pi/mos/img101.png')
	#im = pygame.image.load('/tmp/img102.png')
	return image

listFull = 0 #Store whether the image list is full or not. If it's full, we'll stop it gorwing beyond the end of the screen.

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			cb.cancel() 
			pigpio.stop()
			camera.close()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit()
			if event.key == K_SPACE:
				print "Space Pressed"
				capturedImage=captureImage()
				capturedImage.save('/tmp/img102.png')
				im=pygame.image.load('/tmp/img102.png') #The returned image from the capture is a PIL image. Read this into pygame
				#This is an abominable hack. TODO: Find a way to read directly from stream rather than going via a file
				imageList.append(im)
				if listFull > 0:
					del imageList[0]
				print "List Length = " + str(len(imageList))
				listFull = updateDisplay(imageList)


	
