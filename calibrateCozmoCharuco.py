#!/usr/bin/env python3
#modified from http://answers.opencv.org/question/98447/camera-calibration-using-charuco-and-python/

import cozmo,cv2,sys,time
import numpy as np

#default 60deg, 290 mm focal length (check cozmopedia)
#internal cam mat = [[fx,0,width/2],[0,fy,height/2],[0,0,1]]
#internal cam mat = [[290,0,120],[0,290,160],[0,0,1]]
cam = np.array([[290,0,120],[0,290,160],[0,0,1]]).astype(float)
dist = np.array([[0,0,0,0,0]]).astype(float) #maybe use 10 on the end

def calibration_program(robot: cozmo.robot.Robot):
  global cam,dist

  #start cozmo stream
  robot.camera.image_stream_enabled = True
  while robot.world.latest_image is None:
    time.sleep(0.2)

  #setup aruco markers
  inch = 0.0254 #size of 1 inch in meters
  adict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
  board = cv2.aruco.CharucoBoard_create(3,3,2*inch,inch,adict) #meters
  #cv2.imshow('board',board.draw((600,600)))
  #cv2.waitKey(3)
  #cv2.imwrite('board.png',board.draw((600,600))

  if(cam is None or dist is None):
    #attempt to find cam and dist values
    allCorners = []
    allIds = []

    #look a bunch of times
    print("Starting image capture....")
    for i in range(100):
      #grab an image
      time.sleep(0.1)
      cozmoim = robot.world.latest_image.raw_image
      curim = np.array(cozmoim).astype(np.uint8)
      grayim = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)

      #grab marker poses
      (corners,ids,_) = cv2.aruco.detectMarkers(grayim,adict)
      if(len(corners)>0):
        (val,charCorners,charIds) = cv2.aruco.interpolateCornersCharuco(corners,ids,grayim,board)
        if(charCorners is not None and len(charCorners)>3):
          allCorners.append(charCorners)
          allIds.append(charIds)
        cv2.imshow('detection',cv2.aruco.drawDetectedMarkers(curim,corners,ids))
        cv2.waitKey(1)
      else:
        cv2.imshow('detection',grayim)
        cv2.waitKey(1)

    print("Attempting to recover camera parameters...")
    imsize = grayim.shape
    success = False
    try:
      start = time.time()
      (ret,cam,dist,r,t) = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,None,None)
      end = time.time()
      print("computed in %.2fs" % (end-start))
      print("function returns with:")
      #print("ret ---"+str(ret))
      print("cam ---------")
      print(cam)
      print("dist --------")
      print(dist.shape)
      print(dist)
      ldist = list(dist[0])
      for i in ldist:
        print("%.2f," % (i), end="")
      print()
      #print("r ---"+str(r))
      #print("t ---"+str(t))
      success = True
      print("Success!")
    except:
      print("Failed.")
      sys.exit()

  while True:
    #grab im
    cozmoim = robot.world.latest_image.raw_image
    curim = np.array(cozmoim).astype(np.uint8)
    grayim = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)

    print(grayim.shape)

    #grab marker poses
    (corners,ids,_) = cv2.aruco.detectMarkers(grayim,adict)
    (rvecs,tvecs) = cv2.aruco.estimatePoseSingleMarkers(corners,1,cam,dist)
    if rvecs is not None:
      try:
        idx = list(ids).index([0])
        print("-----")
        print(tvecs[idx])
        print(rvecs[idx])
      except ValueError:
        print("couldn't find 0")

      for i in range(len(rvecs)):
        curim = cv2.aruco.drawAxis(curim,cam,dist,rvecs[i],tvecs[i],1)
      cv2.imshow('detection',curim)
      if(cv2.waitKey(1000) & 0xFF == ord('q')):
        break


cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(calibration_program)
