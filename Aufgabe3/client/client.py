import time
import socket
import select

UDP_IP = "localhost"
UDP_PORT = 8080
MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

def readUDP():
    readable_list = [sock]
    readable, writeable, errord = select.select(readable_list, [], [])
    for s in readable:
        if s is sock:
            data, addr = sock.recvfrom(1024)
            print data,addr 
                     
for i in range(20):
    sock.sendto("%s, %d"%(MESSAGE,i), (UDP_IP, UDP_PORT))  
    sock.recv
    print "message:", "%s, %d"%(MESSAGE,i)
    time.sleep(.1)
    readUDP()
    
    
time.sleep(3)
