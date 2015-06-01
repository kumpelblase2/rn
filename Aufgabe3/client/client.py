import time
import socket
import select
import struct
import csv

UDP_IP = "localhost"
UDP_PORT = 8080
MESSAGE = "Hello, World!"

transferlimit=5

WindowSize=1008
HeadSize=8
ErrorRate=100


print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

log=[]
paketlog=[]
sendCount=0
timeoutCount=0
recAckCount=0
RTTsum=0


filename="test.jpg"
destination="image/img.jpg"
                     
def readFile(fn,chunksize):
    f = open(fn, "rb")
    try:
        chunk=[];
        blocks=[];
        byte = f.read(1)
        while byte != "":
            # Do stuff with byte.
            chunk.append(byte)
            if(len(chunk)>=chunksize):
                #print "Chunk(%d)"%(len(blocks),),chunk
                blocks.append({"chunk":chunk,"send":0,"ack":0,"sendtime":0,"timeout":0,"firstsend":0})
                chunk=[]
            byte = f.read(1)
        blocks.append({"chunk":chunk,"send":0,"ack":0,"sendtime":0,"timeout":0,"firstsend":0})
    finally:
        f.close()
    print len(blocks)
    return blocks
                     
                     
def sequenznum(id=0):
    return struct.pack("Q", id)
                     
def firstmessage(PATH,SIZE,ERRORRATE):
    return "%s%s;%d;%d"%(sequenznum(),PATH,SIZE,ERRORRATE)

def datamessage(id,chunk):
    data=''.join(chunk)
    return "%s%s"%(sequenznum(id),data)

                     
def readUDP():
    r, w, e = select.select([sock], [], [],0)
    for s in r:
        if s is sock:
            data, addr = sock.recvfrom(1024)
            
            if len(data)==8:
                paketID=struct.unpack("Q",data[0:8])[0]
                
                #print "Pack %d was ACK"%(paketID,)
                if(paketID>0):
                    setPacketAck(paketID)
                    
                    
            else:
                print "WRONG ANSWER:",data,addr
            

def testComplete():
    for block in blocks:
        if block.get("ack",0)==0:
            return False
    return True

def setPacketAck(id):
    global RTTsum, recAckCount
    newRTT=time.time()-blocks[id-1]["sendtime"]
    trans=blocks[id-1]["send"]
    recAckCount+=1
    RTTsum+=newRTT
    RTT.calcRTO(newRTT)
    paketlog.append({"PaketID":id,"paketRTT":newRTT,"transmitions":trans,"RTO":RTT.RTO})
    
    
    blocks[id-1]["ack"]=1
    
    
def packetsPending():
    count=0
    for block in blocks:
        if(block.get("ack",0)==0 and block.get("send",0)!=0):
            count+=1
    return count

def getNextBlockID():
    for i,block in enumerate(blocks):
        if(block.get("send",0)==0):
            #print "nextID found ",i
            return i
    return None

def sendPacket(id):
    global sendCount
    blocks[id]["send"]+=1
    blocks[id]["timeout"]=time.time()+RTT.RTO
    blocks[id]["sendtime"]=time.time()
    if(blocks[id].get("firstsend",0)==0):
        blocks[id]["firstsend"]=time.time()
    MESSAGE = datamessage(id+1,blocks[id]["chunk"])
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    sendCount+=1
    
def checkTimeout():
    global timeoutCount
    for i,block in enumerate(blocks):
        if(block.get("ack",0)==0 and block.get("send",0)!=0):
            if(block.get("timeout",0) < time.time()):
                print "retransmit",i
                timeoutCount+=1
                sendPacket(i)
                RTT.doubleRTO()
                

class RetransmitTime:

    def __init__(self):
        self.RTOmax=2
        self.RTO=1
        self.SRTT=1
        self.rttVar=0.5
        self.beta=0.25
        self.alpha=0.125
        self.first=True
    
    def calcRTO(self,newRTT):
        if(self.first==True):
            self.SRTT=newRTT
            self.rttVar=0.5*newRTT 
            self.first=False
        self.rttVar  = (1-self.beta) * self.rttVar + self.beta * abs(self.SRTT - newRTT)
        self.SRTT    = (1-self.alpha) * self.SRTT + self.alpha * newRTT
        self.RTO     = self.SRTT + 4 * self.rttVar 
        if self.RTO > self.RTOmax:
            print "RTOMAX!!!",self.RTO,
            self.RTO=self.RTOmax
        #print "RTO",(newRTT,self.RTO,self.SRTT,self.rttVar)
      
    def doubleRTO(self):
        self.RTO+=self.RTO
        if self.RTO > self.RTOmax:
            self.RTO=self.RTOmax    


RTT=RetransmitTime()
            


'''
for i,block in enumerate(blocks):
    MESSAGE=datamessage(i+1,block["chunk"])
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  
    print "message:", "%s"%(MESSAGE,)
    time.sleep(.001)
    readUDP()
'''


log.append({"FileToSend":filename,"Destination":destination,"Windowsize":WindowSize,"Errorrate":ErrorRate})
blocks=readFile(filename,WindowSize-HeadSize)
sock.sendto(firstmessage(destination,WindowSize,ErrorRate) ,(UDP_IP, UDP_PORT))

startTime=time.time()
while not testComplete():
    time.sleep(.000001) 
    readUDP()
    if packetsPending()<transferlimit:
        #print "send more Packets"
        nextID=getNextBlockID()
        #print "next",nextID
        if (not nextID == None):
            #print "next",nextID
            sendPacket(nextID)
    checkTimeout()
endeTime=time.time()
sock.sendto("FIN", (UDP_IP, UDP_PORT))      

with open('log.csv', 'wb') as logfile:
    csv_writer = csv.writer(logfile)
    csv_writer.writerow( ('PaketID', 'Transmitions', 'RTT','RTO') )
    for lnr in paketlog:
        csv_writer.writerow((lnr["PaketID"],lnr["transmitions"],lnr["paketRTT"],lnr["RTO"]))

    
print "Datei gesendet in: %f s"%(endeTime-startTime,)
print "zu sendende Pakete:",len(blocks)    
print "Gesendete Pakete:",sendCount    
print "Verlorene Pakete:",timeoutCount    
print "Bestaetigte Pakete:",recAckCount  
print "avg. Roundtriptime:",RTTsum/recAckCount

sendCount=0
timeoutCount=0
recAckCount=0
RTTsum=0
time.sleep(3)
