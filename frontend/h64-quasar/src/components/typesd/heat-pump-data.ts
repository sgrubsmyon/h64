export type HeatPumpData = {
  status: string,
  values: {
    values1: {
      time: string,
      millis: number,
      pulse_counter: number
    },
    values2: {
      time: string,
      millis: number,
      pulse_counter: number
    },
    power: number
  }
};

export const emptyHeatPumpData: HeatPumpData = {
  status: 'Waiting for 1st pulse',
  values: {
    values1: {
      time: '',
      millis: NaN,
      pulse_counter: NaN
    },
    values2: {
      time: '',
      millis: NaN,
      pulse_counter: NaN
    },
    power: NaN
  }
};