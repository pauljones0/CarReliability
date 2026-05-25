import json
import time
import requests
import re
from bs4 import BeautifulSoup

# Specific aliases dict from repairpal.py
ALIASES = {
    '1 series': '128i', '3 series': '328i', '5 series': '528i', '6 series': '650i', '7 series': '750i', '8 series': '850i',
    'c class': 'c300', 'c-class': 'c300', 'e class': 'e350', 'e-class': 'e350', 's class': 's550', 's-class': 's550',
    'm class': 'ml350', 'm-class': 'ml350', 'gl class': 'gl450', 'gl-class': 'gl450', 'sl class': 'sl500', 'sl-class': 'sl500',
    'slk class': 'slk280', 'slk-class': 'slk280', 'f series': 'f-150', 'f-series': 'f-150', 'e series': 'e-150', 'e-series': 'e-150',
    'g series': 'g20', '900 series': '940', 'm35h': 'm35', 'qx': 'qx56', 'hs': 'hs250h', 'defender': 'defender-90',
    'suburban': 'suburban-1500', 'c/k': 'c1500', 'rx': 'rx350', 'es': 'es350', 'gs': 'gs350', 'lx': 'lx570', 'is': 'is250',
    'ct': 'ct200h', 'transit': 'transit-connect', 'eighty eight': '88', 'eighty-eight': '88', 'ninety eight': '98', 'ninety-eight': '98',
    'xv': 'xv-crosstrek'
}

def query_repairpal(make, model):
    formatted_make = make.lower().replace(' ', '-')
    model_lower = model.lower().strip()
    
    if model_lower in ALIASES:
        formatted_model = ALIASES[model_lower]
    else:
        formatted_model = model_lower.replace(' ', '-')
        
    url = f"https://repairpal.com/reliability/{formatted_make}/{formatted_model}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code == 429:
        return "RATE_LIMITED", None
    if res.status_code != 200:
        return "NOT_FOUND", None
        
    soup = BeautifulSoup(res.content, 'html.parser')
    data = {}
    
    # Cost
    cost_text = soup.find(string=re.compile(r'average annual repair cost is'))
    if cost_text:
        match = re.search(r'\$(\d+)', cost_text)
        if match:
            data['annual_repair_cost'] = f"${match.group(1)}"
    
    if 'annual_repair_cost' not in data:
        cost_handle = soup.select_one('.slider-chart.cost .slider-handle-text')
        if cost_handle:
            data['annual_repair_cost'] = cost_handle.get_text(strip=True)

    # Rating
    rating_elem = soup.find('span', class_='body-bold', string=re.compile(r'\d\.\d out of 5\.0'))
    if rating_elem:
        data['reliability_rating'] = rating_elem.get_text(strip=True)
    else:
        rating_text = soup.find(string=re.compile(r'Reliability Rating is'))
        if rating_text:
            match = re.search(r'(\d\.\d out of 5\.0)', rating_text)
            if match:
                data['reliability_rating'] = match.group(1)
                
    return "SUCCESS", data

def fill_repairpal():
    with open('aggregated_reliability.json') as f:
        data = json.load(f)
        
    missing_models = [m for m, mdata in data.items() if 'annual_repair_cost' not in mdata]
    print(f"Total models missing annual_repair_cost: {len(missing_models)}")
    
    success_count = 0
    consecutive_429s = 0
    
    for i, model_key in enumerate(missing_models):
        parts = model_key.split('_', 1)
        if len(parts) != 2:
            continue
        make, model = parts
        
        # Strip Land Rover space if it's there
        print(f"[{i+1}/{len(missing_models)}] Fetching {make} {model}...")
        
        status, res_data = query_repairpal(make, model)
        
        if status == "RATE_LIMITED":
            print("  Hit 429 Rate Limit. Sleeping for 30 seconds...")
            consecutive_429s += 1
            if consecutive_429s > 3:
                print("  Too many consecutive 429s. Saving progress and aborting.")
                break
            time.sleep(30)
            # Try once more after sleep
            status, res_data = query_repairpal(make, model)
            if status == "RATE_LIMITED":
                print("  Still rate limited. Aborting.")
                break
            
        consecutive_429s = 0
        
        if status == "SUCCESS" and res_data:
            data[model_key].update(res_data)
            success_count += 1
            print(f"  Success: {res_data}")
            if success_count % 5 == 0:
                with open('aggregated_reliability.json', 'w') as out_f:
                    json.dump(data, out_f, indent=4)
        else:
            print(f"  Status: {status}")
            
        time.sleep(3.0) # Conservative delay to respect rate limit
        
    with open('aggregated_reliability.json', 'w') as out_f:
        json.dump(data, out_f, indent=4)
        
    print(f"Incremental update complete. Added {success_count} entries.")

if __name__ == "__main__":
    fill_repairpal()
