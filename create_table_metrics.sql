-- Create tables inside PostgreSQL TimescaleDB database `inverter`

-- Table with values changing slowly, enough to update only every 5 minutes
CREATE TABLE metrics_slow (
   time                          TIMESTAMPTZ       NOT NULL,
   daily_pv_production           DOUBLE PRECISION  NULL,
   total_pv_production           DOUBLE PRECISION  NULL,
   daily_load_energy_consumption DOUBLE PRECISION  NULL,
   total_load_energy_consumption DOUBLE PRECISION  NULL,
   daily_energy_bought           DOUBLE PRECISION  NULL,
   daily_energy_sold             DOUBLE PRECISION  NULL,
   total_energy_bought           DOUBLE PRECISION  NULL,
   total_energy_sold             DOUBLE PRECISION  NULL,
   battery_soc                   DOUBLE PRECISION  NULL,
   battery_daily_charge          DOUBLE PRECISION  NULL,
   battery_daily_discharge       DOUBLE PRECISION  NULL,
   battery_total_charge          DOUBLE PRECISION  NULL,
   battery_total_discharge       DOUBLE PRECISION  NULL,
   active_power_regulation       DOUBLE PRECISION  NULL
);

-- Table with values changing fast, about every second. Table is updated every 10 seconds
CREATE TABLE metrics_fast (
   time                 TIMESTAMPTZ       NOT NULL,
   pv1_power            DOUBLE PRECISION  NULL,
   pv2_power            DOUBLE PRECISION  NULL,
   pv1_voltage          DOUBLE PRECISION  NULL,
   pv2_voltage          DOUBLE PRECISION  NULL,
   pv1_current          DOUBLE PRECISION  NULL,
   pv2_current          DOUBLE PRECISION  NULL,
   total_load_power     DOUBLE PRECISION  NULL,
   total_grid_power     DOUBLE PRECISION  NULL,
   load_power_l1        DOUBLE PRECISION  NULL,
   load_power_l2        DOUBLE PRECISION  NULL,
   load_power_l3        DOUBLE PRECISION  NULL,
   load_voltage_l1      DOUBLE PRECISION  NULL,
   load_voltage_l2      DOUBLE PRECISION  NULL,
   load_voltage_l3      DOUBLE PRECISION  NULL,
   grid_voltage_l1      DOUBLE PRECISION  NULL,
   grid_voltage_l2      DOUBLE PRECISION  NULL,
   grid_voltage_l3      DOUBLE PRECISION  NULL,
   ct_internal_power_l1 DOUBLE PRECISION  NULL,
   ct_internal_power_l2 DOUBLE PRECISION  NULL,
   ct_internal_power_l3 DOUBLE PRECISION  NULL,
   ct_external_power_l1 DOUBLE PRECISION  NULL,
   ct_external_power_l2 DOUBLE PRECISION  NULL,
   ct_external_power_l3 DOUBLE PRECISION  NULL,
   inverter_power_l1    DOUBLE PRECISION  NULL,
   inverter_power_l2    DOUBLE PRECISION  NULL,
   inverter_power_l3    DOUBLE PRECISION  NULL,
   current_l1           DOUBLE PRECISION  NULL,
   current_l2           DOUBLE PRECISION  NULL,
   current_l3           DOUBLE PRECISION  NULL,
   dc_temperature       DOUBLE PRECISION  NULL,
   ac_temperature       DOUBLE PRECISION  NULL,
   battery_power        DOUBLE PRECISION  NULL,
   battery_voltage      DOUBLE PRECISION  NULL,
   battery_current      DOUBLE PRECISION  NULL,
   battery_temperature  DOUBLE PRECISION  NULL
);

-- Convert tables to TimescaleDB hypertable:
SELECT create_hypertable('metrics_slow', 'time');
SELECT create_hypertable('metrics_fast', 'time');