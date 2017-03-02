import cozmo
import cv2,numpy,time,threading

import Landmarks #need to know what to look for
import LocalMap #need to keep track of objects

###########helper classes for camera calibration & obj detection ###########
class Sight(object):
  def __init__(self,cameraMatrix,distortionArray=None):
    self.matrix = cameraMatrix
    if distortionArray is None:
      self.distortion = numpy.array([[0,0,0,0,0]]).astype(float)
    else: self.distortion = distortionArray

class Detector(object):
  def __init__(self,parent,detector_type="Blind"):
    self.parent = parent
    self.type = detector_type
  def detect(self,image,origin=None,curRot=(0,0,0)):
    return (False,[]) #sees nothing
  def __str__(self):
    return str(self.type)+" Detector"

class CozmoCubeDetector(Detector):
  def __init__(self,parent):
    if not isinstance(parent,CozmoRobot):
      print("Error: only a cozmo robot can detect cozmo cubes.")
      raise Exception("Incompatible Detector")
    super().__init__(parent,"Cube")
  def detect(self,origin=(0,0,0),curRot=(0,0,0)):
    robot = self.parent.robot
    return (False,[]) #how do I get list of seen cubes?!?!?!

class Aruco4x4Detector(Detector):
  def __init__(self,parent,tagSize=50):
    super().__init__(parent,"ArucoTag4x4x250")
    self.tagSize = tagSize
    self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)

  def detect(self,origin=(0,0,0),curRot=(0,0,0)):
    sight = self.parent.vision
    image = self.parent.getImage(gray=True)
    (corners,ids,_) = cv2.aruco.detectMarkers(image,self.arucoDict)
    seenTags = []
    sawSomething = (ids is not None)

    if sawSomething:
      (rots,trans) = cv2.aruco.estimatePoseSingleMarkers( \
                         corners,self.tagSize,sight.matrix,sight.distortion)
      for i in range(len(ids)): #create tag objects
        tvec = trans[i][0]
        tvec = (tvec[0]+origin[0],tvec[1]+origin[1],tvec[2]+origin[2])
        rvec = rots[i][0]
        rvec = (rvec[0]+curRot[0],rvec[1]+curRot[1],rvec[2]+curRot[2])
        curtag = Landmarks.ArucoTag4X4(ids[i][0],tvec,rvec)
        seenTags.append(curtag)

    return (sawSomething,seenTags)


######Player class definition##########
class Player(object):
  def __init__(self,vision,name="Unknown",detectors=[]):
    self.name = name
    self.streamingName = None #not currently streaming vision
    self.worldMap = LocalMap.Map()

    if isinstance(vision,Sight):
      self.vision = vision
    else:
      print("Error. Vision must be an object of type 'Sight'")
      raise Exception("Incorrect parameter")

    for detector in detectors:
      if not isinstance(detector,Detector):
        print("Error. Detectors must all be objects of type 'Detector'")
        raise Exception("Incorrect parameter")
    self.detectors = detectors

  def getImage(self,gray=False,size=None):
    return None #default player is blind
  
  def streamVision(self,gray=False,size=None):
    self.streamingName = "streaming"
    print("Press 'q' to stop streaming.")

    while cv2.waitKey(1) & 0xFF != ord('q'):
      im = self.getImage(gray,size)
      cv2.imshow(self.streamingName,im)

    cv2.destroyWindow(self.streamingName)
    self.streamingName = None

  def updateLook(self,position=(0,0,0),rotation=(0,0,0)):
    visible_objects = []
    for detector in self.detectors:
      (seesSomething,objects) = detector.detect(position,rotation)
      if(seesSomething):
        visible_objects += objects

    #CURRENTLY JUST PRINTS THE VISIBLE OBJECTS.
    #IN THE FUTURE, WILL UPDATE LOCAL MAP TO KEEP TRACK
    for obj in visible_objects:
      p = obj.pos
      self.worldMap.addObject(obj.unique_id,(p[0]-2,p[1]-2,p[2]-2),\
                                            (p[0]+2,p[1]+2,p[2]+2),(1,0,0))

class Webcam(Player):
  def __init__(self):
    #first, make sure webcam exists
    self.camera = cv2.VideoCapture(0)
    (connected,_) = self.camera.read()
    if not connected:
      self.camera.release()
      raise Exception("Webcam could not be accessed")


    #Now, setup vision & super
    cameraMatrix = numpy.array([[40,0,240],[0,40,320],[0,0,1]]).astype(float)
    webcamSight = Sight(cameraMatrix)
    super().__init__(webcamSight,name="Webcam",detectors=[Aruco4x4Detector(self)])

  def getImage(self,gray=False,size=None):
    (succeeds,image) = self.camera.read()
    if succeeds:
      if size is not None: image = cv2.resize(image,size)
      if gray: image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
      return image
    else:
      raise Exception("Webcam image could not be read")

  def __del__(self): #THIS DOESN"T GET CALLED AUTOMATICALLY
    self.camera.release()


class CozmoRobot(Player):
  def __init__(self):
    #first, connect to cozmo
    self.cozmo_id = None #this will be reset by setupCozmo
    self.thread = threading.Thread( \
                     target = lambda: cozmo.run_program(self.setupCozmo))
    self.thread.daemon = True #close if program closes
    self.run = True
    self.thread.start()
    while self.cozmo_id is None: time.sleep(0.2) #will be reset by setupCozmo

    #now that cozmo is connected, setup vision & super
    cameraMatrix = numpy.array([[290,0,120],[0,290,160],[0,0,1]]).astype(float)
    cozmoSight = Sight(cameraMatrix)
    super().__init__(cozmoSight,name="Cozmo "+str(self.cozmo_id), \
                 detectors = [Aruco4x4Detector(self),CozmoCubeDetector(self)])


  def setupCozmo(self,robot):
    #setup camera
    self.robot = robot
    self.robot.camera.image_stream_enabled = True
    while self.robot.world.latest_image is None: time.sleep(0.2)
    
    #grab cozmo's ID for reference
    self.cozmo_id = self.robot.robot_id

    #keep cozmo alive via an infinite loop
    while self.run: time.sleep(0.5)


  def getImage(self,gray=False,size=None):
    try:
      image = self.robot.world.latest_image.raw_image
      image = numpy.array(image).astype(numpy.uint8)
      if size is not None: image = cv2.resize(image,size)
      if gray: image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
      return image
    except:
      raise Exception("Could not access cozmo's camera")


  def __del__(self):
    self.run = False
    time.sleep(0.5)
