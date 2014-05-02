from PIL import Image
 
 
#import Tkinter


backgroundColor = (0,)*3
pixelSize = 4
 
image = Image.open('/Users/timini/Documents/Code/PhotoBooth/testpics/in14_crop1.jpg')
image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
pixel = image.load()
 
for i in range(0,image.size[0],pixelSize):
  for j in range(0,image.size[1],pixelSize):
    for r in range(pixelSize):
      pixel[i+r,j] = backgroundColor
      pixel[i,j+r] = backgroundColor
 
image.save('CropOutput.png')

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