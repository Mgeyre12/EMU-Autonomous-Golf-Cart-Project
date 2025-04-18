//Light control and battery level monitoring for golf cart. By J. Losee 3/20/25

const int batt_monitoring_pin = 0;
float batt_level;
float batt_percent;

void setup() {
  
  Serial.begin(115200);

  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(batt_monitoring_pin, INPUT);

}

void loop() {

  if (Serial.available()) {
      char input = Serial.read();
      if (input == '7') {       //headlights
        digitalWrite(7, HIGH);
      }
      else if (input == '8') {  //right brake
        digitalWrite(8, HIGH);
      }    
      else if (input == '9') {  //right turn
        digitalWrite(9, HIGH);
      }    
      else if (input == 'g') {  //left brake
        digitalWrite(10, HIGH);
      }    
      else if (input == 'h') {  //left turn
        digitalWrite(11, HIGH);
      }  
      else if (input == 'w') {  //right brake
        digitalWrite(7, LOW);
      }    
      else if (input == 'e') {  //right turn
        digitalWrite(8, LOW);
      }    
      else if (input == 'r') {  //left brake
        digitalWrite(9, LOW);
      }    
      else if (input == 't') {  //left turn
        digitalWrite(10, LOW);
      } 
      else if (input == 'y') {  //left turn`
        digitalWrite(11, LOW);
      } 
    } 

  batt_level = analogRead(batt_monitoring_pin);
  batt_level = batt_level;

  if(batt_level<872){
    batt_percent = (0.105*batt_level)-73.22;
    batt_percent = constrain(batt_percent, 0, 255);
  }
  else if(batt_level>872&&batt_level<904.1){
    batt_percent = (1.923*batt_level)-1658.65;
  }
  else if(batt_level>904.1){
    batt_percent = (0.909*batt_level)-742.73;
    batt_percent = constrain(batt_percent, 0, 100);
  }

  Serial.print("Battery level: ");
  Serial.println(batt_percent);

  delay(1000);

}
