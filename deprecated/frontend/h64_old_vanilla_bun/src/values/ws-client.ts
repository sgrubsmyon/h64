export function setupWebSocket() {
  const conn = new WebSocket("wss://inverterdata.h64.viridian-project.org");

  conn.onopen = function () {
    console.log("Connection established!");
  };

  conn.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);

    let group = "faster";

    const timestamp = new Date(data.values[group].time + "Z");
    const timestamp_str = timestamp.toLocaleString("de-DE", {
      dateStyle: "medium", timeStyle: "medium"
    });
    updateValueBox("timestamp", timestamp_str, "", "timestamp");

    updateValueBox("grid-power", data.values[group]["total_grid_power"], "W");
    updateValueBox("load-power", data.values[group]["total_load_power"], "W");
    updateValueBox("pv-power",
      data.values[group]["pv1_power"] + data.values[group]["pv2_power"],
      "W");
    updateValueBox("battery-power", data.values[group]["battery_power"], "W");
    updateValueBox("battery-power", `${data.values["slow"]["battery_soc"]}%`, "",
      "dashboard-value-2nd");
    updateValueBox("pv1-power", data.values[group]["pv1_power"], "W");
    updateValueBox("pv2-power", data.values[group]["pv2_power"], "W");
  };

  function updateValueBox(box_id: string, value: string, unit: string, css_class: string = "") {
    if (css_class === "") css_class = "dashboard-value";
    console.log(`#${box_id} > span.${css_class}`);
    const value_text = document.querySelector(`#${box_id} > span.${css_class}`);
    if (unit !== "") {
      value_text!.innerHTML = `${value} ${unit}`;
    } else {
      value_text!.innerHTML = `${value}`;
    }
  }
}

// const t = {
//     "values": {
//         "slow": {
//             "time": "2023-08-16T22:55:01.501987",
//             "daily_pv_production": 0,
//             "total_pv_production": 123.1,
//             "daily_load_energy_consumption": 0.1,
//             "total_load_energy_consumption": 187.8,
//             "daily_energy_bought": 0.1,
//             "daily_energy_sold": 0,
//             "total_energy_bought": 172.5,
//             "total_energy_sold": 108.7,
//             "battery_soc": 0,
//             "battery_daily_charge": 0,
//             "battery_daily_discharge": 0,
//             "battery_total_charge": 0.2,
//             "battery_total_discharge": 0,
//             "dc_temperature": 25,
//             "ac_temperature": 29.3,
//             "battery_temperature": 25,
//             "battery_voltage": 8.97,
//             "active_power_regulation": 0
//         },
//         "fast": {
//             "time": "2023-08-16T23:00:04.502540",
//             "load_voltage_l1": 231.3,
//             "load_voltage_l2": 230.6,
//             "load_voltage_l3": 232.2,
//             "grid_voltage_l1": 230.2,
//             "grid_voltage_l2": 230.8,
//             "grid_voltage_l3": 232.6,
//             "ct_internal_power_l1": 81,
//             "ct_internal_power_l2": 4,
//             "ct_internal_power_l3": 38,
//             "ct_external_power_l1": 95,
//             "ct_external_power_l2": 24,
//             "ct_external_power_l3": 32,
//             "inverter_power_l1": 0,
//             "inverter_power_l2": 0,
//             "inverter_power_l3": 0,
//             "current_l1": -0.1,
//             "current_l2": -0.1,
//             "current_l3": -0.1,
//             "battery_current": 0
//         },
//         "faster": {
//             "time": "2023-08-16T23:00:21.002084",
//             "total_load_power": 148,
//             "total_grid_power": 150,
//             "load_power_l1": 95,
//             "load_power_l2": 23,
//             "load_power_l3": 30,
//             "pv1_power": 0,
//             "pv2_power": 0,
//             "pv1_voltage": 35.7,
//             "pv2_voltage": 7.8,
//             "pv1_current": 0,
//             "pv2_current": 0,
//             "battery_power": 0
//         }
//     },
//     "status": { "type": "NORMAL", "msg": "" }
// }