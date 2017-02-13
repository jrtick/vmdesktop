import socket

class Client(object):
  def __init__(self,client,ipaddr,port):
    self.client = client
    self.ipaddr = ipaddr
    self.port = port
  def send(self,message):
    self.client.send(message.encode())
  def close(self):
    self.send('q')
    self.client.close()

def getConnection(host = "localhost", port = 42):
  print("opening connection...",end="")
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  client.connect((host,port))
  print("Connected!")

  return Client(client,host,port)


if __name__ == "__main__":
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  print("Enter the ip address you are connecting to:")
  host = input().strip()
  print("Enter the port you are connecting to:")
  port = eval(input())

  client.connect((host,port))

  print("Connected! Type messages below (press enter to send)")
  while True:
    message = input().strip()
    client.send(message.encode())
    if(message == 'q'):
      break

  client.close()
