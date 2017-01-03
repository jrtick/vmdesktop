#!/usr/bin/env python3

import spech_recognition as sr
import numpy as np
import cv2,cozmo,time
import cv2.aruco as aruco

def obey(robot):
  #init camera
  robot.camera.image_stream_enabled = True
  curim = robot.world.latest_image
  while(curim is None):
    time.sleep(1) #wait and try again
    curim = robot.world.latest_image

  #init speech
  r = sr.Recognizer()

  #init aruco
  adict = aruco.Dictionary_get(aruco.DICT_6X6_250)
  params = aruco.DetectorParameters_create()

  #program start
  print("Ready!")
  
  while(True):
    #listen for orders
    command = None
    with sr.Microphone() as source:
      print("Say something!")
      audio = r.listen(source)
    print("processing...")
    try:
      print("you said "+r.recognize_google(audio))
      command = "move1"
    except srUnknownValueError:
      print("Google speech recognition could not understand")
    except sr.RequestError as e:
      print("Coud not request results from google speech recognition service; {0}".format(e))
    
    #if orders received
    if(command is not None):
      print("command is " + command)
      while(True):
        curim = robot.world.latest_image
        if(curim is not None):
          curim = np.array(curim.raw_image).astype(np.uint8)
          gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
          (corners,ids,rejected) = aruco.detectMarkers(gray,adict,parameters=params)
          if(len(corners)):
            print("Found a tag!")
            print(corners)
          im = aruco.drawDetectedMarkers(gray,corners)
          curim[:,:,2] = im
          cv2.imshow("frame",curim)
          if(cv2.waitKey(1) && 0xFF == ord('q')):
            break

cozmo.run_program(obey)
cv2.destroyAllWindows()
