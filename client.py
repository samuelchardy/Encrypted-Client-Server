import socket
import hashlib
from Crypto2 import crypto

cr = crypto()
crypto.genKeys(cr)
crypto.storeKeys(cr)
publicKey = crypto.loadPublicKey(cr)

#CONNECTING TO THE SERVER
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()                           
port = 9999
clientSocket.connect((host, port))  

#RECEIVING SERVERS PUBLIC KEY
serverPublicKey = clientSocket.recv(1024)
print(serverPublicKey)
serverPublicKey = crypto.loadPublicKeyFromBytes(cr, serverPublicKey)

#SEND CLIENTS PUBLIC KEY
clientSocket.send(publicKey)



#LOGIN
data = "Bingo Bango Bongo!"
dataLength  = len(data)
dataPaddingLen = 128-len(data) 
data = data + (' ' * dataPaddingLen)

msg = "1" + str(dataLength) + data
checksum = hashlib.md5(bytes(msg)) 
msg = msg + bytes(checksum)

print("datalen: " + str(len("Bingo Bango Bongo!")))
print("msg : " + str(len(msg)))

sentMsg = crypto.encryptData(cr, msg, serverPublicKey)
print("msg pe: " + str(len(sentMsg)))
#signature = crypto.signMessage(cr, sentMsg)

clientSocket.send(sentMsg)


clientSocket.close()
#print (decryptedMsg)
