from inspect import signature
from datetime import datetime
class Authenticator:  # <---------------------NEEDS TO BECOME A SERVER SUB-CLASS
    # This is to be the only method any given role can access then acess, it has
    # super priveledges to check that the given user can in fact access the other 
    # methods that they intend to aceesss tand then run them for the results to 
     #bepassed back to the caller/. this will also be in a singleton pattern to 
    # stop it being overwritten 


  def getUserID(self,subjectUserName):
    c=self.connectDB()# will become self.server.DB()
    res = -1
    mc = c.cursor()
    mc.execute("Select UserID from personalinfo where Username = '"+str(subjectUserName)+"'")
    results = mc.fetchall()
    
    if mc.rowcount>0:
      res = results[0][0]
      print(res)
    c.close()
    print("in Get user ID" + str(res))
    return res


  def getStaffID(self,subjectUserName ):
    c= self.connectDB()# will become self.server.DB()
    res = -1    
    mc = c.cursor()
    mc.execute("Select staffID from staff where Username = '"+str(subjectUserName)+"'")
    results = mc.fetchall()
    if mc.rowcount>0:
      res = results[0][0]
    c.close()
    return res


  __instance = None
  @staticmethod 
  def getInstance(ConnectDB,LastAuditLogHash):
    """ Static access method. """
    if Authenticator.__instance == None:
        Authenticator(ConnectDB,LastAuditLogHash)
    return Authenticator.__instance


  def __init__(self, ConnectDB,LastAuditLogHash):
    """ Virtually private constructor. """
    if Authenticator.__instance != None:
        raise Exception("This class is a singleton!")
    else:
        Authenticator.__instance = self
    self.Methods=dict()
    self.connectDB=ConnectDB
    self.LastAuditLogHash=LastAuditLogHash
    #Appointments
    self.__AddMethod("getApp",self.getAppointmentByPID, [0,1])
    self.__AddMethod("appApp",self.appendAppointmentByPID, [1])
    self.__AddMethod("writeApp",self.writeToAppointmentByPID, [1])
    #Records
    self.__AddMethod("getRec",self.getRecordByPID, [0,2,3,4,5])
    self.__AddMethod("appRec",self.appendRecordByPID, [2,3])
    self.__AddMethod("writeRec",self.writeToRecordByPID, [3])
    #Prescription
    self.__AddMethod("addPres",self.addPrescription, [3])
    self.__AddMethod("getPresHist",self.getPrescriptionHistory, [2,3])
    self.__AddMethod("getCurPres",self.getCurrentPrescription, [2,3]) 
    #Conditions
    self.__AddMethod("createCond",self.createCondition, [3])
    self.__AddMethod("getCondHist",self.getConditionHistory, [2,3])
    self.__AddMethod("getCurCond",self.getCurrentCondition, [2,3])
    #User
    self.__AddMethod("getUserInfo",self.getUserInfoByUsername,[0,1,2,3,4,5,6])
    self.__AddMethod("updUser",self.updateUsers,[0,1,2,3,4,5,6])
    self.__AddMethod("updPass",self.updatePassword,[0,1,2,3,4,5,6])
    ######### Question Time ############## This one in here or on login?
    self.__AddMethod("updValid",self.updateValidation,[0,1,2,3,4,5,6])
    #Audit Logs
    self.__AddMethod("getAudit",self.getAuditLogs, [4,6])
    #Staff Info 
    self.__AddMethod("addStaff",self.addStaffByUsername,[5,6])
    self.__AddMethod("getStaffInfo",self.getStaffInfoByUsername, [1,5,6])
    self.__AddMethod("appStaffInfo",self.appendStaffInfoByUsername, [5])
    #Role Assignment
    self.__AddMethod("getRoles",self.getRoleBySID,[6]) #remove the 0
    self.__AddMethod("elevateRole",self.elevate, [6])
    #lookupIDs
    self.__AddMethod("getUserID",self.getUserID,[0,1,2,3,4,5,6])
    self.__AddMethod("getStaffID",self.getStaffID,[0,1,2,3,4,5,6])
    self.__AddMethod("returnValidMethods",self.returnValidMethods,[0,1,2,3,4,5,6])


  def __AddMethod(self,FunctionName,Caller,Roles):
    method = dict()
    method.update({"call":Caller,"Args": list(signature(Caller).parameters.keys()),"rolesAccess":Roles})
    self.Methods.update({FunctionName:method})


  def listMethodDetails(self,methodName):
    print(methodName)
    print( "In : "+",".join(list(self.Methods.keys())))
    
    return self.Methods.get(str(methodName)).get("Args")


  def callMethod(self, methodName, UserName, args = None):
    #If role allows perform method
    ReturnDict={}
    hasRoles = []
    myID = self.getUserID(UserName)
    c = self.connectDB() # will become self.server.DB()
    mc = c.cursor()
    mc.execute("SELECT RoleID FROM roles WHERE UserID = "+ str(myID))
    results = mc.fetchall()
    for res in results:
      hasRoles.append(res[0])
  
    ##NamesMethods=print(a[methodName] for a in [set(a.roles)&set(hasRoles).len()>0 for a in Methods]) <-- Steve's weird shit
    KWARGS=dict(zip(self.Methods.get(str(methodName)).get("Args"),args))
    sub = KWARGS.get("subjectUserName", "NOONE AFFECTED")
    print(KWARGS)
    sID = self.getUserID(sub)
    print(sID) #==-1 ???
    if len(list(set(self.Methods.get(methodName).get("rolesAccess")) & set(hasRoles)))>=1 and (hasRoles!=[0] or myID==sID): #this lil bit on the end means that if your just role 0 i.e patient you can only change your own record
      
      ReturnDict.update({"Values":self.Methods.get(methodName).get("call")(**KWARGS), "Success":True})
      #success = True
      #return self.Methods.get(methodName).get("call")(arg in args)
    else:
      ReturnDict.update({"Values":{}, "Success":False})
    dt=datetime.now()
    validTime=dt.strftime("%Y-%m-%d %H:%M:%S")
    
    mc.execute("INSERT INTO audit(UserID, methodCalled, Success, UserSubject, TimeStamp,PreviousHash) VALUES (%s,%s,%s,%s,%s,%s)", (myID, methodName, ReturnDict.get("Success"), sub, validTime, self.LastAuditLogHash()))
    c.commit()
    c.close()
    return ReturnDict


  def returnValidMethods(self, permissionNo):
    NamesMethods=[]
    b=set(permissionNo)
    for a in self.Methods.items():
      if len(list(set(a[1].get("rolesAccess"))&b))>0:
        NamesMethods.append(a[0])
    return NamesMethods


  def getAppointmentByPID(self, subjectUserName ):#finds the next appointment for patient i    
    c= self.connectDB()# will become self.server.DB()
    res = "No appointment"
    mc = c.cursor()
    mc.execute("SELECT NextAppointment from Record where Username = '" + subjectUserName+"'")
    results = mc.fetchall()
    if mc.rowcount>0:
      res = results[0][0]
    c.close()
    return res


  def appendAppointmentByPID(self, subjectUserName, value):
    #updates the next appointment for patient id
    #with key, value
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    if pID>0:  
      mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))
    c.close()


  def writeToAppointmentByPID(self, subjectUserName, value):
    #sends a request to create a new appointment for patient id
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    if pID>0:
      mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))
    c.close()


  #Patient record methods 
  def getRecordByPID(self, subjectUserName):
    #if patient has the same ward as current staff id
    #return a Record containing patients data
    c= self.connectDB()# will become self.server.DB()
    resul = []
    mc = c.cursor()
    pID=self.getUserID(subjectUserName)
    if pID>0:
      c.execute("SELECT * from Record where UserID = "+str(pID))
      results = mc.fetchall()
      for res in results:
        resul.append(res)
    
  ##      print(res)
    c.close()
    return resul


  def appendRecordByPID(self, patientUser, staffUser, key, value):
    #if patient has the same ward as current staff id
    #update field with value at key point
    pID=self.getUserID(patientUser)
    sID=self.getStaffID(staffUser)
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
      #Gets all current values
    if pID>0 and sID>0: 
      mc.execute("SELECT nextappointment from record where UserID = %s AND Doctor = %s",(pID, sID))
      res = mc.fetchall()
      if  mc.rowcount >0:
        NA = res[0][0] 
      else:        
        NA = None      
        
      mc.execute("SELECT Bed from record where UserID = %s and Doctor = %s",(pID,sID))
      res = mc.fetchall()
      if  mc.rowcount >0:
        B = res[0][0]
      else:        
        B = None 
      
      mc.execute("SELECT Ward from record where UserID = %s and Doctor = %s",(pID,sID))
      res = mc.fetchall()
      if  mc.rowcount >0:
        W = res[0][0]  
      else:        
        W = None 
      result = "Nothing has been changed"
        # Depending on key alter with value
      if isinstance(key, str):
        key= key.lower()
        if key == "prescribe":       
          mc.execute("UPDATE  prescription set current=%s where UserId = %s and prescription = %s",(False,pID, value))
          result = "Prescription updated"
        elif key == "cond":
          mc.execute("Update cond set current = %s where Userid = %s and cond = %s",(False, pID, value))
          result = "Condition updated"
        else:
          if key == "nextappointment":
            NA = value
            result = "Next Appointment Changed"
          elif key == "bed":
            B = value
            result = "Bed Changed"
          elif key == "ward":
            W = value
            result = "Ward Changed"
          else:
            result = "not valid keyword"

          mc.execute("UPDATE record SET NextAppointment = %s, Bed = %s, Ward = %s where UserID = %s and Doctor = %s",(NA, B, W, pID, sID))
        c.commit()
        #c.close()
  
      ##print(result)
    c.close()   
    return result


  def writeToRecordByPID(self, subjectUserName, staffUser):
    ######## Needs to get staffID from whoever is logged in ###########
    #if patient has the same ward as current staff id and staffid is the gp/doctors 
    #assert in my list of patients -- a good check but not authentication means
    #send request for patient record to write
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    staffID = self.getStaffID(staffUser)
    if staffID>0 and pID>0:
      mc.execute("INSERT INTO record(UserId, Doctor) VALUES(%s,%s)",(pID, staffID))
    c.close()


  #Get user information
  def getUserInfoByUsername(self, subjectUserName):
    c= self.connectDB()# will become self.server.DB()
    resul = []
    mc = c.cursor()
    mc.execute("Select surname, forename, dob, email from  personalinfo where username = '"+subjectUserName+"'")
    results = mc.fetchall()
    for res in results:
      resul.append(res)
      #print(res) 
    c.close()
    return resul


  # update user fields
  def updateUsers(self, subjectUserName, key, value):
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    result="Invalid Username"
    if pID>0:
      if isinstance(key,str):
        key= key.lower()
        result=""
        if key == "forename": 
          mc.execute("UPDATE  personalinfo set forename=%s where UserId = %s",(value, pID))
          result = "Forename updated"
            
        elif key == "surname":
          mc.execute("Update personalinfo set surname = %s where Userid = %s",(value, pID))
          result = "Surname updated"
            
        elif key == "email":
          mc.execute("UPDATE personalinfo SET email = %s where UserID = %s",(value, pID))
          result = "Email changed"
        else:
          result = "Nothing Changed"
        c.commit()
  
      #print(result)
    c.close()
    return result
  
  #Update password
  def updatePassword(self, subjectUserName, newPassword):
    c= self.connectDB()# will become self.server.DB()
    res = False
    mc = c.cursor()
    mc.execute("select secretanswer from login where username = '" + subjectUserName + "'")
    results = mc.fetchall()
    if mc.rowcount>0:
      sec = results[0][0]
      newPassword += sec
      mc.execute("UPDATE login set password = %s where username = %s",(newPassword,subjectUserName))
      c.commit()
      res = True
    c.close()
    return res


  #Update last vaidated time
  def updateValidation(self, subjectUserName):
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    dt=datetime.now()
    now=dt.strftime("%Y-%m-%d %H:%M:%S")
    mc.execute("UPDATE login SET lastValidation = %s WHERE username = %s",(subjectUserName, now))
    c.commit()
    c.close()


  def addPrescription(self, subjectUserName, value):
  # add Prescription
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    if pID>0:
      mc.execute("INSERT INTO prescription(UserID, Prescription,current) VALUES(%s,%s,%s)",(pID, value,True))
      c.commit()
    c.close()


  # All history
  def getPrescriptionHistory(self, subjectUserName):  
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    resul = []
    pID = self.getUserID(subjectUserName)
    if pID>0:
      mc.execute("Select prescription from prescription where UserId ="+str(pID))
      results = mc.fetchall()
      for res in results:
        resul.append(res)
        #print(res)
    c.close()
    return resul
    

  # current 
  def getCurrentPrescription(self, subjectUserName):
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    resul = []
    pID = self.getUserID(subjectUserName)
    if pID>0:
      mc.execute("Select prescription from prescription where UserId = %s and current = %s",(pID,True))
      results = mc.fetchall()
      for res in results:
        resul.append(res)
        #print(res)
    c.close()
    return resul


  # Conditions
  def createCondition(self, subjectUserName, value): 
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    pID = self.getUserID(subjectUserName)
    if pID>0: 
      mc.execute("INSERT INTO cond(UserID ond urrent) VALUES(%s,%s,%s)",(pID, value,True))
      c.commit()
    c.close()
  
  
  # All history
  def getConditionHistory(self, subjectUserName):
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    resul = []
    pID = self.getUserID(subjectUserName) 
    if pID>0: 
      mc.execute("Select cond from cond where UserId = "+str(pID))
      results = mc.fetchall()
      for res in results:
        resul.append(res)
      #print(res)
    c.close()
    return resul


  # current 
  def getCurrentCondition(self, subjectUserName):  
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    resul = []
    pID = self.getUserID(subjectUserName)
    if pID>0:
      mc.execute("Select cond from cond where UserId = %s and current = %s",(pID,True))
      results = mc.fetchall()
      for res in results:
        resul.append(res)
        #print(res)
    c.close()

    return resul


  #Staff data methods
  def addStaffByUsername(self, subjectUserName):
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    mc.execute("INSERT INTO staff(username) VALUES ('"+subjectUserName+"')")
    c.close()


  def getStaffInfoByUsername(self, subjectUserName):
    #finds and returns the information related to the staff with Username
    c= self.connectDB()# will become self.server.DB()
    resul = []
    mc = c.cursor()
    mc.execute("SELECT * FROM staff INNER JOIN hours ON hours.staffid = staff.staffid where staff.username = '"+subjectUserName+"'")
    results = mc.fetchall()
    for res in results:
      resul.append(res)
      #print(res)
    c.close()
    return resul


  def appendStaffInfoByUsername(self, subjectUserName, key, value):
    #if staff has the same ward as current staffID (managers only)
    #update field with value at key point
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    if  isinstance(key, str):
      key= key.lower()
  
      if key == "ward": 
        mc.execute("UPDATE staff SET ward = %s WHERE username = %s", (value, subjectUserName))
      elif key == "boss":
        mc.execute("UPDATE staff SET LineManager = %s WHERE username = %s", (value, subjectUserName))
      elif key =="hours":
        mc.execute("select * from staff where username = '"+subjectUserName+"'")
        res = mc.fetchall()
        if mc.rowcount>0:
          staffID=res[0][0]
          mc.execute("SELECT * FROM hours where staffID = '"+str(staffID)+"'")

          res = mc.fetchall()
          if  mc.rowcount >0:
            mc.execute("UPDATE hours SET hours = %s WHERE staffid = %s", (value, staffID))
          else:        
            mc.execute("insert into hours(staffid,hours) VALUES (%s,%s)", (staffID,value))
      c.commit()
    c.close()
    

 #Audit logs method
  def getAuditLogs(self, num):
    c = self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    auditLogs = []
    mc.execute("SELECT * FROM audit ORDER BY TimeStamp DESC LIMIT " + str(num))
    results = mc.fetchall()
    for res in results:
      tempLine = str(res[3]) + ": " + str(res[1]) + " attempted to use method " + str(res[2]) + " affecting user " + str(res[4])
      auditLogs.append(tempLine)
  
      #print(tempLine)
    c.close()
    return auditLogs
    #Returns all audit logs


  #Role Assignment
  def getRoleBySID(self, subjectUserName):
    #returns the role of the staff id's account
    c = self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    result=[]
    print("fetching your roles by SID"+subjectUserName)
    userid = self.getUserID(subjectUserName)
    if userid>0:
      mc.execute("select distinct roleID from roles where userID='"+str(userid)+"'")
      results = mc.fetchall()
      for res in results:
        result.append(res[0])
  
      ##print(res)
    c.close()
    return result

  def elevationChecker(self, username):
    c = self.connectDB()
    mc = cursor()
    result = False
    mc.execute("Select userID, timestamp from audit where methodcalled = %s and usersubject = %s order by timestamp desc limit 2",("elevateRole", username))
    result = mc.fetchall()
    if mc.rowcount>1:
      currentUserID = result[0][0]
      prevUserID = result[1][0]
      time = datetime.strptime(str(result[1][1]), "%Y-%m-%d %H:%M:%S")
      dt = datetime.now()
      cTime =dt.strftime("%Y-%m-%d %H:%M:%S")
      cTime = datetime.strptime(str(cTime), "%Y-%m-%d %H:%M:%S")
      difference = cTime - time
      if difference.days<7:
        if callerID!=currentUserID:
          mc.execute("select success from audit where methodcalled = %s and usersubject =%s order by timestamp desc limit 1",("elevationChecker", username))
          res = mc.fetchall()
          if mc.rowcount>0:
            if not res[0][0]:
              result = True
      if not result:
        emailMsg = "Elevation to System Admin has been requested for the username: " + username + ". Please take appropriate action."
        self.server.alertAdmin(emailMsg)
      self.server.hashPreviousLog
      mc.execute("insert into audit(userid, methodcalled, success, usersubject, timestamp, previoushash) values(%s,%s,%s,%s,%s,%s)",(currentUserID, "elevationChecker",result,username,cTime,self.LastAuditLogHash()))
      return result
  def elevate(self, subjectUserName, key, value, value2 = None):
    #Alter the role assigned to new value of the Account with ID
    #0 = patient, 1 = receptionist, 2 = nurse, 3 = doctor
    #4 = regulator, 5 = managerial staff, 6 = Sytem admin]
    c= self.connectDB()# will become self.server.DB()
    mc = c.cursor()
    userid = self.getUserID(subjectUserName)
    result = "Invalid Username"
    if userid>0:
      if isinstance(key,str):
        key= key.lower()
        if key == "replace" or key == "delete": 
          mc.execute("Delete from roles where UserId = %s and RoleID = %s",(userid, value))
          result += "Removed the role " + str(value) + "."
        if value2 != None:
          value = value2
          result += " "
        if key == "replace" or key == "add":
          mc.execute("Insert into roles(userID, roleID) Values(%s,%s)",(userid,value))
          result += "Inserted the Role " + str(value) + "."
        c.commit()
      c.close()
    return result

