Algorithm Plan
=================

Previously collected images will be in consecutively numbered images in the image root directory

- Read the image root directory and find out the name of the highest numbered directory
- Create a new image sub-directory for this run of the software, store as a global
- Load one screen's worth of images from the old images subdirectory. (If there are not enough images in that directory, load them from some alternative location)
- Display the screen's worth images on screen

### Enter main loop
- Wait for input (from the button or spacebar)
- When the button is pressed, throw an event (use interrupts from pigpiod)


### Event handler
- Turn on the camera preview
- Start countdown timer 3,2,1
- Turn off camera preview
- Show 0 (if high latency on the camera)
- Set screen white
- Take image with camera
- Look for faces within the image and crop to those (if there are >1 faces, then generate multiple images)
- If there are no faces detected, then choose the central square region of the image (or abort TO DECIDE)
- For each output image, pixellate and save with a sequential filename in the current image sub-dir
- Add the images to the list for display on screen