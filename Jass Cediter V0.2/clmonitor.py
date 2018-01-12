##############################################
# This Scripts conects to a Socket server and
# reads a Cl and Ph sensor then sends those values
# through the socket conecction every 20 min
#

from gpiotest import *          #functions for pump and valve control
import time, thread             #time and threads modules
import serial, minimalmodbus    #hardware communication modules

###########################
# Server and port config
serverName = 'codeado.com'
serverPort = '9998'

#Time for sending data to server
sendFrec = 5*60


###########################
# Modem config
modemPort = '/dev/ttyS0'
modemBaud = 9600
modemAPN = 'm2m.erictel.pe'


#Serial config for modemCommunication
modemSerial = serial.Serial(port = modemPort,
                            baudrate = modemBaud,
                            timeout=5)

###########################
# Debug Output
class cl: #Prints events on diferent colors for debugging porpouses
    TX = '\033[95m' # Modem GSM Transmited data    _pink
    RX = '\033[94m' # Modem GSM Received data      _blue
    DB = '\033[92m' # Data Base Queries            _lemon
    DBA = '\033[93m' # Data Base Answers            _yellow
    FUN = '\033[91m' # Function Name                -red

#####################################
# Strings used for modem communication
mOK =      "OK"
mERROR =   "ERRO"
mCLOSED =  "CLOS"
mSend =    "SEND OK"
mConn =    "CONNECT OK"
mCBC =     "+CBC" 
mCOP =     "+COP"
mCSQ =     "+CSQ"
mCGR =     "+CGR"
mIPC =     "+IPC"
mCGN =     "+CGN"
mGSN =     "86"   # this is SIMCOMS id found on serial number OR imei
mRIN =     "RING" # when someones makes a call.. it should hang up
mHUP =     "ATH"  # hangS up
mAUT =     "**"   # 
mSttime  =     "**st" # when someones makes a call.. it should hang up
mGttime  =     "**gt" # when someones makes a call.. it should hang up

#####################################
# Modems flags
flagOK     = False
flagERROR  = False
flagPromt  = False
flagSend   = False
flagConn   = False
flagReg    = False
flagPwr    = True
flagFail   = False
flagActaris= False
flagRIN    = False
flagAut    = False
flagTimetoSend = False
flagTimetoMeasure = False
flagWaitPromt = False

GSN = "00000000"
CBC = ""
COP = ""
CSQ = ""
CGN = ""

ph___ph = 0
ph_temp = 0
cl___cl = 0
cl_temp = 0

#######################################
# sim808 response processing functions
def procGSN(text): #read serial number or IMEI
    print cl.DB, "Processisnf GSN"
    global GSN
    if len(text)==17:
        GSN=text[:-2]
        if GSN.isdigit():
            print cl.DB, "GSN:", GSN
            return GSN
    else:
        return ""


def procCBC(text): # //battery levels
    global CBC
    print cl.DB, "Processisnf CBC"
    if len(text.split(","))==3:
        CBC=text.split(",")[2].replace("\r\n","")
        if CBC.isdigit():
            print cl.DB, "CBC:", CBC
            return CBC
    else:
        return ""

def procCSQ(text): #signal quality
    print cl.DB, "Processisnf CSQ"
    global CSQ
    if len(text.split(","))==2:
        CSQ=text.split(":")[1].split(",")[0].replace(" ","")
        if CSQ.isdigit():
            print cl.DB, "CSQ:", CSQ
            return CSQ
    else:
        return ""

def procCGR(text): #Checks if SIMCard is registered
    global flagReg
    if len(text.split(","))==2:
        CGR=text.split(",")[1][0]
        if CGR == '1' or CGR == '5':
            flagReg = True
    else:
        flagReg = False
    print cl.DB, "flagReg:", flagReg

