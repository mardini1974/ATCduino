#!/usr/bin/python

import serial
import time,hal,glob
import struct
from tkMessageBox import showinfo
from Tkinter import Tk
import serial.tools.list_ports

def get_bit( inbyte , inbit ):
    return (inbyte & 2**inbit) >> inbit


def updatestatus():
    global ser
    ser.flushInput()
    ser.write("Q\r\n")
    ser.flush()
    message = ser.read()
    time.sleep(0.1)
    data_left = ser.inWaiting()
    message += ser.read(data_left)
    #if len(message) <3 :
    #    fields = [0,0]
    #print ("%2s,Length=%d"%(message.encode("hex"),len(message)))
    fields = struct.unpack('ii',message)
    return fields
def readParameters():
    ser.flushInput()
    ser.write("?\r\n")
    message = ser.read()
    time.sleep(0.2)
    data_left = ser.inWaiting()
    message += ser.read(data_left)
    #print ("%s,Length=%d"%(message.encode("hex"),len(message)))
    accel,homeoffset,homespeed,homesearchspeed,speed = struct.unpack('fllll',message)
    print "%f"%accel
    print "%d"%homeoffset
    print "%d"%homespeed
    print "%d"%homesearchspeed
    print "%d"%speed
    return accel,homeoffset,homespeed,homesearchspeed,speed


def msgBox (title,message):
    windows =Tk()
    string = str(message)
    showinfo(title=title,message= string)
    windows.wm_withdraw()

c= hal.component("ATCduino")
#connect to first Usb  serial port
ser = serial.Serial(serial.tools.list_ports.comports()[0].device,115200)

c.newpin("piston",hal.HAL_BIT,hal.HAL_IN)
c.newpin("home",hal.HAL_BIT,hal.HAL_IN)
c.newpin("homed",hal.HAL_BIT,hal.HAL_OUT)
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
c.newpin("accel",hal.HAL_FLOAT,hal.HAL_IN)

time.sleep(3)
ser.flushInput()
ser.write ("!\r\n")
time.sleep (0.1)
message= ser.readline()
if message.find('ATC')>-1:
    print ('Found ATC (Auto tool changer) and connecting on port \'%s\''%serial.tools.list_ports.comports()[0].device)

c.ready()
old_piston = False
old_station = 0
old_home = False
old_hspeed = 0
old_hoffsetspeed = 0
old_rspeed = 0
old_hoffset =0
old_command =0
old_accel = 0.0
Stations = [0,0,0,0,0,0,0,0]
try:
    while 1:
        for i in range(0,8):
            Stations[i] = c["stations.s%d"%(i+1)]
        time.sleep(0.5)
        result = updatestatus()
        c['inposition'] = True if get_bit(result[0],1) == 1  else False
        c['position']= result[1]
        c['station'] = round(float(c['position'])/400,0)
        c['Enabled'] = False if get_bit(result[0],0) == 0  else True
        c['homed'] = True if get_bit(result[0],2) == 1 else False


        if c['cmdstation']!= old_command:
            if c['Enabled'] == False:
                if c['homed'] == True:
                    ser.write("M%s\r\n"%Stations[int(c['cmdstation'])])
                    old_command = c['cmdstation']
                else:
                    msgBox("Error","Tool changer not homed yet!...")
            else:
                msgBox("Error","Can't move, motor not Enabled!")


        if c["piston"] !=  old_piston:
            if c["piston"] == True:
                if c["inposition"]== True :
                    ser.write("O\r\n")
                else:
                    msgBox("Error","Motor is running or not homed..")
            else:
                ser.write("J\r\n")
            old_piston = c["piston"]



        if c["hspeed"] !=  old_hspeed:
            ser.write("Z%d\r\n"%c["hspeed"])
            old_hspeed = c["hspeed"]

        if c["HomeOffset"] !=  old_hoffset:
            ser.write("T%d\r\n"%c["HomeOffset"])
            old_hoffset = c["hspeed"]

        if c["hoffsetspeed"] !=  old_hoffsetspeed:
            ser.write("V%d\r\n"%c["hoffsetspeed"])
            old_hofffsetspeed = c["hoffsetspeed"]

        if c["rspeed"] !=  old_rspeed:
            ser.write("S%d\r\n"%c["rspeed"])
            old_rspeed = c["rspeed"]

        if c["accel"] !=  old_accel:
            ser.write("A%d\r\n"%c["accel"])
            old_accel = c["accel"]

        if c.SaveEEprom:
            ser.write("w\r\n")
            c.SaveEEprom = False

        if c.home:
            ser.write("H%d\r\n")

            print ('Homing')
            c.home= False
except KeyboardInterrupt:
    pass

finally:
    print ('ATC has been disconnected')
    raise SystemExit
