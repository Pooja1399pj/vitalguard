"""
Publishes synthetic vitals readings to Pub/Sub topic 'vitals-ingest'.
Simulates a wearable device streaming data.
"""
import json
import pandas as pd
from google.cloud import pubsub_v1
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_ID = "vitals-ingest"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_readings(csv_path="data/synthetic_vitals.csv", limit=20):
    df = pd.read_csv(csv_path)
    sample = df.head(limit)  # small batch for demo, not all 830 rows

    for _, row in sample.iterrows():
        data = row.to_dict()
        message_bytes = json.dumps(data, default=str).encode("utf-8")
        future = publisher.publish(topic_path, message_bytes)
        print(f"Published message ID: {future.result()} | device: {data['device_id']}")

if __name__ == "__main__":
    publish_readings()
