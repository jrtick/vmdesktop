import viewerlib #my opengl viewer library

import time

class Map(object):
  def __init__(self):
    self.viewer = viewerlib.OpenGLViewer(bgcolor=(0.4,0.4,0.4))
    self.displaying = False
    self.addObject((0,0,0),(10,10,10))
  def display(self):
    self.viewer.startThread()
    self.displaying = True
    while not self.viewer.is_visible: time.sleep(0.2)
  def addObject(self,minCoord,maxCoord,color = (1,1,1)):
    self.viewer.objects.append((minCoord,maxCoord,color))
