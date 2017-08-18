'''
    HAL spinbutton
    demo for Gtk bug workaround
    see Gladevcp Manual Section FAQ item 6
'''
import linuxcnc
import os, gtk
import hal
import hal_glib
import cfgparse


class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        global builder1

        self.builder = builder
        builder1 = builder
        inifile = linuxcnc.ini(os.getenv("INI_FILE_NAME"))
        for i in range(1, 9):
            self.spin = self.builder.get_object("hal_spinbutton%d" % i)
            self.spin.set_value(int(inifile.find("STATIONS", "S%d" % i) or 0))
        self.spin = self.builder.get_object("hal_spinbutton9")
        self.spin.set_value(float(inifile.find("PID", "ATCP") or 0))
        self.spin = self.builder.get_object("hal_spinbutton10")
        self.spin.set_value(float(inifile.find("PID", "ATCI") or 0))
        self.spin = self.builder.get_object("hal_spinbutton11")
        self.spin.set_value(float(inifile.find("PID", "ATCD") or 0))
        self.spin = self.builder.get_object("hal_spinbutton12")
        self.spin.set_value(int(inifile.find("HOMING", "OFFSET") or 0))

    def Save(self, widget, data=None):

        global builder1
        # inifile = linuxcnc.ini(os.getenv("INI_FILE_NAME"))
        inifile = os.getenv("INI_FILE_NAME")
        c = cfgparse.ConfigParser()
        f = c.add_file(inifile)
        self.builder = builder1
        for i in range(1, 9):
            r = c.add_option('S%d' % i, type='int', keys='STATIONS')
            self.spin = self.builder.get_object("hal_spinbutton%d" % i)
            r.set(int(self.spin.get_value()), f)
        r = c.add_option('ATCP', type='float', keys='PID')
        self.spin = self.builder.get_object("hal_spinbutton9")
        r.set(float(self.spin.get_value()), f)
        r = c.add_option('ATCI', type='float', keys='PID')
        self.spin = self.builder.get_object("hal_spinbutton10")
        r.set(float(self.spin.get_value()), f)
        r = c.add_option('ATCD', type='float', keys='PID')
        self.spin = self.builder.get_object("hal_spinbutton11")
        r.set(float(self.spin.get_value()), f)
        r = c.add_option('OFFSET', type='int', keys='HOMING')
        self.spin = self.builder.get_object("hal_spinbutton12")
        r.set(int(self.spin.get_value()), f)

        f.write(inifile)

    def on_SaveEEprom_clicked(self, widget):
        print "Saving to EEprom \n!!!Make sure to use it sparingly to preserve EEprom health\r\n "

    def on_Homing_clicked(self, widget):
        print "ATC cmd: Manual Homing"
        c = linuxcnc.command()
        c.set_digital_output(1, 1)

    def on_hal_ATC_piston_clicked(self, widget):
        print "ATC cmd: Manual Piston On"
        c = linuxcnc.command()
        c.set_digital_output(0, 1)


    def on_Piston_off_clicked(self, widget):
        print "ATC cmd: Manual Piston Off"
        c = linuxcnc.command()
        c.set_digital_output(0, 0)


def get_handlers(halcomp, builder, useropts):
    builder1 = None
    return [HandlerClass(halcomp, builder, useropts)]


