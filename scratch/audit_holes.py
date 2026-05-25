import json
import requests
from bs4 import BeautifulSoup

def audit_holes():
    with open('aggregated_reliability.json') as f:
        data = json.load(f)

    missing_vmr = []
    missing_safety = []
    missing_mpg = []
    missing_rp = []
    missing_cc = []

    for model_key, mdata in data.items():
        make, model = model_key.split('_', 1)
        year = mdata.get('data_year')
        
        if 'canadian_price_estimates' not in mdata:
            missing_vmr.append((make, model, year))
        if 'nhtsa_overall_rating' not in mdata:
            missing_safety.append((make, model, year))
        if 'city_mpg' not in mdata:
            missing_mpg.append((make, model, year))
        if 'annual_repair_cost' not in mdata:
            missing_rp.append((make, model, year))
        if 'carcomplaints_count' not in mdata:
            missing_cc.append((make, model, year))

    print(f"Total models in json: {len(data)}")
    print(f"Missing VMR Canada pricing: {len(missing_vmr)}")
    print(f"  Samples: {missing_vmr[:15]}")
    print(f"Missing Safety ratings: {len(missing_safety)}")
    print(f"  Samples: {missing_safety[:15]}")
    print(f"Missing Fuel Economy MPG: {len(missing_mpg)}")
    print(f"  Samples: {missing_mpg[:15]}")
    print(f"Missing RepairPal: {len(missing_rp)}")
    print(f"  Samples: {missing_rp[:15]}")
    print(f"Missing CarComplaints Count: {len(missing_cc)}")
    print(f"  Samples: {missing_cc[:15]}")

if __name__ == "__main__":
    audit_holes()
