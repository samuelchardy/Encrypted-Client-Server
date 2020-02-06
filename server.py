import socket, threading, json, hashlib, smtplib, ssl, pyotp, mysql.connector
from Crypto2           		import crypto
from messageParser     		import messageParser
from Verify            		import Verify
from password_strength 		import PasswordStats
from password_strength 		import PasswordPolicy
from email.mime.multipart 	import MIMEMultipart
from email.mime.text  		import MIMEText
from datetime 				import datetime

class Server():
  
  class ServerThread(threading.Thread):

    def __init__(self,clientAddress,clientsocket,server):
      self.c=crypto()
      self.OTP=Verify()
      crypto.genKeys(self.c)
      crypto.storeKeys(self.c)
      self.server=server
      self.publicKey = crypto.loadPublicKey(self.c)
      threading.Thread.__init__(self)
      self.clientsocket = clientsocket
      self.clientAddress=clientAddress
      print ("New connection added: ", clientAddress)
	  
    def sendOTP(self,email="sampanda91@gmail.com"):
      current_code = self.OTP.get()
      
      #Generate email
      message = MIMEMultipart()
      message["Subject"] = "Your Verification Code"
      message["From"] = self.server.emailAddr
      message["To"] = email

      text = "Your verification code is : " + str(current_code)
      
      msgText = MIMEText(text, "plain")
      message.attach(msgText)
      
      #Connect to SMTP server and send email
      context = ssl.create_default_context()
      print(text)
      
      
      try:
        s=smtplib.SMTP(host='smtp.gmail.com', port = 587)
        s.starttls(context = context)
        s.login(self.server.emailAddr, self.server.pw)
        s.sendmail(self.server.emailAddr, email, message.as_string())
        print("email sent to : " + email)
      except Exception as e:#https://docs.google.com/document/d/1ccYoBdUBAxtwKJIUg5GfgUYkHVz3ZcLgdhttps://docs.google.com/document/d/1ccYoBdUBAxtwKJIUg5GfgUYkHVz3ZcLgd73bXU3QRFM/edit?usp=sharing73bXU3QRFM/edit?usp=sharing
        print(e)
      finally:
        s.quit()
      
    
    def authenticate(self,clientPublicKey):
      loggedin=False
      attempts=3 ####### this can be updates later. 
      while not loggedin:
        attempts-=1
        msg = self.clientsocket.recv(1024)
        if(len(msg) == 294):
          #DECRYPT DATA
          msg = crypto.decryptData(self.c, msg)
          #PARSE MESSAGE INTO ITS COMPONENTS
          command, dataLen, data, checksum = messageParser.parse(self.server.parser, msg)
          print("COMMAND: " + str(command) + "\nDATA LEN: " + str(dataLen) + "\nDATA: " + str(data) + "\nCHECKSUM: " + str(checksum))

        if(int(dataLen) < 255):
          if(command == "A"):
            
            #harvest input user
            #harvest
            splitData = str.split(data.decode("ASCII"),",")
            username = splitData[0]
            password = splitData[1]
			#checkvalidation by ensuring password is  n number of alphanum set. 
            print("username: " + username)
            print("password: " + password)
            if(self.LoginChecker(username,password)):#check against sql server for user/passowrd store#if fails, repeat login loo
              print("\ntrying to log in")#SEND MESSAGE TELLING THEM TO ENTER OTP CODE
              otpMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "1", "Please check your email and enter the code we have sent you!")
              self.clientsocket.send(otpMsg)
              self.sendOTP() # not declared in memory so cant be listened for. 
              print("sent OTP")
			        #RECIEVE OTP CODE
              otpCode = self.clientsocket.recv(1024)
              otpCode = crypto.decryptData(self.c, otpCode)
              command, dataLen, otpCode, checksum = messageParser.parse(self.server.parser, otpCode)
              print(otpCode.decode("ASCII"))
              otpCode = otpCode.decode("ASCII")[:-1]
              print(self.OTP.checkCode(otpCode))
			  
              loggedin=True
              logResult = "Welcome!"
              logCode = "1"
              if(not self.OTP.checkCode(otpCode)):
                logResult = "Incorrect code, please try again!"
                logCode = "0"
              print(logCode)
              logRes = messageParser.make(self.server.parser, self.c, clientPublicKey, logCode, logResult)
              self.clientsocket.send(logRes)
            else:
              failMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "0", "Incorrect username or password!")
              self.clientsocket.send(failMsg)
			 
          elif(command == "B"):
            #user is signing up here
            errorActive = 0
            completeMsg = ""
            print("\ntrying to sign up")
            splitData = str.split(data.decode("ASCII"),",")
            forename = splitData[0]
            surname = splitData[1]
            dob = splitData[2]
            username = splitData[3]
            password = splitData[4]
            password2 = splitData[5]
            secret = splitData[6]


            if(password != password2):
              completeMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "0", "Passwords don't match, please try again!")
              self.clientsocket.send(completeMsg)
            else:
              message = messageParser.make(self.server.parser, self.c, clientPublicKey, "1", "signed up")
              self.signUp(username, password, secret, dob, surname, forename)
              self.clientsocket.send(message)
      
          elif(command == "2"):
            print("\nsomething else")
        else:
          print("Error: Data length value is too large.")
        if attempts<0:
          #time.sleep(60)
          attempts+=1
      #here we're logged in after this loop so well
      #go to give options for authentication. 
    
    
    def LoginChecker(self,username, password):
      #connect to db
      d=self.server.DB()
      c = d.cursor()
        #gets salted password  and salt if user is in db 
      c.execute("select saltypassword from login where username = '"+username+"'")
      res=c.fetchall()
      pword=res[0][0]
      c.execute("select secretanswer from login where username = '"+username+"'")
      res=c.fetchall()
      salt=res[0][0]
        #adds salt to attempted password
      saltedAttempt = password + salt
        #compares
      if saltedAttempt == pword:
        print("Login Successful")
        d.close()
        return True
      else:
        d.close()
        print("#fail") 
      return False
	  
    def signUp(self, username, password, secret, dob, surname, forename):
      dt=datetime.now()
      validTime=dt.strftime("%Y-%m-%d %H:%M:%S")
      password += secret
      c= self.server.DB()
      mc = c.cursor()
      mc.execute("INSERT INTO login VALUES(%s,%s,%s,%s)",(username,password,secret,validTime))
      mc.execute("INSERT INTO personalinfo(Username,Email,Surname,Forename,DOB) VALUES(%s,%s,%s,%s,%s)",(username,username,surname,forename,dob))
      mc.execute("SELECT UserID from personalinfo where Username = '"+username+"'")
      results = mc.fetchall()
      userID = results[0][0] 
      mc.execute("INSERT INTO roles(UserID,RoleID) Values(%s,%s)",(userID,0))
      c.commit()
      c.close()	  
	
    
    def run(self):
      print ("Connection from : "+ str(self.clientAddress))
      #self.csocket.send(bytes("Hi, This is from Server..",'ASCII'))
      msg = ''
      #
      self.clientsocket.send(self.publicKey)

          #GETTING CLIENTS PUBLIC KEY
      clientPublicKey =  self.clientsocket.recv(1024)
      print("client public\n" + str(clientPublicKey))
      clientPublicKey = crypto.loadPublicKeyFromBytes(self.c, clientPublicKey) #<---
      self.authenticate(clientPublicKey)
      #ACCESS TO MAIN FUNCTIONALITY IF YOU HAVE THE RGHT ROLE
            
  def connectDB(self):
    conn = mysql.connector.connect(user="threesixthreedb", 
                                password="Jd19_m_20k02",
                                host="den1.mysql6.gear.host",
                                database="threesixthreedb")
    return conn
 
  def __init__(self,port=9999):
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.host = socket.gethostname()
    self.port = port
    self.serverSocket.bind((self.host, self.port))
    self.parser=messageParser()
    self.serverSocket.listen(5)
    print("Server Active")
    self.emailAddr='363hospitalmfaservice@gmail.com'
    self.pw='InsecurePassword'
    
    
    self.DB=self.connectDB
  #INITIALISE MESSAGEPARSER
    self.parser = messageParser()

  #PASSWORD POLICY
    self.policy = PasswordPolicy.from_names(
      length=24,  		# min length: 8
      uppercase=0,  	# need min. 2 uppercase letters
      numbers=2,  	# need min. 2 digits
      special=0,  	# need min. 1 special characters
      nonletters=0  	# need min. 0 non-letter characters (digits, specials, anything)
  )


  
  
  def run(self):
    while True:
      self.serverSocket.listen(1)
      clientsock, clientAddress = self.serverSocket.accept()
      newthread = self.ServerThread(clientAddress, clientsock,self)
      newthread.start()
      #print("Connected to: " + str(clientAddress))
myserver=Server()
myserver.run()