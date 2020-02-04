import pyotp
class Verify:

  # Initialising time available to 2 mins
  def __init__(self):
    secret = pyotp.random_base32()
    self.OTP = pyotp.TOTP(secret,interval=120)
    
  # Returns code
  def get(self):
    return self.OTP.now()

  #Returns if verified
  def checkCode(self,userCode):
    return self.OTP.verify(userCode)