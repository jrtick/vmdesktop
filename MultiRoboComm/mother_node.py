#this is the server program that will listen to all clients

import viewerlib #will show global map
import server #my server library

import time

#start connection
server_connection = server.setupConnection("localhost")
server_connection.listen_background(2) #allow two robots to connect
while len(server_connection.clients) == 0):
  time.sleep(1)

#if you reach here, you have at least one client
while len(server_connection.clients > 0):
  #grab an update from every client
  msgs = []
  for i in range(len(server_connection.clients)):
    msgs.append(eval(server_connection.await_message(i)))

  #GOFISH protocol. Everyone broadcasts what landmarks they see and this matches them up.
  #message should evaluate to an array of tag IDs

  for i in range(len(msgs)):
    for tagId in msgs[i]:
      for j in range(i+1,len(msgs)):
        if tagId in msgs[j]:
          pass
          #should 1) find rot & trans to align robot j to robot i
          #2) send robot j this alignment and have them synchronize
          #3) remember that robots i and j are connected
          #4) disconnect if either robot says it has been moved

#WHILE ALL THIS IS HAPPENING A GLOBAL WORLD MAP SHOULD BE DISPLAYED!!! 
  

#disconnect when finished
server_connection.close()
