#!/bin/python3


from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


from threading import Thread #for backgrounding window
import math #for rotating objects 

class Particle(object):
  """dummy class at the moment"""
  def __init__(self,x,y,theta=0):
    self.x = x
    self.y = y
    self.theta = theta
    self.weight = 0

#GLOBAL POSITION VARIABLES
particles = []
robo = [0.5,0.5,0]


class OpenGLViewer(object):
  def __init__(self,width=512,height=512,windowName = "a simple viewer",bgcolor = (0,0,0)):
    self.width = width
    self.height = height
    self.bgcolor = bgcolor
    self.aspect = self.width/self.height
    self.windowName = windowName
    self.thread = None

    #opengl params
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(self.width,self.height)
    glPolygonMode(GL_FRONT_AND_BACK,GL_LINE) #default to drawing outlines of shapes
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION) #killing window will not directly kill main program
  def start(self): #displays in foreground
    #window creation
    self.window = glutCreateWindow(self.windowName)
    glViewport(0,0,self.width,self.height)
    glClearColor(self.bgcolor[0],self.bgcolor[1],self.bgcolor[2],0)
    
    #enable transparency
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);


    #function bindings
    glutReshapeFunc(self.reshape)
    glutIdleFunc(glutPostRedisplay) #constantly update screen
    glutKeyboardFunc(self.keyPressed)
    glutDisplayFunc(self.display)
    glutMainLoop()

  def startThread(self): #displays in background
    self.thread = Thread(target=self.start)
    self.thread.daemon = True #ending fg program will kill bg program
    self.thread.start()

  def drawRectangle(self,center,width=0.08,height=None,angle=0,color=(1,1,1),fill=True):
    #default to solid color
    if(len(color)==3):
      color = (color[0],color[1],color[2],1)

    #default to square
    if(height is None):
      height = width

    #calculate offsets
    w = width/2
    h = height/2
    v1 = (-w,-h)
    v2 = (w,-h)
    v3 = (w,h)
    v4 = (-w,h)

    #rotate points
    rad = math.radians(angle)
    tcos = math.cos(rad)
    tsin = math.sin(rad)
    v1 = (tcos*v1[0]-tsin*v1[1],tsin*v1[0]+tcos*v1[1])
    v2 = (tcos*v2[0]-tsin*v2[1],tsin*v2[0]+tcos*v2[1])
    v3 = (tcos*v3[0]-tsin*v3[1],tsin*v3[0]+tcos*v3[1])
    v4 = (tcos*v4[0]-tsin*v4[1],tsin*v4[0]+tcos*v4[1])

    #translate points
    (cx,cy) = center
    v1 = (v1[0]+cx,v1[1]+cy)
    v2 = (v2[0]+cx,v2[1]+cy)
    v3 = (v3[0]+cx,v3[1]+cy)
    v4 = (v4[0]+cx,v4[1]+cy)

    #draw rectangle
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    glColor4f(color[0],color[1],color[2],color[3])
    glBegin(GL_QUADS)
    glVertex2f(v1[0],v1[1])
    glVertex2f(v2[0],v2[1])
    glVertex2f(v3[0],v3[1])
    glVertex2f(v4[0],v4[1])
    glEnd()
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)

  def drawTriangle(self,center,width=0.04,angle=0,color=(1,1,1),fill=True):
    #default to solid color
    if(len(color)==3):
      color = (color[0],color[1],color[2],1)

    #calculate offsets - DRAW AN EQUILATERAL TRIANGLE WITH SIDE LENGTH WIDTH
    #math is just law of sines
    inner = 0.57735*width
    v1 = (0,-inner) #top
    v2 = (1.019727*inner,0.551*inner)
    v3 = (-1.019727*inner,0.551*inner)

    #rotate points
    rad = math.radians(angle)
    tcos = math.cos(rad)
    tsin = math.sin(rad)
    v1 = (tcos*v1[0]-tsin*v1[1],tsin*v1[0]+tcos*v1[1])
    v2 = (tcos*v2[0]-tsin*v2[1],tsin*v2[0]+tcos*v2[1])
    v3 = (tcos*v3[0]-tsin*v3[1],tsin*v3[0]+tcos*v3[1])

    #translate points
    (cx,cy) = center
    v1 = (v1[0]+cx,v1[1]+cy)
    v2 = (v2[0]+cx,v2[1]+cy)
    v3 = (v3[0]+cx,v3[1]+cy)

    #draw triangle
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    glColor4f(color[0],color[1],color[2],color[3])
    glBegin(GL_TRIANGLES)
    glVertex2f(v1[0],v1[1])
    glVertex2f(v2[0],v2[1])
    glVertex2f(v3[0],v3[1])
    glEnd()
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)

  def display(self):
    global robo,particle 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0,1,1,0,1,-1) #top left is (0,0) and bottom right is (1,1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #DISPLAY ALL OBJECTS
    for p in particles:
      self.drawTriangle((p.x,p.y),angle=p.theta,color=(1,0,0))
    self.drawTriangle((robo[0],robo[1]),angle=robo[2],color=(0,0,1)) #robots

    #blocks
    self.drawRectangle((0.25,0.25),0.08,color=(0,1,0))
    self.drawRectangle((0.25,0.75),0.08,color=(0,1,0,0.2))
    self.drawRectangle((0.75,0.25),0.08,color=(0,1,0,0.2))
    self.drawRectangle((0.75,0.75),0.08,color=(0,1,0))

    glutSwapBuffers()

  def reshape(self,width,height):
    glViewport(0,0,width,height)
    self.width = width
    self.height = height
    self.aspect = self.width/self.height
    self.display()
    glutPostRedisplay()

  def keyPressed(self,key,mouseX,mouseY):
    global particles
    if(key == b'c'): #clear currently displaying particles
      particles = []
    if(key == b'q'): #kill window
      glutDestroyWindow(self.window)
      glutLeaveMainLoop()
    else:
      print("Pressed "+str(key)+" at (%d,%d)" % (mouseX,mouseY))



#dummy program to show off viewer
if __name__ == '__main__':
  import random,time #just for demo purposes!
  viewer = OpenGLViewer(bgcolor=(0.4,0.4,0.4)) #create window
  viewer.startThread() #background window and begin displaying
  print("main program begins.")
  while viewer.thread.is_alive():
    particles.append(Particle(random.random(),random.random(),theta=random.random()*360))
    time.sleep(1)
  print("Program terminated")
