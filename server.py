import socket
from password_strength import PasswordStats
from Crypto import crypto

c = crypto()
crypto.genKeys(c)
crypto.storeKeys(c)
publicKey = crypto.loadPublicKey(c)

host = socket.gethostname()
port = 9999

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen(1)

print("Server Active\n\n" + str(publicKey) + "\n")

while True:
  clientSocket, addr = serverSocket.accept()
  print("Connected to: %s" % str(addr))
  clientSocket.send(publicKey)

  msg = clientSocket.recv(1024)
  msg = crypto.decryptData(msg)
  print(msg.decode("ascii"))

  clientSocket.close()
