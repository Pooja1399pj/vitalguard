"""
Agent 2: Data Sanity (ML)
Uses Isolation Forest to detect anomalous vitals readings —
both universally impossible values AND statistically unusual patterns.
"""

import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["bp_systolic", "bp_diastolic", "symptom_severity", "food_glycemic_load"]

def train_model(df):
    """Train Isolation Forest on the feature set."""
    clean_df = df.dropna(subset=FEATURES)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(clean_df[FEATURES])
    return model

def run_agent2(input_csv="data/stage1_passed.csv", output_csv="data/stage2_passed.csv", flagged_csv="data/stage2_flagged.csv"):
    df = pd.read_csv(input_csv)

    # Drop rows with missing critical fields first (hard rule, not ML)
    missing_mask = df[FEATURES].isna().any(axis=1)
    hard_rejected = df[missing_mask].copy()
    df_clean = df[~missing_mask].copy()

    # Hard physiological range check (before ML — catches obvious impossible values)
    def is_physiologically_impossible(row):
        return not (60 <= row["bp_systolic"] <= 200 and 30 <= row["bp_diastolic"] <= 130)

    df_clean["hard_range_fail"] = df_clean.apply(is_physiologically_impossible, axis=1)

    range_ok = df_clean[df_clean["hard_range_fail"] == False].copy()
    range_fail = df_clean[df_clean["hard_range_fail"] == True].copy()

    # ML anomaly detection on the remaining plausible-range data
    model = train_model(range_ok)
    range_ok["anomaly_score"] = model.decision_function(range_ok[FEATURES])
    range_ok["is_anomaly"] = model.predict(range_ok[FEATURES])  # -1 = anomaly, 1 = normal

    passed = range_ok[range_ok["is_anomaly"] == 1].copy()
    ml_flagged = range_ok[range_ok["is_anomaly"] == -1].copy()

    all_flagged = pd.concat([hard_rejected, range_fail, ml_flagged], ignore_index=True)

    passed.to_csv(output_csv, index=False)
    all_flagged.to_csv(flagged_csv, index=False)

    print(f"Agent 2 — Data Sanity (ML)")
    print(f"  Input rows: {len(df)}")
    print(f"  Missing-field rejects: {len(hard_rejected)}")
    print(f"  Impossible-range rejects: {len(range_fail)}")
    print(f"  ML-flagged anomalies: {len(ml_flagged)}")
    print(f"  Passed: {len(passed)}")
    print(f"  Saved passed -> {output_csv}")
    print(f"  Saved flagged -> {flagged_csv}")

    return passed, all_flagged


if __name__ == "__main__":
    run_agent2()
