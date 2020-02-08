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
      self.__AddMethod("getAppointment",getAppointmentByPID, [0,1])
      self.__AddMethod("appendAppointment",appendAppointmentByPID, [1])
      self.__AddMethod("writeAppointment",writeToAppointmentByPID, [1])
      #Records
      self.__AddMethod("getRecord",getRecordByPID, [2,3,4,5])
      self.__AddMethod("appendRecord",appendRecordByPID, [2,3])
      self.__AddMethod("writeRecord",writeToRecordByPID, [3])
      #Audit Logs
      self.__AddMethod("getAudit",getAuditLogs, [4,6])
      #Staff Info 
      self.__AddMethod("getStaffInfo",getStaffInfoBySID, [1,5,6])
      self.__AddMethod("appendStaffInfo",appendStaffInfoBySID, [5])
      self.__AddMethod("writeStaffInfo",writeToStaffInfo, [5])
      self.__AddMethod("deleteStaffInfo",deleteStaffInfo, [5])
      #Role Assignment
      self.__AddMethod("getRole",getRoleBySID,[6])
      self.__AddMethod("elevateRole",elevate, [6])
      
  def __AddMethod(FunctionName,Caller,Roles):,
    method = Dict()
    method.update({"call":Caller, "rolesAccess":Roles})
    self.Methods.append({FunctionName:method})

  def callMethod(methodname, myID, args):
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

  def getAppointmentByPID(username, mc):
#finds the next appointment for patient id
    mc.execute("SELECT NextAppointment from Record where Username = " + 'username')
    results = mc.fetchall()
    res = results[0][0]
    #print(res)
    return results
 def appendAppointmentByPID(pid, key, value):
#updates the next appointment for patient id
#with key, value
    pID = getUserID(username, mc)
    mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))
    results = mc.fetchall()
    return results
  def writeToAppointmentByPID(username, mc):
    #sends a request to create a new appointment for patient id
    pID = getUserID(username, mc)
    mc.execute("UPDATE Record SET NextAppointment = %s WHERE UserID = %s",(value,pID))


  #Patient record methods 
  def getRecordByPID(username,mc):
    #if patient has the same ward as current staff id
    #return a Record containing patients data
    pID=getUserID(username, mc)
    mc.execute("SELECT * from Record where UserID = "+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    results = mc.fetchall()
    
    return results
  def appendRecordByPID(patientUser, staffUser, key, value,mc,c):
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
    
  def writeToRecordByPID(patientUser,staffUser,mc):
    ######## Needs to get staffID from whoever is logged in ###########
    #if patient has the same ward as current staff id and staffid is the gp/doctors 
    #assert in my list of patients -- a good check but not authentication means
    #send request for patient record to write
    pID = getUserID(patientUser,mc)
    staffID = getStaffID(staffUser,mc)
    mc.execute("INSERT INTO record(UserId, Doctor) VALUES(%s,%s)",(pID, staffID))

  #Get user information
  def getUserInfoByUsername(username, mc):
    mc.execute("Select surname, forename, dob, email from  personalinfo where username = '"+username+"'")
    results = mc.fetchall()
    for res in results:
      print(res)
    
    
    return results
  # update user fields
  def updateUsers(username, key, value,mc,c):
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
  def updatePassword(username, newPassword,mc,c)
    mc.execute("select secretanswer from login where username = '" + username + "'")
    results = mc.fetchall()
    sec = results[0][0]
    newPassword += sec
    mc.execute("UPDATE login set password = %s where username = %s",(newPassword,username))
    c.commit()

  #Update last vaidated time
  def updateValidation(username,mc,c):
    dt=datetime.now()
    now=dt.strftime("%Y-%m-%d %H:%M:%S")
    mc.execute("UPDATE login SET lastValidation = %s WHERE username = %s",(username, now))
    c.commit()
    
  def addPrescription(username,value, mc,c):
  # add Prescription
    pID = getUserID(username, mc)
    mc.execute("INSERT INTO prescription(UserID, Prescription,current) VALUES(%s,%s,%s)",(pID, value,True))
    c.commit()
  # All history
  def getPrescriptionHistory(username,mc):  
    pID = getUserID(username, mc)
    mc.execute("Select prescription from prescription where UserId ="+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  # current 
  def getCurrentPrescription(username,mc):
    pID = getUserID(username, mc)
    mc.execute("Select prescription from prescription where UserId = %s and current = %s",(pID,True))
    results = mc.fetchall()
    for res in results:
      print(res)
  ##########################
    return results
  # Conditions
  def createCondition(username, value,mc,c): 
    pID = getUserID(username, mc) 
    mc.execute("INSERT INTO cond(UserID, Cond, current) VALUES(%s,%s,%s)",(pID, value,True))
    c.commit()
  # All history
  def getConditionHistory(username,mc):
    pID = getUserID(username, mc)  
    mc.execute("Select cond from cond where UserId = "+str(pID))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  # current 
  def getCurrentCondition(username,mc):  
    pID = getUserID(username, mc)
    mc.execute("Select cond from cond where UserId = %s and current = %s",(pID,True))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  #Staff data methods
  def addStaffByUsername(username,mc):
    mc.execute("INSERT INTO staff(username) VALUES ('"+uName+"')")

  def getStaffInfoByUsername(username, mc):
    #finds and returns the information related to the staff with Username
    mc.execute("SELECT * FROM staff INNER JOIN hours ON hours.staffid = staff.staffid where staff.username = '"+username+"'")
    results = mc.fetchall()
    for res in results:
      print(res)
    return results

  def appendStaffInfoByUsername(username, mc, c, key, value):
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
  def getAuditLogs(mc, num = 1000):
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
  def getRoleBySID(username,mc)
    #returns the role of the staff id's account
    userid = getUserID(username,mc)
    mc.execute("select distinct roleID from roles where userID="+str(userID))
    results = mc.fetchall()
    for res in results:
      print(res)
    return results
  def elevate(username, mc, c, key, value, value2= None):
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

  def getUserID(Username, mc):
    mc.execute("Select UserID from personalinfo where username = '"+Username+"'")
    results = mc.fetchall()
    res = results[0][0]
    return res

  def getStaffID(Username,mc):
    mc.execute("Select staffID from staff where username = '"+Username+"'")
    results = mc.fetchall()
    res = results[0][0]
    return res
