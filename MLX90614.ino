#include<Wire.h>
int16_t tempAr;
int16_t tempTr;
float tempA, tempT;

void setup() {
Serial.begin(9600);
Wire.begin();
}

void loop() {
Wire.beginTransmission(0x5A);
Wire.write(0x06);
Wire.endTransmission(false);

Wire.requestFrom(0x5A,3);
tempAr=Wire.read();                  //Ambient Temperature
tempTr=Wire.read()<<8 | Wire.read(); //Target Temperature

//Raw data has been retrieved!

//Now to convert data according to the datasheet
//tempA=(tempAr/50.0)-273.15;
//tempT=(tempTr/50.0)-273.15;

//Printing the final values!

Serial.print("tempA = ");
Serial.print(tempAr);
Serial.print("       tempT = ");
Serial.println(tempTr);
delay(500);
}
