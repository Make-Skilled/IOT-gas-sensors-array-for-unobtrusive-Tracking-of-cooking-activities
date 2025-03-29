#include <WiFi.h>
#include <Wire.h>
#include <Keypad.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <ThingSpeak.h>
#include <BlynkSimpleEsp32.h>

Servo myservo;

// Blynk authentication token
#define BLYNK_TEMPLATE_ID "TMPL3_qqGLGXK"
#define BLYNK_TEMPLATE_NAME "Gas Monitoring"
#define BLYNK_AUTH_TOKEN "YourBlynkAuthToken"

const char* ssid = "Redmi 9 Prime";
const char* password = "rajii@0707";

int channelid = 2854419;
const char* apikey = "026A5KCSE7KEEZON";

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Assuming a 16x2 LCD with I2C address 0x27
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Adjust address if needed (0x27 or 0x3F common)

const int gas = 34;  // Use const for pin definitions
const int servoPin = 4;  // Servo pin

const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte rowPins[ROWS] = {23, 26, 25, 19};   
byte colPins[COLS] = {18, 5, 17, 16};    

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

const String password = "DCBA";
String inputPassword = "";

WiFiClient client;

// Blynk virtual pin handler for servo control
BLYNK_WRITE(V1) {
  int value = param.asInt();
  if (value == 1) {
    // Turn motor on - rotate to 180 degrees
    myservo.write(180);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Motor: ON");
    lcd.setCursor(0, 1);
    lcd.print("Angle: 180");
  } else {
    // Turn motor off - rotate back to 0 degrees
    myservo.write(0);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Motor: OFF");
    lcd.setCursor(0, 1);
    lcd.print("Angle: 0");
  }
}

// Function to connect to WiFi
void connectWiFi() {
  WiFi.begin(ssid, password);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    lcd.setCursor(0, 1);
    lcd.print(".");
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");
  delay(1000);
}

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize servo
  ESP32PWM::allocateTimer(0);
  myservo.setPeriodHertz(50);    // Standard 50 hz servo
  myservo.attach(servoPin, 500, 2400); // attaches the servo on pin 4 to the servo object
  myservo.write(0);  // Initialize position to 0 degrees
  
  // Initialize pins
  pinMode(gas, INPUT);
  
  // Initialize sensors and LCD
  sensors.begin();
  lcd.init();
  lcd.backlight();
  
  // Connect to WiFi
  connectWiFi();
  
  // Initialize Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);
  
  // Initialize ThingSpeak
  ThingSpeak.begin(client);
  
  // Initial display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp & Gas Demo");
  lcd.setCursor(0, 1);
  lcd.print("Enter Password");
  delay(2000);
}

void loop() {
  Blynk.run();  // Handle Blynk communications
  
  // Read sensors
  int gasValue = analogRead(gas);
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  
  // Update ThingSpeak
  ThingSpeak.setField(1, tempC);
  ThingSpeak.setField(2, gasValue);
  ThingSpeak.writeFields(channelid, apikey);
  
  // Send sensor values to Blynk
  Blynk.virtualWrite(V2, tempC);    // Temperature on V2
  Blynk.virtualWrite(V3, gasValue); // Gas value on V3

  // Only update display if no keypad input is being processed
  if (inputPassword.length() == 0) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:");
    if (tempC != DEVICE_DISCONNECTED_C) {
      lcd.print(tempC, 1);
      lcd.print("C");
    } else {
      lcd.print("Err");
    }
    
    lcd.setCursor(8, 0);
    lcd.print("G:");
    lcd.print(gasValue);
    
    lcd.setCursor(0, 1);
    lcd.print("Enter Password");
  }

  // Handle keypad input
  char key = keypad.getKey();
  if (key) {
    lcd.clear();
    lcd.setCursor(0, 0);
    
    if (key == '*') {
      inputPassword = "";
      lcd.print("Input Cleared");
      delay(1000);
    } 
    else if (key == '#') {
      if (inputPassword == password) {
        myservo.write(90);
        lcd.print("Password Correct");
        Serial.println("Keypad correct");
      } else {
        lcd.print("Password Wrong");
        Serial.println("Keypad incorrect");
      }
      inputPassword = "";
      delay(1000);
    } 
    else {
      inputPassword += key;
      lcd.print("Entered: ");
      lcd.print(inputPassword);
      Serial.print("Entered: ");
      Serial.println(inputPassword);
    }
  }
  
  delay(100);  // Small delay for stability
 }