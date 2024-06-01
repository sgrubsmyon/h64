-- Create tables inside PostgreSQL TimescaleDB database `weather`

-- Table is written to every 12 seconds
-- time,id/location,Battery,Temperature,Humidity,Wind Gust,Wind Speed,Direction,Rain
CREATE TABLE weather_metrics (
   time                          TIMESTAMPTZ   NOT NULL,
   location                      CHARACTER (5) NULL, -- either 'bshed' for bike shed or 'bport' for bike port or 'gshed' for garden shed or whatever
   battery                       REAL          NULL,
   temperature                   REAL          NULL,
   humidity                      REAL          NULL,
   wind_gust                     REAL          NULL,
   wind_speed                    REAL          NULL,
   wind_direction                REAL          NULL,
   rain                          REAL          NULL
);

-- Convert tables to TimescaleDB hypertables:
SELECT create_hypertable('weather_metrics', 'time');