#include <Servo.h>

// Project 0 — Arduino firmware
// Hardware: Arduino Uno R3, HC-SR04, 5g servo, 3 LEDs, active buzzer

// ---------------- Pins ----------------
const byte PIN_TRIG = 7;
const byte PIN_ECHO = 8;
const byte PIN_SERVO = 9;
const byte PIN_LED_ON = 2;
const byte PIN_LED_PROXIMITY = 3;
const byte PIN_LED_DANGER = 4;
const byte PIN_BUZZER = 5;

// ---------------- Radar configuration ----------------
const int MIN_ANGLE = 0;
const int MAX_ANGLE = 180;
const int ANGLE_STEP = 2;

const float PROXIMITY_CM = 50.0f;
const float DANGER_CM = 20.0f;
const float MAX_DISTANCE_CM = 400.0f;

// Time between measurements. This is deliberately conservative for
// HC-SR04 echo separation and servo movement.
const unsigned long SCAN_INTERVAL_MS = 45;
const unsigned long ECHO_TIMEOUT_US = 23000UL;

// Active buzzer timing.
const unsigned long BUZZER_TOGGLE_MS = 110;

Servo radarServo;

int angle = MIN_ANGLE;
int direction = 1;
unsigned long lastScanMs = 0;
unsigned long lastBuzzerMs = 0;
bool buzzerOn = false;

enum RadarState {
  STATE_CLEAR,
  STATE_PROXIMITY,
  STATE_DANGER
};

RadarState state = STATE_CLEAR;

// ---------------- Setup ----------------
void setup() {
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED_ON, OUTPUT);
  pinMode(PIN_LED_PROXIMITY, OUTPUT);
  pinMode(PIN_LED_DANGER, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  digitalWrite(PIN_TRIG, LOW);
  digitalWrite(PIN_BUZZER, LOW);

  radarServo.attach(PIN_SERVO);
  radarServo.write(90);

  digitalWrite(PIN_LED_ON, HIGH);
  digitalWrite(PIN_LED_PROXIMITY, LOW);
  digitalWrite(PIN_LED_DANGER, LOW);

  Serial.begin(115200);
  Serial.println(F("RADAR,READY,PROJECT_0"));
}

// ---------------- Main loop ----------------
void loop() {
  const unsigned long now = millis();

  updateBuzzer(now);

  if (now - lastScanMs < SCAN_INTERVAL_MS) {
    return;
  }

  lastScanMs = now;

  radarServo.write(angle);

  const float distance = measureDistanceCm();
  state = classifyDistance(distance);
  updateIndicators(state);
  sendMeasurement(angle, distance, state);

  angle += direction * ANGLE_STEP;

  if (angle >= MAX_ANGLE) {
    angle = MAX_ANGLE;
    direction = -1;
  } else if (angle <= MIN_ANGLE) {
    angle = MIN_ANGLE;
    direction = 1;
  }
}

// ---------------- Sensor ----------------
float measureDistanceCm() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);

  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  const unsigned long duration = pulseIn(PIN_ECHO, HIGH, ECHO_TIMEOUT_US);

  if (duration == 0) {
    return -1.0f;
  }

  // HC-SR04 distance ≈ echo time / 58.0 (cm).
  const float distance = duration / 58.0f;

  if (distance <= 0.0f || distance > MAX_DISTANCE_CM) {
    return -1.0f;
  }

  return distance;
}

// ---------------- Classification ----------------
RadarState classifyDistance(float distance) {
  if (distance < 0.0f || distance > MAX_DISTANCE_CM) {
    return STATE_CLEAR;
  }

  if (distance <= DANGER_CM) {
    return STATE_DANGER;
  }

  if (distance <= PROXIMITY_CM) {
    return STATE_PROXIMITY;
  }

  return STATE_CLEAR;
}

const char* stateName(RadarState current) {
  switch (current) {
    case STATE_DANGER: return "DANGER";
    case STATE_PROXIMITY: return "PROXIMITY";
    default: return "CLEAR";
  }
}

// ---------------- Indicators ----------------
void updateIndicators(RadarState current) {
  // LED 1: system is running.
  digitalWrite(PIN_LED_ON, HIGH);

  // LED 2: object is within proximity threshold.
  digitalWrite(PIN_LED_PROXIMITY, current == STATE_PROXIMITY ? HIGH : LOW);

  // LED 3: object is inside danger threshold.
  digitalWrite(PIN_LED_DANGER, current == STATE_DANGER ? HIGH : LOW);
}

// ---------------- Buzzer ----------------
void updateBuzzer(unsigned long now) {
  if (state != STATE_DANGER) {
    buzzerOn = false;
    digitalWrite(PIN_BUZZER, LOW);
    return;
  }

  if (now - lastBuzzerMs >= BUZZER_TOGGLE_MS) {
    lastBuzzerMs = now;
    buzzerOn = !buzzerOn;
    digitalWrite(PIN_BUZZER, buzzerOn ? HIGH : LOW);
  }
}

// ---------------- Serial protocol ----------------
void sendMeasurement(int currentAngle, float distance, RadarState currentState) {
  Serial.print(currentAngle);
  Serial.print(',');

  if (distance < 0.0f) {
    Serial.print(-1);
  } else {
    Serial.print(distance, 1);
  }

  Serial.print(',');
  Serial.println(stateName(currentState));
}
