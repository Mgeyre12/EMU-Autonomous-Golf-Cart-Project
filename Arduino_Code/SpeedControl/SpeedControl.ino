//Closed loop speed control for golf cart. By J. Losee 3/23/25

float duration;
float period;
long refresh = 50;

const int vel_cmd_pin = 9; //PWM output pin used to command the cart speed
const int act_vel_pin = 48; //Input pin used to measure the cart speed
const int drv_enable_pin = 2; //Output pin used to enable the drive motor

double act_vel = 0; //Actual velocity in Hz (1mph = 15.2Hz, 5mph = 76Hz)
double cmd_vel = 0; //Commanded velocity in Hz (0 - 235.3)
double Kp = 0.5;   //Proportional gain
double Ki = 0.1;    //Integral gain
double Kd = 0.5;   //Derivative gain

float last_error = 0;
float error = 0;
float changeError = 0;
float totalError = 0;
float pidTerm = 0;
float pidTerm_scaled = 0; // if the total gain we get is not in the PWM range we scale it down so that it's not bigger than |255|

void setup() {
  
  TCCR2B &= ~ _BV (CS22); // cancel pre-scaler of 64
  TCCR2B |= _BV (CS20);   // no pre-scaler

  Serial.begin(9600);

  pinMode(vel_cmd_pin, OUTPUT);
  pinMode(act_vel_pin, INPUT);
  pinMode(drv_enable_pin, OUTPUT);

  digitalWrite(drv_enable_pin, HIGH);

}

void loop(){

  if (Serial.available()) {
    char input = Serial.read();
    if (input == 'w') { //Increment Kp
        Kp = min(Kp + 0.1, 20);
    }
    else if (input == 's') { //Decrement Kp
        Kp = max(Kp - 0.1, 0);
    }    
    else if (input == 'e') { //Increment Ki
        Ki = min(Ki + 0.01, 20);
    }    
    else if (input == 'd') { //Decrement Ki
        Ki = max(Ki - 0.01, 0);
    }    
    else if (input == 'r') { //Increment Kd
        Kd = min(Kd + 0.1, 20);
    }  
    else if (input == 'f') { //Decrement Kd
        Kd = max(Kd - 0.1, 0);
    } 
    else if (input == 'y') { //Increase the commanded velocity
        cmd_vel = min(cmd_vel + 10, 235);
    }  
    else if (input == 'h') { //Decrease the commanded velocity
        cmd_vel = max(cmd_vel - 10, 0);
    }  
    else if (input == ']') { //Set the commanded velocity to 0
        cmd_vel = 0;
    } 
  }    
  
  PIDcalculation();// find PID value

  analogWrite(vel_cmd_pin, pidTerm_scaled);

  delay(refresh);
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

  Serial.println(",");
  Serial.print("Actual velocity:");
  Serial.print(act_vel);
  Serial.print(",");
  Serial.print("PIDTerm:");
  Serial.print(pidTerm_scaled);
  Serial.print(", Error: ");
  Serial.print(error);
  Serial.print(", ChangeError: ");
  Serial.print(changeError);
  Serial.print(", TotalError: ");
  Serial.print(totalError);
  Serial.print(", Kp: ");
  Serial.print(Kp);
  Serial.print(", Ki: ");
  Serial.print(Ki);
  Serial.print(", Kd: ");
  Serial.print(Kd);

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