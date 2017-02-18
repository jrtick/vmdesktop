import socket,threading


MESSAGE_HEADER_LENGTH = 10
MAX_CONNECTIONS = 10

class WIFICommunicator(object):
  def __init__(self,ipaddr="localhost",port=42):
    self.ipaddr = ipaddr
    self.port = port
    self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.clients = dict() #no one is connected to this
    self.listener = None #no server thread running by default
    self.ready=False
  def getMyIP(self):
    #get my ip address
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(('google.com',0))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr
  def connect(self):
    print("Did nothing.")
  def send(self,message):
    return False #default cannot send messages
  def receive(self):
    return (False,None) #default cannot receive messages
  def close(self):
    if self.read:
      self.ready = False
      for clientAddress in self.clients:
        self.clients[clientAddress].close()
        del(self.clients[clientAddress])
      self.socket.close()

class Sender(WIFICommunicator):
  def connect(self):
    print("Getting connection...",end="")
    self.socket.connect((self.ipaddr,self.port))
    self.ready = True
    print("Connected!")
  def send(self,message):
    if not self.ready:
      print("Error: You didn't connect the Sender yet.")
      raise Exception("Not Connected.")
    global MESSAGE_HEADER_LENGTH
    msglen = str(len(message))
    msg = "0"*(MESSAGE_HEADER_LENGTH-len(msglen))+msglen
    self.socket.sendall(msg.encode())
    self.socket.sendall((message).encode())
    return True
  def close(self):
    if(self.ready):
      self.send("q")
      super().close()

class Receiver(WIFICommunicator):
  def __init__(self,ipaddr=None,port=42):
    if(ipaddr is None):
      super().__init__(self.getMyIP(),port)
    else:
      super().__init__(ipaddr,port)
  def connect(self):
    self.socket.bind((self.ipaddr,self.port))

    self.listener = threading.Thread(target = self.startListening)
    self.listener.daemon = True #close if program closes
    self.listener.start()

    self.ready = True
    print("Starting server at %s on port %d..." % (self.ipaddr,self.port))
  def startListening(self,connections=MAX_CONNECTIONS):
    self.socket.listen(connections) #not fully sure if this is correct
    while len(self.clients) <= connections:
      (client,clientaddr) = self.socket.accept()
      self.clients[clientaddr] = client
      print("Connected to "+str(clientaddr))
  def receive(self,clientAddress):
    global MESSAGE_HEADER_LENGTH
    if clientAddress not in self.clients:
      print("Error: Client %s does not exist" % (clientAddress))
      return (False,None)
    else:
      client = self.clients[clientAddress]
      #first get message length
      size = client.recv(MESSAGE_HEADER_LENGTH).decode()
      i=0
      while size[i]=="0": i+=1
      size = eval(size[i:])

      #now get message
      msg = client.recv(size).decode()
      if msg == "q":
        client.close()
        del(self.clients[clientAddress])
        return (False,None)
      else:
        return (True,msg)
