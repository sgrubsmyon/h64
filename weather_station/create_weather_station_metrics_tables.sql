-- Create tables inside PostgreSQL TimescaleDB database `weather`
-- for holding data read via RTL-SDR antenna from a Bresser 5-in-1 weather station

-- Table is written to every 12 seconds
-- time,id/location,Battery,Temperature,Humidity,Wind Gust,Wind Speed,Direction,Rain
CREATE TABLE weather_metrics (
   time                          TIMESTAMPTZ   NOT NULL,
   location                      CHARACTER (5) NULL, -- either 'bshed' for bike shed or 'bport' for bike port or 'gshed' for garden shed or whatever
   battery_ok                    REAL          NULL,
   temperature_C                 REAL          NULL,
   humidity                      REAL          NULL,
   wind_max_m_s                  REAL          NULL,
   wind_avg_m_s                  REAL          NULL,
   wind_dir_deg                  SMALLINT      NULL,
   rain_mm                       REAL          NULL
);

-- Convert tables to TimescaleDB hypertables:
SELECT create_hypertable('weather_metrics', 'time');