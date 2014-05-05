#! /usr/bin/python

import os

#global size 
size = (123,456)
s=2

filename = str(s) + '.jpg'
path = os.path.join('/Users/timini/Documents/Code/Photobooth/famousFaces/', filename)
def printSize():
	print "Inside function" + str(size[0]) + 's' + str(s)
	
print "Outside function" + str(size[0])
printSize()
print path