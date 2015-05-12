#!/usr/bin/python

'''
    Datei-Transferserver Aufgabe-3 Rechnernetze
'''

import time
import socket
import sys

UDP_IP = "localhost"
UDP_PORT = 8080
MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind( (UDP_IP,UDP_PORT))
#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))









def run():
    print( "Starte Filetransferserver\n" )
    print( "===========================" )
    print( "UDP: [%s:%d]"%(UDP_IP,UDP_PORT) )
    print( "===========================" )
    
    print( "= Now Listening ===========" )
    print( "===========================" )
    while True:    
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print "Got data from", addr
            print "received message:", data
            print( "===========================" )
            sock.sendto("received: '%s'"%(data,), addr)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            traceback.print_exc()
    

if __name__ == "__main__":
    run()
    time.sleep(2)