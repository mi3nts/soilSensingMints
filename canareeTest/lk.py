import serial
import serial.tools.list_ports
import datetime
#from mintsXU4 import mintsSensorReader as mSR
#from mintsXU4 import mintsDefinitions as mD
import sys

def findPorts(strIn1,strIn2):
    ports = list(serial.tools.list_ports.comports())
    allPorts = []
    for p in ports:
        currentPortStr1 = str(p[1])
        currentPortStr2 = str(p[2])
        if(currentPortStr1.find(strIn1)>=0 and currentPortStr2.find(strIn2)>=0 ):
            allPorts.append(str(p[0]).split(" ")[0])
    return allPorts

#check if port is correct with for p in ports
canareePorts = findPorts("Canaree PM","PID=10C4:EA60")[0]
loRaE5MiniPorts = findPorts("CP2102N USB to UART Bridge Controller","PID=10C4:EA60")[0]
gpsPorts = findPorts("u-blox 7 - GPS/GNSS Receiver","PID=1546:01A7")[0]

def openSerial(portIn,baudRate):
    ser = serial.Serial(
            port = portIn,
            baudrate = baudRate,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0)

    return ser;
  
def readSerialLineStr(serIn, timeOutSensor, strExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime) < timeOutSensor:   
            for c in serIn.read():
                line.append(chr(c))

                if chr(c) == '\n':
                    if startFound == True:
                        dataString = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        dataStringData = dataStringPost.split(',')
                        
                        if dataStringPost.find(strExpected) > 0:
                            return dataStringData;
                        else:
                            line = []
                    else:    
                        startFound = True
                        line = []


def main():
  
    serE5Mini    = openSerial(loRaE5MiniPorts,9600)
    serCanaree   = openSerial(canareePorts,115200)
    serGPS       = openSerial(gpsPorts,9600)
    

    print(" ")
    print("Connected to: " + serE5Mini.portstr)
    print("Connected to: " + serCanaree.portstr)
    print("Connected to: " + serGPS.portstr)
    print(" ")

    lineE5 = []
    lineCanaree = []
    lineGPS = []

    while True:
        try:
            #for a in serE5Mini.read():
                #lineE5.append(chr(a))
                #if chr(a) == '\n':
                    #dataStringE5 = (''.join(lineE5))
                    #print(dataStringE5)
                    #lineE5 = []
                    
            #for b in serCanaree.read():
                #lineCanaree.append(chr(b))
                #if chr(b) == '\n':
                    #dataStringCanaree = (''.join(lineCanaree))
                    #print(dataStringCanaree)
                    #lineCanaree = []
                    
            sensorData = readSerialLineStr(serGPS, 2, "GGA")
            print(sensorData)
            
        except:
            print("Incomplete String Read")
            lineE5 = []
            lineGPS = []
            lineCanaree = []
            


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")

    print("Monitoring E5, Canaree, GPS")
    main()
