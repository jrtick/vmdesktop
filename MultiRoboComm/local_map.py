import camera,aruco_tags #my camera and aruco libraries
import viewerlib #my opengl viewer
import client,server #my internet codes

import time

USE_CLIENT = False
USE_SERVER = False


if USE_SERVER:
  server_connection = server.setupConnection('localhost')
  server_connection.listen_background()



#cozmo_pos = robot.pose.position.x_y_z #returns a 3-tuple
#cozmo_rot = robot.pose_angle.degrees

#create watchers
cam = camera.LaptopCam()
aruco_watcher = aruco_tags.ArucoWatcher(cam)

#create a viewer
viewer = viewerlib.OpenGLViewer(bgcolor=(0.4,0.4,0.4))
viewer.startThread() #background the window

#communicate
if USE_CLIENT:
  connection = client.getConnection()
  connection.send("hi")

#do work
while viewer.is_visible: #close when user presses escape
  aruco_watcher.detect() #updates seen tag positions
  time.sleep(0.5)

  if USE_CLIENT:
    connection.send("heyyyy")

  #if USE_CLIENT and aruco_watcher.tagset.isUpdated:
  #  print("Updating!")
  #  connection.send("UPDATE")
  #  for tag in aruco_watcher.tagset.tags:
  #    connection.send(str(tag))
  #  connection.send("END")
  #  aruco_watcher.tagset.isUpdated = False

if USE_CLIENT:
  connection.send("q")
  time.sleep(1)
  connection.close()
