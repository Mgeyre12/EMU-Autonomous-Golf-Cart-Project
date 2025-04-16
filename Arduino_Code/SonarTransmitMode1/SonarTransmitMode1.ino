#include <SoftwareSerial.h>
unsigned char buffer_RTT[4] = {0};// Used to store data read from the serial port
int Distance = 0;//Used to store the read distance value
unsigned char CS;//Save checksum
SoftwareSerial mySerial(0, 1); //  RX, TX   Echo=7, Trig=8  origanal RX=7, TX=8  so  Echo=0 is after 1, Trig=1 

void setup() {
  Serial.begin(115200); // microcontroller to computer
  mySerial.begin(9600); // sonar to microcontroller 
}

void loop() {
  if(mySerial.available() > 0){
    delay(4);

    if(mySerial.read() == 0xff){    //Judge packet header
      buffer_RTT[0] = 0xff;
      for (int i=1; i<4; i++){
        buffer_RTT[i] = mySerial.read();    //Read data
      }
      CS = buffer_RTT[0] + buffer_RTT[1]+ buffer_RTT[2];  //Compute checksum
      if(buffer_RTT[3] == CS) {
        Distance = (buffer_RTT[1] << 8) + buffer_RTT[2];//Calculate distance
        Serial.println(Distance);
        
      // if (Distance < 1542) {  // suppose to be around 5ft which would be approx. 1524mm
      //   Serial.println("A"); // Stop
      // }
      // else if ((1542 <= Distance) && (Distance <= 4580)) {  // suppose to be between 5ft and 15ft which would be approx. 1524mm to 4572mm 
      //   Serial.println("B"); // Slow down
      // }
      // else {
      //   Serial.println("C"); // Continue 
      // }
    }
  }
}
}