def auditBackup(self):
  c = self.connectDB()
  mc = c.cursor()
  
  mc.execute("select timestamp from audit where methodcalled = 'backup' order by timestamp desc limit 1")
  time = mc.fetchall()

  if mc.rowcount>0:
    time = datetime.strptime(str(result[0][0]), "%Y-%m-%d %H:%M:%S")
    dt = datetime.now()
    cTime =dt.strftime("%Y-%m-%d %H:%M:%S")
    cTime = datetime.strptime(str(cTime), "%Y-%m-%d %H:%M:%S")
    difference = cTime - time
    if difference.days>1:
      self.server.hashPreviousLog    
      mc.execute("insert into audit(userID, methodcalled, success, timestamp, previoushash) values(%s,%s,%s,%s,%s)",(0,"backup",True,cTime,self.LastAuditLogHash()))
      #Write to file
      f = open("AuditBackup.txt", "a")
      mc.execute("Select * from audit where timestamp>" + time+ " order by timestamp desc")
      results = mc.fetchall()
      for res in results:
        f.write(res)
        f.write("\n")
      f.close()
  else:
    dt = datetime.now()
    cTime =dt.strftime("%Y-%m-%d %H:%M:%S")
    self.server.hashPreviousLog
    mc.execute("insert into audit(userID, methodcalled, success, timestamp, previoushash) values(%s,%s,%s,%s,%s)",(0,"backup",True,cTime,self.LastAuditLogHash()))
    f = open("AuditBackup.txt", "a")
    mc.execute("Select * from audit order by timestamp desc")
    results = mc.fetchall()
    for res in results:
      f.write(res)
      f.write("\n")
    f.close()
  c.commit()
  c.close()
