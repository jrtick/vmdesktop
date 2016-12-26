#!/usr/bin/env python3

#Jordan Tick
#My own workspace B)
#Testing opencv and cozmo's camera
#check out ~/.local/lib/python3.5/site-packages/cozmo for camera.py to find how to get an RGB image?????

import cozmo
import time,sys,numpy as np
import cv2
WIN_NAME = "display"

#automatic canny edge detection as written by
#http://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
def auto_canny(image,sigma=0.33):
  # compute the median of the single channel pixel intensities
  v = np.median(image)
  
  # apply automatic Canny edge detection using the computed median
  lower = int(max(0, (1.0 - sigma) * v))
  upper = int(min(255, (1.0 + sigma) * v))
  edged = cv2.Canny(image, lower, upper)
  
  # return the edged image
  return edged

def myProgram(robot):
  robot.camera.image_stream_enabled = True #tell robot we need stream of images
  delay = 0.001 #seconds
  print("running program...")
  cv2.namedWindow(WIN_NAME)
  try:
    windowOpen=True
    while(windowOpen): #close program when exit window
      windowOpen= (cv2.getWindowProperty(WIN_NAME,0) >= 0) #whether or not window still exists
      curim = robot.world.latest_image #grab image from camera
      if curim is not None and windowOpen: #(won't be valid originally until camera sets up)
        gray3channel = np.array(curim.raw_image).astype(np.uint8) #returns a 3 channel greyscale image
        gray3channel = cv2.bilateralFilter(gray3channel,9,20,20)
        gray = cv2.cvtColor(gray3channel,cv2.COLOR_BGR2GRAY) #make officially grayscale
        edges = auto_canny(gray,sigma=0.2)
        
        gray3channel[:,:,2]=edges#opencv displays images as BGR -,-
        cv2.imshow(WIN_NAME,gray3channel)
        cv2.waitKey(int(1000/60)) #try to be roughly 60 fps
      time.sleep(delay) #don't freeze python...
  except: #currently raises error when window closes, unsure why
    print("error received:",sys.exc_info())
    print("window closed.")

cozmo.robot.Robot.drive_off_charger_on_connect = False #stay on charger
cozmo.run_program(myProgram)
