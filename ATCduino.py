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
                print ('Found ATC (Auto tool changer) and connecting on port \'%s\''%port)
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
c.newpin("position",hal.HAL_FLOAT,hal.HAL_OUT)
c.newpin("command",hal.HAL_FLOAT,hal.HAL_OUT)
c.newpin("cmdstation",hal.HAL_FLOAT,hal.HAL_IN)
c.newpin("stations.s1",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s2",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s3",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s4",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s5",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s6",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s7",hal.HAL_S32,hal.HAL_IN)
c.newpin("stations.s8",hal.HAL_S32,hal.HAL_IN)

c.newpin("HomeOffset",hal.HAL_S32,hal.HAL_IN)
c.newpin("SaveEEprom",hal.HAL_BIT,hal.HAL_IN)
c.newpin("hspeed",hal.HAL_S32,hal.HAL_IN)
c.newpin("hoffsetspeed",hal.HAL_S32,hal.HAL_IN)
c.newpin("rspeed",hal.HAL_S32,hal.HAL_IN)

config = ConfigParser.ConfigParser()
config.read('ATCduino.ini')
c.ready()
#ser.writelines ('N1=00000:2=08384:3=16768:4=25152')
#time.sleep(1)
#ser.writelines ('N5=33536:6=41920:7=50304:8=58688')
#time.sleep(1)
old_piston = False
old_station = 0
old_home = False
inpos='0'
position = '0'
enabled = '0'
cmd = '0'
p =  '0'
i = '0'
d= '0'
retry = 0
message = ser.readline()
ser.write("q\r\n")
time.sleep(0.1)
message = ser.readline()
p,i,d = message.split(",")
c["PID.P"] = float(p)
c["PID.I"] = float(i)
c["PID.D"] = float(d)
old_pidp = 0
old_pidi = 0
old_pidd = 0
old_hspeed = 0
old_hoffsetspeed = 0
old_rspeed = 0


Stations = [0,0,0,0,0,0,0,0]
try:
    while 1:
        ser.write("X%s\r\n" % Stations[int(c.cmdstation)])
        time.sleep(0.1)
        message= ser.readline()
        try:
            inpos,position,cmd,enabled = message.split(",")
            for i in range(0,8):
                Stations[i] = c["stations.s%d"%(i+1)]
            c['inposition'] = True if inpos.rstrip('\r\n') == "1"  else False
            c['position']= float(position)
            c['command']= float(cmd)
            c['station'] = round(float(position)/8384,0)
            c['Enabled'] = False if enabled.rstrip('\r\n') == "0"  else True
        except:
            pass
        if c["piston"] !=  old_piston:
            if c.piston == True:
                ser.write("O\r\n")
            else:
                ser.write("J\r\n")
            old_piston = c["piston"]

        if c["PID.P"] !=  old_pidp:
            ser.write("p%f\r\n"%c["PID.P"])
            old_pidp = c["PID.P"]

        if c["PID.I"] !=  old_pidi:
            ser.write("i%f\r\n"%c["PID.I"])
            old_pidi = c["PID.I"]

        if c["PID.D"] !=  old_pidd:
            ser.write("d%f\r\n"%c["PID.D"])
            old_pidd = c["PID.D"]

        if c["hspeed"] !=  old_hspeed:
            ser.write("V%d\r\n"%c["hspeed"])
            old_hspeed = c["hspeed"]

        if c["hoffsetspeed"] !=  old_hoffsetspeed:
            ser.write("C%d\r\n"%c["hoffsetspeed"])
            old_hofffsetspeed = c["hoffsetspeed"]

        if c["rspeed"] !=  old_rspeed:
            ser.write("Z%d\r\n"%c["rspeed"])
            old_rspeed = c["rspeed"]

        if c.SaveEEprom:
            ser.write("w\r\n")
            c.SaveEEprom = False

        if c.home:
            ser.write("M%d\r\n"%c["HomeOffset"])
            print ('Homing')
            c.home= False
except KeyboardInterrupt:
    pass

finally:
    print ('ATC has been disconnected')
    raise SystemExit
