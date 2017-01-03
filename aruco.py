import numpy as np
import cv2,cozmo
import cv2.aruco as aruco

def myProgram(robot):
  robot.camera.image_stream_enabled = True
  while(True):
    curim = robot.world.latest_image
    if(curim is not None):
      curim = np.array(curim.raw_image).astype(np.uint8)
      gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
      adict = aruco.Dictionary_get(aruco.DICT_6X6_250)
      params = aruco.DetectorParameters_create()
      (corners,ids,rejected) = aruco.detectMarkers(gray,adict,parameters=params)
      if(len(corners)):
        print("corners is",corners)
      im = aruco.drawDetectedMarkers(gray,corners)

      curim[:,:,2] = im
      im = curim

      cv2.imshow('frame',im)
      if(cv2.waitKey(1) & 0xFF == ord('q')):
        break

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(myProgram)
cv2.destroyAllWindows()
