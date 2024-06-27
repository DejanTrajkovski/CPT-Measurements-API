#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h> // Include the WebServer library
#include <vector>

// Wi-Fi credentials
const char* ssid = "<Enter the SSID of the WIFI network>";
const char* password = "Enter the PASSWOD of the WIFI network";

// Server URL
const char* serverUrl = "http:/<MEASUEMENTSAPI.PY_IP>/add";


// Encoder definitions and functions
const int CLOCK_PIN = 4; // White Pin
const int DATA_PIN = 18; // Green Pin
const int BIT_COUNT = 12; // 12 Bit Mode  5 to 12 bit mode
const float CALIBRATION_FACTOR = 515.089; // Encoder steps per mm
const int MAX_ENCODER_VALUE = 4096; // Maximum value for 12-bit encoder

int previous_encoder_value = 0;
int total_rotations = 0;

std::vector<int> loads;
std::vector<float> positions;

int measurement_interval = 5;

WebServer server(80); // Create an instance of the WebServer on port 80

unsigned long shiftIn(const int data_pin, const int clock_pin, const int bit_count) {
  unsigned long data = 0;
  digitalWrite(clock_pin, HIGH); // Always set to high before reading
  
  for (int i = 0; i < bit_count; i++) {
    data <<= 1;
    digitalWrite(clock_pin, LOW);
    delayMicroseconds(1);
    digitalWrite(clock_pin, HIGH);
    delayMicroseconds(1);
    data |= digitalRead(data_pin);
  }
  return data;
}

float readPosition() {
  unsigned long sample1 = shiftIn(DATA_PIN, CLOCK_PIN, BIT_COUNT);
  delayMicroseconds(20); // Clock must be high for 20 microseconds before a new sample can be taken
  return (sample1 & 0x0FFF);
}

float calculatePositionInMM(float encoder_value) {
  // Check for encoder wraparound
  if (encoder_value < (0.1 * MAX_ENCODER_VALUE) && previous_encoder_value > (0.9 * MAX_ENCODER_VALUE)) {
    total_rotations++;
  } else if (encoder_value > (0.9 * MAX_ENCODER_VALUE) && previous_encoder_value < (0.1 * MAX_ENCODER_VALUE)) {
    total_rotations--;
  }

  previous_encoder_value = encoder_value;

  // Calculate the total position in encoder steps
  float total_encoder_steps = (total_rotations * MAX_ENCODER_VALUE) + encoder_value;

  // Convert encoder steps to mm
  return total_encoder_steps / CALIBRATION_FACTOR;
}

// Stepper motor and load cell definitions and functions
#define dirPIN 33               // Pin that sets motor direction
#define stepPIN 32              // Pin that turns motor for one step
#define stepsPerRevolution 1600 // Number of motor steps per revolution

int endSwitchPIN = 23;          // Pin that reads end switch state
int sleepPIN = 22;              // Pin that enables stepper motor
int forceSensorPIN = 34;        // Pin that reads force sensor

int endswitchState = 0;
int forceSensorValue = 0;
int step_delay = 1000; // Delay for motor speed control

const int mm_per_revolution = 5;  // Movement per revolution in mm
const int steps_per_mm = stepsPerRevolution / mm_per_revolution; // Steps per mm


void sendDataToServer(const std::vector<int>& loads, const std::vector<float>& positions) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"loads\": [";
    for (size_t i = 0; i < loads.size(); i++) {
      jsonPayload += String(loads[i]);
      if (i < loads.size() - 1) {
        jsonPayload += ",";
      }
    }
    jsonPayload += "], \"positions\": [";
    for (size_t i = 0; i < positions.size(); i++) {
      jsonPayload += String(positions[i], 2);
      if (i < positions.size() - 1) {
        jsonPayload += ",";
      }
    }
    jsonPayload += "]}";

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Wi-Fi not connected");
  }
}

void return_to_zero() {
  Serial.println("RETURN penetrometer to TOP position");

  endswitchState = digitalRead(endSwitchPIN);
  Serial.println(endswitchState);

  digitalWrite(dirPIN, HIGH);

  while (endswitchState == 1) {
    digitalWrite(stepPIN, HIGH);
    delayMicroseconds(step_delay / 4);
    digitalWrite(stepPIN, LOW);
    delayMicroseconds(step_delay / 4);
    endswitchState = digitalRead(endSwitchPIN);
  }
  total_rotations = 0;
  previous_encoder_value = 0; // Reset encoder value
  Serial.println("Penetrometer is in TOP position");
}

