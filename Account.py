from Crypto2 import crypto
import json

cr2 = crypto()


class Account():
  def signup(self, uname, pass1, pass2, sec):
    if(pass1 == pass2):
        #accept
        #generate user key
        secpad = 16 - (len(sec) % 16)
        
        sec = sec + (' ' * secpad) #pad sec to multiple of 16 bytes for AES
        ivpad = 16 - (len(pass2) % 16)
        pass2 = pass2 + (' ' * ivpad)

        #aes = AES.new(sec, AES.MODE_CBC, pass2)
        #toCipher = uname + pass1
        #toCipherPad = 16 - (len(toCipher) % 16)
        #toCipher = toCipher + (' ' * toCipherPad)
        #cipher = aes.encrypt(toCipher)
	
	toCipher = uname + pass1
	#generate keys and then make an encrypted version of uname and password
	
	
        #create user on file
        file = open("userfile.json", 'a') #open user file in append mode
        toDump = str([uname,pass1,cipher])
        json.dump(toDump,file)

        
        return cipher #returns the unique (hopefully) signature for the user created
    else:
        #reject
        return -1 #rogue value to identify failure of account creation

  #def login(uname, pass):
