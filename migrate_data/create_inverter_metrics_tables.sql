-- Create tables inside PostgreSQL TimescaleDB database `h64`

-- Table with values changing slowly, enough to update only every 5 minutes
CREATE TABLE inverter_metrics_slow (
   time                          TIMESTAMPTZ      NOT NULL,
   daily_pv_production           DOUBLE PRECISION NULL,
   total_pv_production           DOUBLE PRECISION NULL,
   daily_load_energy_consumption DOUBLE PRECISION NULL,
   total_load_energy_consumption DOUBLE PRECISION NULL,
   daily_energy_bought           DOUBLE PRECISION NULL,
   daily_energy_sold             DOUBLE PRECISION NULL,
   total_energy_bought           DOUBLE PRECISION NULL,
   total_energy_sold             DOUBLE PRECISION NULL,
   battery_soc                   DOUBLE PRECISION NULL,
   battery_daily_charge          DOUBLE PRECISION NULL,
   battery_daily_discharge       DOUBLE PRECISION NULL,
   battery_total_charge          DOUBLE PRECISION NULL,
   battery_total_discharge       DOUBLE PRECISION NULL,
   dc_temperature                DOUBLE PRECISION NULL,
   ac_temperature                DOUBLE PRECISION NULL,
   battery_temperature           DOUBLE PRECISION NULL,
   battery_voltage               DOUBLE PRECISION NULL,
   active_power_regulation       DOUBLE PRECISION NULL
);

-- Table with values changing fast, about every second. Table is updated every 3 seconds
CREATE TABLE inverter_metrics_faster (
   time             TIMESTAMPTZ      NOT NULL,
   total_load_power DOUBLE PRECISION NULL,
   total_grid_power DOUBLE PRECISION NULL,
   load_power_l1    DOUBLE PRECISION NULL,
   load_power_l2    DOUBLE PRECISION NULL,
   load_power_l3    DOUBLE PRECISION NULL,
   pv1_power        DOUBLE PRECISION NULL,
   pv2_power        DOUBLE PRECISION NULL,
   pv1_voltage      DOUBLE PRECISION NULL,
   pv2_voltage      DOUBLE PRECISION NULL,
   pv1_current      DOUBLE PRECISION NULL,
   pv2_current      DOUBLE PRECISION NULL,
   battery_power    DOUBLE PRECISION NULL
);
