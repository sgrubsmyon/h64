#!/usr/bin/env python3

from datetime import datetime
import numpy as np

interval_fast = 10 # seconds
interval_slow = 5 * 60 # minutes

now = datetime.now()
now_second = now.second + now.microsecond * 1e-6
print(now_second)
now_minute = now.minute
print(now_minute)

next_round_seconds_interval = np.ceil(now_second / 10) * 10
print(next_round_seconds_interval)
# seconds_until_10 =
