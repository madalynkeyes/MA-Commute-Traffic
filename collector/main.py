import csv
import json
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

TOMTOM_KEY = os.environ["TOMTOM_KEY"]
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
SEGMENTS_PATH = "collector/segments.csv"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "data")


def load_segments(path):
    """Read segments.csv and return a list of dicts, one per segment."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def fetch_segment(segment, key):
    """Call TomTom for one segment and return its flowSegmentData dict."""
    r = requests.get(TOMTOM_URL, params={"key": key, "point": f"{segment['lat']},{segment['lon']}", "unit": "mph"}, timeout=10)
    r.raise_for_status()
    d = r.json()["flowSegmentData"]
    return d


def write_jsonl(records, path):
    """Write a list of dicts to a file, one JSON object per line."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

from google.cloud import storage

GCS_BUCKET = os.environ["GCS_BUCKET"]

def upload_to_gcs(local_path, bucket_name, blob_name):
    """Upload a local file to Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    return f"gs://{bucket_name}/{blob_name}"

def main():
    collected_at = datetime.now(timezone.utc)
    segments = [s for s in load_segments(SEGMENTS_PATH) if not s["active_to"]]

    records = []
    succeeded, failed = 0, 0

    for segment in segments:
        try:
            d = fetch_segment(segment,TOMTOM_KEY)
            records.append({"segment_id": segment["segment_id"], "collected_at": collected_at.isoformat(),"response": d, "error": None})
            succeeded += 1
        except Exception as e:
            failed += 1
            print(f"{segment['segment_id']} failed: {e}")
            records.append({
                "segment_id": segment["segment_id"],
                "collected_at": collected_at.isoformat(),
                "response": None,
                "error": str(e),
            })

    filename = f"{collected_at.strftime('%Y%m%dT%H%MZ')}.jsonl"
    output_path = os.path.join(OUTPUT_DIR, filename)

    write_jsonl(records, output_path)
    print(f"Wrote {len(records)} records to {output_path} ({succeeded} ok, {failed} failed)")
    blob_name = f"raw/dt={collected_at.strftime('%Y-%m-%d')}/{filename}"
    gcs_path = upload_to_gcs(output_path, GCS_BUCKET, blob_name)
    print(f"Uploaded to {gcs_path}")


if __name__ == "__main__":
    main()