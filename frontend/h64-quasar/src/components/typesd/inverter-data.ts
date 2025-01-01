export type InverterData = {
  status: {
    type: string,
    msg: string
  },
  values: {
    slow: {
      time: string,
      daily_pv_production: number,
      total_pv_production: number,
      daily_load_energy_consumption: number,
      total_load_energy_consumption: number,
      daily_energy_bought: number,
      daily_energy_sold: number,
      total_energy_bought: number,
      total_energy_sold: number,
      battery_soc: number,
      battery_daily_charge: number,
      battery_daily_discharge: number,
      battery_total_charge: number,
      battery_total_discharge: number,
      dc_temperature: number,
      ac_temperature: number,
      battery_temperature: number,
      battery_voltage: number,
      active_power_regulation: number
    },
    fast: {
      time: string,
      load_voltage_l1: number,
      load_voltage_l2: number,
      load_voltage_l3: number,
      grid_voltage_l1: number,
      grid_voltage_l2: number,
      grid_voltage_l3: number,
      ct_internal_power_l1: number,
      ct_internal_power_l2: number,
      ct_internal_power_l3: number,
      ct_external_power_l1: number,
      ct_external_power_l2: number,
      ct_external_power_l3: number,
      inverter_power_l1: number,
      inverter_power_l2: number,
      inverter_power_l3: number,
      current_l1: number,
      current_l2: number,
      current_l3: number,
      battery_current: number
    },
    faster: {
      time: string,
      total_load_power: number,
      total_grid_power: number,
      load_power_l1: number,
      load_power_l2: number,
      load_power_l3: number,
      pv1_power: number,
      pv2_power: number,
      pv1_voltage: number,
      pv2_voltage: number,
      pv1_current: number,
      pv2_current: number,
      battery_power: number
    }
  }
};

export const emptyInverterData: InverterData = {
  status: {
    type: 'NORMAL',
    msg: ''
  },
  values: {
    slow: {
      time: '',
      daily_pv_production: NaN,
      total_pv_production: NaN,
      daily_load_energy_consumption: NaN,
      total_load_energy_consumption: NaN,
      daily_energy_bought: NaN,
      daily_energy_sold: NaN,
      total_energy_bought: NaN,
      total_energy_sold: NaN,
      battery_soc: NaN,
      battery_daily_charge: NaN,
      battery_daily_discharge: NaN,
      battery_total_charge: NaN,
      battery_total_discharge: NaN,
      dc_temperature: NaN,
      ac_temperature: NaN,
      battery_temperature: NaN,
      battery_voltage: NaN,
      active_power_regulation: NaN
    },
    fast: {
      time: '',
      load_voltage_l1: NaN,
      load_voltage_l2: NaN,
      load_voltage_l3: NaN,
      grid_voltage_l1: NaN,
      grid_voltage_l2: NaN,
      grid_voltage_l3: NaN,
      ct_internal_power_l1: NaN,
      ct_internal_power_l2: NaN,
      ct_internal_power_l3: NaN,
      ct_external_power_l1: NaN,
      ct_external_power_l2: NaN,
      ct_external_power_l3: NaN,
      inverter_power_l1: NaN,
      inverter_power_l2: NaN,
      inverter_power_l3: NaN,
      current_l1: NaN,
      current_l2: NaN,
      current_l3: NaN,
      battery_current: NaN
    },
    faster: {
      time: '',
      total_load_power: NaN,
      total_grid_power: NaN,
      load_power_l1: NaN,
      load_power_l2: NaN,
      load_power_l3: NaN,
      pv1_power: NaN,
      pv2_power: NaN,
      pv1_voltage: NaN,
      pv2_voltage: NaN,
      pv1_current: NaN,
      pv2_current: NaN,
      battery_power: NaN
    }
  }
};