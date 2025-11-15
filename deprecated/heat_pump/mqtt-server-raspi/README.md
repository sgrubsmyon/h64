## Install MQTT server Mosquitto on your server

See:
* https://mosquitto.org/download/
* https://www.arubacloud.com/tutorial/how-to-install-and-secure-mosquitto-on-ubuntu-20-04.aspx

```
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt update
sudo apt install mosquitto
```

Check version:

```
mosquitto -version
```

Check status:

```
sudo systemctl status mosquitto
```

## Configure MQTT server to listen on IP address

https://community.home-assistant.io/t/mosquitto-allow-local-network-access/284833/9
https://mosquitto.org/documentation/authentication-methods/

Password file does not work, gives error "File cannot be opened", maybe AppArmor?
(https://www.opensuse-forum.de/thread/65529-mosquitto-kann-passwort-file-nicht-lesen-error-unable-to-open-pwfile/)
Instead, I allow anonymous login and use a secret token that clients must send
(unencrpyted, so can easily be sniffed, but I think it's secure enough for home purposes).

<!--
Create password file:

```
sudo mosquitto_passwd -c /etc/mosquitto/conf.d/passwords hp_electric_meter
sudo mosquitto_passwd /etc/mosquitto/conf.d/passwords guavapi
sudo cat /etc/mosquitto/conf.d/passwords
```
-->

Add config file:

```
sudo vim /etc/mosquitto/conf.d/listener.conf
```

```
listener 1883 0.0.0.0
# allow_anonymous false
# password_file /etc/mosquitto/conf.d/passwords # does not work
allow_anonymous true
```


## Install Mosquitto client on your laptop

```
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt update
sudo apt install mosquitto-clients
```

## Test MQTT message delivery

Terminal 1 on laptop: (receiving messages)

```
mosquitto_sub -h 192.168.1.1 -t /home/heat_pump/electric_power_pulse
```

Terminal 2 on laptop: (sending messages)

```
mosquitto_pub -h 192.168.1.1 -t /home/heat_pump/electric_power_pulse -m "Hello World!"
```