import camera,aruco_tags #my camera and aruco libraries
import viewerlib #my opengl viewer
import client #my client library

import time

#cozmo_pos = robot.pose.position.x_y_z #returns a 3-tuple
#cozmo_rot = robot.pose_angle.degrees

#establish connection
myclient = client.Client("localhost",42)
print("Connected!")

#create watchers
cam = camera.LaptopCam()
aruco_watcher = aruco_tags.ArucoWatcher(cam,43)

#create a viewer
viewer = viewerlib.OpenGLViewer(bgcolor=(0.4,0.4,0.4))
viewer.startThread() #background the window
viewerPose = ((-5,0,-5),(5,10,5),(1,0,0)) #put our robot in center
viewer.objects = [viewerPose]
time.sleep(1)

#do work
while viewer.is_visible: #close when user presses escape

  #look for tags and update them in the world map
  aruco_watcher.detect() #updates seen tag positions
  msg = []
  if(len(aruco_watcher.tagset.tags) > 0):
    objs = [viewerPose]
    for tag in aruco_watcher.tagset.tags:
      center = tag.pos
      msg += [(tag.id,center.tolist())]
      mini = (center[0]-5,center[1]-5,center[2]-5)
      maxi = (center[0]+5,center[1]+5,center[2]+5)
      objs += [(mini,maxi,(0,1,0))]
    viewer.objects = objs
  myclient.send(str(msg))
