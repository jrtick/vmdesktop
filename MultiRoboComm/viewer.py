#!/bin/python3


from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


from threading import Thread #for backgrounding window
import math #for rotating objects 

#GLOBAL POSITION VARIABLES
robo = [0.5,0.5,0]


class OpenGLViewer(object):
  def __init__(self,width=512,height=512,windowName = "a simple viewer",bgcolor = (0,0,0)):
    self.width = width
    self.height = height
    self.bgcolor = bgcolor
    self.aspect = self.width/self.height
    self.windowName = windowName
    self.thread = None
    self.fov = 50 # degrees
    self.near = 1
    self.far = 1000000
    self.camera_location = [0,1,0]
    self.look_dir = [0,0]

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
    glEnable(GL_DEPTH_TEST)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    #function bindings
    glutReshapeFunc(self.reshape)
    glutIdleFunc(glutPostRedisplay) #constantly update screen
    glutSpecialFunc(lambda *a: self.keyPressed(*a,special=True))
    glutKeyboardFunc(self.keyPressed)
    glutDisplayFunc(self.display)
    glutMainLoop()

  def startThread(self): #displays in background
    self.thread = Thread(target=self.start)
    self.thread.daemon = True #ending fg program will kill bg program
    self.thread.start()

  def drawRectangularPrism(self,mini,maxi,color=(1,1,1,1),fill=True):
    if(len(color)==3):
      color = (color[0],color[1],color[2],1)
    verts = []
    points = [mini,maxi]
    pts = []
    for i in [0,1]:
      for j in [0,1]:
        for k in [0,1]:
          pts += [(points[i][0],points[j][1],points[k][2])]

    self.draw3DRectangle(pts[0],pts[1],pts[3],pts[2],color,fill)
    self.draw3DRectangle(pts[0],pts[2],pts[6],pts[4],color,fill)
    self.draw3DRectangle(pts[0],pts[1],pts[5],pts[4],color,fill)
    self.draw3DRectangle(pts[4],pts[6],pts[7],pts[5],color,fill)
    self.draw3DRectangle(pts[2],pts[3],pts[7],pts[6],color,fill)
    self.draw3DRectangle(pts[1],pts[3],pts[7],pts[5],color,fill)

  def draw3DRectangle(self,v1,v2,v3,v4,color=(1,1,1,1),fill=True):
    #default to solid color
    if(len(color)==3):
      color = (color[0],color[1],color[2],1)

    #draw rectangle
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    glColor4f(color[0],color[1],color[2],color[3])
    glBegin(GL_QUADS)
    glVertex3f(v1[0],v1[1],v1[2])
    glVertex3f(v2[0],v2[1],v2[2])
    glVertex3f(v3[0],v3[1],v3[2])
    glVertex3f(v4[0],v4[1],v4[2])
    glEnd()
    if(fill):
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
  
  def draw2DRectangle(self,center,width=0.08,height=None,angle=0,color=(1,1,1),fill=True):
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

  def display(self):
    global robo
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(self.fov,self.aspect,self.near,self.far)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    loc = self.camera_location
    theta = self.look_dir[0]
    l = math.sin(theta)/math.cos(theta/2)
    phi = (math.pi-theta)/2
    lookpt = [loc[0]-l*math.sin(phi),loc[1],loc[2]-l*math.cos(phi)+1]
    gluLookAt(*loc, *lookpt, *[0, 1, 0]) #+y is always up

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #floor
    self.draw3DRectangle(*[(-1000,0,-1000),(100,0,-1000),(1000,0,1000),(-1000,0,1000)],color=(0,0,0))
    
    #blocks
    self.draw3DRectangle(*[(-20,-20,100),(20,-20,100),(20,20,100),(-20,20,100)],color=(1,0,0))
    self.draw3DRectangle(*[(-20,-20,-100),(20,-20,-100),(20,20,-100),(-20,20,-100)],color=(1,0,1))
    self.drawRectangularPrism((-50,-50,-50),(50,50,50))

    glutSwapBuffers()

  def reshape(self,width,height):
    glViewport(0,0,width,height)
    self.width = width
    self.height = height
    self.aspect = self.width/self.height
    self.display()
    glutPostRedisplay()

  def keyPressed(self,key,mouseX,mouseY,special=False):
    if(special):
      loc = self.camera_location
      theta = self.look_dir[0]
      l = math.sin(theta)/math.cos(theta/2)
      phi = (math.pi-theta)/2
      xdif = -l*math.sin(phi)
      zdif = 1-l*math.cos(phi)
      length = (xdif**2+zdif**2)**0.5
      xdif /= length
      zdif /= length
      if(key==GLUT_KEY_UP):
        self.camera_location[0] += xdif
        self.camera_location[2] += zdif
      elif(key==GLUT_KEY_DOWN):
        self.camera_location[0] -= xdif
        self.camera_location[2] -= zdif
      elif(key==GLUT_KEY_LEFT):
        self.look_dir[0] -= math.pi/180
      elif(key==GLUT_KEY_RIGHT):
        self.look_dir[0] += math.pi/180
      else:
        print("Pressed "+str(key)+" at (%d,%d)" % (mouseX,mouseY))
    elif(key == b'\x1b'): #kill window
      glutDestroyWindow(self.window)
      glutLeaveMainLoop()
    elif(key == b'q'):
      self.camera_location[1] += 0.5
    elif(key == b'z'):
      self.camera_location[1] -= 0.5
    elif(key == b'i'):
      print(self.camera_location)
    else:
      print("Pressed "+str(key)+" at (%d,%d)" % (mouseX,mouseY))



#dummy program to show off viewer
if __name__ == '__main__':
  import random,time #just for demo purposes!
  viewer = OpenGLViewer(bgcolor=(0.4,0.4,0.4)) #create window
  viewer.startThread() #background window and begin displaying
  print("main program begins.")
  while viewer.thread.is_alive():
    time.sleep(1)
  print("Program terminated")
