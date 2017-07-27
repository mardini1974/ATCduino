#!/usr/bin/python

__author__ = 'M.Mardini'
from serial import Serial
import time,hal

c= hal.component("ATCduino")

ser =Serial("/dev/ttyUSB0",115200)
time.sleep(1)
print ser.readline()
#ser.write ('!\r\n')
#sleep(0.1)
# print ser.readline()
# ser.write ('f!\r\n')
# sleep(0.1)
# print ser.readline()
c.newpin("piston",hal.HAL_BIT,hal.HAL_IN)
c.newpin("inposition",hal.HAL_BIT,hal.HAL_OUT)
c.newpin("Enabled",hal.HAL_BIT,hal.HAL_IN)
c.newpin("station",hal.HAL_S32,hal.HAL_OUT)
c.newparam("s1",hal.HAL_S32,hal.HAL_RW)
c.newparam("s2",hal.HAL_S32,hal.HAL_RW)
c.newparam("s3",hal.HAL_S32,hal.HAL_RW)
c.newparam("s4",hal.HAL_S32,hal.HAL_RW)
c.newparam("s5",hal.HAL_S32,hal.HAL_RW)
c.newparam("s6",hal.HAL_S32,hal.HAL_RW)
c.newparam("s7",hal.HAL_S32,hal.HAL_RW)
c.newparam("s8",hal.HAL_S32,hal.HAL_RW)
c.newparam("PID.P",hal.HAL_FLOAT,hal.HAL_RW)
c.newparam("PID.I",hal.HAL_FLOAT,hal.HAL_RW)
c.newparam("PID.D",hal.HAL_FLOAT,hal.HAL_RW)
ser.write ('N1=00000:2=08384:3=16768:4=25152:5=33536:6=41920:7=50304:8=58688\r\n')
old_piston = False
time.sleep(1)
c.ready()
try:
    while 1:
        time.sleep(0.1)
        ser.write ('U\r\n')
        message= ser.readline()
        #print message
        p,i,d,inpos,station,enabled = message.split(",")
        c['PID.P'] = float(p)
        c['PID.I'] = float(i)
        c['PID.D'] = float(d)
        c['inposition'] = True if inpos.rstrip('\r\n') == "1"  else False
        c['station'] = int(station)
        c['Enabled'] = False if enabled.rstrip('\r\n') == "0"  else True
        #print p,i,d,inpos,station,enabled
        if c["piston"] !=  old_piston:
            if c.piston == True:
                ser.write("O\r\n")
            else:
                ser.write("J\r\n")
            old_piston = c["piston"]

except KeyboardInterrupt: pass
finally:
    ser.close()
    c.exit()
