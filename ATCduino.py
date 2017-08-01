#!/usr/bin/python

import serial
import time,hal,glob
import ConfigParser

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
#print serial_ports()
ser = serial.Serial(serial_ports()[0],115200)
#ser = serial.Serial("/dev/ttyUSB0",115200)
#print ser.readline()

c.newpin("piston",hal.HAL_BIT,hal.HAL_IN)
c.newpin("home",hal.HAL_BIT,hal.HAL_IN)
c.newpin("inposition",hal.HAL_BIT,hal.HAL_OUT)
c.newpin("Enabled",hal.HAL_BIT,hal.HAL_IN)
c.newpin("station",hal.HAL_FLOAT,hal.HAL_OUT)
c.newpin("cmdstation",hal.HAL_FLOAT,hal.HAL_IN)
c.newpin("stations.s1",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s2",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s3",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s4",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s5",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s6",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s7",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s8",hal.HAL_S32,hal.HAL_IN)
c.newpin("PID.P",hal.HAL_FLOAT,hal.HAL_IN)
c.newpin("PID.I",hal.HAL_FLOAT,hal.HAL_IN)
c.newpin("PID.D",hal.HAL_FLOAT,hal.HAL_IN)
config = ConfigParser.ConfigParser()
config.read('ATCduino.ini')
c.ready()
#ser.writelines ('N1=00000:2=08384:3=16768:4=25152')
#time.sleep(1)
#ser.writelines ('N5=33536:6=41920:7=50304:8=58688')
#time.sleep(1)
old_piston = False
old_station = -1.0
old_home = False
inpos='0'
station = '0'
enabled = '0'
Stations = [0,0,0,0,0,0,0,0]
try:
    while 1:
        ser.write ('U\r\n')
        time.sleep(0.1)
        message= ser.readline()
        #print message
        try:
            inpos,station,enabled = message.split(",")
        except:
            pass
        #c['PID.P'] = float(p)
        #c['PID.I'] = float(i)
        #c['PID.D'] = float(d)
        for i in range(0,8):
            Stations[i] = c["stations.s%d"%(i+1)]
        c['inposition'] = True if inpos.rstrip('\r\n') == "1"  else False
        c['station'] = float(station)
        c['Enabled'] = False if enabled.rstrip('\r\n') == "0"  else True
        #print inpos,station,enabled
        if c["piston"] !=  old_piston:
            if c.piston == True:
                ser.write("O\r\n")
            else:
                ser.write("J\r\n")
            old_piston = c["piston"]
        if c.cmdstation != old_station:
            ser.write("X%s\r\n"%int(Stations[int(c.cmdstation)]))
            print ("X%s\r\n"%int(Stations[int(c.cmdstation)]))
            old_station = c.cmdstation
        if c.home == True:
            ser.write("M\r\n")
            c.home= False
except KeyboardInterrupt: pass
finally:
    ser.close()
    c.exit()
