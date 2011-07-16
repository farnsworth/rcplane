import socket
import select
#import serial

#ser = serial.Serial('/dev/tty.usbserial-A100eDSH', 9600)

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind( (HOST, PORT) )
s.setblocking(0)
inputs = [s]

while True:
    readable,writable,exceptional = select.select( inputs,[],inputs, None)
    
    for r in readable:
        data,addr = r.recvfrom(1024)
        splittedData = data.split("@")
        splittedData.pop()
        for i in splittedData:
            print i+"@"
        if ("c" in splittedData):
            s.sendto("r",addr)
    for e in exceptional:
        print "exceptional"

s.close()
    
#ser.close()
