#include <WiFi.h>
#include <Wire.h>
#include <Keypad.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <ThingSpeak.h>

Servo myservo;

const char* ssid = "Redmi 9 Prime";
const char* password= "rajii@0707";

int channelid=2854419;
const char* apikey= "026A5KCSE7KEEZON";

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Assuming a 16x2 LCD with I2C address 0x27
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Adjust address if needed (0x27 or 0x3F common)

const int gas = 34;  // Use const for pin definitions

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

void setup() {
  WiFi.begin(ssid, password);
  pinMode(gas, INPUT);
  Serial.begin(9600);
  myservo.attach(4);
  myservo.write(0);
    
  // Initialize sensors and LCD
  sensors.begin();
  lcd.init();
  lcd.backlight();
  
  // Initial display
  lcd.setCursor(0, 0);
  lcd.print("Temp & Gas Demo");
  lcd.setCursor(0, 1);
  lcd.print("Enter Password");
  delay(2000);  // Show initial message for 2 seconds
  ThingSpeak.begin(client);
}

void loop() {
  // Read sensors
  int gasValue = analogRead(gas);
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  
  ThingSpeak.setField(1, tempC);
  ThingSpeak.setField(2, gasValue);
  
  ThingSpeak.writeFields(channelid, apikey);

  // Only update display if no keypad input is being processed
  if (inputPassword.length() == 0) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:");
    if (tempC != DEVICE_DISCONNECTED_C) {
      lcd.print(tempC, 1);  // Display with 1 decimal place
      lcd.print("C");
    } else {
      lcd.print("Err");
    }
    
    lcd.setCursor(8, 0);  // Move to right side of first line
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