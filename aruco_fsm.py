from cozmo_fsm import *
import numpy,cv2,time

class StateMachineProgram(StateNode):
  def __init__(self,showDisplay=True,arucolibname=cv2.aruco.DICT_4X4_250):
    super().__init__()
    
    #setup cozmo image stream
    self.robot.camera.image_stream_enabled = True
    while(self.robot.world.latest_image is None):
      time.sleep(0.2)

    if(showDisplay):
      #setup opencv display window
      cv2.namedWindow(self.windowName)
      cv2.startWindowThread()

    #setup aruco dictionary
    self.aruco_lib = cv2.aruco.Dictionary_get(aruco_lib)
    self.aruco_params = cv2.aruco.DetectorParameters_create()
    



class ArucoSearch(StateNode):
  def init(self,aruco_lib = cv2.aruco.DICT_4X4_100):
    """user needs to specify which aruco dict they want cozmo to look for"""
    super.__init__()

    #setup aruco dictionary
    self.aruco_lib = cv2.aruco.Dictionary_get(aruco_lib)
    self.aruco_params = cv2.aruco.DetectorParameters_create()

    #setup any necessary vars
    self.windowName = "aruco_frame"


  def start(self,event=None):
    if self.running: return
    super().start(event)

    #setup cozmo image stream
    self.robot.camera.image_stream_enabled = True
    while(self.robot.world.latest_image is None):
      time.sleep(0.2)

    #setup opencv display window
    cv2.namedWindow(self.windowName)
    cv2.startWindowThread()

    #run aruco detection until user presses 'q'
    while True:
      (_,_,im) = self.detect()
      cv2.imshow(self.windowName,im)
      if(cv2.waitKey(1) & 0xFF == ord('q')):
        break


  def stop(self):
    if not self.running: return
    cv2.destroyWindow(self.windowName) #close window
    super().stop()


  def detect(self):
    #grab an image
    cozmoim = robot.world.latest_image.raw_image
    curim = np.array(cozmoim).astype(np.uint8)
    gray = cv2.cvtColor(curim,cv2.COLOR_BGR2GRAY)

    #detect tags & annotate image
    (corners,ids,_) = cv2.aruco.detectMarkers(gray,self.aruco_lib,parameters=self.aruco_params)
    curim = arudo.drawDetectedMarkers(curim,corners,ids)

    #return ids, bboxes, and an annotated im for display
    return (ids,corners,curim)
