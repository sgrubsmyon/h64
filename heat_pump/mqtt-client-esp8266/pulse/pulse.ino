/*
  Based on
    https://randomnerdtutorials.com/esp8266-nodemcu-mqtt-publish-dht11-dht22-arduino/
*/

// #include "DHT.h"
#include <ESP8266WiFi.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>
#include "time.h"

#define WIFI_SSID "REPLACE_WITH_YOUR_SSID"
#define WIFI_PASSWORD "REPLACE_WITH_YOUR_PASSWORD"

// Raspberri Pi Mosquitto MQTT Broker
#define MQTT_HOST IPAddress(192, 168, 1, 1)
// For a cloud MQTT broker, type the domain name
//#define MQTT_HOST "example.com"
#define MQTT_PORT 1883

// MQTT Topics
#define MQTT_TOPIC "/home/heat_pump/electric_power_pulse"
#define MQTT_TOKEN "bfed7b62-980d-46e7-90d5-5cf0fe8179cf"

// The GPIO pin that the power meter S0 interface is connected to
#define S0_PIN 4 // GPIO4 is labeled D2 on the NodeMCU ESP8266 (see pinput diagrams PDF)

// Time server (see https://microcontrollerslab.com/current-date-time-esp8266-nodemcu-ntp-server/)
#define NTP_SERVER "pool.ntp.org" // default, https://www.ntppool.org/zone/de: "In most cases it's best to use pool.ntp.org to find an NTP server (or 0.pool.ntp.org, 1.pool.ntp.org, etc if you need multiple server names). The system will try finding the closest available servers for you."
// #define NTP_SERVER "de.pool.ntp.org" // https://www.zeitserver.de/deutschland/deutsche-pool-zeitserver/, https://www.ntppool.org/zone/de
// #define NTP_SERVER "ptbtime4.ptb.de" // https://www.ptb.de/cms/ptb/fachabteilungen/abtq/gruppe-q4/ref-q42/zeitsynchronisation-von-rechnern-mit-hilfe-des-network-time-protocol-ntp.html
#define UTC_OFFSET_SEC 0 // I want to get always the UTC time, for Germany it would be 3600 seconds
#define DAYLIGHT_OFFSET_SEC 0 // I want to get always the UTC time, for Germany it would be 3600 seconds (1 hour extra during DST)

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

const uint8_t qos = 2; // QoS = 2 means: make sure that the MQTT message is delivered, but only once
unsigned long pulse_counter = 0; // As extra precaution: send an incremental counter value with each pulse,
                                 // just in case that in spite of QoS = 2 duplicate messages are received

void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void onWifiConnect(const WiFiEventStationModeGotIP& event) {
  Serial.println("Connected to Wi-Fi.");
  configTime(UTC_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER); // connect to NTP server
  Serial.println(getLocalTime());
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

String getLocalTime() {
  time_t rawtime;
  struct tm* timeinfo;
  time(&rawtime);
  timeinfo = localtime(&rawtime);
  // for time formatting, see https://randomnerdtutorials.com/esp32-date-time-ntp-client-server-arduino/
  char time_string[19];
  // strftime(time_string, 19, "%Y-%m-%d %H:%M:%S", timeinfo); // example: 2024-11-18 20:28:16
  strftime(time_string, 19, "%F %T", timeinfo); // equivalent to the line above
  return time_string;
}

String buildMessage() {
  // String message = String("{'token': '");
  // message += String(MQTT_TOKEN);
  // message += String("', 'time': '");
  String message = String("{'time': '");
  message += getLocalTime();
  message += String("', 'millis': ");
  message += millis();
  message += String(", 'pulse_counter': ");
  message += pulse_counter;
  message += "}";

  return message;
}

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

void sendMessage() {
  String message = buildMessage();
  uint16_t packetIdPub = mqttClient.publish(MQTT_TOPIC, qos, true, message.c_str());
  Serial.printf("Publishing on topic %s at QoS %i, packetId: %i\n", MQTT_TOPIC, qos, packetIdPub);
  Serial.printf("Message: %s\n", message);
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

int previous_pin_state = 1; // inital pin state is 1, which means there is no pulse

void loop() {
  int pin_state = digitalRead(S0_PIN);
  if (pin_state != previous_pin_state) {
    // There is a change (a pulse has either started or ended)
    if (pin_state == 0) {
      // A new pulse has started!
      pulse_counter += 1;

      // Send an MQTT message
      sendMessage();
    }

    previous_pin_state = pin_state;
  }
}