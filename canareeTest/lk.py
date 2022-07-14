import serial
import serial.tools.list_ports
import datetime
#from mintsXU4 import mintsSensorReader as mSR
#from mintsXU4 import mintsDefinitions as mD
import sys

#dataFolder  = mD.dataFolder
#canereePort = "/dev/ttyUSB0"
baudRate = 115200

def findPorts(strIn1,strIn2):
    ports = list(serial.tools.list_ports.comports())
    allPorts = []
    for p in ports:
        currentPortStr1 = str(p[1])
        currentPortStr2 = str(p[2])
        if(currentPortStr1.find(strIn1)>=0 and currentPortStr2.find(strIn2)>=0 ):
            allPorts.append(str(p[0]).split(" ")[0])
    return allPorts

canareePorts = findPorts("Canaree PM","PID=10C4:EA60")[0]

def main():
    ser = serial.Serial(
    port = canareePorts,\
    baudrate = baudRate,\
    parity = serial.PARITY_NONE,\
    stopbits = serial.STOPBITS_ONE,\
    bytesize = serial.EIGHTBITS,\
    timeout = 0)

    print(" ")
    print("Connected to: " + ser.portstr)
    print(" ")

    line = []

    while True:
        try:
            for c in ser.read():
                line.append(chr(c))
                # print(line)
                if chr(c) == '\n':
                    dataString     = (''.join(line))
                    print(dataString)
                    line = []
                    break
        except:
            print("Incomplete String Read")
            line = []
    ser.close()


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")

    print("Monitoring Canaree on port: {0}".format(canareePorts) + " with baudrate " + str(baudRate))
    main()
