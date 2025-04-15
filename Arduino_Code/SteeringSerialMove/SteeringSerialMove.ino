// Define Steering Servo Motor control pins
#define ENABLE_PIN 11    // Enables the motor
#define DIRECTION_PIN 10 // Sets motor direction (left/right)
#define STEP_PIN 8      // Sends step pulses to the motor

void setup() {
  Serial.begin(115200); // Serial communication for commands
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  //digitalWrite(ENABLE_PIN, HIGH); // Enable motor
  Serial.println("Motor Ready. Send 'L<steps>' to turn left. 'R<steps>' to turn right. 'X' to disable via Serial.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read serial input
    command.trim(); // Remove any extra spaces

    if (command.startsWith("L")) {
      int steps = command.substring(2).toInt(); // Extract step count
      Serial.print("Turning Left: "); Serial.println(steps);
      moveMotor(steps, HIGH); // Move Left
    }
    else if (command.startsWith("R")) {
      int steps = command.substring(2).toInt(); // Extract step count
      Serial.print("Turning Right: "); Serial.println(steps);
      moveMotor(steps, LOW); // Move Right
    }
    else if (command == "X") {
      if(!digitalRead(ENABLE_PIN)){
        digitalWrite(ENABLE_PIN, HIGH);
        Serial.println("Steering Servo Enabled");
        delay(100);
      }else{
        digitalWrite(ENABLE_PIN, LOW); // Disable motor
        Serial.println("Steering Servo Disabled");
        delay(100);
      }
    }
    else {
      Serial.println("Invalid Command! Send 'L<steps>' to turn left or 'R<steps>' to turn right or 'X' to toggle enable via Serial.");
    }
  }
}


// Function to move the ClearPath motor
void moveMotor(int steps, bool direction) {
  digitalWrite(ENABLE_PIN, HIGH); // Enable motor
  digitalWrite(DIRECTION_PIN, direction); // Set direction (HIGH = CW, LOW = CCW)

  for (int i = 0; i < steps; i++) {

    if(!digitalRead(ENABLE_PIN)){
    Serial.println("Motor stopped due to torque limit. Restartting....");
    digitalWrite(ENABLE_PIN, HIGH);
    delay(500);
  }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(100); // Adjust pulse timing as needed
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(100);
  }
}
