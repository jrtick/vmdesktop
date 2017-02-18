import cv2 #needed for webcam

import cozmo,numpy,time,threading #needed for cozmo

class Camera(object):
  def __init__(self):
    self.id = None
    self.distortionArray = numpy.array([[0,0,0,0,0]]).astype(float)
    self.cameraMatrix = numpy.array([[1,0,0],[0,1,0],[0,0,1]]).astype(float)

  def getImage(self,size=None):
    return None #empty
  def __del__(self):
    pass
  def stream(self,gray=False,size=None):
    """opens a window continuously streaming camera"""
    self.streamingName = "streaming"
    print("Press 'q' to stop streaming.")

    while cv2.waitKey(1) & 0xFF != ord('q'):
      if(gray):
        im = self.getGrayscaleImage(size)
      else:
        im = self.getImage(size)
      cv2.imshow(self.streamingName,im)

    cv2.destroyWindow(self.streamingName)
    self.streamingName = None

  def getGrayscaleImage(self,size=None):
    image = self.getImage(size)
    return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)


class LaptopCam(Camera):
  def __init__(self):
    """Create a webcam object. Only one can exist at a time."""
    super().__init__()
    self.id = 0 #can only have one anyways...
    self.cameraMatrix = numpy.array([[40,0,240],[0,40,320],[0,0,1]]).astype(float)
    self.mycam = cv2.VideoCapture(0)
    self.streamingName = None
    
    #see if can connect to camera
    (connected,_) = self.mycam.read()
    if not connected:
      self.mycam.release()
      raise Exception("Camera could not be accessed.")

  def getImage(self,size=None):
    """returns image from webcam. size should be (width,height)"""
    (succeeds,image) = self.mycam.read()
    if succeeds:
      if size is None: return image
      else: return cv2.resize(image,size)
    else:
      raise Exception("Image could not be read.")

  def __del__(self):
    """releases webcam."""
    super().__del__()
    self.mycam.release()

class CozmoCam(Camera):
  def __init__(self):
    """starts cozmo running as a background thread."""
    super().__init__()
    self.cameraMatrix = numpy.array([[290,0,120],[0,290,160],[0,0,1]]).astype(float)
    self.thread = threading.Thread(target = lambda: cozmo.run_program(self.setupCozmo))
    self.thread.daemon = True #close if program closes
    self.run = True
    self.thread.start()
    while self.cozmo_id is None: #will be set by thread
      time.sleep(0.2)

  def getImage(self,size=None):
    try:
      assert(self.run)
      image = numpy.array(self.robot.world.latest_image.raw_image).astype(numpy.uint8)
    except:
      raise Exception("Could not access cozmo's camera")

    if size is None: return image
    else: return cv2.resize(image,size)

  def setupCozmo(self,robot):
    self.robot = robot
    robot.camera.image_stream_enabled = True
    while robot.world.latest_image is None: time.sleep(0.2)
    
    self.id = self.robot.robot_id

    while self.run: #keep cozmo alive by infinitely looping
      time.sleep(1)

  def __del__(self):
    """releases cozmo."""
    super().__del__()
    self.run = False #will kill cozmo in one sec
















