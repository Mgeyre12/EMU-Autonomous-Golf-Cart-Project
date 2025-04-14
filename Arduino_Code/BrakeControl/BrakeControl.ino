// Define Braking Servo Motor Control Pins
#define ENABLE_PIN 11    // Enables the motor
#define DIRECTION_PIN 10 // Sets motor direction (left/right)
#define STEP_PIN 8      // Sends step pulses to the motor
int brakePos;
int brakeStepLimit;

void setup() {
  Serial.begin(115200); // Serial communication for commands
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  brakePos = 0; //initialize brake position index to zero
  brakeStepLimit = 2000; // maximum steps engaging brake clockwise before torque limit reached

  digitalWrite(ENABLE_PIN, HIGH); // Enable motor
  Serial.println("Brake Servo Ready. Send 'CW<steps>' to turn clockwise, 'CC<steps>' to turn counter-clockwise, 'X' to toggle enable via Serial.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read serial input
    command.trim(); // Remove any extra spaces

    if (command.startsWith("CW")) { //clockwise to engage brake
      int steps = command.substring(3).toInt(); // Extract step count
      if(steps+brakePos <= brakeStepLimit){ //check if commanded steps don't exceed limit
        Serial.print("Brake engaging: "); Serial.println(steps);
        moveMotor(steps, HIGH); // Move clockwise
        brakePos += steps;
      }
      else{ //if commanded steps exceed limit, set to servo limit
        Serial.print("Brake engaging: "); Serial.println(steps);
        moveMotor(brakeStepLimit-brakePos, HIGH); // Move clockwise to limit
        Serial.println("Brake servo limit reached!");
        brakePos = brakeStepLimit;
      }
    }
    else if (command.startsWith("CC")) { //counter-clockwise to disengage brake
      int steps = command.substring(3).toInt(); // Extract step count
      if(brakePos-steps >= 0){ //check if commanded steps don't let servo pass the zero-position
        Serial.print("Brake disengaging "); Serial.println(steps);
        moveMotor(steps, LOW); // Move counterclockwise
        brakePos -= steps;
      }
      else{ //if commanded steps go lower than zero-position, set to servo limit
        Serial.print("Brake disengaging "); Serial.println(steps);
        moveMotor(brakePos, LOW); // Move counterclockwise
        brakePos = 0;
      }
    }

    else if (command == "X") {
        brakePos = 0;
      if(!digitalRead(ENABLE_PIN)){
        digitalWrite(ENABLE_PIN, HIGH);
        Serial.println("Brake Servo Enabled");
        delay(100);
      }else{
        digitalWrite(ENABLE_PIN, LOW); // Disable motor
        Serial.println("Brake Servo Disabled");
        delay(100);
      }
    }
    else {
      Serial.println("Invalid Command! Send 'CW<steps>' to turn clockwise, 'CC<steps>' to turn counter-clockwise, 'X' to toggle enable via Serial.");
    }
  }
}


// Function to move the ClearPath motor
void moveMotor(int steps, bool direction) {
  digitalWrite(ENABLE_PIN, HIGH); // Enable motor
  digitalWrite(DIRECTION_PIN, direction); // Set direction (HIGH = CW, LOW = CC)

  for (int i = 0; i < steps; i++) {
    if(!digitalRead(ENABLE_PIN)){
    Serial.println("Motor stopped due to torque limit. Restarting....");
    digitalWrite(ENABLE_PIN, HIGH);
    delay(500);
    brakePos = 0;
  }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(100); // Adjust pulse timing as needed
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(100);
  }
}