import Communication,Players

COMMUNICATE = True
BECOME_SERVER = True

#setup connections
player = Players.Webcam() #Players.cozmoRobot()


if BECOME_SERVER:
  server = Communication.Receiver(ipaddr="localhost",port=42)
  server.connect()

if COMMUNICATE:
  player.communicator = Communication.Sender(ipaddr="localhost",port=42)
  player.communicator.connect()
  print("Player connected!")
else:
  player.communicator = None

player.worldMap.display() #show world viewer

#update world view until user closes world map
while player.worldMap.viewer.is_visible:
  player.updateLook() #look for objects
  if COMMUNICATE:
    player.communicator.send(str(player.worldMap.viewer.objects)) #tell mother node

#cleanup when done
if COMMUNICATE:
  player.communicator.close()
