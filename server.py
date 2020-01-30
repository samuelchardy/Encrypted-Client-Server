import socket
from password_strength import PasswordStats
from password_strength import PasswordPolicy
from Crypto2           import crypto
from messageParser     import messageParser

#INITIALISE ENCRYPTION OBJECT/ KEYS
c = crypto()
crypto.genKeys(c)
crypto.storeKeys(c)
publicKey = crypto.loadPublicKey(c)

#INITIALISE MESSAGEPARSER
parser = messageParser()

#PASSWORD POLICY
policy = PasswordPolicy.from_names(
    length=8,  		# min length: 8
    uppercase=2,  	# need min. 2 uppercase letters
    numbers=2,  	# need min. 2 digits
    special=1,  	# need min. 1 special characters
    nonletters=0  	# need min. 0 non-letter characters (digits, specials, anything)
)


#SETUP SERVER
host = socket.gethostname()
port = 9999
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
  clientPublicKey = crypto.loadPublicKeyFromBytes(c, clientPublicKey) #<---

  #GETTING MESSAGE, DECRYPT IT, PRINT 
  while True:
    msg = clientSocket.recv(1024)
    if(len(msg) == 294):
      #DECRYPT DATA
      msg = crypto.decryptData(c, msg)
      #PARSE MESSAGE INTO ITS COMPONENTS
      command, dataLen, data, checksum = messageParser.parse(parser, msg)
      print("COMMAND: " + str(command) + "\nDATA LEN: " + str(dataLen) + "\nDATA: " + str(data) + "\nCHECKSUM: " + checksum)

      if(int(dataLen) < 255):
        if(command == "0"):
          print("\ntrying to log in")
        elif(command == "1"):
          print("\ntrying to sign up")
          splitData = str.split(data,",")
          username = splitData[0]
          password = splitData[1]
          password2 = splitData[2]

          listOfErrors = policy.test(password)
          if(len(listOfErrors) > 0):
            errorMsg = "Error: Your password must contain the following: "
            for error in listOfErrors:
              errorMsg += str(error) + " " 
            print(errorMsg)
            completeMsg = messageParser.make(parser, c, clientPublicKey, 1, errorMsg)

          if(password != password2):
            completeMsg = messageParser.make(parser, c, clientPublicKey, 1, "Error: Passwords do not match, please try again!")
          


        elif(command == "2"):
          print("\nsomething else")
      else:
        print("Error: Data length value is too large.")


  clientSocket.close()
