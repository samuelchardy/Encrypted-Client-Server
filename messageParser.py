class messageParser:
  def parse(self, message):    
    command = message[0]
    dataLen = message[1:3]
    data = message[3:int(dataLen)+4]
    checksum = message[131:294]

    return command, dataLen, data, checksum
