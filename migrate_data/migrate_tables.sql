-- Migrate H64 data tables from old self-made setup (many Python scripts)
-- to new setup where all data is collected with Home Assistant as central
-- point and then sent from Home Assistant via MQTT to a single Python script
-- that inserts select data into tables for long term storage and archiving.

INSERT INTO inverter_slow (
  time, battery_soc, daily_pv_production, total_pv_production,
  daily_load_energy_consumption, total_load_energy_consumption,
  daily_energy_bought, daily_energy_sold,
  total_energy_bought, total_energy_sold,
  daily_battery_charge, daily_battery_discharge,
  total_battery_charge, total_battery_discharge,
  battery_temperature, dc_temperature, temperature
) SELECT time, battery_soc, daily_pv_production, total_pv_production,
    daily_load_energy_consumption, total_load_energy_consumption,
    daily_energy_bought, daily_energy_sold,
    total_energy_bought, total_energy_sold,
    battery_daily_charge, battery_daily_discharge,
    battery_total_charge, battery_total_discharge,
    battery_temperature, dc_temperature, ac_temperature
  FROM inverter_metrics_slow;

INSERT INTO inverter_fast (
  time, grid_power, load_power, load_l1_power, load_l2_power, load_l3_power,
  battery_power, pv1_power, pv2_power
) SELECT time, total_grid_power, total_load_power,
    load_power_l1, load_power_l2, load_power_l3,
    CASE WHEN battery_power > 0 AND battery_power < 1e-30 THEN 0 ELSE battery_power END, -- prevent REAL underflow
    CASE WHEN pv1_power > 0 AND pv1_power < 1e-30 THEN 0 ELSE pv1_power END, -- prevent REAL underflow
    CASE WHEN pv2_power > 0 AND pv2_power < 1e-30 THEN 0 ELSE pv2_power END -- prevent REAL underflow
  FROM inverter_metrics_faster;

INSERT INTO heat_pump (time)
  SELECT time FROM heat_pump_metrics_electric_power_pulse;

INSERT INTO weather_station (
  time, location, id, battery_ok, temperature_C, humidity,
  wind_max_m_s, wind_avg_m_s, wind_dir_deg, rain_mm
) SELECT time, location, id, battery_ok, temperature_C, humidity,
    wind_max_m_s, wind_avg_m_s, wind_dir_deg, rain_mm
  FROM weather_station_metrics;
