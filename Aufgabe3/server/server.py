#!/usr/bin/python

'''
    Datei-Transferserver Aufgabe-3 Rechnernetze
'''

import time
import socket
import select
import sys
import struct
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 8080
MESSAGE = "Hello, World!"

path=""
windowSize=0

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind( (UDP_IP,UDP_PORT))
#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

errorrate=10
errorcount=0
ackresponse=[]
pakets=dict()

def sequenznum(id=0):
    return struct.pack("Q", id)

def addResponse(msg,timetosend):
    global errorcount,errorrate
    errorcount+=1
    if errorcount%errorrate!=0:
        ackresponse.append({"msg":msg,"time":timetosend,"send":0})
    else:
        print "ACK DROPPED",msg

def getAckResponse():
    for item in ackresponse:
        if item["time"]<time.time():
            ackresponse.remove(item)
            return item
    
class conLock:
    def __init__(self,TO=5):
        self.lock = False
        self.addr = "0.0.0.0"
        self.TOtime = TO
        self.timeout = 0
    
    def setlock(self, addr = None):
        if(not self.lock):
            print "+ Locked"
            self.addr = addr
            self.lock = True
            self.clearTimeout()
            pakets=dict()
    
    def unlock(self,reason = ""):
        if(self.lock):
            print "- Unlocked: %s"%(reason,)
            ackresponse=[]
            self.lock=False
        
    def clearTimeout(self):
        rest = (self.timeout-time.time())
        self.timeout = time.time()+self.TOtime
        return rest
    
    def checkTime(self):
        if(time.time()>self.timeout):
            self.unlock("Timeout")
        
    def isLocked(self):
        return self.lock
    
    def conAccept(self,addr = None):
        if(self.lock and addr == self.addr):
            print "Timeout cleared, rest was:%f"%self.clearTimeout()
        return addr == self.addr or not self.lock

def writeToFile(pakets):
    print "writing File to: %s"%(path,)
    dir=os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(path, "wb")
    try:
        for line in pakets:
            f.write(pakets[line])
    finally:
        f.close()
        
def initTransfer(param):
    global path
    path,windowSize,errorrate=param
    print "Starte Dateitransfer nach:\n%s"%(path,)
    return True #TODO CHECK
        
def run():
    Locker = conLock(5)
    print( "Starte Filetransferserver\n" )
    print( "===========================" )
    print( "UDP: [%s:%d]"%(UDP_IP,UDP_PORT) )
    print( "===========================" )
    
    print( "= Now Listening ===========" )
    print( "===========================" )
    while True:
        Locker.checkTime()
        time.sleep(0.001)
        
        
        
        r,w,x = select.select([sock],[],[],0)
        for s in r:
            if s is sock:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                if(Locker.conAccept(addr = addr)):
                    if len(data)<8:
                        if data=="FIN":
                            for line in pakets:
                                print line,pakets[line]
                            writeToFile(pakets)
                            Locker.unlock("Final Packet")
                    else:
                        if(struct.unpack("Q",data[0:8])[0]==0):
                            print "=== FIRST-MESSAGE ==="
                            param=data[8:].split(";")
                            print param
                            destinationPath=param[0]
                            windowSize=param[1]
                            ErrorRate=param[2]
                            if(initTransfer(param)):
                                Locker.setlock(addr)
                        
                        
                        if(Locker.isLocked()):
                            packetnr=struct.unpack("Q",data[0:8])[0]
                            transfer=data[8:]
                            print "Got data from", addr
                            print "PacketNR.:",packetnr
                            print "received message:", transfer, len(transfer)
                            print( "===========================" )
                            if(packetnr>0):
                                pakets[packetnr]=transfer
                            addResponse(sequenznum(packetnr),time.time()+0.01)
                            #sock.sendto("received: '%s'"%(data,), addr)
            
        if(Locker.isLocked()):
            packet=getAckResponse()
            if packet:
                sock.sendto(packet["msg"], addr)

    

if __name__ == "__main__":
    run()
    time.sleep(2)