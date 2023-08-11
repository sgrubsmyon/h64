#!/usr/bin/env python3

from datetime import datetime
import time
import numpy as np
from read_deye_inverter import data_of_metric_group

start_point = {
    "faster": (0, 0),  # 0 minutes, 0 seconds
    "fast": (0, 4.5),  # 0 minutes, 4.5 seconds
    "slow": (0, 1.5)  # 0 minutes, 1.5 seconds
}

interval = {
    "faster": (0, 3),  # 3 seconds
    "fast": (0, 15),  # 15 seconds
    "slow": (5, 0)  # 5 minutes, 0 seconds
}

# slow sampling is privileged: if it would be skipped because
# previous sampling took too much time, it is done nevertheless
minute_of_last_slow_sampling = -999.0

sampling_points = {}  # sampling points are in minutes (within any one hour)
for group in start_point:
    minute_startpoint = start_point[group][0] + start_point[group][1] / 60
    minute_interval = interval[group][0] + interval[group][1] / 60
    sampling_points[group] = np.arange(
        minute_startpoint, 60, minute_interval)

curr_values = {}

def sample(minute_of_last_slow_sampling):
    now = datetime.now()
    now_minute = now.minute + now.second / 60 + now.microsecond * 1e-6 / 60
    # print(f"Now: {now.minute}:{now.second + now.microsecond * 1e-6}")

    if (now_minute - minute_of_last_slow_sampling) > (interval["slow"][0] + interval["slow"][1] / 60):
        # Last slow sampling is too much in the past,
        # do it right now!
        print("Slow sampling was skipped, is now done before others.")
        next_sampling_group = "slow"
        next_sampling_delta_t = 0
    else:
        closest_sampling_point = {}
        for group in sampling_points:
            delta_ts = sampling_points[group] - now_minute
            # Remove sampling points of the past (negative time difference delta_t)
            delta_ts = delta_ts[delta_ts > 0]
            # Find next upcoming sampling point (closest in time in the future)
            delta_t = np.min(delta_ts)
            closest_sampling_point[group] = delta_t
        # Find which metric group has the smallest delta_t
        next_sampling_group = min(closest_sampling_point,
                                  key=closest_sampling_point.get)
        # Minutes until next sampling:
        next_sampling_delta_t = closest_sampling_point[next_sampling_group]

    # Wait until the next sampling point is due
    # time.sleep() takes seconds as parameter
    time.sleep(next_sampling_delta_t * 60)

    now = datetime.now()
    now_minute = now.minute + now.second / 60 + now.microsecond * 1e-6 / 60
    if next_sampling_group == "slow":
        minute_of_last_slow_sampling = now_minute
    print(f"{now.minute}:{now.second + now.microsecond * 1e-6}: Sampling '{next_sampling_group}'")

    data = data_of_metric_group(next_sampling_group)
    curr_values[next_sampling_group] = data
    print(curr_values)
    # print(data)

    # Repeat the same process
    sample(minute_of_last_slow_sampling)


# Start the infinite sampling loop
sample(minute_of_last_slow_sampling)
