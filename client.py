import socket
import time
import os
from Crypto2       import crypto
from messageParser import messageParser
import getpass

#INITIALISE ENCRYPTION OBJECT/ KEYS
cr = crypto()
crypto.genKeys(cr)
crypto.storeKeys(cr)
publicKey = crypto.loadPublicKey(cr)

#INITIALISE MESSAGEPARSER
parser = messageParser()

#CONNECTING TO THE SERVER
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()                           
port = 9999
clientSocket.connect((host, port))  

#RECEIVING SERVERS PUBLIC KEY
serverPublicKey = clientSocket.recv(1024)
print(serverPublicKey)
serverPublicKey = crypto.loadPublicKeyFromBytes(cr, serverPublicKey)

#SEND CLIENTS PUBLIC KEY
clientSocket.send(publicKey)

#TEST MESSAGE
#data = "Bingo Bango Bongo!"
#sentMsg = messageParser.make(parser, cr, serverPublicKey, 255, data)
#print(sentMsg)
#signature = crypto.signMessage(cr, sentMsg)
#clientSocket.send(sentMsg)


#USER INTERFACE
while True:
  os.system('clear')
  print("------------------------\n1: Log in\n2: Sign up\n------------------------\n")
  choice = raw_input()

  if(choice == "1"):
    #LOG IN - (0, data length, "username,password,", checksum)
    os.system('clear')
    print("Username: ")
    userName = raw_input()
    password = getpass.getpass("Password: ")
    data = userName + "," + password + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey, 1, data)

    if(messageParser.checkData(parser, userName)):
      if(messageParser.checkData(parser, password)):
        clientSocket.send(completeMsg)
      else:
        print("Error: Don't put commas in the password!")
        time.sleep(3.5)
    else:
      print("Error: Don't put commas in the username!")
      time.sleep(3.5)

  elif(choice == "2"):
    #SIGN UP - (1, data length, "username,password,password2,", checksum)
    os.system('clear')
    print("Username: ")
    userName = raw_input()
    password = getpass.getpass("Password: ")
    password2 = getpass.getpass("Re-enter Password: ")
    dataA = userName + "," + password + "," + password2 + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey, 1, dataA)
    clientSocket.send(completeMsg)

  response = clientSocket.recv(1024)
  print(response)

clientSocket.close()
#print (decryptedMsg)