def procCGN(text): #reads GLONASS output (Latitude n' longitude)
    global CGN
    print cl.DB, "... procCGN"
    CGN = "0.0,0.0"
    if len(text.split(","))>5:
        CGNSplit = text.split(",")
        if CGNSplit[1]=="1":
            CGN = "%s,%s"%(CGNSplit[3],CGNSplit[4])
    print cl.DB, "CGN:", CGN
    return CGN 


def procCOP(text): #reads service provider
    global COP
    print cl.DB, "... procCOP"
    if len(text.split(","))==3:
        COP = text.split(",")[2].replace("\r\n","").replace('"','')
        print cl.DB, "COP:", COP
        return COP
    else:
        return ""


def waitOk(timeout): # waits for Ok on modem line
    global flagOK, flagERROR
    flagOk = False
    flagERROR = False
    timeout = timeout*10
    t = 0
    while timeout>t:
        time.sleep(0.1)
        t = t + 1
        if flagOK or flagERROR: 
            flagOK=False
            flagERROR=False
            return True
    return False

def waitConn(timeout):  # waits for server connection
    print cl.DB, "Waiting con...." 
    global flagERROR,flagOK,flagConn
    flagOK=False
    flagERROR=False
    flagConn=False
    timeout= timeout*10
    t = 0
    while timeout>t:
        t=t+1
        if flagConn: 
            return True
        time.sleep(0.1)
    return False


def sendCommand(command,timeout): #Commands trhoug modem line AT format
    global flagOk, flagError
    flagOk = False
    flagERROR = False
    modemSerial.write("AT+")
    modemSerial.write(command)
    modemSerial.write("\r")
    print cl.TX, "AT+%s"%command
    waitResponse = waitOk(timeout)
    return waitResponse

def waitSend(timeout): #waits for send confirmation
    global flagSend
    print cl.DB, "---WaitingSend..."
    timeout= timeout*10
    t = 0
    while timeout>t:
        t=t+1
        if flagSend:
            print cl.DB, "....SendTrue"

            return True
        time.sleep(.1)

    print cl.DB, "....SendFlase"
    return False


def waitPromt(timeout):  # waits for '>' on modem line
    print cl.DB, "---WaitingPromt..."
    global flagPromt
    timeout= timeout*10
    t = 0
    while timeout>t:
        t=t+1
        if flagPromt:
            flagPromt=False
            print cl.DB, "OUT--- True"
            return True
        time.sleep(0.1)
    print cl.DB, "OUT--- False"
    return False

def sendServer(message): # Sends data to server
    global flagSend
    lenght=0
    flagPromt=False
    flagSend=False
    lenght = len(message)
    modemSerial.write("AT+CIPSEND=%d\r"%lenght)
    if waitPromt(10):
        modemSerial.write(message)
    return waitSend(20)

def sysStatus(): #Reads data from modem status
    print cl.DB, "--Getting Data Status"
    sendCommand("CGNSINF",5) #reads GLONASS data
    time.sleep(1)
    sendCommand("CSQ",5)      #reads sinal level
    time.sleep(1)
    sendCommand("CBC",5)      #reads batery
    time.sleep(1)
    sendCommand("COPS?",5)   #reads Operator
    time.sleep(1)

def sim808Init(): #Inits modem
    global flagOK
    while True:
        if sendCommand("GSN",5):
            if sendCommand("CGNSPWR=1",5):
                break

def read_float(instrument, register): # reads float data inverting register order
    b1 = instrument.read_register(register)
    b2 = instrument.read_register(register+1)
    b1 = "{0:0{1}X}".format(b1,4) 
    b2 = "{0:0{1}X}".format(b2,4)
    return struct.unpack('!f', (b2+b1).decode('hex'))[0]


