#include <OneWire.h>
#include <DallasTemperature.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <LiquidCrystal_I2C.h>

String serverName = "http://192.168.1.35:5000/adddata";

const char* ssid = "BMKG HOME";
const char* password = "bmkg97012";
const char* server = "api.thingspeak.com";
const char* apiKey = "XOF7EIVKF08IY2T5";
WiFiClient client;

const int oneWireBus = 2;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27,16,2);

void setup() {
  lcd.begin();
  Serial.begin(9600);
  sensors.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print('.');
  }
}

void loop() {
  float tmin = 1000;
  float tmax = 0;
  float tavg = 0;
  float t[60];

  for (int i = 0; i < 60; i++) {
    sensors.requestTemperatures();
    float temperatureC = sensors.getTempCByIndex(0);
    t[i] = temperatureC;
    Serial.print(temperatureC);
    Serial.println("ºC");
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("Suhu:");
    lcd.setCursor(0,1);
    lcd.print(t[i]);
    delay(1000);
    lcd.clear();
  }

  for (int i = 0; i < 60; i++) {
    if (t[i] > tmax) {
      tmax = t[i];
    }
    if (t[i] < tmin) {
      tmin = t[i];
    }
    tavg = tavg + t[i];
  }

  tavg = tavg / 60;

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
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    // Free resources
    http.end();
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("Data sent");
    lcd.clear();
  } else {
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("Data not send");
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
