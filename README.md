# ATCduino
Automatic tool changer for Linuxcnc with Arduino UNO
## INTRO
ATCduino ( Automatic tool changer arduino ) is tool changer for 8 stations tools using stepper motor control
The ATC can work as standalone or in conjunction with linuxcnc, commands to the ATC are sent through serial port.
When connected to **Linuxcnc** a remap M6 is essential to make it work
## Commands for Standalone 
through your serial connection to ATCduino send these commands followed by new line:
 + Homing : Send H  to home sensor. 
 + Move   : Send Mxxxx where xxxx is the distance in forward direction, return a message (See **message**).
 + Piston Forward : Send O (not zero).
 + Piston Backward: Send J.
 + Save Paramters value to eeprom : Send W.
 + Recover parameter settings : Send R.
 + Get position: Send '?' without quotes, return position.
 + Get "How am I" : Send '!" witout quotes, return "ATC" this is used in communication with linuxcnc.
 + Get "Firmware version" : Send F, return firmware version.
 + Get state : Send 'Q' return a C struct two 4 byte integers first one is bits see( **bits** )and the second is the current position.
 + Reset position : Send B, no return message will be recieved but you can read postion sending '?'.
#### Message:
 After sending a move command ATCduino will send back a message including the following:
 + IN old position.
 + target position.
  the message is comma separated (old position, Target position).
#### bits:
  +bit 0 Enabled.
  +bit 1 inpostion.
  +bit 2 homed.
  +bit 3 searching.
  +bit 4 piston.
  +bit 5 is running.
  +bits 6-32 (not used). 
  
 ```
 Due to serial communication some glitches may occur if no command is sent, to overcome 
 this glitches a move command must  be always sent to Arduino, to make sure no glitches will happen.
 ```
 
## Installation for Linuxcnc
Copy the following files to your config Directory:
+ ATCduino.hal
+ ATCduino.py
+ ATCduino_gui.hal
+ ATCduinoui.py
+ ATCduino.ui
+ postgui_list.hal
+ nc_subroutines (Whole Directory).
+ python (Whole Directory).

In you ini file add the following lines (make sure the first 5 lines are in **[RS274NGC]** section, other lines doesn't matter
where to pu them

```
SUBROUTINE_PATH = nc_subroutines:python:../../nc_files/remap_lib/common_nc_subs:macros
LOG_LEVEL = 9
FEATURES = 30
ON_ABORT_COMMAND = O <on_abort> call
REMAP=M6   modalgroup=6  prolog=change_prolog   ngc=rack_change  epilog=change_epilog

[CHANGE_POSITION]
X = 10
Y = 100
Z = -50

[ATCPINS]
# This is the pin number which connected to motion.digital-out-xx
##outputs

PISTON = 0
HOME = 1
#Change this pin number to match machine's  spindle digital output number .
LOCK = 2
SAVEEPROM = 3

#inputs

ENABLE = 0
INPOSITION = 1

#Analog output
CMDSTATION = 0

[DWELL]
LOCK_TIME = 1.5
MYSTERY = 2
NEW_TOOL = 1.0
POST_UNLOCK = 0.5
PISTON_TIME_OUT = 2
TURNING_TIME_OUT = 25
[STATIONS]
S1 = 0
S2 = 8384
S3 = 16768
S4 = 25152
S5 = 33536
S6 = 41920
S7 = 50304
S8 = 58688

[HOMING]
OFFSET = 4000

[PARAMETER]
ACCEL = 20000
```
refer to gmoccapy.ini to see how they are arranged.
note we must add ATCduino.hal to HAL section in the ini file
```
HALFILE = ATCduino.hal
# Single file that is executed after the GUI has started.
POSTGUI_HALFILE = postgui_list.hal
```
also note instead of calling postgui.hal we replaced it with **postgui_list.hal** to add extra post gui hal files.

**Important note for tool prepare-tool prepared and and tool change - tool changed loop signals
must be available in you hal file refer to core_sim.hal**

## Usage
As a role of thumb lin linuxcnc when adding a new component always start linuxcnc from a terminal 
```
cd /home/USERNAME/linuxcnc/configs/YOUR_CONFIG
then
linuxcnc YOUR_CONFIG.ini
```
it's easier to debug any problems during startup, you must see during startup a message similar to the following:
``` 
Found ATC (Auto tool changer) and connecting on port /tty/USB0 
```
when linuxcnc exit you will see 
```
ATC has been disconnected
```
after a successful startup you will notice a screen **ATC** you can edit your settings there also for quick calibration, or you can change them directly in the ini file.
### Auto tool change
a normal tool change command like
```
T2M6
```
will do the following:
1. Tool wheel will turn to corresponding pocket (if changed).
2. Piston will extend to receive the tool.
3. Return loaded tool to it's pocket.
4. Disengage tool from spindle.
5. Safety move away from the tool.
6. Retract piston.
7. Turning to the new requested tool pocket.
8. Extend piston.
9. Move spindle to receive position.
10. Lock tool in spindle.
11. Retract piston.
12. Safety move for spindle, tool is ready.
to change order of movement depending on your setup refer to /nc_subroutines/rack_change.ngc for complete usage

### Manual ATC commands.
Take extra measures when using manual commands, these commands used when a certain movement of ATC needed 
you can do it from 2 places 
1. from ATC settings screen.
2. from G-code commands (refer to /nc_subroutines/rack_change.ngc for complete usage)
```
Turning wheel
M68 E(analog output) Q(pocket)
(analog output) refer to ini file section [ATCPINS] to know which analog output motion pin is used
example:
'M68 E0 Q3 =  Turn wheel on output 0 to station 3'
```
```
Piston moves
1. M64 P(piston digital output) set digital output pin on meaning set piston forward.
2. M65 P(piston digital output) set digital output pin off meaning set piston backward.
(piston digital output) refer to ini file section [ATCPINS] to know which digital output motion pin is used

```
```
Homing
Piston moves
1. M64 P(homing digital output) set digital output pin on meaning set piston forward.
(homing digital output) refer to ini file section [ATCPINS] to know which digital output motion pin is used
```





