import cv2.aruco

#######HELPER FUNCTIONS ###############
def coordToStr(v,precision=2):
  (x,y,z) = v
  format_string = "%."+str(precision)+"f"
  xStr = format_string % (x)
  yStr = format_string % (y)
  zStr = format_string % (z)
  return "(%s,%s,%s)" % (xStr,yStr,zStr)

####END HELPER FUNCTIONS ################


######DEFINITION OF LANDMARKS###############
class Landmark(object):
  def __init__(self,position=[0,0,0],rotation=[0,0,0], \
               landmark_type = "Unknown",landmark_id = None):
    #to orient about a single object, need BOTH position and rotation
    self.pos = position
    self.rot = rotation

    #for matching Landmarks, need IDs and types
    self.type = landmark_type
    self.type_id = landmark_id
    self.unique_id = str(self.type)+"_"+str(self.type_id)

  #print functions
  def __str__(self):
    return self.unique_id+" with pos/rot=(%s,%s)" % \
               (coordToStr(self.pos),coordToStr(self.rot))
  def __repr__(self): 
    return self.unique_id


class ArucoTag4X4(Landmark):
  def __init__(self,tagNum,position=[0,0,0],rotation=[0,0,0]):
    super().__init__(position,rotation,"ArucoTag_4x4",tagNum)

class Cube(Landmark):
  def __init__(self,cubeNum,position=[0,0,0],rotation=[0,0,0]):
    super().__init__(position,rotation,"Cube",cubeNum)



class ArucoTagInfo(object):
  """This class keeps track of tag dictionary and tag size"""
  def __init__(self,tagDictionary=cv2.aruco.DICT_4X4_250,tagSize=50):
    self.arucoDict = cv2.aruco.Dictionary_get(tagDictionary)
    self.tagSize = tagSize
