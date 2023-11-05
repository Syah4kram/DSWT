#include <OneWire.h>
#include <DallasTemperature.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <SD.h>
#include "RTClib.h"
#define CSV_PARSER_DONT_IMPORT_SD
#include <CSV_Parser.h>

String serverName = "http://192.168.1.249:5000/adddata";
RTC_DS3231 rtc;

const char* ssid = "BMKG HOME";
const char* password = "bmkg97012";
const char* server = "api.thingspeak.com";
const char* apiKey = "XOF7EIVKF08IY2T5";
WiFiClient client;

const int oneWireBus = 2;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);
const int chipSelect = 15;

void setup() {
  lcd.begin();
  Serial.begin(9600);
  sensors.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print('.');
  }

  //Serial.print("Initializing SD card...");
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    return;
  }
  Serial.println("card initialized.");
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }
  // Adjust waktu
  if (rtc.lostPower()) {
    Serial.println("RTC lost power, let's set the time!");
    // When time needs to be set on a new device, or after a power loss, the
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
}

void loop() {
  float dtmax = -127;
  float dtmin = 100;
  
  DateTime now = rtc.now();
  //SD
  String namefile = "";
  int sd = now.day();
  int sm = now.month();
  if (sd < 10) {
    namefile += String(0) + String(now.day());
  } else {
    namefile += String(now.day());
  }
  if (sm < 10) {
    namefile += String(0) + String(now.month());
  } else {
    namefile += String(now.month());
  }
  namefile += String(now.year());
  namefile += ".csv";
  
  File dataFile = SD.open(namefile);
  // Mengirimkan data ke SD
  if (SD.exists(namefile)) {
    Serial.println("log.csv exists");
  } else {
    dataFile = SD.open(namefile, FILE_WRITE);
    Serial.println("create log.csv");
    dataFile.println("dt,tavg,tmax,tmin");
    dataFile.close();
  }
  dataFile = SD.open(namefile);
  if (dataFile) {
    CSV_Parser cp(/*format*/ "sfff", /*has_header*/ true, /*delimiter*/ ',', /*quote_char*/ "'");
    while (dataFile.available()) {
      cp << (char)dataFile.read();
    }
    dataFile.close();
    Serial.println("Mengambil data dari SD Card...");

    Serial.println("Mengolah data...");
    char** datetime = (char**)cp["dt"];
    float* atavg = (float*)cp["tavg"];
    float* atmax = (float*)cp["tmax"];
    float* atmin = (float*)cp["tmin"];

    int tmaxlen = cp.getRowsCount();
    int tminlen = cp.getRowsCount();

    for (int i = 0; i < tmaxlen; i++) {
      if (dtmax < atmax[i]) {
        dtmax = atmax[i];
      }
    }
    for (int i = 0; i < tminlen; i++) {
      if (dtmin > atmin[i]) {
        dtmin = atmin[i];
      }
    }
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Suhu Max:");
    lcd.setCursor(0, 1);
    lcd.print(dtmax);
    delay(1000);
    lcd.clear();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Suhu Min:");
    lcd.setCursor(0, 1);
    lcd.print(dtmin);
    delay(1000);
    lcd.clear();
    
    Serial.println();
    Serial.print('Tmax: ');
    Serial.print(dtmax);
    Serial.print(', Tmin: ');
    Serial.println(dtmin);
    Serial.println();
  } else {
    Serial.println("error opening log.csv");
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Error opening");
    lcd.setCursor(0, 1);
    lcd.print(namefile);
    delay(500);
    lcd.clear();
  }
  dataFile = SD.open(namefile, FILE_WRITE);

  float tmin = 1000;
  float tmax = 0;
  float tavg = 0;
  float t[60];
  int jml = 0;

  for (int i = 0; i < 60; i++) {
    sensors.requestTemperatures();
    float temperatureC = sensors.getTempCByIndex(0);
    if (t[i] != -127) {
      t[i] = temperatureC;
    } else {
      t[i] = -127;
    }
    Serial.print(temperatureC);
    Serial.println("ºC");
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Suhu:");
    lcd.setCursor(0, 1);
    lcd.print(t[i]);
    delay(1000);
    lcd.clear();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Suhu Max:");
    lcd.setCursor(0, 1);
    lcd.print(dtmax);
    delay(1000);
    lcd.clear();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Suhu Min:");
    lcd.setCursor(0, 1);
    lcd.print(dtmin);
    delay(1000);
    lcd.clear();
  }

  for (int i = 0; i < 60; i++) {
    if (t[i] > -127) {
      if (t[i] > tmax) {
        tmax = t[i];
      }
      if (t[i] < tmin) {
        tmin = t[i];
      }
      tavg = tavg + t[i];
      jml++;
    }
  }

  tavg = tavg / jml;

  // Localhost
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String serverPath = serverName + "?field1=";
    serverPath = serverPath + tavg;
    serverPath = serverPath + "&field2=";
    serverPath = serverPath + tmax;
    serverPath = serverPath + "&field3=";
    serverPath = serverPath + tmin;
    Serial.println(serverPath.c_str());
    http.begin(client, serverPath.c_str());

    int httpResponseCode = http.GET();
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    // Free resources
    http.end();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Data sent");
    lcd.clear();
  } else {
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Data not send");
    delay(500);
    lcd.clear();
  }

  String dataString = "'";
  if (sd < 10) {
    dataString += String(0) + String(now.day());
  } else {
    dataString += String(now.day());
  }
  if (sm < 10) {
    dataString += String(0) + String(now.month());
  } else {
    dataString += String(now.month());
  }
  dataString += String(now.year());
  dataString += "T";
  if (now.hour() < 10) {
    dataString += String(0) + String(now.hour());
  } else {
    dataString += String(now.hour());
  }
  if (now.minute() < 10) {
    dataString += String(0) + String(now.minute());
  } else {
    dataString += String(now.minute());
  }
  if (now.second() < 10) {
    dataString += String(0) + String(now.second());
  } else {
    dataString += String(now.second());
  }
  dataString += "Z',";

  dataString += String(tavg);
  dataString += ",";
  dataString += String(tmax);
  dataString += ",";
  dataString += String(tmin);

  dataFile = SD.open(namefile, FILE_WRITE);
  // Mengirimkan data ke SD
  if (dataFile) {
    dataFile.println(dataString);
    Serial.println(dataString);
    dataFile.close();
  } else {
    Serial.println("error opening log.csv");
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Error opening");
    lcd.setCursor(0, 1);
    lcd.print(namefile);
    delay(500);
    lcd.clear();
  }
  // Thingspeak
  /*
    if (client.connect(server, 80)) {
    String postStr = apiKey;
    postStr += "&field1=";
    postStr += String(tavg);
    postStr += "&field2=";
    postStr += String(tmax);
    postStr += "&field3=";
    postStr += String(tmin);

    client.print("POST /update HTTP/1.1\n");
    client.print("Host: api.thingspeak.com\n");
    client.print("Connection: close\n");
    client.print("X-THINGSPEAKAPIKEY: ");
    client.print(apiKey);
    client.print("\n");
    client.print("Content-Type: application/x-www-form-urlencoded\n");
    client.print("Content-Length: ");
    client.print(postStr.length());
    client.print("\n\n");
    client.print(postStr);

    Serial.println("Data posted to Thingspeak!");
    client.stop();
    } else {
    Serial.println("Failed to connect to Thingspeak");
    }
  */
}
