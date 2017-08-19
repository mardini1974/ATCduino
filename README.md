# ATCduino
Automatic tool changer for Linuxcnc with Arduino UNO
## INTRO
ATCduino ( Automatic tool changer arduino ) is tool changer for 8 stations tools on a geneva wheel controling a pololu dc geared
motor with encoder (64 ppr x 131 reduction) the motor controled in closed position PID loop based on ([misan pid dc servo](https://github.com/misan/dcservo)).

The ATC can work as standalone or in conjuction with linuxcnc, commands to the ATC are sent through serial port.
When connected to **Linuxcnc** a remap M6 is essential to make it work
## Commands for Standalone 
through your serial connection to ATCduino send these commands followed by new line:
 + Homing : Send Mxxxx where xxxx is the distance in forward direction after returning to home sensor. 
 + Move   : Send Xxxxx where xxxx is the distance in forward direction, return a message (See **message**).
 + Piston Forward : Send O (not zero).
 + Piston Backward: Send J.
 + Set PID P : Send Pxxx where xxx the value of proportional gain accept float point.
 + Set PID I : Send Ixxx where xxx the value of Integral gain accept float point.
 + Set PID D : Send Dxxx where xxx the value of Dervative gain accept float point.
 + Get PID settings : Send Q, will return a message with settings (kp,ki,kd)
 + Save PID settings to eeprom : Send W.
 + Recover PID settings : Send R.
 + Clear PIDsettings : Send K.
 + Get position: Send '?' without quotes, return position.
 + Get "How am I" : Send '!" witout quotes, return "ATC" this is used in communication with linuxcnc.
 + Get "Firmware version" : Send F, return firmware version.
 + Get Home sensor state : Send T return 1 = On or 0=off.
 + Reset position : Send B, no return message will be recieved but you can read postion sending '?'.
#### Message
 After sending a move command ATCduino will send back a message including the following:
 + IN position 1 = position reached , or 0 = still moving.
 + Current position.
 + Target position.
 + Enabled 1 = can run, 0 = blocked,(can the motor run connected to piston retract signal).
 
 the message is comma separated (inposition, Currentposition , Target position,  Enabled ).
 
 ```
 Due to serial communication some glitches may occur if no command is sent, to overcome 
 this glitches a move command must  be always sent to arduino, to make sure no glitchs will happen.
 ```
 
## Installation for Linuxcnc
Copy the following files to your config 
