import cv2.aruco


class Tag(object):
  """tag struct"""
  def __init__(self,pos,rot,tagID):
    self.pos = pos
    self.rot = rot
    self.id = tagID

  def __str__(self):
    return "id: %d trans: (%.2f,%.2f,%.2f) rot = (%.2f,%.2f,%.2f)" % \
                   (self.id,self.pos[0],self.pos[1],self.pos[2],self.rot[0],self.rot[1],self.rot[2])

class TagSet(object):
  """set of currently visible tags"""
  def __init__(self):
    self.tags = []
    self.isUpdated = False

  def update(self,tag):
    new = True
    self.isUpdated = True
    for t in self.tags:
      if t.id == tag.id:
        new = False
        t.pos = tag.pos
        t.rot = tag.rot
        break
    if new:
      self.tags += [tag]

  def wipe(self):
    self.tags = []


def tuple3Add(x,y): return (x[0]+y[0],x[1]+y[1],x[2]+y[2])
def tuple3Sub(x,y): return (x[0]-y[0],x[1]-y[1],x[2]-y[2])

class ArucoWatcher(object):
  def __init__(self,camera,tagSize=50,tagDictionary=cv2.aruco.DICT_4X4_250):
    self.camera = camera #from my camera.py library
    self.arucoDict = cv2.aruco.Dictionary_get(tagDictionary)
    self.tagSize = tagSize
    self.tagset = TagSet() #will keep track of current tags in memory

  def detect(self):
    im = self.camera.getGrayscaleImage()
    (corners,ids,_) = cv2.aruco.detectMarkers(im,self.arucoDict)
    
    if ids is not None:
      cammat = self.camera.cameraMatrix
      camdistortion = self.camera.distortionArray
      (rots,trans) = cv2.aruco.estimatePoseSingleMarkers(corners,self.tagSize,cammat,camdistortion)
      for i in range(len(ids)): #update understanding of the world
        curtag = Tag(trans[i][0],rots[i][0],ids[i][0])
        self.tagset.update(curtag)


