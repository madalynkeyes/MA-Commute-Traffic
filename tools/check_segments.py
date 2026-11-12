import csv, json, math, os, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["TOMTOM_KEY"]
URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"


def meters(a, b):
    """Approximate distance in meters between two [lon, lat] points."""
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(h))


with open("collector/segments.csv", newline="") as f:
    rows = sorted(csv.DictReader(f), key=lambda r: (r["trip"], int(r["seq"])))
    rows = [r for r in rows if not r["active_to"]]

features, seen, prev = [], {}, None
for row in rows:
    r = requests.get(URL, params={"key": KEY, "point": f"{row['lat']},{row['lon']}", "unit": "mph"}, timeout=10)
    r.raise_for_status()
    d = r.json()["flowSegmentData"]
    coords = [[c["longitude"], c["latitude"]] for c in d["coordinates"]["coordinate"]]

    ends = (tuple(coords[0]), tuple(coords[-1]))
    if ends in seen:
        print(f"  WARNING: {row['segment_id']} is the same segment as {seen[ends]}")
    seen[ends] = row["segment_id"]

    length = sum(meters(coords[i], coords[i + 1]) for i in range(len(coords) - 1))
    gap = ""
    if prev and prev["trip"] == row["trip"]:
        g = min(meters(prev["end"], coords[0]), meters(prev["end"], coords[-1]))
        gap = f", gap from previous: {g:.0f} m"
    print(f"{row['segment_id']}: {d['frc']}, {length:.0f} m{gap}")

    prev = {"trip": row["trip"], "end": coords[-1]}
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {"segment_id": row["segment_id"], "trip": row["trip"], "frc": d["frc"]},
    })

with open("segments_check.geojson", "w") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f)
print("Drag segments_check.geojson onto geojson.io to see the segments.")