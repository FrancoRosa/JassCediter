import time
import minimalmodbus, serial, struct

def read_float(instrument, register):
    time.sleep(1)
    b1 = instrument.read_register(register)
    time.sleep(1)
    b2 = instrument.read_register(register+1)
    b1 = "{0:0{1}X}".format(b1,4) 
    b2 = "{0:0{1}X}".format(b2,4)
    return struct.unpack('!f', (b2+b1).decode('hex'))[0]

while True:
    #########################################
    #Sensor de PH
    rTempValue = 0  # Temperature value
    rPH = 1         # Main Mesuare Value
    rTestVolt = 2   # Main test Voltage
    rMeasPot = 3    # Measuring potencial
    rTempStatus = 5 # Temperature status

    phsensor = minimalmodbus.Instrument('/dev/ttyUSB0',2)
    phsensor.serial.baudrate=9600
    phsensor.serial.parity=serial.PARITY_NONE
    #phsensor.debug=True

    tempH20 = phsensor.read_register(rTempValue,1)
    time.sleep(1)
    phH20 = phsensor.read_register(rPH,2)
    time.sleep(1)

    print time.ctime()
    print "PH Temper:", tempH20
    print "PH Value :", phH20

    #########################################
    #Sensor de Cloro
    rConcentration = 0x0000  # Temperature value
    rCurrent = 0x0002   # Main test Voltage
    rTemp = 0x0004         # Main Mesuare Value

    clsensor = minimalmodbus.Instrument('/dev/ttyUSB0',10)
    clsensor.serial.baudrate=19200
    clsensor.serial.parity = serial.PARITY_EVEN
    #clsensor.debug=True

    ##
    #De calibracion:
    A = 0.0658
    B = 2.6829
    print "Cl Temper:", read_float(clsensor,rTemp)
    print "Cl Concen:", A+B*read_float(clsensor,rConcentration)
    print ""
    time.sleep(30)


