import RPi.GPIO as GPIO

pin_Sup = 20
pin_Sdw = 21
pin_Pum = 16
pin_Val = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_Sup, GPIO.IN)
GPIO.setup(pin_Sdw, GPIO.IN)
GPIO.setup(pin_Pum, GPIO.OUT)
GPIO.setup(pin_Val, GPIO.OUT)

def Val_on():
    GPIO.output(pin_Val,GPIO.LOW)
    print "...Val: On"

def Val_off():
    GPIO.output(pin_Val,GPIO.HIGH)
    print "...Val: Off"

def Pum_on():
    GPIO.output(pin_Pum,GPIO.LOW)
    print "...Pum: On"

def Pum_off():
    GPIO.output(pin_Pum,GPIO.HIGH)
    print "...Pum: Off"

def Sw_status():
    dw = GPIO.input(pin_Sdw)
    up = GPIO.input(pin_Sup)
    if up and dw:
        return "...Status: error"
    else:
        if up:
            return "...Status: full"
        if dw:
            return "...Status: empty"
    if not(up or dw):
        return "...Status: medium"

Pum_off()
Val_off()
#while True:
#    print "...", Sw_status()
#    sleep(1)