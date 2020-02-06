import socket, hashlib, time, os, getpass
from Crypto2           import crypto
from messageParser     import messageParser
from password_strength import PasswordStats
from password_strength import PasswordPolicy

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

#USER INTERFACE
attempts = 0

while True:
  os.system('cls')
  print("------------------------\n1: Log in\n2: Sign up\n------------------------\n")
  choice = input()

  if(choice == "1"):
    #LOG IN - (0, data length, "username,password,", checksum)
    os.system('cls')
    print("Username: ")
    userName = input()
    password = getpass.getpass("Password: ")
    m = hashlib.md5()
    m.update(password.encode("ASCII"))
    passwordMD5 = m.hexdigest()
    data = userName + "," + passwordMD5 + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey, "A", data)

    if(messageParser.checkData(parser, userName)):
      if(messageParser.checkData(parser, password)):
        clientSocket.send(completeMsg)
        #RECIEVE OTP MESSAGE
        otpResponse = clientSocket.recv(1024)
        otpResponse = crypto.decryptData(cr, otpResponse)
        command, dataLen, otpData, checksum = messageParser.parse(parser, otpResponse)
        print(otpData.decode("UTF-8"))
        
        if(command == "1"):
          enteredCode = input()
          otpReply = messageParser.make(parser, cr, serverPublicKey, "A", enteredCode)
          clientSocket.send(otpReply)
		
          newResponse = clientSocket.recv(1024)
          newResponse = crypto.decryptData(cr, newResponse)
          newCommand, dataLen, data, checksum = messageParser.parse(parser, newResponse)
          print(data.decode("ASCII"))

          if(newCommand == "1"):
            while True:
		  	#Only print what the user is able to do...
              print("OPTIONS...")
              enteredCode = input()
              userChoice = messageParser.make(parser, cr, serverPublicKey, "A", enteredCode)
              clientSocket.send(userChoice)
		
        else:
          attempts += 1
      else:
        print("Error: Don't put commas in the password!")
        attempts += 1
        time.sleep(3.5)
    else:
      print("Error: Don't put commas in the username!")
      attempts += 1
      time.sleep(3.5)

  elif(choice == "2"):
    #SIGN UP - (1, data length, "username,password,password2,", checksum)
    os.system('cls')
    print("Forename: ")
    forename = input()
    print("Surname: ")
    surname = input()
    print("Date of Birth (yyyy/mm/dd): ")
    dob = input()
    print("Username: ")
    userName = input()
    password=""
    password2=""
    policy = PasswordPolicy.from_names(
      length=8,  		# min length: 8
      uppercase=2,  	# need min. 2 uppercase letters
      numbers=2,  	# need min. 2 digits
      special=1,  	# need min. 1 special characters
      nonletters=0  	# need min. 0 non-letter characters (digits, specials, anything)
    )
    validpassword=False
    while not validpassword:	 
      password = getpass.getpass("Password: ")
      password2 = getpass.getpass("Re-enter Password: ")
      listOfErrors = policy.test(password)

      if(len(listOfErrors) > 0):
        errorActive = 1
        errorMsg = "Error: Your password must contain the following: "
        for error in listOfErrors:
          errorMsg += str(error) + " " 
        print(errorMsg)
      else:
        validpassword=True
	
    print("Please enter a random word, you will not be asked for this in the future.")
    secret = input()
    m = hashlib.md5()
    m.update(password.encode("UTF-8"))
    password1MD5 = m.hexdigest()
	
    m = hashlib.md5()
    m.update(password2.encode("UTF-8"))
    password2MD5 = m.hexdigest()
    
    dataA = forename + "," + surname + "," + dob + "," + userName + "," + password1MD5 + "," + password2MD5 + "," + secret + ","
    completeMsg = messageParser.make(parser, cr, serverPublicKey,"B", dataA)
    clientSocket.send(completeMsg)

    response = clientSocket.recv(1024)
    response = crypto.decryptData(cr, response)
    command, dataLen, data, checksum = messageParser.parse(parser, response)
    print(data.decode("UTF-8"))
    time.sleep(3.5)
	
  if(attempts == 3):
    attempts = 0
    for i in range(0,15):
      os.system("cls")
      print("You have attempted to log in and fail multiple times, please wait " + str(15-i) + " seconds before trying again!")
      time.sleep(1)

clientSocket.close()
#print (decryptedMsg)


'''

'''