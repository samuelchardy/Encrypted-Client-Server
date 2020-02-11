
from datetime import datetime
class Authenticator:  # <---------------------NEEDS TO BECOME A SERVER SUB-CLASS
    # This is to be the only method any given role can access then acess, it has
    # super priveledges to check that the given user can in fact access the other 
    # methods that they intend to aceesss tand then run them for the results to 
     #bepassed back to the caller/. this will also be in a singleton pattern to 
    # stop it being overwritten 

  __instance = None
  @staticmethod 
  def getInstance():
    """ Static access method. """
    if Authenticator.__instance == None:
        Authenticator()
    return Authenticator.__instance
  def __init__(self):
    """ Virtually private constructor. """
    if Authenticator.__instance != None:
        raise Exception("This class is a singleton!")
    else:
        Authenticator.__instance = self
    self.Methods=[]
    
    #Appointments
    self.__AddMethod("getAppointment",self.getAppointmentByPID, [0,1])
    self.__AddMethod("appendAppointment",self.appendAppointmentByPID, [1])
    self.__AddMethod("writeAppointment",self.writeToAppointmentByPID, [1])
    #Records
    self.__AddMethod("getRecord",self.getRecordByPID, [0,2,3,4,5])
    self.__AddMethod("appendRecord",self.appendRecordByPID, [2,3])
    self.__AddMethod("writeRecord",self.writeToRecordByPID, [3])
    #Prescription
    self.__AddMethod("addPrescription",self.addPrescription, [3])
    self.__AddMethod("getPrescriptionHistory",self.getPrescriptionHistory, [2,3])
    self.__AddMethod("getCurrentPrescription",self.getCurrentPrescription, [2,3]) 
    #Conditions
    self.__AddMethod("createCondition",self.createCondition, [3])
    self.__AddMethod("getConditionHistory",self.getConditionHistory, [2,3])
    self.__AddMethod("getCurrentCondition",self.getCurrentCondition, [2,3])
    #User
    self.__AddMethod("getUserInfo",self.getUserInfoByUsername,[0,1,2,3,4,5,6])
    self.__AddMethod("updateUser",self.updateUsers,[0,1,2,3,4,5,6])
    self.__AddMethod("updatePassword",self.updatePassword,[0,1,2,3,4,5,6])
    ######### Question Time ############## This one in here or on login?
    self.__AddMethod("updateValidation",self.updateValidation,[0,1,2,3,4,5,6])
    #Audit Logs
    self.__AddMethod("getAudit",self.getAuditLogs, [4,6])
    #Staff Info 
    self.__AddMethod("addStaff",self.addStaffByUsername,[5,6])
    self.__AddMethod("getStaffInfo",self.getStaffInfoByUsername, [1,5,6])
    self.__AddMethod("appendStaffInfo",self.appendStaffInfoByUsername, [5])
    #Role Assignment
    self.__AddMethod("getRole",self.getRoleBySID,[6])
    self.__AddMethod("elevateRole",self.elevate, [6])
    
  def __AddMethod(self,FunctionName,Caller,Roles):
    method = dict()
    method.update({"call":Caller, "rolesAccess":Roles})
    self.Methods.append({FunctionName:method})

  def callMethod(methodname, username, args):
    #If role allows perform method
    ReturnDict={}
    hasRoles = []
    myID = getUserID(username)
    c = connectDB() # will become self.server.DB()
    mc = c.cursor()
    mc.execute("SELECT RoleID FROM roles WHERE UserID = "+ str(myID))
    results = mc.fetchAll()
    for res in results:
      hasRoles.append(res[0])
    #NamesMethods=print(a[methodName] for a in [set(a.roles)&set(hasRoles).len()>0 for a in Methods]) <-- Steve's weird shit
    success = False
    if list(set(Methods[methodname][rolesAccess]) & set(hasRoles)).len()>=1:
      ReturnDict.update({"Values":Methods[methodName]["call"](args), "Success":True})
      success = True
      return Methods[methodname]["call"](args)
    else: 
      ReturnDict.update({"Values":Methods[methodName]["call"](args), "Success":False})
    dt=datetime.now()
    validTime=dt.strftime("%Y-%m-%d %H:%M:%S")
    sub = args[0]
    if isinstance(sub, str):
      sID = getUserID(sub)
    else:
      sID = None
    mc.execute("INSERT INTO audit(UserID, methodCalled, Success, UserSubject, TimeStamp) VALUES (%s,%s,%s,%s,%s)", (myID, methodname, success, sID, validTime))
    c.commit()
    c.close()
    return ReturnDict


  def returnValidMethods(self, permissionNo):
    hasRoles = []
    myID = getUserID(username)
    c = connectDB() # will become self.server.DB()
    mc = c.cursor()
    mc.execute("SELECT RoleID FROM roles WHERE UserID = "+ str(myID))
    results = mc.fetchAll()
    for res in results:
      hasRoles.append(res[0])
    for a in Methods:
      if [set(a[rolesAccess])&set([permissionNo])].len()>0:
        NamesMethods.append(a[methodName])
   
    return NamesMethod


  def getAppointmentByPID(self, username, mc):#finds the next appointment for patient id
    mc.execute("SELECT NextAppointment from Record where Username = " + 'username')
    results = mc.fetchall()
    res = results[0][0]
    print(res)

  def appendAppointmentByPID(self,username, mc, c, value):
    #updates the next appointment for patient id
    #with key, value
    pID = getUserID(username, mc)
    mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))
    results = mc.fetchall()
    
    print(results)
  def writeToAppointmentByPID(self,username, mc):
    #sends a request to create a new appointment for patient id
    pID = getUserID(username, mc)
    mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))


  #Patient record methods 
  def getRecordByPID(self,username,mc):
    #if patient has the same ward as current staff id
    #return a Record containing patients data
    pID=getUserID(username, mc)
    mc.execute("SELECT * from Record where UserID = "+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    results = mc.fetchall()
    
    return results
  def appendRecordByPID(self,patientUser, staffUser, key, value,mc,c):
    #if patient has the same ward as current staff id
    #update field with value at key point
    pID=getUserID(patientUser,mc)
    sID=getStaffID(staffUser,mc)
    #Gets all current values
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
        
        mc.execute("UPDATE record SET NextAppointment = %s, Bed = %s, Ward = %s where UserID = %s and Doctor = %s",(NA, B, W, pID, staffID))
      c.commit()
    print(result)
    
    
    return result
    
  def writeToRecordByPID(self,patientUser,staffUser,mc):
    ######## Needs to get staffID from whoever is logged in ###########
    #if patient has the same ward as current staff id and staffid is the gp/doctors 
    #assert in my list of patients -- a good check but not authentication means
    #send request for patient record to write
    pID = getUserID(patientUser,mc)
    staffID = getStaffID(staffUser,mc)
    mc.execute("INSERT INTO record(UserId, Doctor) VALUES(%s,%s)",(pID, staffID))

  #Get user information
  def getUserInfoByUsername(self,username, mc):
    mc.execute("Select surname, forename, dob, email from  personalinfo where username = '"+username+"'")
    results = mc.fetchall()
    for res in results:
      print(res)
    
    
    return results
  # update user fields
  def updateUsers(self,username, key, value,mc,c):
    pID = getUserID(username, mc)
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
      print(result)
      
    
      return results
  #Update password
  def updatePassword(self,username, newPassword,mc,c):
    mc.execute("select secretanswer from login where username = '" + username + "'")
    results = mc.fetchall()
    sec = results[0][0]
    newPassword += sec
    mc.execute("UPDATE login set password = %s where username = %s",(newPassword,username))
    c.commit()

  #Update last vaidated time
  def updateValidation(self,username,mc,c):
    dt=datetime.now()
    now=dt.strftime("%Y-%m-%d %H:%M:%S")
    mc.execute("UPDATE login SET lastValidation = %s WHERE username = %s",(username, now))
    c.commit()
    
  def addPrescription(self,username,value, mc,c):
  # add Prescription
    pID = getUserID(username, mc)
    mc.execute("INSERT INTO prescription(UserID, Prescription,current) VALUES(%s,%s,%s)",(pID, value,True))
    c.commit()
  # All history
  def getPrescriptionHistory(self,username,mc):  
    pID = getUserID(username, mc)
    mc.execute("Select prescription from prescription where UserId ="+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  # current 
  def getCurrentPrescription(self,username,mc):
    pID = getUserID(username, mc)
    mc.execute("Select prescription from prescription where UserId = %s and current = %s",(pID,True))
    results = mc.fetchall()
    for res in results:
      print(res)
  ##########################
    return results
  # Conditions
  def createCondition(self,username, value,mc,c): 
    pID = getUserID(username, mc) 
    mc.execute("INSERT INTO cond(UserID, Cond, current) VALUES(%s,%s,%s)",(pID, value,True))
    c.commit()
  # All history
  def getConditionHistory(self,username,mc):
    pID = getUserID(username, mc)  
    mc.execute("Select cond from cond where UserId = "+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  # current 
  def getCurrentCondition(self,username,mc):  
    pID = getUserID(username, mc)
    mc.execute("Select cond from cond where UserId = %s and current = %s",(pID,True))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  #Staff data methods
  def addStaffByUsername(self,username,mc):
    mc.execute("INSERT INTO staff(username) VALUES ('"+uName+"')")

  def getStaffInfoByUsername(self,username, mc):
    #finds and returns the information related to the staff with Username
    mc.execute("SELECT * FROM staff INNER JOIN hours ON hours.staffid = staff.staffid where staff.username = '"+username+"'")
    results = mc.fetchall()
    for res in results:
      print(res)
    return results

  def appendStaffInfoByUsername(self,username, mc, c, key, value):
    #if staff has the same ward as current staffID (managers only)
    #update field with value at key point
    if  isinstance(key, str):
      key= key.lower()
   
      if key == "ward": 
          
        mc.execute("UPDATE staff SET ward = %s WHERE username = %s", (value, username))
      elif key == "boss":
      
        mc.execute("UPDATE staff SET LineManager = %s WHERE username = %s", (value, username))
      elif key =="hours":
        mc.execute("select * from staff where username = '"+username+"'")
        res = mc.fetchall()
        staffID=res[0][0]
        mc.execute("SELECT * FROM hours where staffID = '"+str(staffID)+"'")
        
        res = mc.fetchall()
        if  mc.rowcount >0:
          mc.execute("UPDATE hours SET hours = %s WHERE staffid = %s", (value, staffID))
        else:        
          mc.execute("insert into hours(staffid,hours) VALUES (%s,%s)", (staffID,value))
      c.commit()
    

 #Audit logs method
  def getAuditLogs(self,mc, num = 1000):
    auditLogs = []
    mc.execute("SELECT * FROM audit ORDER BY TimeStamp DESC LIMIT " + str(num))
    results = mc.fetchall()
    for res in results:
      tempLine = str(res[3]) + ": " + str(res[1]) + " attempted to use method " + str(res[2]) + " affecting user " + str(res[4])
      auditLogs.append(tempLine)
      print(tempLine)
    return auditLogs
    #Returns all audit logs

  #Role Assignment
  def getRoleBySID(self,username,mc):
    #returns the role of the staff id's account
    result=[]
    userid = getUserID(username,mc)
    mc.execute("select distinct roleID from roles where userID="+str(userID))
    results = mc.fetchall()
    for res in results:
      result.append(res[0])
      print(res)
    return result
  def elevate(self,username, mc, c, key, value, value2= None):
    #Alter the role assigned to new value of the Account with ID
    #0 = patient, 1 = receptionist, 2 = nurse, 3 = doctor
    #4 = regulator, 5 = managerial staff, 6 = Sytem admin]
    userid = getUserID(username,mc)
    if isinstance(key,str):
      key= key.lower()
      result = ""
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
      return results

  def getUserID(self,Username, mc):
    mc.execute("Select UserID from personalinfo where username = '"+Username+"'")
    results = mc.fetchall()
    res = results[0][0]
    return res

  def getStaffID(self,Username,mc):
    mc.execute("Select staffID from staff where username = '"+Username+"'")
    results = mc.fetchall()
    res = results[0][0]
    return res

