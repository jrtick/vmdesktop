import Communication,Players

COMMUNICATE = False

#setup connections
player = Players.Webcam() #Players.cozmoRobot()
if COMMUNICATE:
  player.communicator = Communication.Sender(ipaddr="localhost",port=42)
else:
  player.communicator = None
player.worldMap.display() #show world viewer

#update world view until user closes world map
while player.worldMap.viewer.is_visible:
  player.updateLook() #look for objects
  if COMMUNICATE:
    player.communicator.send(str(player.uniqueObjects)) #tell mother node

#cleanup when done
if COMMUNICATE:
  player.communicator.close()
