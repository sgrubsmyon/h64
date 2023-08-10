#!/usr/bin/env python3

from datetime import datetime
import numpy as np

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

sampling_points = {} # sampling points are in minutes (within any one hour)
for group in start_point:
    minute_startpoint = start_point[group][0] + start_point[group][1] / 60
    minute_interval = interval[group][0] + interval[group][1] / 60
    sampling_points[group] = np.arange(
        minute_startpoint, 60, minute_interval)

now = datetime.now()
now_minute = now.minute + now.second / 60 + now.microsecond * 1e-6 / 60
print("now:", now_minute)

closest_sampling_point = {}
for group in sampling_points:
    delta_ts = sampling_points[group] - now_minute
    # Remove sampling points of the past (negative time difference delta_t)
    delta_ts = delta_ts[delta_ts > 0]
    delta_t = np.min(delta_ts)
    closest_sampling_point[group] = delta_t
next_sampling_group = min(closest_sampling_point, key=closest_sampling_point.get)
next_sampling_delta_t = closest_sampling_point[next_sampling_group]
next_sampling_minute = now_minute + next_sampling_delta_t
next_sampling_full_minute = int(np.floor(next_sampling_minute))
next_sampling_full_second = (next_sampling_minute - next_sampling_full_minute) * 60
print(f"next sampling: group {next_sampling_group} at {next_sampling_full_minute}:{next_sampling_full_second}")
