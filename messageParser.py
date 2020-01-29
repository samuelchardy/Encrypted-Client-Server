import hashlib
from Crypto2       import crypto

class messageParser:
  def parse(self, message):    
    command = message[0]
    dataLen = message[1:3]
    data = message[3:int(dataLen)+4]
    checksum = message[131:294]

    return command, dataLen, data, checksum


  def make(self, cr, publicKey, command, data):
    dataLength  = len(data)
    dataPaddingLen = 128-len(data)
    data = data + (' ' * dataPaddingLen)

    msg = str(command) + str(dataLength) + data
    checksum = hashlib.md5(bytes(msg))
    msg = msg + bytes(checksum)

    encryptedMsg = crypto.encryptData(cr, msg, publicKey)
    return encryptedMsg