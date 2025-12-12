#!/bin/bash

# Run this script on new server 'guava'

# Simple pg_dump approach did not work due not corrupted blocks
## Create dump on old server
#ssh guavapi pg_dump -U postgres -h localhost h64 > h64_old.sql
## Import dump into extra DB on old server
#psql -U postgres -h localhost -c 'drop database h64_old;'
#psql -U postgres -h localhost -c 'create database h64_old with owner postgres;'
#psql -U postgres -h localhost -d h64_old < h64_old.sql

# Create temprary tables in h64 database
psql -U postgres -h localhost -d h64 < create_heat_pump_metrics_tables.sql
psql -U postgres -h localhost -d h64 < create_inverter_metrics_tables.sql
psql -U postgres -h localhost -d h64 < create_weather_station_metrics_tables.sql

# Create dumps on old server
echo ""
echo "Create dumps..."
ssh guavapi "
  psql -U postgres -h localhost -d h64 -c \"COPY (SELECT * FROM heat_pump_metrics_electric_power_pulse) TO '/usb-data/h64_old/h64_heat_pump.csv' WITH DELIMITER ',' CSV HEADER; COPY (SELECT * FROM inverter_metrics_slow) TO '/usb-data/h64_old/h64_inverter_slow.csv'  WITH DELIMITER ',' CSV HEADER; COPY (SELECT * FROM weather_station_metrics) TO '/usb-data/h64_old/h64_weather_station.csv'  WITH DELIMITER ',' CSV HEADER;\"
"
# Special case for inverter_metrics_faster due to corrupt blocks
ssh guavapi "
  psql -U postgres -h localhost -d h64 -c \"COPY (SELECT time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power FROM inverter_metrics_faster ORDER BY time LIMIT 5000000) TO '/usb-data/h64_old/h64_inverter_faster_head.csv'  WITH DELIMITER ',' CSV HEADER;\"
";
ssh guavapi "
  psql -U postgres -h localhost -d h64 -c \"COPY (SELECT time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power FROM inverter_metrics_faster ORDER BY time DESC LIMIT 16000000) TO '/usb-data/h64_old/h64_inverter_faster_tail_reverse.csv'  WITH DELIMITER ',' CSV HEADER;\"
"

# Copy dumps over
echo ""
echo "Copy dumps..."
rsync -rtlPvi guavapi:/usb-data/h64_old/h64_*.csv ~/h64_old/

# Reverse the tail dump to correct order
echo ""
echo "Reverse inverter tail dump..."
# Write CSV header row
head -n 1 ~/h64_old/h64_inverter_faster_tail_reverse.csv > ~/h64_old/h64_inverter_faster_tail.csv
# Pass all lines except first into tac to reverse
tail -n +2 ~/h64_old/h64_inverter_faster_tail_reverse.csv | tac >> ~/h64_old/h64_inverter_faster_tail.csv

# Insert dumps into temporary tables
echo ""
echo "Insert dumps..."
echo "Heat pump..."
psql -U postgres -h localhost -d h64 -c "\copy heat_pump_metrics_electric_power_pulse (time) FROM '/home/mvoge/h64_old/h64_heat_pump.csv' DELIMITER ',' CSV HEADER;"
echo "Inverter faster head..."
psql -U postgres -h localhost -d h64 -c "\copy inverter_metrics_faster (time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power) FROM '/home/mvoge/h64_old/h64_inverter_faster_head.csv' DELIMITER ',' CSV HEADER;"
echo "Inverter faster tail..."
psql -U postgres -h localhost -d h64 -c "\copy inverter_metrics_faster (time, total_load_power, total_grid_power, load_power_l1, load_power_l2, load_power_l3, pv1_power, pv2_power, battery_power) FROM '/home/mvoge/h64_old/h64_inverter_faster_tail.csv' DELIMITER ',' CSV HEADER;"
echo "Inverter slow..."
psql -U postgres -h localhost -d h64 -c "\copy inverter_metrics_slow (time, daily_pv_production, total_pv_production, daily_load_energy_consumption, total_load_energy_consumption, daily_energy_bought, daily_energy_sold, total_energy_bought, total_energy_sold, battery_soc, battery_daily_charge, battery_daily_discharge, battery_total_charge, battery_total_discharge, dc_temperature, ac_temperature, battery_temperature, battery_voltage, active_power_regulation) FROM '/home/mvoge/h64_old/h64_inverter_slow.csv' DELIMITER ',' CSV HEADER;"
echo "Weather station..."
psql -U postgres -h localhost -d h64 -c "\copy weather_station_metrics (time, location, id, battery_ok, temperature_C, humidity, wind_max_m_s, wind_avg_m_s, wind_dir_deg, rain_mm) FROM '/home/mvoge/h64_old/h64_weather_station.csv' DELIMITER ',' CSV HEADER;"
