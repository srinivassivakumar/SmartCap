#include "Wire.h"
int aXr,aYr,aZr,tmr,gXr,gYr,gZr;
float aX,aY,aZ,tm,gX,gY,gZ;

void setup() {
Serial.begin(9600);
Wire.begin();
//Waking up the MPU6050
Wire.beginTransmission(0x68);
Wire.write(0x6B);
Wire.write(0x00);    //Write 0x40 to sleep
Wire.endTransmission(true);
}

void loop() {
//Getting raw readings
Wire.beginTransmission(0x68);
Wire.write(0x3B);
Wire.endTransmission(false);

Wire.requestFrom(0x68, 14);
aXr=Wire.read()<<8 | Wire.read();
aYr=Wire.read()<<8 | Wire.read();
aZr=Wire.read()<<8 | Wire.read();
tmr=Wire.read()<<8 | Wire.read();
gXr=Wire.read()<<8 | Wire.read();
gYr=Wire.read()<<8 | Wire.read();
gZr=Wire.read()<<8 | Wire.read();

//Conversion of Raw Data
aX=((2.0)*aXr)/32768;
aY=((2.0)*aYr)/32768;
aZ=((2.0)*aZr)/32768;

gX=((250.0)*gXr)/32750;
gY=((250.0*gYr))/32750;
gZ=((250.0*gZr))/32750;

Serial.print("aX=");
Serial.print(aX);
Serial.print("  aY=");
Serial.print(aY);

Serial.print("  aZ=");
Serial.print(aZ);

Serial.print("  gX=");
Serial.print(gX);

Serial.print("  gY=");
Serial.print(gY);

Serial.print("  gZ=");
Serial.print(gZ);
Serial.println();

delay(500);
}
