from sys import exit

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
  print("pyOpenGL imported")
except:
  print("Can't locate pyopengl. Please install.")
  exit(0)

#GLOBAL VARS#
Window = None
WindowSize = (600,600)

def display():
  global WindowSize
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  gluPerspective(50,WindowSize[0]/WindowSize[1],0.5,20.0) #fov,aspect,near,far

  #make axes
  axes = glGenLists(1)
  glNewList(axes, GL_COMPILE)
  glPushMatrix()
  glTranslate(0, 0, -5)
  make_cube((1,1,10), highlight=True, color=color_red, edges=False)
  glPopMatrix()
  glPushMatrix()
  glTranslate(-5, 0, 0)
  make_cube((10,1,1), highlight=True, color=color_green, edges=False)
  glPopMatrix()
  glPushMatrix()
  glTranslate(0, 5, 0)
  make_cube((1,10,1), highlight=True, color=color_blue, edges=False)
  glPopMatrix()
  glEndList()

  glCallList(axes)
  glutSwapBuffers()
  print("Hi")

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(WindowSize[0],WindowSize[1])
Window = glutCreateWindow(b"PyOpenGL Viewer")
glClearColor(0,0,0,0)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)
glutDisplayFunc(display)
glutMainLoop()
