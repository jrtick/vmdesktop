#!/usr/bin/env python3

SHOW_TAGS = False

import speech_recognition as sr #requires internet & pyaudio
import numpy as np
import cv2,cozmo,time,sys
print("imports complete")

def cozmo_control(robot,tagID,adict,params,dims,p=0.5):
  curbox = None
  center = np.array([dims[0]/2,dims[1]/2])
  print("center is",str(center.tolist()))
  while(True):
    curim = robot.world.latest_image
    while(curim is None): #wait 'til an image is grabbed
      time.sleep(0.1)
      curim = robot.world.latest_image
    curim = np.array(curim.raw_image).astype(np.uint8)
    gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
    (points,ids,_) = cv2.aruco.detectMarkers(gray,adict,parameters=params)
    markers = dict()
    if(len(points)): #found a tag
      for i in range(len(ids)):
        try:
          markers[ids[i][0]] += [points[i]]
        except:
          markers[ids[i][0]] = [points[i]]
    try:
      tagloc = markers[tagID]
    except:
      print("target off sight. mission failed")
      break
    print(tagloc)
    curbox = np.copy(markers[tagID][0])
    curpos = np.average(curbox)
    err = (center-curpos) #pos needs neck up neg needs down
    sideways = err[0] #pos means turn left, neg means turn right
    print("error is",str(err.tolist()))
    if(abs(sideways)<10):
      break
    time.sleep(1)
    robot.turn_in_place(cozmo.util.degrees( sideways*p  )).wait_for_completed()
  maxdist = 0
  for i in range(4):
    for j in range(4):
      curdist = (curbox[0][i][0]-curbox[0][j][0])**2+(curbox[0][i][1]-curbox[0][j][1])**2
      if(curdist>maxdist):
        maxdist = curdist
  print("cursize is "+str(maxdist))
  return maxdist

def lookaround(robot):
  #setup cozmo's view and arms
  robot.move_lift(10)
  robot.set_head_angle(cozmo.util.degrees(10)).wait_for_completed()

  #init camera
  print("initializing camera...")
  robot.camera.image_stream_enabled = True
  curim = robot.world.latest_image
  dim = None
  while(dim is None):
    time.sleep(1) #wait and try again
    curim = robot.world.latest_image
    if(curim is not None):
      dim = np.array(curim.raw_image).shape
  print("will be displayed as a",dim,"image")
  #init speech
  print("initializing speech...")
  r = sr.Recognizer()

  #init aruco
  print("initializing aruco tags...")
  adict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
  params = cv2.aruco.DetectorParameters_create()
  
  #have robot sweep the field looking for tags
  numturns = 8
  savedims = np.zeros((dim[0],dim[1],dim[2],numturns))
  step = -360/numturns
  commands = {
  "zero":0,"0":0,
  "one":1,"won":1,"1":1,
  "two":2,"too":2,"to":2,"2":2,
  "three":3,"3":3,
  "four":4,"for":4,"4":4,
  "five":5,"5":5,
  "six":6,"6":6,
  "seven":7,"7":7,
  "eight":8,"ate":8,"8":8,
  "nine":9,"9":9}
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
    if(command is not None and command in commands.keys()):
      lookfor = commands[command]
      found = False
      markers = dict() #most recent list of seen tags
      for i in range(numturns):
        print("step", i)
        curim = robot.world.latest_image
        while(curim is None): #wait 'til an image is grabbed
          time.sleep(0.1)
          curim = robot.world.latest_image
        curim = np.array(curim.raw_image).astype(np.uint8)
        gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
        (points,ids,_) = cv2.aruco.detectMarkers(gray,adict,parameters=params)
        markers = dict()
        if(len(points)): #found a tag
          for i in range(len(ids)):
            try:
              markers[ids[i][0]] += [points[i]]
            except:
              markers[ids[i][0]] = [points[i]]
          print("found tags ",str(markers.keys()))
          im = cv2.aruco.drawDetectedMarkers(gray,points)
          curim[:,:,1] = im
        savedims[:,:,:,i] = np.copy(curim)
        display = np.concatenate(tuple([savedims[:,:,:,j] for j in range(i+1)]),axis=1).astype(np.uint8)
        print(display.shape)
        cv2.imshow("all frames",display)
        cv2.waitKey(100)
        cv2.imshow("curframe",curim)
        cv2.waitKey(100)
        if(lookfor is not None and lookfor in markers.keys()):
          found = True
          break
        else:
          robot.turn_in_place(cozmo.util.degrees(step)).wait_for_completed()

      cv2.destroyAllWindows()
      if(lookfor is not None):
        if(found):
          robot.say_text("found tag %d" % (lookfor)).wait_for_completed()
        else:
          robot.say_text("Could not find tag %d" % (lookfor)).wait_for_completed()

      if(found):
        while(True):
          sizeOfObject = cozmo_control(robot,lookfor,adict,params,dim)
          if(sizeOfObject<5000):
            robot.drive_straight(cozmo.util.distance_mm(150),cozmo.util.speed_mmps(50)).wait_for_completed() 
          else:
            break

def obey(robot):
  global SHOW_TAGS
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
  adict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
  params = cv2.aruco.DetectorParameters_create()

  if(SHOW_TAGS):
    tag1 = cv2.aruco.drawMarker(adict,1,300)
    tag2 = cv2.aruco.drawMarker(adict,2,300)
    cv2.imshow("tag1",tag1)
    cv2.waitKey(1)
    cv2.imshow("tag2",tag2)
    cv2.waitKey(1000)

  #program start
  print("Ready!")
  commands = {
  "zero":0,"0":0,
  "one":1,"won":1,"1":1,
  "two":2,"too":2,"to":2,"2":2,
  "three":3,"3":3,
  "four":4,"for":4,"4":4,
  "five":5,"5":5,
  "six":6,"6":6,
  "seven":7,"7":7,
  "eight":8,"ate":8,"8":8,
  "nine":9,"9":9}
  
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
      try:
        command = commands[command]
      except:
        print("couldn't recognize command",command)
        break
      print("command is " + str(command))
      #robot.say_text("you want me to find tag %d" % (command)).wait_for_completed()
      finished = False
      while(True):
        curim = robot.world.latest_image
        if(curim is not None):
          curim = np.array(curim.raw_image).astype(np.uint8)
          gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
          (corners,ids,rejected) = cv2.aruco.detectMarkers(gray,adict,parameters=params)
          markers = dict()
          if(len(corners)):
            #print("Found a tag!")
            for i in range(len(ids)):
              try:
                markers[ids[i][0]] += [corners[i]]
              except:
                markers[ids[i][0]] = [corners[i]]
            #print(markers)
          try:
            im = cv2.aruco.drawDetectedMarkers(gray,markers[command])
            curim[:,:,1] = im
          except:
            pass
          cv2.imshow("frame",curim)
          letter = cv2.waitKey(1) & 0xFF
          if(letter in [ord("n"),ord("q")]):
            finished = (letter==ord("q"))
            break
      if(finished):
        break
print("about to start...")
cozmo.robot.Robot.drive_off_charger_on_connect = True #stay on charger
cozmo.run_program(lookaround)
cv2.destroyAllWindows()
