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
      Methods=[]
      #Own record
      __AddMethod("getMyRecord",getownRecord,[0])
      #Appointments
      __AddMethod("getAppointment",getAppointmentByPID, [0,1])
      __AddMethod("appendAppointment",appendAppointmentByPID, [1])
      __AddMethod("writeAppointment",writeToAppointmentByPID, [1])
      #Records
      __AddMethod("getRecord",getRecordByPID, [2,3,4,5])
      __AddMethod("appendRecord",appendRecordByPID, [2,3])
      __AddMethod("writeRecord",writeToRecordByPID, [3])
      #Audit Logs
      __AddMethod("getAudit",getAuditLogs, [4,6])
      #Staff Info 
      __AddMethod("getStaffInfo",getStaffInfoBySID, [1,5,6])
      __AddMethod("appendStaffInfo",appendStaffInfoBySID, [5])
      __AddMethod("writeStaffInfo",writeToStaffInfo, [5])
      __AddMethod("deleteStaffInfo",deleteStaffInfo, [5])
      #Role Assignment
      __AddMethod("getRole",getRoleBySID,[6])
      __AddMethod("elevateRole",elevate, [6])
      
  def __AddMethod(FunctionName,Caller,Roles):,
    method = Dict()
    method.update({"call":Caller, "rolesAccess":Roles})
    Methods.append({FunctionName:method})

  def callMethod(methodname, myID, args):
    #If role allows perform method
    ReturnDict={}
    #insert SQL connection here to pickup the roles of staff and the method rights per name of method  
    #if (myID.valid())
      if list(set(Methods[methodname][rolesAccess]) & set(myID.getRoles)).len()>=1:
        ReturnDict.update({"Values":Methods[methodName]["call"](args), "Success":True})
        return Methods[methodname]["call"](args)
      else 
        ReturnDict.update({"Values":Methods[methodName]["call"](args), "Success":False})
      return ReturnDict


def getAppointmentByPID(pid):
#finds the next appointment for patient id

def appendAppointmentByPID(pid, key, value):
#updates the next appointment for patient id
#with key, value

def writeToAppointmentByPID(pid):
#sneds a request to create a new appointment for patient id

#Patient record methods  
def getRecordByPID(pid):
#if patient has the same ward as current staff id
#return a Record containing patients data

def appendRecordByPID(pid, key, value):
#if patient has the same ward as current staff id
#update field with value at key point
patientRecord.update(key,value)

def writeToRecordByPID(pid):
#if patient has the same ward as current staff id and staffid is the gp/doctors 
#assert in my list of patients -- a good check but not authentication means
#send request for patient record to write 

#Staff data methods
def getStaffInfoBySID(sid)
#finds and returns the information related to the staff with StaffID

def appendStaffInfoBySID(sid, key, value)
#if staff has the same ward as current staffID (managers only)
#update field with value at key point

def writeToStaffInfo(sid)
#if staff has the same ward as current staffID (managers only) 
#send request for staff data to write 

def deleteStaffInfo(sid)
#if staff has the same ward as current staffID (managers only)
#send a request for the deletion of staff data

#Audit logs method
def getAuditLogs()
#Returns all audit logs

#Role Assignment
def getRoleBySID(sid)
#returns the role of the staff id's account
def elevate(ID, value):
#Alter the role assigned to new value of the Account with ID
#0 = patient, 1 = receptionist, 2 = nurse, 3 = doctor
#4 = regulator, 5 = managerial staff, 6 = Sytem admin


#class SysAdmin(Account):
# def elevate(Account):
#Switch account from staff to patient

#also return audit logs

#class Regulator(Account):
# def getAuditLogs()
#Returns all audit logs
#  return {}

def getownRecord(pid):
return {}
def getAppointmentByPID(pid):
return {}
