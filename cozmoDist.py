#!/usr/bin/env python3
import cozmo,cv2,numpy,time

def deg(rad):
  return rad/3.14159265*180

def aruco_poses(robot):
  #setup constants
  #cozmo has 60deg FOV, 290mm focal length, 240x320 images
  #internal cam mat = [[fx,0,width/2],[0,fy,height/2],[0,0,1]]
  cameraMatrix = numpy.array([[290,0,120],[0,290,160],[0,0,1]]).astype(float)
  distortionArray = numpy.array([[0,0,0,0,0]]).astype(float) #assume no distortion?
  arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
  tagSize = 50 #translations units will be in this unit so tag=50mm
  axisLen = tagSize/2

  #start cozmo stream
  robot.camera.image_stream_enabled = True
  while robot.world.latest_image is None: time.sleep(0.2)

  while cv2.waitKey(1) & 0xff != ord('q'): #close when user presses 'q'
    curim = numpy.array(robot.world.latest_image.raw_image).astype(numpy.uint8)
    grayim = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)

    (corners,ids,_) = cv2.aruco.detectMarkers(grayim,arucoDict)
    info = dict()
    if ids is not None:
      (rots,trans) = cv2.aruco.estimatePoseSingleMarkers(corners,tagSize,cameraMatrix,distortionArray)
      for i in range(len(ids)):
        curID = ids[i][0]
        curim = cv2.aruco.drawAxis(curim,cameraMatrix,distortionArray,rots[i],trans[i],axisLen)
        info[curID] = "tag %d has " % (curID)
        info[curID] += "trans: (%.2f,%.2f,%.2f) " % (trans[i][0][0],trans[i][0][1],trans[i][0][2])
        info[curID] += "and rot: (%.2f,%.2f,%.2f)"% (deg(rots[i][0][0]),deg(rots[i][0][1]),deg(rots[i][0][2]))

      #print out distance information in sorted ID order
      foundtags = list(info.keys())
      foundtags.sort()
      for i in foundtags: print(info[i])

    #display images
    curim = cv2.aruco.drawDetectedMarkers(curim,corners,ids)
    cv2.imshow('Aruco',curim)

cozmo.run_program(aruco_poses)
cv2.destroyAllWindows()
