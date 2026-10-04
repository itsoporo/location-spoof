#!/usr/bin/env python3
"""
generate_route_gpx.py

Creates a GPX file with timestamped waypoints tracing a straight line
between two coordinates, at a chosen speed. Feed the result into:

    pymobiledevice3 developer dvt simulate-location play route.gpx

EDIT THE VARIABLES BELOW, or pass them as command-line args:
    python3 generate_route_gpx.py <start_lat> <start_lon> <end_lat> <end_lon> [speed_kmh] [output.gpx]
"""

import sys
import math
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------
# CONFIGURABLE DEFAULTS
# ---------------------------------------------------------------------
START_LAT = 30.61555329099483    # Islamabad
START_LON = -96.3457213995742
END_LAT = 30.5909008
END_LON = -96.3363027
SPEED_KMH = 20         # simulated driving speed
POINT_INTERVAL_SECONDS = 1  # how often a waypoint is placed (smoothness)
OUTPUT_FILE = "route.gpx"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def build_gpx(start_lat, start_lon, end_lat, end_lon, speed_kmh, interval_s, out_path):
    distance_km = haversine_km(start_lat, start_lon, end_lat, end_lon)
    total_seconds = (distance_km / speed_kmh) * 3600
    num_points = max(2, int(total_seconds / interval_s))

    now = datetime.now(timezone.utc)

    trkpts = []
    for i in range(num_points + 1):
        frac = i / num_points
        lat = start_lat + (end_lat - start_lat) * frac
        lon = start_lon + (end_lon - start_lon) * frac
        t = now + timedelta(seconds=i * interval_s)
        t_str = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        trkpts.append(f'      <trkpt lat="{lat:.7f}" lon="{lon:.7f}"><time>{t_str}</time></trkpt>')

    gpx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="generate_route_gpx.py" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Simulated Drive</name>
    <trkseg>
{chr(10).join(trkpts)}
    </trkseg>
  </trk>
</gpx>
"""
    with open(out_path, "w") as f:
        f.write(gpx_content)

    print(f"Wrote {num_points + 1} waypoints to {out_path}")
    print(f"Distance: {distance_km:.2f} km, duration: {total_seconds/60:.1f} minutes at {speed_kmh} km/h")


def main():
    args = sys.argv[1:]
    start_lat, start_lon, end_lat, end_lon = START_LAT, START_LON, END_LAT, END_LON
    speed_kmh, out_path = SPEED_KMH, OUTPUT_FILE

    if len(args) >= 4:
        start_lat, start_lon, end_lat, end_lon = map(float, args[0:4])
    if len(args) >= 5:
        speed_kmh = float(args[4])
    if len(args) >= 6:
        out_path = args[5]

    build_gpx(start_lat, start_lon, end_lat, end_lon, speed_kmh, POINT_INTERVAL_SECONDS, out_path)


if __name__ == "__main__":
    main()
