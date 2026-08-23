"""
Agent 1: Device Integrity
Validates device signature/auth. Rejects spoofed or unsigned devices.
"""

import pandas as pd

def validate_device(row):
    """
    Checks if a reading comes from a legitimate, registered device.
    In production this would verify an HMAC signature using a per-device secret.
    Here, we use the synthetic 'signature_valid' flag + device_id pattern check
    to simulate that validation.
    """
    device_id = row.get("device_id", "")
    user_id = row.get("user_id", "")
    signature_valid = row.get("signature_valid", False)

    # Rule 1: signature must be valid
    if not signature_valid:
        return False, "Invalid or missing device signature"

    # Rule 2: device_id must match expected pattern for that user
    expected_device = f"device_{user_id}"
    if device_id != expected_device:
        return False, f"Device ID mismatch: expected {expected_device}, got {device_id}"

    return True, "OK"


def run_agent1(input_csv="data/synthetic_vitals.csv", output_csv="data/stage1_passed.csv", rejected_csv="data/stage1_rejected.csv"):
    df = pd.read_csv(input_csv)

    results = df.apply(validate_device, axis=1)
    df["agent1_pass"] = [r[0] for r in results]
    df["agent1_reason"] = [r[1] for r in results]

    passed = df[df["agent1_pass"] == True].copy()
    rejected = df[df["agent1_pass"] == False].copy()

    passed.to_csv(output_csv, index=False)
    rejected.to_csv(rejected_csv, index=False)

    print(f"Agent 1 — Device Integrity")
    print(f"  Total rows: {len(df)}")
    print(f"  Passed: {len(passed)}")
    print(f"  Rejected: {len(rejected)}")
    print(f"  Saved passed -> {output_csv}")
    print(f"  Saved rejected -> {rejected_csv}")

    return passed, rejected


if __name__ == "__main__":
    run_agent1()
