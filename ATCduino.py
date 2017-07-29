#!/usr/bin/python

import serial
import time,hal,glob
def serial_ports():
    ports = glob.glob('/dev/tty[A-Za-z]*')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port,115200)
            message= s.readline()
            time.sleep(0.1)
            s.write ("!\r\n")
            time.sleep(0.1)
            message= s.readline()
            if message.find('ATC')>-1:
                result.append(port)
            s.close()

        except (OSError, serial.SerialException):
            pass
    return result

c= hal.component("ATCduino")

ser =serial.Serial(serial_ports()[0],115200)
ser.readline()
c.newpin("piston",hal.HAL_BIT,hal.HAL_IN)
c.newpin("home",hal.HAL_BIT,hal.HAL_IN)
c.newpin("inposition",hal.HAL_BIT,hal.HAL_OUT)
c.newpin("Enabled",hal.HAL_BIT,hal.HAL_IN)
c.newpin("station",hal.HAL_FLOAT,hal.HAL_OUT)
c.newpin("cmdstation",hal.HAL_FLOAT,hal.HAL_IN)
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
old_station = -1.0
old_home = False
time.sleep(1)
c.ready()
try:
    while 1:
        ser.write ('U\r\n')
        time.sleep(0.1)

        message= ser.readline()
        print message
        inpos,station,enabled = message.split(",")
        #c['PID.P'] = float(p)
        #c['PID.I'] = float(i)
        #c['PID.D'] = float(d)
        c['inposition'] = True if inpos.rstrip('\r\n') == "1"  else False
        c['station'] = float(station)
        c['Enabled'] = False if enabled.rstrip('\r\n') == "0"  else True
        #print p,i,d,inpos,station,enabled
        if c["piston"] !=  old_piston:
            if c.piston == True:
                ser.write("O\r\n")
            else:
                ser.write("J\r\n")
            old_piston = c["piston"]
        if c.cmdstation != old_station:
            ser.write("L%s\r\n"%int(c.cmdstation))
            print ("L%s\r\n"%int(c.cmdstation))
            old_station = c.cmdstation
        if c.home == True:
            ser.write("M\r\n")
            c.home= False
except KeyboardInterrupt: pass
finally:
    ser.close()
    c.exit()
