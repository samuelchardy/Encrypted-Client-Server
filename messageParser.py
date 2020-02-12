import hashlib
from Crypto2 import crypto

class messageParser:
  def parse(self, message):    
    command = bytes([message[0]])
    dataLen = message[1:4]
    data = message[4:int(dataLen)+5]
    checksum = message[132:293]
    return str(command.decode("UTF-8")), dataLen, data, checksum
	

  def make(self, cr, publicKey, command, data):
    dataPaddingLen = 3-len(data)
    #dataLength  = str(dataPaddingLen*'0') + str(len(data))
    dataLength = str(len(data)).zfill(3)
    dataPadding = 128-len(data)
    data = data + (' ' * dataPadding)
    msg = str(command) + dataLength + data
    checksum = hashlib.md5(bytes(msg.encode("ASCII")))
    msg = str(msg) + str(checksum)
    encryptedMsg = crypto.encryptData(cr, msg, publicKey)
    return encryptedMsg


  def checkData(self, data):
    if("," not in data):
      return True
    else:
      return False
    
