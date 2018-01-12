from time import sleep, strftime, localtime, time
import minimalmodbus, serial

print ">>>>>>>>>>>>>>>>"

n=0

# Power Analizer ModBus Registers
rTV = 0 # Temperature value
rPH = 1 # Main Mesuare Value
rVV = 2 # Main test Voltage
rVP = 3 # Measuring potencial
rTS = 5 # Temperature status


def readreg(reg,dec,baudios,paridad,address):
	instrument = minimalmodbus.Instrument('/dev/ttyUSB0',address) # port name, slave address (in decimal)
	#instrument.debug = True
	instrument.serial.baudrate = baudios
	instrument.serial.bytesize = 8
	instrument.serial.parity   = paridad
	instrument.serial.stopbits = 1
	instrument.serial.timeout  = 1  # seconds
	instrument.mode = minimalmodbus.MODE_RTU
	while True:
		sleep(0.1)
		try:
	
			return instrument.read_register(reg, dec) # Registernumber, number of decimals
		
		except:
			pass

"""
TV = readreg(rTV,1,9600,serial.PARITY_NONE,2)
PH = readreg(rPH,2,9600,serial.PARITY_NONE,2)
VV = readreg(rVV,3,9600,serial.PARITY_NONE,2)
VP = readreg(rVP,4,9600,serial.PARITY_NONE,2)
TS = readreg(rTS,0,9600,serial.PARITY_NONE,2)

print "MEDICIONES DEL SENSOR DE pH"
print "Temperatura:	", TV
print "pH:				", PH
print "Voltage:		", VV
print "Potencia:		", VP
print "Estado de temperatura:", TS

sleep(1)
"""
#sensortype 		= readreg(0X300,0,19200,serial.PARITY_EVEN,10) # 
#hardware 		= readreg(0x308,0,19200,serial.PARITY_EVEN,10)
#firmware 		= readreg(0x309,0,19200,serial.PARITY_EVEN,10)
#ennsteilheit 	= readreg(0x30a,0,19200,serial.PARITY_EVEN,10)
#serienumber 	= readreg(0x30c,0,19200,serial.PARITY_EVEN,10)
#teilenummer 	= readreg(0x317,0,19200,serial.PARITY_EVEN,10)

#slaveaddress 	= readreg(0x400,0,19200,serial.PARITY_EVEN,10)
#baudrate 		= readreg(0x401,0,19200,serial.PARITY_EVEN,10)
#paritystop 		= readreg(0x402,0,19200,serial.PARITY_EVEN,10)

concentrat_ppm 	= readreg(0x0000,0,19200,serial.PARITY_EVEN,10) # Registernumber, number of decimals
cell_current 	= readreg(0x0002,0,19200,serial.PARITY_EVEN,10)
temperature 	= readreg(0x0004,3,19200,serial.PARITY_EVEN,10)

#ppm 			= readreg(0x200,0,19200,serial.PARITY_EVEN,10)
#decimals 		= readreg(0x201,0,19200,serial.PARITY_EVEN,10)

#asas 			= readreg(0x022e,0,19200,serial.PARITY_EVEN,10)


print "MEDICIONES DEL SENSOR DE CLORO"

print "concentrat_ppm:", concentrat_ppm
print "cell_current:", cell_current
print "temperature:", temperature

