##This file is inspired by
##https://gist.github.com/claymcleod/028386b860b75e4f5472

import pygame,os
import time,threading

#whether this is a library or a test
run_as_app = (__name__ == "__main__")

class PS4Controller(object):
  #class variables
  pygame_initialization_complete = False
  system_controller_count = 0


  def __init__(self,controllerID=0,displayInfo=False):
    self.thread = None #not running in background
    if(displayInfo):
      print("initializing controller...")
    #setup pygame
    if(not PS4Controller.pygame_initialization_complete):
      self.init_pygame(displayInfo)
    
    #find and initialize controller
    if(controllerID>=0 and controllerID<PS4Controller.system_controller_count):
      self.joystick = pygame.joystick.Joystick(controllerID)
      self.controllerID=controllerID
      if(not self.joystick.get_init()):
        self.joystick.init()
    
    #create a PS4 controller specific button map
    #arrows are mapped to the pygame joystick hat
    #bumpers also have an axis associated to them
    #no touchpad support that I know of (google?)
    self.buttonValues = dict()
    self.buttonMap = ["square","x","circle","triangle","left-trigger","right-trigger","left-bumper","right-bumper","share","options","left-press","right-press","power","touchpad","left","right","up","down"]
    for button in self.buttonMap:
      self.buttonValues[button] = False #not pressed

    self.axisValues = dict()
    self.axisMap = ["left-horizontal","left-vertical","right-horizontal","left-trigger","right-trigger","right-vertical"]
    for axis in self.axisMap:
      self.axisValues[axis] = 0.0 #no pressure on joystick
    
    if(displayInfo):
      print("controller initialized")


  def init_pygame(self,displayInfo=False):
    if(displayInfo):
      print("this is the first controller you are initializing. Initializing pygame...")
    #must init pygame if this is the first controller you are initializing
    pygame.init()
    count = pygame.joystick.get_count()
    PS4Controller.system_controller_count = count
    if(displayInfo):
      print("%d controllers connected to your system" % (count))
      if(count>0):
        print("There names are:")
        for i in range(count):
          cur_joystick = pygame.joystick.Joystick(i)
          print("%d -> %s" % (cur_joystick.get_id(),cur_joystick.get_name()))
    PS4Controller.pygame_initialization_complete = True


  def print_status(self):
    for button in self.buttonMap:
      print("%s: %d" % (button,self.buttonValues[button]))
    for axis in self.axisMap:
      print("%s: %.2f" % (axis,self.axisValues[axis]))

  def processEvent(self,event):
    if(event.type == pygame.JOYAXISMOTION):
      if(event.axis in [3,4]): #triggers should only go from 0 to 1
        self.axisValues[self.axisMap[event.axis]] = (event.value+1)*0.5
      elif(event.axis in [1,5]): #vert movement vals need flipped
        self.axisValues[self.axisMap[event.axis]] = -event.value
      else:
        self.axisValues[self.axisMap[event.axis]] = event.value
    elif(event.type == pygame.JOYBUTTONDOWN):
      self.buttonValues[self.buttonMap[event.button]] = True
    elif(event.type == pygame.JOYBUTTONUP):
      self.buttonValues[self.buttonMap[event.button]] = False
    elif(event.type == pygame.JOYHATMOTION):
      self.buttonValues[self.buttonMap[14]]=(event.value[0]==-1)
      self.buttonValues[self.buttonMap[15]]=(event.value[0]==1)
      self.buttonValues[self.buttonMap[16]]=(event.value[1]==1)
      self.buttonValues[self.buttonMap[17]]=(event.value[1]==-1)


  def listen_foreground(self):
    print("beginning listen stream...")
    while True:
      different = False
      for event in pygame.event.get():
        different = True
        self.processEvent(event)
      #if(different):
      #  os.system("clear")
      #  self.print_status()

  def bg_proc(self):
    while True:
      for event in pygame.event.get():
        self.processEvent(event)

  def listen_background(self):
    if(self.thread is not None): #don't fork more than once
      print("Already listening to this device")
      return -1
    self.thread = threading.Thread(target=self.bg_proc)
    self.thread.daemon = True
    self.thread.start()

if(run_as_app):
  start = time.time()
  controller = PS4Controller(displayInfo=True)
  controller.listen_background()
  end = time.time()
  print("setup completes in %.2f seconds" % (end-start))

  while True:
    time.sleep(0.1)
    os.system("clear")
    controller.print_status()
