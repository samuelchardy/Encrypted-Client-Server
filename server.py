import socket, threading, json, hashlib, smtplib, ssl, pyotp, mysql.connector, os, time
from Crypto2           		import crypto
from messageParser     		import messageParser
from Verify            		import Verify
from password_strength 		import PasswordStats
from password_strength 		import PasswordPolicy
from email.mime.multipart import MIMEMultipart
from email.mime.text  		import MIMEText
from datetime 				    import datetime
from Authenticator 		    import Authenticator
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
      self.username = ""
      print ("New connection added: ", clientAddress)
      self.loggedin=False


    def sendOTP(self,email="sampanda91@gmail.com"): #used during testing
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
      self.loggedin=False
      attempts=2 ####### this can be updates later. 
      while not self.loggedin:
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
            self.username = username
            password = splitData[1]
			      #checkvalidation by ensuring password is  n number of alphanum set. 
            print("username: " + username)
            print("password: " + password)
            if(self.LoginChecker(username,password)):#check against sql server for user/passowrd store#if fails, repeat login loo
              print("\ntrying to log in")#SEND MESSAGE TELLING THEM TO ENTER OTP CODE

              if(self.revalidatedUser(username)):  
                otpMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "X", "Please check your email and enter the code we have sent you!")
                self.clientsocket.send(otpMsg)
      
                self.sendOTP(self.getEmailforUser(username)) # not declared in memory so cant be listened for.     <--------------get user Email
                print("sent OTP")
                #RECIEVE OTP CODE
                otpCode = self.clientsocket.recv(1024)
                otpCode = crypto.decryptData(self.c, otpCode)
                command, dataLen, otpCode, checksum = messageParser.parse(self.server.parser, otpCode)
                print(otpCode.decode("ASCII"))
                otpCode = otpCode.decode("ASCII")[:-1]
                print(self.OTP.checkCode(otpCode))
          
                logResult = ""
                logCode = ""
                if(not self.OTP.checkCode(otpCode)):
                  logResult = "Incorrect code, please try again!"
                  logCode = "0"
                  self.loggedin = False
                  self.username = username
                  self.loginAttempt(username, False)
                  attempts-=1
                else:
                  self.loggedin=True
                  logResult = "Welcome!"
                  logCode = "1"
                  self.username = username
                  self.loginAttempt(username, True)

                print(logCode)
                logRes = messageParser.make(self.server.parser, self.c, clientPublicKey, logCode, logResult)
                self.clientsocket.send(logRes)
              else:
                loginMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "Z", "Loged In")
                self.clientsocket.send(loginMsg)
                self.loggedin=True
            else:
              failMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "0", "Incorrect username or password!")
              self.clientsocket.send(failMsg)
              self.loginAttempt(username, False)
              attempts-=1
			 
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
            email = splitData[4]
            password = splitData[5]
            password2 = splitData[6]
            secret = splitData[7]

            if(password != password2):
              completeMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "0", "Passwords don't match, please try again!")
              self.clientsocket.send(completeMsg)
              attempts-=1
            else:
              message = messageParser.make(self.server.parser, self.c, clientPublicKey, "1", "signed up")
              self.signUp(username, password, secret, dob, surname, forename, email)
              self.clientsocket.send(message)
          elif(command == "2"):
            print("\nsomething else")
        else:
          print("Error: Data length value is too large.")
          attempts-=1

        if attempts<0:
          self.timeoutLogin(self.username)
          if not self.checkLogins(self.username):
            self.alertAdmin(self.username)
          attempts+=1
          delay=60
          for i in range(delay):
            #os.system("cls")
            #print("You have attempted to log in and fail multiple times, please wait an extra " + str(delay-i) + " seconds before trying again!")
            time.sleep(1)
          print("Timeout Over")
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
        print("Passwords Matched")
        d.close()
        return True
      else:
        d.close()
        print("Failed Login") 
      return False


    def getEmailforUser(self, username):
      try: 
        c= self.server.DB()
        mc = c.cursor()
        mc.execute("SELECT Email from personalinfo where Username = '"+username+"'")
        results = mc.fetchall()
        return results[0][0]
      except:
        return null


    def signUp(self, username, password, secret, dob, surname, forename, email):
      dt=datetime.now()
      validTime=dt.strftime("%Y-%m-%d %H:%M:%S")
      password += secret
      c= self.server.DB()
      mc = c.cursor()
      mc.execute("INSERT INTO login VALUES(%s,%s,%s,%s)",(username,password,secret,validTime))
      mc.execute("INSERT INTO personalinfo(Username,Email,Surname,Forename,DOB) VALUES(%s,%s,%s,%s,%s)",(username,email,surname,forename,dob))
      mc.execute("SELECT UserID from personalinfo where Username = '"+username+"'")
      results = mc.fetchall()
      userID = results[0][0] 
      mc.execute("INSERT INTO roles(UserID,RoleID) Values(%s,%s)",(userID,0))
      c.commit()
      c.close()	  
    

    #######TESTING##########################################
    def timeoutLogin(self, username):
      c = self.server.DB()
      mc = c.cursor()
      uID = Authenticator.getUserID(self.server.Authenticator, username)
      dt=datetime.now()
      now= dt.strftime("%Y-%m-%d %H:%M:%S")
      mc.execute("INSERT INTO audit(userid, methodcalled, success, timestamp,PreviousHash) VALUES(%s,%s,%s,%s,%s)",(uID,"Timeout",False,now,self.server.hashPreviousLog()))
      c.commit()
      c.close()
      print("Logged timeout")


    def loginAttempt(self, username, success):
      c = self.server.DB()
      mc = c.cursor()
      uID = Authenticator.getUserID(self.server.Authenticator, username)
      dt=datetime.now()
      now= dt.strftime("%Y-%m-%d %H:%M:%S")
      mc.execute("INSERT INTO audit(userid, methodcalled, success, timestamp,PreviousHash) VALUES(%s,%s,%s,%s,%s)",(uID,"LoginAttempt",success,now,self.server.hashPreviousLog()))
      c.commit()
      print("Logged login attempt")
      c.close()


    def checkLogins(self, username):
      print("Checking past login attempts")
      c = self.server.DB()
      mc = c.cursor()
      clear = False
      uID = Authenticator.getUserID(self.server.Authenticator, username)
      mc.execute("SELECT success from audit where methodcalled = 'LoginAttempt' and userid = "+str(uID)+" order by timestamp desc limit 9")
      results = mc.fetchall()
      for res in results:
        if res[0] == True:
          clear = True
          break
      c.close()
      return clear


    def alertAdmin(self, username):
      print("Alerting sys admins of suspicious behaviour")
      #@title Email OTP to Recipient
      c = self.server.DB()
      mc = c.cursor()
      #Hardcoded - hospital account details
      address = '363hospitalmfaservice@gmail.com'
      pw = 'InsecurePassword'
        
      #Get these from db
      mc.execute("SELECT email from personalinfo inner join roles on roles.userid =personalinfo.userid where roleid=6")
      results = mc.fetchall()
      recipients = []
      for res in results:
        recipients.append(res[0])
      #recipients.append('george.f.h.chandler@gmail.com')
      #recipients.append('theanonymousfreakyguy@googlemail.com')
      c.close()
        
      #Generate email
      message = MIMEMultipart()
      message["Subject"] = "Multiple access attempts"
      message["From"] = address
      message["To"] = ", ".join(recipients)

      text = "The user: " + username + " has failed to login 9 times. Please execute order 66."

      msgText = MIMEText(text, "plain")
      message.attach(msgText)

      #Connect to SMTP server and send email
      context = ssl.create_default_context()
      try:
        s = smtplib.SMTP(host='smtp.gmail.com', port = 587)
        s.starttls(context = context)
        s.login(address, pw)
        s.sendmail(address, recipients, message.as_string())
      except Exception as e:#https://docs.google.com/document/d/1ccYoBdUBAxtwKJIUg5GfgUYkHVz3ZcLgdhttps://docs.google.com/document/d/1ccYoBdUBAxtwKJIUg5GfgUYkHVz3ZcLgd73bXU3QRFM/edit?usp=sharing73bXU3QRFM/edit?usp=sharing
        print(e)
      finally:
        s.quit()


    def revalidatedUser(self, user):
      c = self.server.DB()
      mc = c.cursor()
      mc.execute("SELECT LastValidation from login where username = '"+user+"'")
      insertion_date = mc.fetchall()
      dt = datetime.now()
      
      insertion_date = datetime.strptime(str(insertion_date[0][0]), "%Y-%m-%d %H:%M:%S")
      cTime =dt.strftime("%Y-%m-%d %H:%M:%S")
      cTime = datetime.strptime(str(cTime), "%Y-%m-%d %H:%M:%S")
      print(cTime)
      print(insertion_date)
      time_between_insertion = cTime - insertion_date

      if  time_between_insertion.days>14:
        print ("The insertion date is older than 14 days")
        return True
        mc.execute("update login set LastValidation = %s where username = %s",(cTime, username))
        c.commit()
      else:
        print ("The insertion date is not older than 14 days")
        return False



    def run(self):
      print ("Connection from : "+ str(self.clientAddress))
      msg = ''
      self.clientsocket.send(self.publicKey)
      #GETTING CLIENTS PUBLIC KEY
      clientPublicKey =  self.clientsocket.recv(1024)
      print("client public\n" + str(clientPublicKey))
      clientPublicKey = crypto.loadPublicKeyFromBytes(self.c, clientPublicKey) #<---
      self.authenticate(clientPublicKey)
      #ACCESS TO MAIN FUNCTIONALITY IF YOU HAVE THE RGHT ROLE
      while self.loggedin:
        roles = self.server.Authenticator.callMethod("getRoles", self.username,self.username)
        methods = self.server.Authenticator.returnValidMethods(roles)
        methods = methods[0:len(methods)-1]
        methodsStr = ""
        for method in methods:
          methodsStr = methodsStr + method + ","

        cliMsg = messageParser.make(self.server.parser, self.c, clientPublicKey, "1", methodsStr)
        self.clientsocket.send(cliMsg)

        while True:
          cliInput = self.clientsocket.recv(1024)
          cliInput = crypto.decryptData(self.c, cliInput)
          command, dataLen, dataMethod, checksum = messageParser.parse(self.server.parser, cliInput)
          dataMethod = dataMethod.decode("ASCII")
          print(dataMethod)
          #Authenticator.callMethod(dataMethod)

	# await user log off
 	# listen for commands call for authenticator
  def connectDB(self):
    conn = mysql.connector.connect(user="threesixthreedb", 
                                password="Jd19_m_20k02",
                                host="den1.mysql6.gear.host",
                                database="threesixthreedb")
    return conn

    
  def hashPreviousLog(self):
    c = self.connectDB()
    mc = c.cursor()
    auditLogs = []
    mc.execute("SELECT * FROM audit ORDER BY TimeStamp DESC")
    result = str(list(mc.fetchone()))
    assert result not None, "Error: Audits are empty."
    m = hashlib.md5()
    m.update(result)
    hashedResult = m.hexdigest()
    c.close()
    return hashedResult

  
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
    self.Authenticator=Authenticator(self.connectDB,self.hashPreviousLog)
    
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
