#include "Arduino.h"
template <typename T> unsigned int serial_writeAnything (const T& value)
  {
    const byte * p = (const byte*) &value;
    unsigned int i;
    for (i = 0; i < sizeof value; i++)
          Serial.write(*p++);
    return i;
        
  }  // end of Serial_writeAnything
 

