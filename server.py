import socket
from password_strength import PasswordStats
from Crypto2           import crypto
from messageParser     import messageParser

#INITIALISE ENCRYPTION OBJECT/ KEYS
c = crypto()
crypto.genKeys(c)
crypto.storeKeys(c)
publicKey = crypto.loadPublicKey(c)

#INITIALISE MESSAGEPARSER
parser = messageParser()

#SETUP SERVER
host = socket.gethostname()
port = 9999
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen(1)

print("Server Active\n\n" + str(publicKey) + "\n")

while True:
  #SENDING SERVERS PUBLIC KEY
  clientSocket, addr = serverSocket.accept()
  print("Connected to: %s" % str(addr))
  clientSocket.send(publicKey)

  #GETTING CLIENTS PUBLIC KEY
  clientPublicKey = clientSocket.recv(1024)
  print("client public\n" + clientPublicKey)
  clientPublicKey = crypto.loadPublicKeyFromBytes(c, clientPublicKey)

  #GETTING MESSAGE, DECRYPT IT, PRINT 
  while True:
    msg = clientSocket.recv(1024)
    if(len(msg) == 294):
      #DECRYPT DATA
      msg = crypto.decryptData(c, msg)

      #PARSE MESSAGE INTO ITS COMPONENTS
      command, dataLen, data, checksum = messageParser.parse(parser, msg)
      print("COMMAND: " + str(command) + "\nDATA LEN: " + str(dataLen) + "\nDATA: " + str(data) + "\nCHECKSUM: " + checksum)

      if(command == "0"):
        print("\ntrying to sign up")
      elif(command == "1"):
        print("\ntrying to log in")
      elif(command == "2"):
        print("\nsomething else")


  clientSocket.close()
