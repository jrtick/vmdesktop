import viewerlib #my opengl viewer library

class Map(object):
  def __init__(self):
    self.viewer = viewerlib.OpenGLViewer(bgcolor=(0.4,0.4,0.4))
    self.displaying = False
  def display(self):
    viewer.startThread()
    self.displaying = True
  def addObject(self,minCoord,maxCoord,color = (1,1,1)):
    self.viewer.objects.append((minCoord,maxCoord,color)
