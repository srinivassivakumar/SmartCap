#define echoPin 2    //Pin 2 will be used for echo pin of sensor
#define trigPin 3    //Pin 3 will be used for trig pin of sensor

long duration;      //This variable will store pulse length at echo pin
float dist;       //This variable will store the calculated distance

void setup() {
  pinMode(trigPin,OUTPUT); //Declaring trig (Pin 3) as Output
  pinMode(echoPin,INPUT);  //Declaring echo (Pin 2) as Input
  Serial.begin(9600);   //Starts tha serial monitor
}

void loop() {
  //Clearing any data on the Sensor
  digitalWrite(trigPin,LOW); //Making trig (Pin 3) Low
  delayMicroseconds(2);   //Waiting 2 microseconds
  
  //Preparing to send the sound waves
  digitalWrite(trigPin, HIGH); //Making trig (Pin 3) High
  delayMicroseconds(10);    //Waiting 10 microseconds (more than 10 will also work)
  digitalWrite(trigPin,LOW);   //Making trig (Pin 3) LOW
  //This triggers the sensor and it starts sending a pattern of sound (8 small pulses)
  //As soon as the whole pattern is emitted, the Sensors sets the echo (Pin 2) HIGH

  //When the pattern of sound is successfully recieved at the reciever,
  //the Sensor makes Echo (Pin 2) Low 
  //To measure time taken by sound, we need to measure time for which echo (Pin 2) was HIGH
  duration=pulseIn(echoPin,HIGH); //This measures time for which echo(Pin 2) was HIGH in microseconds
  dist=duration*0.034/2;       //This gives distance in cm
  Serial.print("distance=");
  Serial.println(dist);      //Printing the value
  delay(500);
}
