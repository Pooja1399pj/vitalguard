"""
Agent 5: Personal Insight
Runs a lightweight statistical correlation over the user's own synthetic
readings, then generates a plain-language, non-diagnostic explanation
using a rule-based template (Gemini API integration ready but billing
pending -- this template mirrors the same reasoning approach).
"""
import pandas as pd

FEATURES = ["food_glycemic_load", "symptom_severity"]

def compute_correlation(df: pd.DataFrame, user_id: str) -> dict:
    user_df = df[df["user_id"] == user_id].dropna(subset=FEATURES)
    if len(user_df) < 5:
        return {"user_id": user_id, "correlation": None, "n_readings": len(user_df)}

    corr = user_df["food_glycemic_load"].corr(user_df["symptom_severity"])
    return {
        "user_id": user_id,
        "correlation": round(corr, 3),
        "n_readings": len(user_df),
        "avg_glycemic_load": round(user_df["food_glycemic_load"].mean(), 1),
        "avg_symptom_severity": round(user_df["symptom_severity"].mean(), 2)
    }

def generate_insight(stats: dict) -> str:
    """
    Template-based plain-language insight generator.
    Mirrors the same non-diagnostic, observational framing that would
    be sent to Gemini -- swap this function for a live Gemini call
    once API billing is active, same input/output contract.
    """
    corr = stats["correlation"]
    n = stats["n_readings"]
    avg_glycemic = stats["avg_glycemic_load"]
    avg_symptom = stats["avg_symptom_severity"]

    if corr is None:
        return "Not enough logged readings yet to identify a pattern. Keep tracking for a few more days."

    if corr > 0.3:
        strength = "a noticeable pattern"
        direction = "higher glycemic-load days tend to line up with more symptom flares"
        suggestion = "you might gently experiment with lower-glycemic meals on days you want to feel your best."
    elif corr < -0.3:
        strength = "an interesting pattern"
        direction = "your symptom severity tends to be lower on higher glycemic-load days"
        suggestion = "this could be worth discussing with a doctor, since it runs against the usual expectation."
    else:
        strength = "no strong pattern"
        direction = "your food glycemic load and symptom severity don't show a clear relationship"
        suggestion = "other factors (sleep, stress, cycle phase) might be more relevant to track alongside food."

    return (
        f"Based on your last {n} logged readings, we noticed {strength}: "
        f"{direction} (average glycemic load {avg_glycemic}, average symptom severity {avg_symptom}/4). "
        f"This is just an observed trend in your own data, not a diagnosis -- {suggestion}"
    )

def run_agent5(input_csv="data/synthetic_vitals.csv", user_id="user_2"):
    df = pd.read_csv(input_csv)
    stats = compute_correlation(df, user_id)

    print(f"=== Statistical finding for {user_id} ===")
    print(stats)

    print("\n=== Generated insight ===")
    insight = generate_insight(stats)
    print(insight)

if __name__ == "__main__":
    run_agent5()
