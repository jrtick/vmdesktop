import socket

class Client(object):
  def __init__(self,ipaddr,port):
    self.ipaddr = ipaddr
    self.port = port
    print("opening connection...",end="")
    self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.client.connect((ipaddr,port))
    print("Connected!")

  def send(self,message):
    msglen = str(len(message))
    msg = "0"*(10-len(msglen))+msglen
    self.client.sendall(msg.encode())
    self.client.sendall((message).encode())

  def close(self):
    self.client.sendall("q".encode())
    self.client.close()


if __name__ == "__main__":
  print("Enter the ip address you are connecting to:")
  host = input().strip()
  if(host==""): host = "localhost"
  print("Enter the port you are connecting to:")
  port = input().strip()
  if(port==""): port = 42
  else: port = eval(port) 

  client = Client(host,port)

  while True:
    print("Type messages below (press enter to send)")
    message = input().strip()
    if(message==""): message = "[]"
    client.send(message)
    if(message == 'q'):
      break

  client.close()
