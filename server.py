import socket, threading
from password_strength import PasswordStats
from password_strength import PasswordPolicy
from Crypto2           import crypto
from messageParser     import messageParser


class Server():

  class ServerThread(threading.Thread):

    def __init__(self,clientAddress,clientsocket):
      self.c=crypto()
      self.parser=messageParser()
      crypto.genKeys(self.c)
      crypto.storeKeys(self.c)
    
      self.publicKey = crypto.loadPublicKey(self.c)
      threading.Thread.__init__(self)
      self.clientsocket = clientsocket
      self.clientAddress=clientAddress
      print ("New connection added: ", clientAddress)
    def authenticate(self):
      loggedin=False
      attempts=3 ####### this can be updates later. 
      while not loggedin:
        attempts-=1
        msg = self.clientsocket.recv(1024)
        if(len(msg) == 294):
          #DECRYPT DATA
          msg = crypto.decryptData(self.c, msg)
          #PARSE MESSAGE INTO ITS COMPONENTS
          command, dataLen, data, checksum = messageParser.parse(self.parser, msg)
          print("COMMAND: " + str(command) + "\nDATA LEN: " + str(dataLen) + "\nDATA: " + str(data) + "\nCHECKSUM: " + checksum)

        if(int(dataLen) < 255):
          if(command == "1"):
            print("\ntrying to log in")
            loggedin=True


            #check against sql server for user/passowrd store
          elif(command == "2"):
            #user is signing up here
            errorActive = 0
            completeMsg = ""
            print("\ntrying to sign up")
            splitData = str.split(data,",")
            username = splitData[0]
            password = splitData[1]
            password2 = splitData[2]

            listOfErrors = policy.test(password)
            if(password != password2):
              errorActive = 1
              completeMsg = "Error: Passwords do not match, please try again!\n"

            if(len(listOfErrors) > 0):
              errorActive = 1
              errorMsg = "Error: Your password must contain the following: "
              for error in listOfErrors:
                errorMsg += str(error) + " " 
              print(errorMsg)
              completeMsg = completeMsg + errorMsg

            if(errorActive == 1):
              completeMsg = messageParser.make(parser, c, clientPublicKey, 1, completeMsg)
              self.clientsocket.send(completeMsg)
            else:
              message = messageParser.make(parser, c, clientPublicKey, 1, "signed up")
              self.clientsocket.send(message)

          elif(command == "2"):
            print("\nsomething else")
        else:
          print("Error: Data length value is too large.")
        if attempts<0:
          #time.sleep(60)
          attempts+=1
      #here we're logged in after this loop so well
    def run(self):
      print ("Connection from : "+ str(self.clientAddress))
      #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
      msg = ''
      #
      self.clientsocket.send(self.publicKey)

          #GETTING CLIENTS PUBLIC KEY
      clientPublicKey =  self.clientsocket.recv(1024)
      print("client public\n" + clientPublicKey)
      clientPublicKey = crypto.loadPublicKeyFromBytes(self.c, clientPublicKey) #<---
      self.authenticate()
      #ACCESS TO MAIN FUNCTIONALITY IF YOU HAVE THE RGHT ROLE
            

  def __init__(self,port=9999):
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.host = socket.gethostname()
    self.port = port
    self.serverSocket.bind((self.host, self.port))

    self.serverSocket.listen(5)
    print("Server Active")
    
    
    

  #INITIALISE MESSAGEPARSER
    self.parser = messageParser()

  #PASSWORD POLICY
    self.policy = PasswordPolicy.from_names(
      length=8,  		# min length: 8
      uppercase=2,  	# need min. 2 uppercase letters
      numbers=2,  	# need min. 2 digits
      special=1,  	# need min. 1 special characters
      nonletters=0  	# need min. 0 non-letter characters (digits, specials, anything)
  )



  def run(self):
    while True:
      self.serverSocket.listen(1)
      clientsock, clientAddress = self.serverSocket.accept()
      newthread = self.ServerThread(clientAddress, clientsock)
      newthread.start()
      #print("Connected to: " + str(clientAddress))
myserver=Server()
myserver.run()
      ################################################################################################################################################

#       \*
# #INITIALISE ENCRYPTION OBJECT/ KEYS
# c = crypto()
# crypto.genKeys(c)
# crypto.storeKeys(c)
# publicKey = crypto.loadPublicKey(c)

# #INITIALISE MESSAGEPARSER
# parser = messageParser()

# #PASSWORD POLICY
# policy = PasswordPolicy.from_names(
#     length=8,  		# min length: 8
#     uppercase=2,  	# need min. 2 uppercase letters
#     numbers=2,  	# need min. 2 digits
#     special=1,  	# need min. 1 special characters
#     nonletters=0  	# need min. 0 non-letter characters (digits, specials, anything)
# )


# #SETUP SERVER
# host = socket.gethostname()
# port = 9999
# serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serverSocket.bind((host, port))
# serverSocket.listen(1)

# print("Server Active\n\n" + str(publicKey) + "\n")

# while True:
#   #SENDING SERVERS PUBLIC KEY
#   clientSocket, addr = serverSocket.accept()
#   print("Connected to: %s" % str(addr))
#   clientSocket.send(publicKey)

#   #GETTING CLIENTS PUBLIC KEY
#   clientPublicKey = clientSocket.recv(1024)
#   print("client public\n" + clientPublicKey)
#   clientPublicKey = crypto.loadPublicKeyFromBytes(c, clientPublicKey) #<---

#   #GETTING MESSAGE, DECRYPT IT, PRINT 
#   while True:
#     msg = clientSocket.recv(1024)
#     if(len(msg) == 294):
#       #DECRYPT DATA
#       msg = crypto.decryptData(c, msg)
#       #PARSE MESSAGE INTO ITS COMPONENTS
#       command, dataLen, data, checksum = messageParser.parse(parser, msg)
#       print("COMMAND: " + str(command) + "\nDATA LEN: " + str(dataLen) + "\nDATA: " + str(data) + "\nCHECKSUM: " + checksum)

#       if(int(dataLen) < 255):
#         if(command == "0"):
#           print("\ntrying to log in")


          
#         elif(command == "1"):
#           errorActive = 0
#           completeMsg = ""
#           print("\ntrying to sign up")
#           splitData = str.split(data,",")
#           username = splitData[0]
#           password = splitData[1]
#           password2 = splitData[2]

#           listOfErrors = policy.test(password)
#           if(password != password2):
#             errorActive = 1
#             completeMsg = "Error: Passwords do not match, please try again!\n"

#           if(len(listOfErrors) > 0):
#             errorActive = 1
#             errorMsg = "Error: Your password must contain the following: "
#             for error in listOfErrors:
#               errorMsg += str(error) + " " 
#             print(errorMsg)
#             completeMsg = completeMsg + errorMsg

#           if(errorActive == 1):
#             completeMsg = messageParser.make(parser, c, clientPublicKey, 1, completeMsg)
#             clientSocket.send(completeMsg)
#           else:
#             message = messageParser.make(parser, c, clientPublicKey, 1, "signed up")
#             clientSocket.send(message)

#         elif(command == "2"):
#           print("\nsomething else")
#       else:
#         print("Error: Data length value is too large.")


#   clientSocket.close()
