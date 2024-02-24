#define tempPin A3  //temperature pin is A3

float temp;   //This variable will store the temperature measured by sensor
float vltg;   //This variable will store the voltage at Arduino Pi A3 (Sensor Output)

void setup() {
  Serial.begin(9600);   //Starts the serial monitor
}

void loop() {
  vltg=(analogRead(tempPin)*5.0)/1023;     //This is the voltage at Pin A3 (Sensor Output)
  temp=vltg*100.0;  
       //This is the formula of temperature given in the datasheet
  //analogRead() gives value between 0 to 1023. 0 means 0V, 1023 means 5V
  //to convert this output in volts unit, multiply by 5.0, divide by 1023
  
  //Printing the temperature on the computer
  Serial.print("temp=");
  Serial.println(temp);
  
  delay(500);
}
