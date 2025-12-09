#!/bin/bash

# Run this script on new server 'guava'

## Create dump on old server
#ssh guavapi pg_dump -U postgres -h localhost h64 > h64_old.sql
## Import dump into extra DB on old server
#psql -U postgres -h localhost -c 'drop database h64_old;'
#psql -U postgres -h localhost -c 'create database h64_old with owner postgres;'
#psql -U postgres -h localhost -d h64_old < h64_old.sql

# Create temporary database
psql -U postgres -h localhost -c 'DROP DATABASE h64_old;'
psql -U postgres -h localhost -c 'CREATE DATABASE h64_old WITH OWNER postgres;'
psql -U postgres -h localhost -d h64_old -c 'CREATE EXTENSION IF NOT EXISTS timescaledb;'

# Create temprary tables
psql -U postgres -h localhost -d h64_old < deprecated/heat_pump/mqtt-server-raspi/create_heat_pump_metrics_tables.sql
psql -U postgres -h localhost -d h64_old < deprecated/inverter/create_inverter_metrics_tables.sql
psql -U postgres -h localhost -d h64_old < deprecated/weather_station/create_weather_station_metrics_tables.sql

# Create dumps on old server
echo ""
echo "Create dumps..."
ssh guavapi "psql -U postgres -h localhost -d h64 -c \"COPY (SELECT * FROM heat_pump_metrics_electric_power_pulse) TO '/usb-data/h64_heat_pump.csv'  WITH DELIMITER ',' CSV HEADER; COPY (SELECT time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power FROM inverter_metrics_faster) TO '/usb-data/h64_inverter_faster.csv'  WITH DELIMITER ',' CSV HEADER; COPY (SELECT * FROM inverter_metrics_slow) TO '/usb-data/h64_inverter_slow.csv'  WITH DELIMITER ',' CSV HEADER; COPY (SELECT * FROM weather_station_metrics) TO '/usb-data/h64_weather_station.csv'  WITH DELIMITER ',' CSV HEADER;\""

# Copy dumps over
echo ""
echo "Copy dumps..."
rsync -rtlPvi guavapi:/usb-data/h64_*.csv /tmp/

# Insert dumps into temporary database
echo ""
echo "Insert dumps..."
echo "Heat pump..."
psql -U postgres -h localhost -d h64_old -c "COPY heat_pump_metrics_electric_power_pulse (time) FROM '/tmp/h64_heat_pump.csv' DELIMITER ', ' CSV HEADER;"
echo "Inverter faster..."
psql -U postgres -h localhost -d h64_old -c "COPY inverter_metrics_faster (time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power) FROM '/tmp/h64_inverter_faster.csv' DELIMITER ', ' CSV HEADER;"
echo "Inverter slow..."
psql -U postgres -h localhost -d h64_old -c "COPY inverter_metrics_slow (time, daily_pv_production, total_pv_production, daily_load_energy_consumption, total_load_energy_consumption, daily_energy_bought, daily_energy_sold, total_energy_bought, total_energy_sold, battery_soc, battery_daily_charge, battery_daily_discharge, battery_total_charge, battery_total_discharge, dc_temperature, ac_temperature, battery_temperature, battery_voltage, active_power_regulation) FROM '/tmp/h64_inverter_slow.csv' DELIMITER ', ' CSV HEADER;"
echo "Weather station..."
psql -U postgres -h localhost -d h64_old -c "COPY weather_station_metrics (time, location, id, battery_ok, temperature_C, humidity, wind_max_m_s, wind_avg_m_s, wind_dir_deg, rain_mm) FROM '/tmp/h64_weather_station.csv' DELIMITER ', ' CSV HEADER;"
