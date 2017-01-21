import numpy as np
import cv2,cozmo,time,PIL
import cv2.aruco as aruco

def myProgram(robot,dict_name=aruco.DICT_5X5_100):
  adict = aruco.Dictionary_get(dict_name)
  params = aruco.DetectorParameters_create()

  robot.camera.image_stream_enabled = True

  #wait until images have started
  while(True):
    if(robot.world.latest_image is not None):
      break
    else:
      time.sleep(0.2)

  #continuously look for aruco tags
  while(True):
    cozmoim = robot.world.latest_image.raw_image
    cozmoim = cozmoim.resize((cozmoim.width*2,cozmoim.height*2))
    curim = np.array(cozmoim).astype(np.uint8)
    gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)
    (corners,ids,rejected) = aruco.detectMarkers(gray,adict,parameters=params)

    annotated_im = aruco.drawDetectedMarkers(curim,corners,ids)
    
    cv2.imshow('frame',annotated_im)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
      break

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(myProgram)
cv2.destroyAllWindows()
