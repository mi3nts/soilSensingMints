import serial
import serial.tools.list_ports
import datetime
import time
import numpy as np
import sys

def openSerial(portIn, baudRate):
    ser = serial.Serial(
            port = portIn,
            baudrate = baudRate,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0)

    return ser

def findPorts(strIn1, strIn2):
    ports = list(serial.tools.list_ports.comports())
    allPorts = []
    for p in ports:
        currentPortStr1 = str(p[1])
        currentPortStr2 = str(p[2])
        if(currentPortStr1.find(strIn1)>=0 and currentPortStr2.find(strIn2)>=0 ):
            allPorts.append(str(p[0]).split(" ")[0])
    return allPorts
  
def sendCommand(serIn, commandStrIn, timeOutIn):
    serIn.write(str.encode(commandStrIn + '\r'))
    line = []
    lines = []
    startTime = time.time()
    while (time.time()-startTime)<timeOutIn:
        for c in serIn.read():
            line.append(chr(c))
            if chr(c) == '\n':
                dataString = (''.join(line)).replace("\n","").replace("\r","")
                lines.append(dataString)
                print(dataString)
                line = []
                break
    return lines


canareePorts = findPorts("Canaree PM","PID=10C4:EA60")[0]
loRaE5MiniPorts = findPorts("CP2102N USB to UART Bridge Controller","PID=10C4:EA60")[0]
gpsPorts = findPorts("u-blox 7 - GPS/GNSS Receiver","PID=1546:01A7")[0]

serE5Mini = openSerial(loRaE5MiniPorts, 9600)
    

print(" ")
print("Connected to: " + serE5Mini.portstr)
print(" ")

ID = sendCommand(serE5Mini, "AT+ID=DevEui", 1) #test if it receives AT
print(ID)
serE5Mini.close()
