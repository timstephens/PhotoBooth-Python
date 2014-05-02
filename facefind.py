import cv2

def detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("/Users/timini/Documents/Code/PhotoBooth/haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (100,100))

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

def box(rects, img):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
    cv2.imwrite('/Users/timini/Documents/Code/PhotoBooth/detected.jpg', img);

rects, img = detect("/Users/timini/Documents/Code/PhotoBooth/photo.jpg")
box(rects, img)
print rects
print "done"