def sysReadSensors(): #Reads sensors conected to modbus
    global ph___ph,ph_temp,cl___cl,cl_temp
        #########################################
        #Sensor de PH
    while True:
        time.sleep(20)
        ##################### tank fill
        print cl.DBA, ">>> >>> Ingreso de Agua"
        Val_on()
        while True:
            time.sleep(0.1)
            if Sw_status() == "full":
                print cl.DBA, Sw_status()
                print cl.DBA, ">>> >>> Cierre de Valvula"
                Val_off()
                break
        
        ##################### tank filled
        print cl.DBA, ">>> >>> Contenedor lleno"
        print cl.DBA, ">>> >>> Tiempo de Reposo", str(sendFrec-60)

        time.sleep(sendFrec-60)
        print cl.DBA, ">>> >>> Realizar Mediciones"

        rTempValue = 0  # Temperature value
        rPH = 1         # Main Mesuare Value

        phsensor = minimalmodbus.Instrument('/dev/ttyUSB0',2)
        phsensor.serial.baudrate=9600
        clsensor.serial.parity = serial.PARITY_NONE
        #phsensor.debug=True

        try:
            ph_temp = phsensor.read_register(rTempValue,1)
            time.sleep(1)
        except:
            print cl.DBA, "ModbusError PH"
            pass
        
        try:
            ph___ph = phsensor.read_register(rPH,2)
            time.sleep(1)
        except:
            print cl.DBA, "ModbusError PH"
            pass
        #########################################
        #Sensor de Cloro
        rConcentration = 0x0000  # Temperature value
        rTemp = 0x0004         # Main Mesuare Value

        clsensor = minimalmodbus.Instrument('/dev/ttyUSB0',10)
        clsensor.serial.baudrate=19200
        clsensor.serial.parity = serial.PARITY_EVEN
        #clsensor.debug=True

        try:
            cl_temp = read_float(clsensor,rTemp)
            time.sleep(1)
        except:
            print cl.DBA, "ModbusError CL"
            pass
            
        try:
            cl___cl = read_float(clsensor,rConcentration)
            #Valores de Calibracion:
            A = 0.0658
            B = 2.6829

            cl___cl = A+B*cl___cl 
            time.sleep(1)
        except:
            print cl.DBA, "ModbusError CL"
            pass
        print cl.DB, ">>> >>> Medicion de sensores"
        time.sleep(1*20)
        
        print cl.DB, ">>> >>> Vaciando"
        Pum_on()
        while True:
            time.sleep(0.1)
            if Sw_status() == "empty":
                print cl.DBA, Sw_status()
                Pum_off()
                break
        
        time.sleep(1*20)
        


def connectServer(): # Starts a socket conection
    global flagOk, flagError, flagReg 
    global flagConn, flagAut
    flagConn = False
    flagAut = False
    time.sleep(2)
    sendCommand("CGREG?",15)
    time.sleep(5)
    print cl.DB, "...Reg:", flagReg
    if flagReg:
        flagOk=False
        sendCommand("CIPSHUT",15)
        if not(sendCommand("CPIN?",25) and
            sendCommand("CSQ",15) and
            sendCommand("CGREG?",15) and
            sendCommand("CGATT?",15) and
            sendCommand("CSTT=\"%s\",\"\",\"\""%modemAPN ,35) and
            sendCommand("CIICR",15)):
            return False
        
        sendCommand("CIFSR",5)
        sendCommand("CIPSTART=\"TCP\",\"%s\",%s"%(serverName,serverPort),25)
        if waitConn(10): 
            print cl.DB, "...Conected to server"
            time.sleep(5)

            if flagAut:
                print cl.DB, "...conection thread"
                return sendServer(str(GSN))
        else:
            return False
    else: 
        return False



#hardwarepinout definitions made for arduino
led = 13 # green led on arduino
inp =  3 # input to detect powercuts shoudl be high
rxs = 10 # arduino soft rx
txs = 11 # arduino soft tx


tStatus = 60  # Seconds to wait to send status
tMeasur = 120 # Seconds to wait to send a measurement
sw_z = 110    # Size of UARTBuffer
sw_g = 30     # Size of LatLonIPBuffer and dateTime

sw_b  = ''      #SoftSerial internal Buffer
sw_m  = ''      #Output buffer
sw_c  = ''            #SoftSerial char
sw_i  = 0            #SoftSerial index


