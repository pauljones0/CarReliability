import requests
import json
import re
from bs4 import BeautifulSoup

def debug_repairpal():
    print("=== Debugging RepairPal ===")
    url = "https://repairpal.com/reliability/acura/integra"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("RepairPal Status:", res.status_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Let's search for "out of 5.0" in the text
    text = soup.get_text()
    rating_matches = re.findall(r'\d\.\d out of 5\.0', text)
    print("All 'out of 5.0' text matches:", rating_matches)
    
    # Search for all elements with class 'body-bold'
    body_bold_elems = soup.find_all(class_='body-bold')
    print("body-bold elements containing digits:")
    for el in body_bold_elems:
        if any(c.isdigit() for c in el.text):
            print("  -", repr(el.text.strip()))

def debug_carcomplaints():
    print("=== Debugging CarComplaints ===")
    url = "https://www.carcomplaints.com/Honda/Accord/2018/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("CarComplaints Status:", res.status_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Let's search for "complaints" or "on file"
    text = soup.get_text()
    matches = re.findall(r'.{0,50}complaints on file for the.{0,50}', text)
    print("Text matches for complaints on file:")
    for m in matches:
        print("  -", repr(m))
        
    # Let's look for how the number of complaints is presented on the page
    # Let's print some dd or dt elements or headers
    print("Looking for headers/divs related to complaint counts:")
    for h in soup.find_all(['h1', 'h2', 'h3', 'div', 'p']):
        if 'complaints' in h.text.lower() and any(c.isdigit() for c in h.text):
            print("  -", h.name, repr(h.text.strip()[:100]))

def debug_caredge():
    print("=== Debugging CarEdge ===")
    # Acura Integra
    url = "https://caredge.com/acura/integra/maintenance"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("CarEdge Acura Integra Status:", res.status_code)
    # If 404, maybe let's search if caredge has Acura Integra
    
def debug_safety():
    print("=== Debugging Safety Ratings ===")
    url = "https://api.nhtsa.gov/SafetyRatings/modelyear/2000/make/acura/model/integra"
    res = requests.get(url)
    print("Safety Ratings API Status:", res.status_code)
    if res.status_code == 200:
        print("Response JSON:", res.json())

def debug_fueleconomy():
    print("=== Debugging Fuel Economy ===")
    # 2006 Mercury Montego
    url = "https://www.fueleconomy.gov/ws/rest/vehicle/menu/options"
    params = {'year': 2006, 'make': 'Mercury', 'model': 'Montego'}
    headers = {'Accept': 'application/json'}
    res = requests.get(url, params=params, headers=headers)
    print("Fuel Economy Status:", res.status_code)
    print("Response JSON:", res.json() if res.status_code == 200 else res.text)

if __name__ == "__main__":
    debug_repairpal()
    debug_carcomplaints()
    debug_caredge()
    debug_safety()
    debug_fueleconomy()
