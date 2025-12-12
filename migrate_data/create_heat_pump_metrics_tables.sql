-- Create tables inside PostgreSQL TimescaleDB database `h64`
-- for holding data read via RTL-SDR antenna from a Bresser 5-in-1 weather station

-- Table is written to upon every pulse of the heat pump power meter (one pulse every 0.001 kWh)
CREATE TABLE heat_pump_metrics_electric_power_pulse (
   time TIMESTAMPTZ NOT NULL -- time in the following format: "2024-11-18 20:28:16"
);
