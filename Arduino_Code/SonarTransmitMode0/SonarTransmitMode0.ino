#define ECHOPIN 7// Pin to receive echo pulse
#define TRIGPIN 8// Pin to send trigger pulse
int distance;
void setup(){
  Serial.begin(115200);
  pinMode(ECHOPIN, INPUT);
  pinMode(TRIGPIN, OUTPUT);
  //digitalWrite(ECHOPIN, HIGH);

}
void loop(){
  digitalWrite(TRIGPIN, LOW); // Set the trigger pin to low for 2uS
  delayMicroseconds(2);
  digitalWrite(TRIGPIN, HIGH); // Send a 10uS high to trigger ranging
  delayMicroseconds(20);
  digitalWrite(TRIGPIN, LOW); // Send pin low again
  distance = pulseIn(ECHOPIN, HIGH)/58; // Read in times pulse
  //Serial.println(distance);
  Serial.print(distance);
  Serial.println(" cm");                   
  delay(50);// Wait 50mS before next ranging
}