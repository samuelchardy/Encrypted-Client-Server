import socket
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
data = "Bingo Bango Bongo!"
sentMsg = messageParser.make(parser, cr, serverPublicKey, 1, data)
#signature = crypto.signMessage(cr, sentMsg)
clientSocket.send(sentMsg)


#USER INTERFACE
while True:
  #os.system('cls')
  print("------------------------\n1: Log in\n2: Sign up\n------------------------\n")
  choice = raw_input()

  if(choice == "1"):
    #LOG IN - (1, data length, "username,password,", checksum)
    #os.system('cls')
    print("Username: ")
    userName = raw_input()
    password = getpass.getpass("Password: ")
    data = userName + "," + password + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey, 1, data)
    clientSocket.send(sentMsg)
  elif(choice == "2"):
    #SIGN UP - (2, data length, "username,password,password2,", checksum)
    os.system('cls')
    print("Username: ")
    userName = raw_input()
    password = getpass.getpass("Password: ")
    password2 = getpass.getpass("Re-enter Password: ")
    dataA = userName + "," + password + "," + password2 + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey, 1, dataA)
    clientSocket.send(sentMsg)


clientSocket.close()
#print (decryptedMsg)
