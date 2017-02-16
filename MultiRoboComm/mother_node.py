#this is the server program that will listen to all clients

import viewerlib #will show global map
import server #my server library

import time
from threading import Thread

NUM_CLIENTS=2
MARKERS = None


#start connection
server_connection = server.Server("localhost")
server_connection.listen_foreground(NUM_CLIENTS) #allow two robots to connect
MARKERS = [[] for i in range(NUM_CLIENTS)]


def updateMarkers():
  while True:
    #update every client
    for i in range(len(server_connection.clients)):
      msg = server_connection.await_message(i)
      if(msg=='q'): del(MARKERS[i])
      else: MARKERS[i]=eval(msg)
listen_thread = Thread(target=updateMarkers)
listen_thread.daemon = True #ending fg program will kill bg program
listen_thread.start()


#if you reach here, you have at least one client
while len(server_connection.clients) > 0:
  #GOFISH protocol. Everyone broadcasts what landmarks they see and this matches them up.
  #message should evaluate to an array of tag IDs
  for i in range(len(MARKERS)):
    for j in range(i+1,len(MARKERS)):
      print(MARKERS[i],MARKERS[j])
      #should 1) find rot & trans to align robot j to robot i
      #2) send robot j this alignment and have them synchronize
      #3) remember that robots i and j are connected
      #4) disconnect if either robot says it has been moved

#WHILE ALL THIS IS HAPPENING A GLOBAL WORLD MAP SHOULD BE DISPLAYED!!! 
  

#disconnect when finished
server_connection.close()
