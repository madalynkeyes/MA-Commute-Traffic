import csv, json, os, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["TOMTOM_KEY"]
URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

features, seen = [], {}
with open("collector/segments.csv") as f:
    for row in csv.DictReader(f):
        r = requests.get(URL, params={"key": KEY, "point": f"{row['lat']},{row['lon']}", "unit": "mph"}, timeout=10)
        r.raise_for_status()
        d = r.json()["flowSegmentData"]
        coords = [[c["longitude"], c["latitude"]] for c in d["coordinates"]["coordinate"]]
        ends = (tuple(coords[0]), tuple(coords[-1]))
        if ends in seen:
            print(f"WARNING: {row['segment_id']} is the same segment as {seen[ends]}")
        seen[ends] = row["segment_id"]
        print(f"{row['segment_id']}: {d['frc']}, {d['currentSpeed']} mph")
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"segment_id": row["segment_id"], "frc": d["frc"]},
        })

with open("segments_check.geojson", "w") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f)
print("Drag segments_check.geojson onto geojson.io to see the segments.")