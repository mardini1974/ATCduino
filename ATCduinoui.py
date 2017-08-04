'''
    HAL spinbutton
    demo for Gtk bug workaround
    see Gladevcp Manual Section FAQ item 6
'''
import linuxcnc
import os
import hal
import hal_glib


class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.builder = builder
        inifile = linuxcnc.ini(os.getenv("INI_FILE_NAME"))
        for i in range(1,9):
            self.spin = self.builder.get_object("hal_spinbutton%d" %i)
            self.spin.set_value(int(inifile.find("STATIONS","S%d"%i)or 0))
    def Save(self,halcomp,builder,useropts):
        self.builder = builder
        inifile = linuxcnc.ini(os.getenv("INI_FILE_NAME"))
        linuxcnc.ini()
def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
