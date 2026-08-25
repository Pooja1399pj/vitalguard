"""
Subscribes to 'vitals-ingest-sub', runs each reading through
Agent 1 (Device Integrity) then Agent 2 (Data Sanity), and writes
the result to Firestore.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
from google.cloud import pubsub_v1, firestore
from agents.device_integrity import validate_device

load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = "vitals-ingest-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

db = firestore.Client(project=PROJECT_ID)

def process_message(message):
    data = json.loads(message.data.decode("utf-8"))
    print(f"\nReceived: {data['device_id']} | BP {data['bp_systolic']}/{data['bp_diastolic']}")

    passed, reason = validate_device(data)
    if not passed:
        print(f"  REJECTED by Agent 1: {reason}")
        db.collection("rejected_readings").add({**data, "reason": reason})
        message.ack()
        return

    bp_ok = 60 <= data["bp_systolic"] <= 200 and 30 <= data["bp_diastolic"] <= 130
    if not bp_ok:
        print(f"  REJECTED by Agent 2: BP out of physiological range")
        db.collection("rejected_readings").add({**data, "reason": "impossible BP range"})
        message.ack()
        return

    print(f"  PASSED all checks -> writing to Firestore")
    db.collection("valid_readings").add(data)
    message.ack()

def listen():
    print("Listening for messages on vitals-ingest-sub...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_message)
    try:
        streaming_pull_future.result(timeout=30)
    except Exception:
        streaming_pull_future.cancel()
        print("\nStopped listening.")

if __name__ == "__main__":
    listen()
