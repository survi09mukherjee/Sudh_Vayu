#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// -------- WiFi --------
const char* ssid = "ESP32HOTSPOT";
const char* password = "12345678";

// -------- Server --------
const char* serverName = "http://10.89.92.20:8000/sensor";

// -------- Pins --------
#define DHTPIN 4
#define DHTTYPE DHT22
#define MQ135_PIN 34
#define BUZZER_PIN 25

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int mq135_value = analogRead(MQ135_PIN);

    // Check if DHT failed
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("DHT read failed!");
      return;
    }

    // 🔊 Simple buzzer logic
    if (mq135_value > 2000) {
      digitalWrite(BUZZER_PIN, HIGH);
    } else {
      digitalWrite(BUZZER_PIN, LOW);
    }

    // 📡 Send HTTP POST
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";
    jsonData += "\"co\":" + String(mq135_value) + ",";
    jsonData += "\"temp\":" + String(temperature) + ",";
    jsonData += "\"humidity\":" + String(humidity);
    jsonData += "}";

    int httpResponseCode = http.POST(jsonData);

    Serial.println("------ DATA SENT ------");
    Serial.print("Temp: "); Serial.println(temperature);
    Serial.print("Humidity: "); Serial.println(humidity);
    Serial.print("MQ135: "); Serial.println(mq135_value);
    Serial.print("Response Code: "); Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(5000); // send every 5 sec
}