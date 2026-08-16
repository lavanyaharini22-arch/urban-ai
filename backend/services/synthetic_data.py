"""
Generates realistic synthetic sensor data and demo images so the
application always has something to run on, even with no real dataset.
Never crashes due to a missing dataset — falls back to DEMO MODE.
"""
import random
import time
from models.sensor_net import FEATURE_STATS


def generate_synthetic_reading(scenario: str = "random") -> dict:
    """scenario: 'random' | 'flood' | 'pollution' | 'normal'"""
    reading = {}
    for feat, (mean, std) in FEATURE_STATS.items():
        reading[feat] = round(random.gauss(mean, std), 2)

    if scenario == "flood":
        reading["rainfall"] = round(random.uniform(40, 90), 2)
        reading["humidity"] = round(random.uniform(80, 98), 2)
    elif scenario == "pollution":
        reading["pm25"] = round(random.uniform(150, 300), 2)
        reading["aqi"] = round(random.uniform(200, 400), 2)
    elif scenario == "normal":
        reading["rainfall"] = round(random.uniform(0, 3), 2)
        reading["aqi"] = round(random.uniform(20, 60), 2)

    reading["timestamp"] = int(time.time())
    return reading


def generate_time_series(n=24, scenario="random"):
    return [generate_synthetic_reading(scenario) for _ in range(n)]