void move_stepper(bool direction, int steps) {
  digitalWrite(dirPIN, direction);
  
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPIN, HIGH);
    delayMicroseconds(step_delay); // Half of the interval
    digitalWrite(stepPIN, LOW);
    delayMicroseconds(step_delay); // Half of the interval

    forceSensorValue = analogRead(forceSensorPIN);
    float encoder_value = readPosition();
    float position_mm = calculatePositionInMM(encoder_value);
  }
}

void move_stepper_measurement(bool direction, int steps) {
  digitalWrite(dirPIN, direction);
  float current_position_mm = 0.0;
  int measurement_counter = 0; // Counter to track every 100th measurement

  while (current_position_mm > -95.3) {
    for (int i = 0; i < steps; i++) {
      digitalWrite(stepPIN, HIGH);
      delayMicroseconds(step_delay); // Half of the interval
      digitalWrite(stepPIN, LOW);
      delayMicroseconds(step_delay); // Half of the interval
      float encoder_value = readPosition();
      float position_mm = calculatePositionInMM(encoder_value);

      // Only append every 100th measurement
      if (measurement_counter % measurement_interval == 0) {
        forceSensorValue = analogRead(forceSensorPIN);
        loads.push_back(forceSensorValue);
        positions.push_back(position_mm);
      }
      measurement_counter++;

      Serial.print("Position (mm): ");
      Serial.println(position_mm);
      current_position_mm = position_mm;
    }
  }

  sendDataToServer(loads, positions);
  loads.clear();
  positions.clear();
  Serial.println("Data sent to server");

}

void return_to_zero_and_measure() {
  Serial.println("Return penetrometer to top position");
  
  float current_position_mm = 0.0;
  int measurement_counter = 0;
  endswitchState = digitalRead(endSwitchPIN);
  Serial.println(endswitchState);

  digitalWrite(dirPIN, HIGH);

  while (endswitchState == 1) {
    digitalWrite(stepPIN, HIGH);
    delayMicroseconds(step_delay);
    digitalWrite(stepPIN, LOW);
    delayMicroseconds(step_delay);
    endswitchState = digitalRead(endSwitchPIN);
    
    float encoder_value = readPosition();
    float position_mm = calculatePositionInMM(encoder_value);

    if (measurement_counter % measurement_interval == 0) {
        forceSensorValue = analogRead(forceSensorPIN);
        loads.push_back(forceSensorValue);
        positions.push_back(position_mm);
      }
      measurement_counter++;

      Serial.print("Position (mm): ");
      Serial.println(position_mm);
      current_position_mm = position_mm;
  }

  total_rotations = 0;
  previous_encoder_value = 0; // Reset encoder value
  Serial.println("Penetrometer is in TOP position");

  // Send the collected data to the server
  sendDataToServer(loads, positions);
  loads.clear();
  positions.clear();
  Serial.println("Data sent to server");
}

void make_measurement() {
  // Perform the measurement procedure
  Serial.println("Starting measurement");
  return_to_zero_and_measure();
  move_stepper_measurement(false, steps_per_mm);
  return_to_zero();
    //return_to_zero_and_measure();

}

void move_up() {
  move_stepper(HIGH, steps_per_mm * 5);
}

void move_down(){
  move_stepper(LOW, steps_per_mm * 5);
}


void setup() {
  Serial.begin(115200); // Match the baud rate to the encoder code
  pinMode(DATA_PIN, INPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  digitalWrite(CLOCK_PIN, HIGH);

  pinMode(dirPIN, OUTPUT); // HIGH move up, LOW move down
  pinMode(stepPIN, OUTPUT);

  pinMode(endSwitchPIN, INPUT);
  pinMode(sleepPIN, OUTPUT);
  pinMode(forceSensorPIN, INPUT);

  digitalWrite(sleepPIN, HIGH);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Define routes
  server.on("/triggerMeasurement", HTTP_POST, []() {
    server.send(200, "text/plain", "Measurement triggered");
    make_measurement(); // Call the function to make a measurement
  });

  server.on("/moveUp", HTTP_POST, []() {
    server.send(200, "text/plain", "Move down by 5mm");
    move_up(); // Call the function to make a measurement
  });

  server.on("/moveDown", HTTP_POST, []() {
    server.send(200, "text/plain", "Move up by 5mm");
    move_down(); // Call the function to make a measurement
  });

  server.on("/returnToZero", HTTP_POST, []() {
    server.send(200, "text/plain", "Move up by 5mm");
    return_to_zero(); // Call the function to make a measurement
  });


  // Start server
  server.begin();
}

void loop() {
  server.handleClient(); // Handle incoming client requests
}
