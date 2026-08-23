import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_normal_data(n_rows=800, n_users=10):
    rows = []
    start_time = datetime(2026, 8, 1)
    for i in range(n_rows):
        user_id = f"user_{np.random.randint(1, n_users+1)}"
        rows.append({
            "timestamp": (start_time + timedelta(hours=i)).isoformat(),
            "user_id": user_id,
            "device_id": f"device_{user_id}",
            "bp_systolic": int(np.random.normal(115, 10)),
            "bp_diastolic": int(np.random.normal(75, 8)),
            "symptom_severity": np.random.randint(0, 5),
            "food_glycemic_load": round(np.random.uniform(10, 80), 1),
            "signature_valid": True
        })
    return pd.DataFrame(rows)

def inject_bad_rows(df, n_bad=30):
    bad_rows = []
    start_time = datetime(2026, 8, 1)
    for i in range(n_bad):
        bad_type = np.random.choice(["impossible_bp", "spoofed_device", "missing_field"])
        row = {
            "timestamp": (start_time + timedelta(hours=800+i)).isoformat(),
            "user_id": f"user_{np.random.randint(1, 11)}",
            "device_id": "device_unknown" if bad_type == "spoofed_device" else f"device_user_{np.random.randint(1,11)}",
            "bp_systolic": int(np.random.choice([40, 250, -5])) if bad_type == "impossible_bp" else int(np.random.normal(115, 10)),
            "bp_diastolic": int(np.random.choice([20, 150])) if bad_type == "impossible_bp" else int(np.random.normal(75, 8)),
            "symptom_severity": np.random.randint(0, 5),
            "food_glycemic_load": round(np.random.uniform(10, 80), 1) if bad_type != "missing_field" else None,
            "signature_valid": False if bad_type == "spoofed_device" else True
        }
        bad_rows.append(row)
    return pd.DataFrame(bad_rows)

if __name__ == "__main__":
    normal_df = generate_normal_data()
    bad_df = inject_bad_rows(normal_df)
    full_df = pd.concat([normal_df, bad_df], ignore_index=True)
    full_df.to_csv("data/synthetic_vitals.csv", index=False)
    print(f"Generated {len(normal_df)} normal rows + {len(bad_df)} bad rows")
    print(f"Saved to data/synthetic_vitals.csv")