def checktime():
    global flagTimetoSend

    print "...checktime"
    while True:
        now = int(time.time())
        
        if now%sendFrec ==0:
            flagTimetoSend=True
        time.sleep(1)

##########################################
##########################################To DO, funtion to enable time to send, maybe 
##########################################
##########################################

#This thread read all data coming from sim808
def sim808Receiver():
    global flagWaitPromt, flagOK, flagERROR, flagPromt
    global flagConn, flagSend, flagRIN, flagAut
    global COP,CSQ,CBC,CGN,GSN 
    
    i=0
    while True:
        
        modemResponse = modemSerial.readline()
        print cl.RX, repr(modemResponse), len(modemResponse)
        if '>' in modemResponse:
            print cl.DB, "Promt Received..."
            flagPromt = True
            flagWaitPromt = False
            globals().update(locals())


        if mOK     in modemResponse[:2]: 
            flagOK = True
        if mERROR  in modemResponse[:4]: 
            flagERROR=True
        if mCLOSED in modemResponse[:4]:  
            print cl.DB, "...mCLOSED"
            flagConn=False
        
        if mSend in modemResponse[:7]:  
            print cl.DB, "...mSend"
            flagSend=True

        if mConn in modemResponse[:10]: 
            flagConn=True
        if mRIN    in modemResponse[:4]:  
            flagRIN=True
        if mAUT    in modemResponse[:2]:  
            print cl.DB, "mAUT"
            flagAut=True
        if mCBC    in modemResponse[:4]: 
            procCBC(modemResponse)
        if mCSQ    in modemResponse[:4]: 
            procCSQ(modemResponse)
        if mCGR    in modemResponse[:4]: 
            procCGR(modemResponse)
        if mCGN    in modemResponse[:4]: 
            procCGN(modemResponse)
        if mGSN    in modemResponse[:2]: 
            procGSN(modemResponse)
        if mCOP    in modemResponse[:4]: 
            procCOP(modemResponse)
        if mGttime in modemResponse[:4]: 
            procGTtime(modemResponse)
        if mSttime in modemResponse[:4]: 
            procSTtime(modemResponse)
        if len(modemResponse.split('.'))==4: 
            flagOK=True

        globals().update(locals())

        time.sleep(0.05)

#This thread works whith simcom module, conects to server and sends data
def sim808Connection():
    global flagConn, flagTimetoSend, flagTimetoMeasure, flagRIN
    global COP,CSQ,CBC,CGN,GSN 
    global ph___ph,ph_temp,cl___cl,cl_temp
    global flagPromt

    sim808Init()

    while True:
        if connectServer():
            print "...FlagCon:", flagConn
            while flagConn:
                print cl.DB, "flagTimetoSend", repr(flagTimetoSend)
                
                if flagTimetoSend:
                    sysStatus() # Getdata from modem
                    message ="%s,%s,%s,%s,%s,%2.2f,%2.2f,%2.2f,%2.2f"%(GSN,COP,CSQ,CBC,CGN,ph___ph,ph_temp,cl___cl,cl_temp)
                    print "message:", message, len(message)
                    print "GSN:",GSN 
                    print "COP:",COP 
                    print "CSQ:",CSQ 
                    print "CBC:",CBC 
                    print "CGN:",CGN 
                    print "ph___ph:"   ,ph___ph
                    print "ph_temp:" ,ph_temp
                    print "cl___cl:"   ,cl___cl
                    print "cl_temp:" ,cl_temp

                    if not sendServer(message):
                        break
                    flagTimetoSend=False


                if flagRIN:
                    modemSerial.send(mHUP)
                    flagRIN=False
                time.sleep(5)

        time.sleep(10)

thread.start_new_thread(checktime,())
thread.start_new_thread(sim808Receiver,())
thread.start_new_thread(sysReadSensors,())


while True:
    sim808Connection()
