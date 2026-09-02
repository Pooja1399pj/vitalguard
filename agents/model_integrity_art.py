"""
Agent 3: Model Integrity
Defends the Agent 2 Isolation Forest model against adversarial evasion —
demonstrates a crafted attack fooling the undefended model, then shows
detection/defense catching it by monitoring rate-of-change between
consecutive readings from the same device/user.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

FEATURES = ["bp_systolic", "bp_diastolic", "symptom_severity", "food_glycemic_load"]

def train_baseline_model(df):
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(df[FEATURES])
    return model

def craft_adversarial_sample(base_row, epsilon_systolic=70, epsilon_diastolic=40):
    adv_row = base_row.copy()
    adv_row["bp_systolic"] = adv_row["bp_systolic"] - epsilon_systolic
    adv_row["bp_diastolic"] = adv_row["bp_diastolic"] - epsilon_diastolic
    return adv_row

def rate_of_change_check(prev_row, new_row, max_plausible_systolic_drop=30, max_plausible_diastolic_drop=20):
    """
    Real physiological BP does not swing 70+ points between consecutive
    readings minutes/hours apart. A jump larger than this is itself
    suspicious -- a signature of tampering/adversarial injection,
    regardless of whether the new value looks 'normal' on its own.
    """
    systolic_drop = prev_row["bp_systolic"] - new_row["bp_systolic"]
    diastolic_drop = prev_row["bp_diastolic"] - new_row["bp_diastolic"]
    return (systolic_drop > max_plausible_systolic_drop) or (diastolic_drop > max_plausible_diastolic_drop)

def confidence_signature_check(score_before, score_after, threshold_shift=0.05):
    return (score_after - score_before) > threshold_shift

def run_agent3(input_csv="data/stage2_passed.csv"):
    df = pd.read_csv(input_csv)
    model = train_baseline_model(df)

    dangerous_row = {
        "bp_systolic": 195, "bp_diastolic": 125,
        "symptom_severity": 4, "food_glycemic_load": 75.0
    }
    dangerous_df = pd.DataFrame([dangerous_row])

    print("=== BEFORE ATTACK ===")
    score_before = model.decision_function(dangerous_df[FEATURES])[0]
    pred_before = model.predict(dangerous_df[FEATURES])[0]
    print(f"Original reading: {dangerous_row}")
    print(f"Anomaly score: {score_before:.4f} | Prediction: {'ANOMALY' if pred_before == -1 else 'NORMAL'}")

    adv_row = craft_adversarial_sample(dangerous_row)
    adv_df = pd.DataFrame([adv_row])

    print("\n=== AFTER ADVERSARIAL PERTURBATION (attack) ===")
    score_after = model.decision_function(adv_df[FEATURES])[0]
    pred_after = model.predict(adv_df[FEATURES])[0]
    print(f"Perturbed reading (claimed to be the SAME patient, moments later): {adv_row}")
    print(f"Anomaly score: {score_after:.4f} | Prediction: {'ANOMALY' if pred_after == -1 else 'NORMAL'}")

    attack_succeeded = (pred_before == -1 and pred_after == 1)
    if attack_succeeded:
        print("\n⚠️  ATTACK SUCCEEDED on the anomaly-detector-only pipeline — misclassified as NORMAL")
    else:
        print("\n(Model alone still caught it, no bypass this run)")

    print("\n=== AGENT 3 DEFENSE (rate-of-change + score-shift monitoring) ===")
    suspicious_shift = confidence_signature_check(score_before, score_after)
    suspicious_jump = rate_of_change_check(dangerous_row, adv_row)

    if suspicious_shift or suspicious_jump:
        print("🛡️  Agent 3 flagged this as a SUSPECTED ADVERSARIAL EVASION ATTEMPT")
        if suspicious_jump:
            print(f"    Reason: implausible reading swing for the same device "
                  f"(systolic {dangerous_row['bp_systolic']} -> {adv_row['bp_systolic']}, "
                  f"diastolic {dangerous_row['bp_diastolic']} -> {adv_row['bp_diastolic']})")
        if suspicious_shift:
            print(f"    Reason: anomaly score shifted sharply ({score_before:.4f} -> {score_after:.4f})")
        print("    Action: reading routed to manual review, NOT auto-accepted as normal")
    else:
        print("No adversarial signature detected.")

if __name__ == "__main__":
    run_agent3()
