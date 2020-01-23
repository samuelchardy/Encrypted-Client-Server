import socket
from Crypto import crypto

c = crypto()
crypto.genKeys(c)
crypto.storeKeys(c)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()                           
port = 9999
clientSocket.connect((host, port))  

serverPublicKey = clientSocket.recv(1024)
print(serverPublicKey)
serverPublicKey = crypto.loadPublicKeyFromBytes(c, serverPublicKey)

msg = ("This is the message!").encode("ascii")
encryptMsg = crypto.encryptData(c, msg, serverPublicKey)

clientSocket.send(encryptMsg)

clientSocket.close()
#print (decryptedMsg)
