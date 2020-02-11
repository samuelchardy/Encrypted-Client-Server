import hashlib
from Crypto2       import crypto

class messageParser:
  def parse(self, message):    
    token = message[0:31]
    command = bytes([message[32]])
    dataLen = message[33:36]
    data = message[36:int(dataLen)+36]
    checksum = message[164:325]

    return str(token), str(command.decode("ASCII")), dataLen, data, checksum
	
  def make(self, cr, publicKey, token, command, data):
    dataPaddingLen = 3-len(data)
    #dataLength  = str(dataPaddingLen*'0') + str(len(data))
    dataLength = str(len(data)).zfill(3)

    dataPadding = 128-len(data)
    data = data + (' ' * dataPadding)
    msg = str(token) + str(command) + dataLength + data
    checksum = hashlib.md5(bytes(msg.encode("ASCII")))
    msg = str(msg) + str(checksum)

    encryptedMsg = crypto.encryptData(cr, msg, publicKey)
    return encryptedMsg


  def checkData(self, data):
    if("," not in data):
      return True
    else:
      return False
    
