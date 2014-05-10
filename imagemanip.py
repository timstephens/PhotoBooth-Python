from PIL import Image
import os
 
#import Tkinter


backgroundColor = (0,)*3
pixelSize = 6
imSize = (240,240)

for num in range (1,17):
	filename = str(num) + '.jpg'
	path = os.path.join('/home/pi/mos/famousFacesIn/', filename)
	 
	image = Image.open(path)
	image = image.resize(imSize, Image.NEAREST) #Make all the images the same size (90x90)
	image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
	image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
	pixel = image.load()
 
	for i in range(0,image.size[0],pixelSize):
	  for j in range(0,image.size[1],pixelSize):
		for r in range(pixelSize):
		  pixel[i+r,j] = backgroundColor
		  pixel[i,j+r] = backgroundColor
 	path = os.path.join('/home/pi/mos/imageRoot/famousFaces/', filename)

	image.save(path)

'''
from Tkinter import Tk, Canvas, Frame, BOTH, NW
import Image 
import ImageTk

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("High Tatras")        
        self.pack(fill=BOTH, expand=1)
        
        self.img = Image.open("output.png")
        self.tatras = ImageTk.PhotoImage(self.img)

        canvas = Canvas(self, width=self.img.size[0]+20, 
           height=self.img.size[1]+20)
        canvas.create_image(10, 10, anchor=NW, image=self.tatras)
        canvas.pack(fill=BOTH, expand=1)


def main():
  
    root = Tk()
    ex = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
    
    '''