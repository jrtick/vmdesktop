import socket
from threading import Thread

class Server(object):
  def __init__(self,ipaddr=None,port=42):
    self.ipaddr = ipaddr
    self.port = port
    self.clients = []

    if(ipaddr is None):
      #get my ip address
      s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
      s.connect(('google.com',0))
      ipaddr = s.getsockname()[0]
      s.close()

    #now, setup a server
    print("Starting server at %s on port %d..." % (ipaddr,port))
    self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.server.bind((ipaddr,port))


  def listen_foreground(self,count = 1):
    if(count==1):
      print("Awaiting connection...")
    else:
      print("Awaiting %d connections..." % (count))
    self.server.listen(count)

    for i in range(count):
      (client,clientaddr) = self.server.accept()
      self.clients.append((client,clientaddr))
      print("connected to "+str(client))

    print("All connected! Ready to receive messages")

  def await_message(self,clientNum,size=None):
    if(clientNum >= len(self.clients)):
      print("Error. Client %d does not exist" % (clientNum))
      return
    else:
      if(size is None):
        size = self.clients[clientNum][0].recv(10).decode().strip()
        i=0
        while size[i]=="0": i+=1
        size = eval(size[i:])
      msg = self.clients[clientNum][0].recv(size).decode().strip()
      print("%s says %s" % (self.clients[clientNum][1],msg))
      if msg == "q":
        self.clients[clientNum][0].close()
        del(self.clients[clientNum])
      return msg

  def listen_background(self,count=1):
    self.thread = Thread(target=self.listen_foreground, args=[count])
    self.thread.daemon = True #ending fg program will kill bg program
    self.thread.start()

  def send(self,message):
    self.server.send(message.encode())

  def close(self):
    for client in self.clients:
      client.close()
    self.server.close()
    print("Server closed.")




if __name__ == "__main__":
  port = 42

  #get my ip address
  s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
  s.connect(('google.com',0))
  ipaddr = s.getsockname()[0]
  s.close()

  #now, setup a server
  print("Starting server at %s on port %d..." % (ipaddr,port))
  server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  host = ipaddr
  server.bind((host,port))

  #get a connection
  print("awaiting connection...")
  server.listen(1)
  (client,clientaddr) = server.accept()
  print("connected to "+str(client))

  #print received messages
  while True:
     data = client.recv(1024).decode().strip()
     print("client says: %s" % (data))
     if(data == 'q'):
       break

  #garbage collect
  client.close()
  server.close()
