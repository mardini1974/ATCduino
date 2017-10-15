import warnings
import serial
import serial.tools.list_ports

def find_arduino():
    for pinfo in serial.tools.list_ports.comports():
        print(pinfo.serial_number)

print serial.tools.list_ports.comports()[0].device