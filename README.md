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

Create database:

```
$ psql -U postgres -h localhost
> CREATE database yourdatabasename;
> \c yourdatabasename
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

Create tables for h64:

```
$ cd inverter
$ psql -U postgres -h localhost -d yourdatabasename -f create_inverter_metrics_tables.sql
```

Open h64 database in psql:

```
$ psql -U postgres -h localhost -d yourdatabasename
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


## Create and edit config file

```
$ cp -i config.cfg.example config.cfg
$ chmod 600 config.cfg
```

Edit file config.cfg and fill in your numbers.


## Create directory for log file(s)

```
$ sudo mkdir /var/log/h64
```


## Rename and edit run.sh.example

```
$ cp -i run.sh.example run.sh
$ vim run.sh
```


## Create systemd unit file

```
$ sudo vim /etc/systemd/system/h64.service
```

```
[Unit]
Description=Unit file for running h64 family home data collection tools

[Service]
ExecStart=/home/<yourusername>/h64/run.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```
$ sudo systemctl daemon-reload
$ sudo systemctl enable h64.service
$ sudo systemctl start h64.service
```
