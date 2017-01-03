#!/usr/bin/env python3

import speech_recognition as sr
import numpy as np
import cv2,cozmo,time,sys
import cv2.aruco as aruco
print("imports complete")

def obey(robot):
  #init camera
  print("initializing camera...")
  robot.camera.image_stream_enabled = True
  curim = robot.world.latest_image
  while(curim is None):
    time.sleep(1) #wait and try again
    curim = robot.world.latest_image

  #init speech
  print("initializing speech...")
  r = sr.Recognizer()

  #init aruco
  print("initializing aruco tags...")
  adict = aruco.Dictionary_get(aruco.DICT_6X6_250)
  params = aruco.DetectorParameters_create()

  tag1 = aruco.drawMarker(adict,1,300)
  tag2 = aruco.drawMarker(adict,2,300)
  cv2.imshow("tag1",tag1)
  cv2.waitKey(1)
  cv2.imshow("tag2",tag2)
  cv2.waitKey(1000)

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
      command = r.recognize_google(audio)
      print("you said "+command)
      if(command.lower in ["exit","finish","quit","stop","over"]):
        sys.exit()
    except sr.UnknownValueError:
      print("Google speech recognition could not understand")
    except sr.RequestError as e:
      print("Coud not request results from google speech recognition service; {0}".format(e))
    
    #if orders received
    if(command is not None):
      if(command.lower() in ["one","1"]):
        command = 1
      elif(command.lower() in ["two","to","too","2"]):
        command = 2
      else:
        print("couldn't recognize command",command)
        break
      print("command is " + str(command))
      while(True):
        curim = robot.world.latest_image
        if(curim is not None):
          curim = np.array(curim.raw_image).astype(np.uint8)
          gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
          (corners,ids,rejected) = aruco.detectMarkers(gray,adict,parameters=params)
          markers = dict()
          if(len(corners)):
            print("Found a tag!")
            for i in range(len(ids)):
              markers[ids[i][0]] = [corners[i]]
            print(markers)
          try:
            im = aruco.drawDetectedMarkers(gray,markers[command])
            curim[:,:,1] = im
          except:
            pass
          cv2.imshow("frame",curim)
          if(cv2.waitKey(1) & 0xFF == ord('q')):
            break
print("about to start...")
cozmo.run_program(obey)
cv2.destroyAllWindows()
