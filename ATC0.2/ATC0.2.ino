
#include <AccelStepper.h>
#include <EEPROM.h>
#include "libs.h"

// Define a stepper and the pins it will use
AccelStepper stepper(AccelStepper::DRIVER,4,7); // Defaults to AccelStepper::DRIVER Zaxis on ARcduino CNC Shield
#define piston 12
#define homeSensor 11
#define enableRunPin 10
#define stepperEnable 8
#define firmware "0.2"//frimware version

bool homed;
bool homeSearch;
bool pistonCmd;
long target1;
struct parameters{
      float accel;
      long homeOffset;
      long homeSpeed;
      long homeSearchSpeed;
      long commandMaxSpeed;};
struct messages{
  long statusByte;
  //bit 0 Enabled
  //bit 1 inpostion
  //bit 2 homed
  //bit 3 searching
  //bit 4 piston
  //bit 5 
  //bit 6 
  //bit 7 
  long positionCV;
  
} message;
parameters Parameter;

void writetoEEPROM() { // keep PID set values in EEPROM so they are kept when arduino goes off
  EEPROM.put(0,Parameter);
  
  Serial.println("\nPID values stored to EEPROM");
  //Serial.println(cks);
}

void recoverfromEEPROM() {
  
    Serial.println(F("*** Found PID values on EEPROM"));
    EEPROM.get(0,Parameter);
}

void setup()
{
  recoverfromEEPROM() ; 
  stepper.setMaxSpeed(Parameter.commandMaxSpeed);
  stepper.setAcceleration(Parameter.accel);
  stepper.setEnablePin  (stepperEnable);
  stepper.setPinsInverted(false,false,true);
  pinMode(homeSensor,INPUT_PULLUP);  
  pinMode(enableRunPin,INPUT_PULLUP);
  pinMode(piston,OUTPUT);
  pistonCmd = true;
  homed = false;
  homeSearch = false;
  Serial.begin(115200);
}


void serialEvent() {
 while (Serial.available()){
 char cmd = Serial.read();
   long target = 0;
   if(cmd>'Z') cmd-=32;
   switch(cmd) {
    case '?': serial_writeAnything(Parameter);break;
    case 'M': {
      if (digitalRead(enableRunPin) == 0){
        target=Serial.parseInt();
        if (homed) if (0<=target && target<90000)target1 = target ;
        Serial.print(stepper.currentPosition());
        Serial.print(",");
        Serial.println(target1);
        }
        else
        {
        Serial.println("Can't Move");  
        }
        break;
    }
    case 'S': Parameter.commandMaxSpeed=Serial.parseInt(); stepper.setMaxSpeed(Parameter.commandMaxSpeed);break;
    case 'A': Parameter.accel = Serial.parseInt(); stepper.setAcceleration(Parameter.accel);break;
    //case 'H': help(); break;
    case '!': Serial.println ("ATC");break;
    case 'F': Serial.println (firmware);break;
    case 'O': if (stepper.distanceToGo() == 0) pistonCmd = true;Serial.println ("Piston On");break;
    case 'J': pistonCmd = false ;Serial.println ("Piston Off");break;
    case 'H': homed = false;homeSearch = false;
    case 'V': Parameter.homeSpeed=Serial.parseInt();break;
    case 'Z': Parameter.homeSearchSpeed = Serial.parseInt();break;
    case 'T': Parameter.homeOffset =Serial.parseInt();break; 
    case 'W': writetoEEPROM(); break;
    case 'R': recoverfromEEPROM() ; break;
    case 'Q': serial_writeAnything(message);break;
    case 'E': Serial.println(stepper.distanceToGo());break;
    
   }
 }
}


void loop()
{
    if (digitalRead(enableRunPin) == 0) stepper.enableOutputs(); else stepper.disableOutputs(); //Can motor run
    if (pistonCmd) digitalWrite (piston,LOW);else digitalWrite (piston,HIGH); //piston control
    if (!homed & !homeSearch){ //not homed and not searching for home
      stepper.setSpeed(Parameter.homeSearchSpeed);
      stepper.runSpeed();
      if (digitalRead(homeSensor) == 0) 
      {
        
        stepper.setCurrentPosition(0);
        stepper.setSpeed(Parameter.homeSpeed);
        homeSearch = true;
      }}
      if (!homed & homeSearch){ //not homed yet but seraching is started
        stepper.moveTo(Parameter.homeOffset);
        stepper.run();
        if (stepper.distanceToGo() == 0) {homed = true;stepper.setCurrentPosition(0);}
        
        }
      
      if (homed & homeSearch){ //now get the movemnet commands
      // If at the end of travel go to the other end
      if (stepper.distanceToGo() == 0)stepper.moveTo(target1);stepper.run();
        }

      message.statusByte = digitalRead(enableRunPin) <<0;
      message.statusByte |= ((stepper.distanceToGo() == 0)? 1 : 0) <<1;
      message.statusByte |= homed <<2;
      message.statusByte |= homeSearch <<3;
      message.statusByte |= pistonCmd <<4;
      message.positionCV = stepper.currentPosition();
}
