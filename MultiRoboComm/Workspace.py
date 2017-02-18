import Communication,Players


#setup connections
player = Players.Webcam() #Players.cozmoRobot()
player.communicator = Communication.Sender(ipaddr="localhost",port=42)
player.worldMap.display() #show world viewer

#update world view until user closes world map
while player.worldMap.viewer.is_visible:
  player.updateLook() #look for objects
  player.communicator.send(str(player.uniqueObjects)) #tell mother node

#cleanup when done
player.communicator.close()
