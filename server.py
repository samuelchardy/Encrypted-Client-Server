import socket

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9999
serverSocket.bind((host, port))

serverSocket.listen(5)
print("Server Active")

while True:
    clientSocket,addr = serverSocket.accept()      
    print("Connected to: %s" % str(addr))
    
    msg = "Connected to " + str(host) + ":" + str(port) + "\r\n" 
    clientSocket.send(msg.encode('ascii'))
    clientSocket.close()
