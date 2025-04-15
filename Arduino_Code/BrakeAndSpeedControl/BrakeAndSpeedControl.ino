// Define Braking Servo Motor Control Pins
#define BRAKE_ENABLE_PIN 11    // Enables the motor
#define DIRECTION_PIN 10 // Sets motor direction (left/right)
#define STEP_PIN 8      // Sends step pulses to the motor
int brakePos;
int brakeStepLimit;

float duration;
float period;
int refresh = 10;

const int vel_cmd_pin = 9; //PWM output pin used to command the cart speed
const int act_vel_pin = 48; //Input pin used to measure the cart speed
const int drv_enable_pin = 2; //Output pin used to enable the drive motor

double act_vel = 0; //Actual velocity in Hz (1mph = 15.2Hz, 5mph = 76Hz)
int cmd_vel = 0; //Commanded velocity in Hz (0 - 235)
int vel_cmd_limit;
double Kp = 0.5;   //Proportional gain
double Ki = 0.1;   //Integral gain
double Kd = 0.5;   //Derivative gain

float last_error = 0;
float error = 0;
float changeError = 0;
float totalError = 0;
float pidTerm = 0;
float pidTerm_scaled = 0; // if the total gain we get is not in the PWM range we scale it down so that it's not bigger than |255|

void setup() {
  Serial.begin(115200); // Serial communication for commands
  pinMode(BRAKE_ENABLE_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(vel_cmd_pin, OUTPUT);
  pinMode(act_vel_pin, INPUT);
  pinMode(drv_enable_pin, OUTPUT);

  //increase PWM frequency for speed command
  TCCR2B &= ~ _BV (CS22); // cancel pre-scaler of 64
  TCCR2B |= _BV (CS20);   // no pre-scaler

  digitalWrite(drv_enable_pin, HIGH); //enable accelerator switch

  brakePos = 0; //initialize brake position index to zero
  brakeStepLimit = 2000; // maximum steps engaging brake clockwise before torque limit reached
  vel_cmd_limit = 235;

  //digitalWrite(BRAKE_ENABLE_PIN, HIGH); // Enable motor
  Serial.println("Brake Servo Ready. Send 'CW<steps>' to turn clockwise, 'CC<steps>' to turn counter-clockwise, 'X' to toggle enable via Serial.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read serial input
    command.trim(); // Remove any extra spaces

    if (command.startsWith("CW")) { //clockwise to engage brake
      int steps = command.substring(3).toInt(); // Extract step count
      cmd_vel = 0; // set speed command to zero
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
      if(!digitalRead(BRAKE_ENABLE_PIN)){
        digitalWrite(BRAKE_ENABLE_PIN, HIGH);
        Serial.println("Brake Servo Enabled");
        delay(100);
      }else{
        digitalWrite(BRAKE_ENABLE_PIN, LOW); // Disable motor
        Serial.println("Brake Servo Disabled");
        delay(100);
      }
    }
    else if (command.startsWith("S")) { //command speed
      if(cmd_vel > 0 && cmd_vel <= 235){ //check if commanded speed is valid
        digitalWrite(BRAKE_ENABLE_PIN, LOW); //disable brake
        cmd_vel = command.substring(1).toInt(); // Extract and set speed command
      }
      else{ 
        cmd_vel = 0;
        Serial.println("Speed command invalid");
      }
    }
    else {
      Serial.println("Invalid Command!");
    }
  }
  PIDcalculation();// find PID value
  analogWrite(vel_cmd_pin, pidTerm_scaled);
  delay(refresh);
}


// Function to move the ClearPath motor
void moveMotor(int steps, bool direction) {
  digitalWrite(BRAKE_ENABLE_PIN, HIGH); // Enable motor
  digitalWrite(DIRECTION_PIN, direction); // Set direction (HIGH = CW, LOW = CC)

  for (int i = 0; i < steps; i++) {
    if(!digitalRead(BRAKE_ENABLE_PIN)){
    Serial.println("Motor stopped due to torque limit. Restarting....");
    digitalWrite(BRAKE_ENABLE_PIN, HIGH);
    delay(5);
    brakePos = 0;
  }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(100); // Adjust pulse timing as needed
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(100);
  }
}

void PIDcalculation(){
  duration = pulseIn(act_vel_pin, LOW); //stores duration of a HIGH to LOW pulse in microseconds
  period = (duration * 2.0)/1000000.0; //calculate period in seconds assuming 50% duty cycle
  if(period!=0){ //if statement to avoid dividing by zero
    act_vel = (1/period); //calcultate frequency from period
  }
  else{
    act_vel = 0;
  }
  // Serial.println(",");
  // Serial.print("Actual velocity:");
  // Serial.print(act_vel);
  // Serial.print(",");
  // Serial.print("PIDTerm:");
  // Serial.print(pidTerm_scaled);
  // Serial.print(", Error: ");
  // Serial.print(error);
  // Serial.print(", ChangeError: ");
  // Serial.print(changeError);
  // Serial.print(", TotalError: ");
  // Serial.print(totalError);
  // Serial.print(", Kp: ");
  // Serial.print(Kp);
  // Serial.print(", Ki: ");
  // Serial.print(Ki);
  // Serial.print(", Kd: ");
  // Serial.print(Kd);
  error = cmd_vel - act_vel;
  changeError = error - last_error; // derivative term
  totalError += error; //accumalate errors to find integral term
  pidTerm = (Kp * error) + (Ki * totalError) + (Kd * changeError);//total gain
  if(cmd_vel==0){ //Set the output to 0 if the commanded velocity is 0
    error = 0;
    totalError = 0;
    changeError = 0;
    pidTerm_scaled = 0;
  }

  last_error = error;
}