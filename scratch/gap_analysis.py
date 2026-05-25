#!/usr/bin/env python3
"""
Deep gap analysis: for each source, print which models are missing data
and try to cluster them by likely reason (discontinued brand, BYD, no image, etc.)
"""
import json
from collections import defaultdict

DISCONTINUED_MAKES = {
    'Oldsmobile', 'Saturn', 'Pontiac', 'Plymouth', 'Mercury', 'Hummer',
    'Saab', 'Suzuki', 'Scion', 'Isuzu', 'Daewoo', 'Eagle', 'Geo'
}

FIELDS = [
    ("annual_repair_cost",       "RepairPal cost"),
    ("reliability_rating",       "RepairPal rating"),
    ("carcomplaints_count",      "CarComplaints count"),
    ("worst_year",               "CarComplaints worst year"),
    ("recall_count",             "NHTSA recalls"),
    ("complaint_count",          "NHTSA complaints"),
    ("city_mpg",                 "FuelEconomy MPG"),
    ("canadian_price_estimates", "VMR Canada pricing"),
    ("nhtsa_overall_rating",     "Safety rating"),
    ("ten_year_maintenance_cost","CarEdge maintenance"),
    ("historical_reliability",   "Dashboard Light"),
    ("data_year",                "Year resolved"),
]

with open("aggregated_reliability.json") as f:
    data = json.load(f)

total = len(data)

print(f"\n{'='*80}")
print(f"  DEEP GAP ANALYSIS — {total} models")
print(f"{'='*80}\n")

for field_key, field_label in FIELDS:
    missing = [(k, v) for k, v in data.items() if v.get(field_key) is None]
    if not missing:
        print(f"✅ {field_label}: 100% coverage\n")
        continue

    # Cluster by likely reason
    byd = [k for k, v in missing if k.startswith("BYD_")]
    discontinued = [k for k, v in missing if any(k.startswith(m+"_") for m in DISCONTINUED_MAKES)]
    no_year = [k for k, v in missing if v.get("data_year") is None and not k.startswith("BYD_")]
    has_year = [k for k, v in missing if v.get("data_year") is not None and not k.startswith("BYD_")]

    print(f"❌ {field_label}: {len(missing)}/{total} missing ({len(missing)/total*100:.1f}%)")
    if byd:
        print(f"   • BYD (separate pipeline): {len(byd)}")
    if discontinued:
        print(f"   • Discontinued makes: {len(discontinued)}")
        for k in sorted(discontinued):
            print(f"       - {k}")
    if no_year:
        print(f"   • No year could be resolved: {len(no_year)}")
        for k in sorted(no_year):
            print(f"       - {k} (fields: {[fk for fk,_ in FIELDS if data[k].get(fk) is not None]})")
    if has_year:
        remaining = [k for k in has_year if k not in [x for x in byd+discontinued+no_year]]
        if remaining:
            print(f"   • Has year but still missing ({len(remaining)} models — may be fixable):")
            for k in sorted(remaining)[:30]:
                yr = data[k].get('data_year','?')
                print(f"       - {k} (year={yr})")
            if len(remaining) > 30:
                print(f"       ... and {len(remaining)-30} more")
    print()

# Summary: models with 0 data at all
empty = [(k, v) for k, v in data.items() if sum(1 for fk,_ in FIELDS if v.get(fk) is not None) == 0]
print(f"\n{'='*80}")
print(f"  Models with ZERO data fields: {len(empty)}")
for k, v in empty:
    print(f"    - {k}")

# Models missing ONLY RepairPal (otherwise well-covered)
rp_only = [(k,v) for k,v in data.items()
           if v.get("annual_repair_cost") is None
           and v.get("city_mpg") is not None
           and v.get("worst_year") is not None]
print(f"\n  Models missing ONLY RepairPal cost (but otherwise covered): {len(rp_only)}")
for k, v in sorted(rp_only)[:40]:
    yr = v.get('data_year','?')
    print(f"    - {k} (year={yr})")
if len(rp_only) > 40:
    print(f"    ... and {len(rp_only)-40} more")
print(f"{'='*80}\n")
