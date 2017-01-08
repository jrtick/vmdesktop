##This file is inspired by
##https://gist.github.com/claymcleod/028386b860b75e4f5472
#works with python AND python3, assuming you have the below libraries

import pygame #used for recognizing ps4 controller as a joystick
import os #used for printing realtime controller setup
import time #used for timing stats and polls
import threading #used for monitoring controller in background

#whether this is a library or a test
run_as_app = (__name__ == "__main__")

class PS4Controller(object):
  #class variables
  pygame_initialization_complete = False
  system_controller_count = 0


  def __init__(self,controllerID=0,displayInfo=False):
    self.thread = None #not running in background
    self.killRequest = False #can request to stop a bg thread

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
    else:
      print("Error. Could not find PS4 controller. Is your controller attached via USB to your computer?")
    
    #create a PS4 controller specific button map
    #arrows are mapped to the pygame joystick hat
    #bumpers also have an axis associated to them
    #no touchpad support that I know of (google?)
    self.buttonMap = ["square","x","circle","triangle","left-trigger-button","right-trigger-button","left-bumper","right-bumper","share","options","left-press","right-press","power","touchpad","left","right","up","down"]
    self.buttonValues = dict()
    for button in self.buttonMap:
      self.buttonValues[button] = False #not pressed

    self.axisMap = ["left-horizontal","left-vertical","right-horizontal","left-trigger","right-trigger","right-vertical"]
    self.axisValues = dict()
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
      val = event.value
      wall = 0.99999999999
      if(val<-wall):
        val= -wall
      elif(val>wall):
        val=wall
      if(event.axis in [3,4]): #triggers should only go from 0 to 1
        self.axisValues[self.axisMap[event.axis]] = (val+1)*0.5
      elif(event.axis in [1,5]): #vert movement vals need flipped
        self.axisValues[self.axisMap[event.axis]] = -val
      else:
        self.axisValues[self.axisMap[event.axis]] = val
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
    if(self.thread is not None):
      print("Don't call listen_foreground if you have listen_background running.")
      print("This leads to performance issues (lag).")
      print("You can call '__youcontrollervar__.stop_listening()' to kill the background listening process")
      return -1
    while True:
      different = False
      for event in pygame.event.get():
        different = True
        self.processEvent(event)
      if(different):
        os.system("clear")
        self.print_status()


  def bg_proc(self):
    while(not self.killRequest):
      for event in pygame.event.get():
        self.processEvent(event)
  def listen_background(self):
    self.killRequest = False #assert that this thread will start
    if(self.thread is not None): #don't fork more than once
      print("Already listening to this device")
      return -1
    self.thread = threading.Thread(target=self.bg_proc)
    self.thread.daemon = True
    self.thread.start()


  def clear_vars(self):
    for button in self.buttonMap:
      self.buttonValues[button] = False #not pressed
    for axis in self.axisMap:
      self.axisValues[axis] = 0.0 #no pressure on joystick
  def stop_listening(self):
    if(self.thread is not None):
      self.killRequest = True #tell bg thread to stop listening
      print("Attempting to kill process...")
      while(self.thread.isAlive()):
        time.sleep(1)
      self.thread = None
      self.clear_vars()
      print("Process killed")


  def getValue(self,name):
    if(self.thread is None):
      print("Warning, you have not setup the event listener.")
      return -1
    elif(name in self.buttonMap):
      return self.buttonValues[name]
    elif(name in self.axisMap):
      return self.axisValues[name]
    else:
      print("Query not recognized. Acceptable queries are:")
      print(self.buttonMap)
      print(self.axisMap)



if(run_as_app):
  start = time.time()
  controller = PS4Controller(displayInfo=True)
  end = time.time()
  print("setup completes in %.2f seconds" % (end-start))
  time.sleep(2)
  controller.listen_foreground()
