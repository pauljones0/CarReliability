#!/usr/bin/env python3
"""
Coverage analysis for aggregated_reliability.json.
Prints a table of field coverage percentages.
"""
import json
import sys

FIELDS = [
    ("historical_reliability",      "Dashboard Light"),
    ("annual_repair_cost",          "RepairPal cost"),
    ("reliability_rating",          "RepairPal rating"),
    ("worst_year",                  "CarComplaints worst year"),
    ("worst_category",              "CarComplaints worst cat"),
    ("carcomplaints_count",         "CarComplaints count"),
    ("recall_count",                "NHTSA recalls"),
    ("complaint_count",             "NHTSA complaints"),
    ("city_mpg",                    "FuelEconomy MPG"),
    ("canadian_price_estimates",    "VMR Canada pricing"),
    ("ten_year_maintenance_cost",   "CarEdge maintenance"),
    ("nhtsa_overall_rating",        "Safety rating"),
    ("data_year",                   "Year resolved (non-BYD)"),
]

path = sys.argv[1] if len(sys.argv) > 1 else "aggregated_reliability.json"

with open(path) as f:
    data = json.load(f)

total = len(data)
print(f"\n{'='*70}")
print(f"  Coverage report — {total} models total")
print(f"  Source: {path}")
print(f"{'='*70}")
print(f"  {'Field':<32} {'Count':>6}  {'Coverage':>8}")
print(f"  {'-'*32}  {'-'*6}  {'-'*8}")

for key, label in FIELDS:
    count = sum(1 for v in data.values() if v.get(key) is not None)
    pct = count / total * 100
    bar = "▓" * int(pct / 5)
    print(f"  {label:<32} {count:>6}  {pct:>7.1f}%  {bar}")

# Overall: models with >= 5 fields populated
complete = sum(1 for v in data.values() if sum(1 for k, _ in FIELDS if v.get(k) is not None) >= 5)
print(f"\n  Models with ≥5 fields populated: {complete}/{total} ({complete/total*100:.1f}%)")
print(f"{'='*70}\n")
