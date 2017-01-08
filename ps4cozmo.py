import cozmo,time,cv2
import numpy as np
from ps4controller import PS4Controller as Controller

#globals
windowName = None
windowNameWhenActive = "viewport"
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
aruco_parameters = cv2.aruco.DetectorParameters_create()
seen_cubes = []

def shareController(robot,share_button):
  global windowName,windowNameWhenActive
  global aruco_dict,aruco_parameters
  global seen_cubes

  if(share_button and windowName is None): #create window
    print("initializing feed")
    windowName = windowNameWhenActive
    time.sleep(1)
  elif(share_button): #destroy window
    print("killing feed")
    cv2.destroyWindow(windowName)
    windowName = None
    seen_cubes = []
    time.sleep(1)

  image = np.array(robot.world.latest_image.raw_image).astype(np.uint8)

  #aruco marker detection
  gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
  (corners,ids,_) = cv2.aruco.detectMarkers(gray,aruco_dict,parameters=aruco_parameters)
  annotated = cv2.aruco.drawDetectedMarkers(gray,corners,ids)

  #cube detection
  try:
    #cube = robot.world.wait_for_observed_light_cube(timeout=0.01)
    cubes = robot.world.wait_until_observe_num_objects(num=3,object_type=cozmo.objects.LightCube,timeout=0.01)
    
    for cube in cubes:
      if not cube in seen_cubes:
        seen_cubes += [cube]
    #if(cube is not None):
    #  if(cube not in seen_cubes):
    #    seen_cubes += [cube]
  except:
    pass

  for cube in seen_cubes:
    #cube.set_lights(cozmo.lights.red_light.flash())
    cube.set_light_corners(None, None, None, None)
  for cube in cubes:
    cube.set_lights(cozmo.lights.green_light.flash())

  #face = robot.world.wait_for_observed_face(timeout=0.1)?

  #output image
  if(windowName is not None):
    annotated_image = np.copy(image)
    annotated_image[:,:,2] = annotated
    cv2.imshow(windowName,annotated_image)
    cv2.waitKey(1)


def armController(robot,value):
  robot.move_lift(4*value)

def headController(robot,value):
  robot.move_head(4*value)

def movementController(robot,value):
  (rotation,movement) = value
  if(abs(rotation)<0.1):
    rotation=0
  if(abs(movement)<0.01):
    movement=0
  left = 500*(movement+rotation)
  right = 500*(movement-rotation)
  robot.drive_wheels(left,right)

  #rotAngle = cozmo.util.degrees(rotation*20)
  #robot.turn_in_place(rotAngle).wait_for_completed()

#modified from 08_drive_to_charger_test.py from cozmo sdk examples
def drive_to_charger(robot):
  # try to find the charger
  charger = None

  if robot.world.charger and robot.world.charger.pose.is_comparable(robot.pose):
    charger = robot.world.charger #cozmo already knows locaton
  else:
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace) #look around
    charger = robot.world.wait_for_observed_charger(timeout=30)
    look_around.stop()

  if charger: #found the charger
    robot.go_to_object(charger, cozmo.util.distance_mm(65.0)).wait_for_completed()


def buttonController(robot,cross,circle,triangle,square):
  if(circle):
    drive_to_charger(robot)
  #tie buttons to actions? Like turn or goto charger or flash cubes
  #robot.pickup_object(targ).wait_for_completed() #06_pickup*

def cozmo_control(robot,controller):
  #robot.start_freeplay_behaviors()
  robot.set_all_backpack_lights(cozmo.lights.red_light)
  print("Robot connected.")

  print("Initializing camera...")
  robot.camera.image_stream_enabled = True
  curim = robot.world.latest_image
  while(curim is None):
    time.sleep(1)
    curim = robot.world.latest_image
  print("Camera initialized")

  while(not controller.getValue("power")):#hit power button to end
    #toggle camera with share button
    shareController(robot,controller.getValue("share"))

    #toggle arm setup with bumpers (left for up, right for down)
    leftval = controller.getValue("left-trigger")
    rightval = controller.getValue("right-trigger")
    armController(robot,leftval-rightval)

    #toggle head movement with right stick
    val = controller.getValue("right-vertical")
    headController(robot,val)

    #movement control with left stick
    horiz = controller.getValue("left-horizontal")
    vert  = controller.getValue("left-vertical")
    movementController(robot,(horiz,vert))

    #button controller
    xbutton = controller.getValue("x")
    obutton = controller.getValue("circle")
    tbutton = controller.getValue("triangle")
    sbutton = controller.getValue("square")
    buttonController(robot,xbutton,obutton,tbutton,sbutton)

  robot.set_backpack_lights_off()


if __name__ == "__main__":
  controller = Controller()
  controller.listen_background()

  cozmo.robot.Robot.drive_off_charger_on_connect = False
  cozmo.run_program(lambda robot: cozmo_control(robot,controller))

  controller.stop_listening()
  cv2.destroyAllWindows()
  print("Program terminated.")
