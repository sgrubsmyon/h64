# Code for collecting and visualizing data at a random family home

This repository includes code to read Modbus data from a Deye inverter
(model SUN-10K-SG04LP3-EU) via sending TCP packets over Wifi. The Deye
code is adopted from https://github.com/kbialek/deye-inverter-mqtt
(many thanks!).


## Install dependencies

This code is intended to be run on a small server such as a Raspberry Pi, running an
Ubuntu server OS (https://ubuntu.com/download/raspberry-pi).


### PostgreSQL and TimescaleDB

See https://docs.timescale.com/self-hosted/latest/install/installation-linux/.

Install PostgreSQL and TimescaleDB:

```
$ sudo apt install gnupg postgresql-common apt-transport-https lsb-release wget
$ sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
$ echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
$ wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
$ sudo apt update
$ sudo apt install timescaledb-2-postgresql-14
$ timescaledb-tune
$ sudo apt update
$ sudo apt install postgresql-client
$ sudo systemctl restart postgresql
$ sudo -u postgres psql
> \password postgres
> \q
```

#### Create database for h64

```
$ psql -U postgres -h localhost
> CREATE database h64;
> \c h64
> CREATE EXTENSION IF NOT EXISTS timescaledb;
> \dx
                                                List of installed extensions
    Name     | Version |   Schema   |                                      Description                                      
-------------+---------+------------+---------------------------------------------------------------------------------------
 plpgsql     | 1.0     | pg_catalog | PL/pgSQL procedural language
 timescaledb | 2.11.1  | public     | Enables scalable inserts and complex queries for time-series data (Community Edition)
(2 rows)
> \q
```

Open h64 database in psql:

```
$ psql -U postgres -h localhost -d h64
```

##### Create tables for inverter data:

```
$ cd inverter
$ psql -U postgres -h localhost -d h64 -f create_inverter_metrics_tables.sql
```

##### Create tables for weather data:

```
$ cd weather_station
$ psql -U postgres -h localhost -d h64 -f create_weather_station_metrics_tables.sql
```

##### Create tables for heat pump data:

```
$ cd heat_pump
$ psql -U postgres -h localhost -d h64 -f create_heat_pump_metrics_tables.sql
```



### Python

```
<!-- Optional:
# Create a virtual environment:
$ sudo apt update && sudo apt upgrade
$ sudo apt install python3.10-venv # or whatever version is the currently used one
# In the directory of h64:
$ python3.10 -m venv venv
$ source venv/bin/activate
-->

$ pip install --upgrade pip
$ pip install numpy
$ pip install pandas
$ pip install libscrc
$ sudo apt install libpq-dev
$ pip install psycopg2
$ pip install --upgrade websockets
```

<!-- (deprecated, now using Bun for the websocket servers)
### Node.js

Find latest curl command on https://github.com/nvm-sh/nvm, e.g.:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash
```

Close terminal and open new terminal for changes to apply.

Show available installable node versions:
```
$ nvm ls-remote
```

Install latest listed LTS version (e.g.):
```
$ nvm install v12.16.1
```

Install node packages:

```
$ cd inverter/node_ws_server
$ npm install
```
-->

### Bun

See https://bun.sh/.

```
$ curl -fsSL https://bun.sh/install | bash
```

Install packages:

```
$ cd inverter/bun_ws_server
$ bun install
$ cd weather_station/bun_ws_server
$ bun install
```

### Vue.js

<!--
https://vuejs.org/guide/quick-start.html#creating-a-vue-application

Here is how the project was created:

```
$ npm create vue@latest
Need to install the following packages:
create-vue@3.7.2
Ok to proceed? (y) y

Vue.js - The Progressive JavaScript Framework

✔ Project name: … h64
✔ Add TypeScript? … Yes
✔ Add JSX Support? … No
✔ Add Vue Router for Single Page Application development? … Yes
✔ Add Pinia for state management? … No
✔ Add Vitest for Unit Testing? … No
✔ Add an End-to-End Testing Solution? › No
✔ Add ESLint for code quality? … Yes
✔ Add Prettier for code formatting? … Yes

Scaffolding project in /home/mvoge/Documents/Markus/i/code/h64/frontend/h64...

```
cd h64
npm install
npm run format
npm run dev
```
-->

```
$ cd frontend/h64
$ npm install
$ npm run format
```

Start the development server:

```
$ npm run dev
```

Ship to production:

```
$ npm run build
```


## Deploy

### Create and edit config file

```
$ cp -i config.cfg.example config.cfg
$ chmod 600 config.cfg
```

Edit file config.cfg and fill in your numbers.


### Create directory for log file(s)

```
$ sudo mkdir /var/log/h64
$ sudo chown yourusername:yourusername /var/log/h64/
```


### Install systemd unit files

```
$ sudo cp -i unit-files/* /etc/systemd/system/
```

Edit all unit files and replace "yourusername" with your user name. If needed,
change the specified location of the h64 scripts.

```
$ sudo vim -p /etc/systemd/system/h64*
```

Enable and start the daemons.

```
$ sudo systemctl daemon-reload
$ sudo systemctl enable h64-inverter-websocket.service h64-inverter-insert.service
$ sudo systemctl start h64-inverter-websocket.service h64-inverter-insert.service
```


### Configure nginx proxy for WebSocket server

See: https://www.nginx.com/blog/websocket-nginx/

Create a CNAME subdomain DNS entry for `[inverterdata, weatherdata, ...]`, e.g. `[inverterdata.example.com, weatherdata.example.com, ...]`.

Create file `/etc/nginx/sites-available/h64`:

```
map $http_upgrade $connection_upgrade {
	default upgrade;
	'' close;
}

upstream websocket_inverter {
	server localhost:8765;
}

upstream websocket_weather {
	server localhost:8766;
}

# ...

server {
	server_name inverterdata.example.com;
	listen 80;
	location / {
		proxy_pass http://websocket_inverter;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection $connection_upgrade;
		proxy_set_header Host $host;
	}
}

server {
	server_name weatherdata.example.com;
	listen 80;
	location / {
		proxy_pass http://websocket_weather;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection $connection_upgrade;
		proxy_set_header Host $host;
	}
}

# ...
```

Activate it and restart nginx:

```
$ cd /etc/nginx/sites-enabled/
$ sudo ln -s ../sites-available/h64
$ sudo systemctl restart nginx
```

Generate the Let's Encrypt TLS/SSL certificate with certbot.

If not yet done, install certbot:

```
$ sudo apt-get remove certbot
$ sudo snap install --classic certbot
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Run certbot to generate certificates and auto-edit the nginx config files:

```
$ sudo certbot --nginx
```

Certbot will modify the nginx config file appropriately.

WebSocket server now accessible TLS encrypted under `wss://inverterdata.example.com`!

You can test the server by opening `about:blank` in web browser, pressing F12 and pasting this code into the JS console:

```
var conn = new WebSocket('wss://inverterdata.example.com');
conn.onopen = function(e) {
    console.log("Connection established!");
};

conn.onmessage = function(e) {
    console.log(e.data);
};
```

### Configure nginx for frontend

Copy frontend to web server's document root:

```
$ sudo rsync -rtlPvi ~/h64/frontend/h64_purejs/ /var/www/html/h64/
```

Create server config:

```
sudo vim /etc/nginx/sites-available/h64
```

Add:

```
server {
    server_name h64.example.com;
    root /var/www/html/h64;
    access_log /var/log/nginx/h64-access.log;
    #error_log /var/log/nginx/h64-error.log info;
    error_log /var/log/nginx/h64-error.log;

    listen 80;
}

```

Restart nginx:

```
$ sudo systemctl restart nginx
```

Generate the Let's Encrypt TLS/SSL certificate with certbot.

```
$ sudo certbot --nginx
```

Certbot will modify the nginx config file appropriately.
