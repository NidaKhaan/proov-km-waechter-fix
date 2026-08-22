# analyze.py
# The two factors that actually predict a breakdown are km_since_service and avg_daily_km.
# Total mileage and age look obvious but the data shows no meaningful difference between
# cars that broke down and cars that did not on those columns (+0.3% and -0.2% mean gap).
# km_since_service alone explains most of the risk: cars in the highest quartile broke down
# at a 56.7% rate vs 3.3% for recently-serviced cars — a 17x gap. avg_daily_km adds a clear
# secondary signal (6.7% low-usage rate vs 43.3% high-usage). load_factor has a modest
# gradient. age_years and odometer_km are noise.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# ── Step 1: Compare the two groups column by column ──────────────────────────
broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

print("=== Group comparison: broke-down vs did-not ===")
print(f"  Cars that broke down : {len(broke)}")
print(f"  Cars that did not    : {len(ok)}")
print()

cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
print(f"{'Column':<20} {'Mean(broke)':>12} {'Mean(ok)':>12} {'Gap':>8}  Verdict")
print("-" * 72)
SIGNAL_THRESHOLD = 15.0   # treat a >15% mean gap as a meaningful signal
signals = []
for c in cols:
    mb = broke[c].mean()
    mo = ok[c].mean()
    gap = (mb - mo) / mo * 100
    verdict = "SIGNAL" if abs(gap) >= SIGNAL_THRESHOLD else "noise"
    if abs(gap) >= SIGNAL_THRESHOLD:
        signals.append(c)
    print(f"{c:<20} {mb:>12.1f} {mo:>12.1f} {gap:>+7.1f}%  {verdict}")

print()
print(f"Columns that separate the groups (>{SIGNAL_THRESHOLD}% mean gap):")
for s in signals:
    print(f"  • {s}")
print()

# ── Step 2: Breakdown rate by quartile (shows the shape of each signal) ──────
print("=== Breakdown rate by quartile ===")
for c in signals:
    labels = ["Q1(low)", "Q2", "Q3", "Q4(high)"]
    df[f"_q_{c}"] = pd.qcut(df[c], 4, labels=labels, duplicates="drop")
    rates = df.groupby(f"_q_{c}", observed=True)["broke_down"].mean()
    print(f"\n  {c}:")
    for q, r in rates.items():
        bar = "#" * int(r * 30)
        print(f"    {q:<10} {r:.1%}  {bar}")
print()

# ── Step 3: Build a 0-to-100 risk score ──────────────────────────────────────
# Min-max normalise each signal column to [0, 1], then average them.
# We use only km_since_service and avg_daily_km — the two with the clearest quartile
# gradient. load_factor has a weaker, less monotonic pattern so it is excluded.
score_cols = ["km_since_service", "avg_daily_km"]

df_score = df[["car_id", "broke_down"] + score_cols].copy()
for c in score_cols:
    lo, hi = df_score[c].min(), df_score[c].max()
    df_score[f"_norm_{c}"] = (df_score[c] - lo) / (hi - lo)

norm_cols = [f"_norm_{c}" for c in score_cols]
df_score["risk_score"] = (df_score[norm_cols].mean(axis=1) * 100).round(1)

# ── Step 4: Rank by risk, print top 10 ───────────────────────────────────────
ranked = df_score.sort_values("risk_score", ascending=False).reset_index(drop=True)
ranked.index += 1   # 1-based rank

print("=== Top 10 cars by risk score ===")
print(f"{'Rank':<5} {'Car ID':<12} {'Risk':>6}  {'km_since_svc':>13} {'avg_daily_km':>13}  {'Broke?':>7}")
print("-" * 60)
for rank, row in ranked.head(10).iterrows():
    broke_flag = "YES" if row["broke_down"] == 1 else "-"
    print(
        f"{rank:<5} {row['car_id']:<12} {row['risk_score']:>5.1f}  "
        f"{row['km_since_service']:>13,.0f} {row['avg_daily_km']:>13,.0f}  {broke_flag:>7}"
    )

print()
print("=== Summary ===")
top10_broke = ranked.head(10)["broke_down"].sum()
print(f"  Cars that actually broke down in the top 10: {top10_broke}/10")
baseline_rate = df["broke_down"].mean()
print(f"  Baseline breakdown rate across all 120 cars: {baseline_rate:.1%}")
print(f"  (A random pick of 10 would contain ~{baseline_rate*10:.1f} broken cars on average.)")
