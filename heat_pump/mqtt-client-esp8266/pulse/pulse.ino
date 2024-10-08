/*
  Based on
    https://randomnerdtutorials.com/esp8266-nodemcu-mqtt-publish-dht11-dht22-arduino/
*/

// #include "DHT.h"
#include <ESP8266WiFi.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>

#define WIFI_SSID "REPLACE_WITH_YOUR_SSID"
#define WIFI_PASSWORD "REPLACE_WITH_YOUR_PASSWORD"

// Raspberri Pi Mosquitto MQTT Broker
#define MQTT_HOST IPAddress(192, 168, 1, 1)
// For a cloud MQTT broker, type the domain name
//#define MQTT_HOST "example.com"
#define MQTT_PORT 1883

// MQTT Topics
#define MQTT_TOPIC "/home/heat_pump/electric_power_pulse"

// The GPIO pin that the power meter S0 interface is connected to
#define S0_PIN 4 // GPIO4 is labeled D2 on the NodeMCU ESP8266 (see pinput diagrams PDF)

// Digital pin connected to the DHT sensor
// #define DHTPIN 14

// Uncomment whatever DHT sensor type you're using
//#define DHTTYPE DHT11   // DHT 11
// #define DHTTYPE DHT22  // DHT 22  (AM2302), AM2321
//#define DHTTYPE DHT21   // DHT 21 (AM2301)

// Initialize DHT sensor
// DHT dht(DHTPIN, DHTTYPE);

// Variables to hold sensor readings
// float temp;
// float hum;

AsyncMqttClient mqttClient;
Ticker mqttReconnectTimer;

WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;
Ticker wifiReconnectTimer;

unsigned long previousMillis = 0;  // Stores last time temperature was published
const long interval = 5000;       // Interval at which to publish sensor readings
const uint8_t qos = 2;

void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void onWifiConnect(const WiFiEventStationModeGotIP& event) {
  Serial.println("Connected to Wi-Fi.");
  connectToMqtt();
}

void onWifiDisconnect(const WiFiEventStationModeDisconnected& event) {
  Serial.println("Disconnected from Wi-Fi.");
  mqttReconnectTimer.detach();  // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
  wifiReconnectTimer.once(2, connectToWifi);
}

void connectToMqtt() {
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();
}

void onMqttConnect(bool sessionPresent) {
  Serial.println("Connected to MQTT.");
  Serial.print("Session present: ");
  Serial.println(sessionPresent);
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  Serial.printf("Disconnected from MQTT, reason: %s.", reason);

  if (WiFi.isConnected()) {
    mqttReconnectTimer.once(2, connectToMqtt);
  }
}

/*void onMqttSubscribe(uint16_t packetId, uint8_t qos) {
  Serial.println("Subscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
  Serial.print("  qos: ");
  Serial.println(qos);
}

void onMqttUnsubscribe(uint16_t packetId) {
  Serial.println("Unsubscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}*/

void onMqttPublish(uint16_t packetId) {
  Serial.print("Publish acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  // dht.begin();

  wifiConnectHandler = WiFi.onStationModeGotIP(onWifiConnect);
  wifiDisconnectHandler = WiFi.onStationModeDisconnected(onWifiDisconnect);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  //mqttClient.onSubscribe(onMqttSubscribe);
  //mqttClient.onUnsubscribe(onMqttUnsubscribe);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  // If your broker requires authentication (username and password), set them below
  //mqttClient.setCredentials("REPlACE_WITH_YOUR_USER", "REPLACE_WITH_YOUR_PASSWORD");

  connectToWifi();
}

void loop() {
  unsigned long currentMillis = millis();
  // Every X number of seconds (interval = 10 seconds)
  // it publishes a new MQTT message
  if (currentMillis - previousMillis >= interval) {
    // Save the last time a new reading was published
    previousMillis = currentMillis;
    
    // // New DHT sensor readings
    // hum = dht.readHumidity();
    // // Read temperature as Celsius (the default)
    // temp = dht.readTemperature();
    // // Read temperature as Fahrenheit (isFahrenheit = true)
    // //temp = dht.readTemperature(true);

    // // Publish an MQTT message on topic esp/dht/temperature
    // uint16_t packetIdPub1 = mqttClient.publish(MQTT_PUB_TEMP, 1, true, String(temp).c_str());
    // Serial.printf("Publishing on topic %s at QoS 1, packetId: %i ", MQTT_PUB_TEMP, packetIdPub1);
    // Serial.printf("Message: %.2f \n", temp);

    // // Publish an MQTT message on topic esp/dht/humidity
    // uint16_t packetIdPub2 = mqttClient.publish(MQTT_PUB_HUM, 1, true, String(hum).c_str());
    // Serial.printf("Publishing on topic %s at QoS 1, packetId %i: ", MQTT_PUB_HUM, packetIdPub2);
    // Serial.printf("Message: %.2f \n", hum);

    // Basically, use the publish() method on the mqttClient object to publish data on a topic. The publish() method accepts the following arguments, in order:

    // * MQTT topic (const char*)
    // * QoS (uint8_t): quality of service – it can be 0, 1 or 2
    // * retain flag (bool): retain flag
    // * payload (const char*) – in this case, the payload corresponds to the sensor reading

    // The QoS (quality of service) is a way to guarantee that the message is delivered. It can be one of the following levels:

    // 0: the message will be delivered once or not at all. The message is not acknowledged. There is no possibility of duplicated messages;
    // 1: the message will be delivered at least once, but may be delivered more than once;
    // 2: the message is always delivered exactly once;
    // Learn about MQTT QoS: https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.dev.doc/q029090_.htm

    // Publish an MQTT message on topic esp/dht/temperature
    String message = String("{ 'token': 'bfed7b62-980d-46e7-90d5-5cf0fe8179cf', 's0_pin': ");
    message += digitalRead(S0_PIN);
    message += " }";
    uint16_t packetIdPub = mqttClient.publish(MQTT_TOPIC, qos, true, message.c_str());
    Serial.printf("Publishing on topic %s at QoS %i, packetId: %i\n", MQTT_TOPIC, qos, packetIdPub);
    Serial.printf("Message: %s\n", message);
  }
}