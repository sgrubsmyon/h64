## Setup

Based on https://randomnerdtutorials.com/esp8266-nodemcu-mqtt-publish-dht11-dht22-arduino/

### Install Arduino IDE on your laptop

Go to https://www.arduino.cc/en/software, download "Linux ZIP file 64 bits (X86-64)".

Unzip and create symlink to file `arduino-ide` in any directory on your `$PATH`.

### Install ESP8266 Board in Arduino IDE

https://randomnerdtutorials.com/how-to-install-esp8266-board-arduino-ide/

1. In your Arduino IDE, go to File> Preferences
2. Enter http://arduino.esp8266.com/stable/package_esp8266com_index.json into the “Additional Boards Manager URLs” field as shown in the figure below. Then, click the “OK” button:
3. Note: if you already have the ESP32 boards URL, you can separate the URLs with a comma as follows:
```
https://dl.espressif.com/dl/package_esp32_index.json, http://arduino.esp8266.com/stable/package_esp8266com_index.json
```
4. Open the Boards Manager. Go to Tools > Board > Boards Manager…
5. Search for ESP8266 and press install button for the “ESP8266 by ESP8266 Community“:
6. That’s it. It should be installed after a few seconds.

### Install Async MQTT client library for ESP8266

Code is here: https://github.com/marvinroger/async-mqtt-client?tab=readme-ov-file

On your laptop:

```
cd ~/bin
git clone https://github.com/marvinroger/async-mqtt-client.git
```

Read the docs inside `/docs`.

1. Download latest release, link is in `1.-Getting-started.md`
2. Load the .zip with Sketch → Include Library → Add .ZIP Library
3. Download dependency (link also on Markdown file) and install it in same way

### Set permissions for writing to ESP8266

(If permission denied error when connecting to ESP8266)

https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux

```
sudo usermod -a -G dialout <username>
```