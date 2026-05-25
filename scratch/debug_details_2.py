import requests
import re
from bs4 import BeautifulSoup

def debug_carcomplaints():
    url = "https://www.carcomplaints.com/Honda/Accord/2018/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Print first 2000 chars of body text
    print("=== CarComplaints Honda Accord 2018 body text snippet ===")
    print(soup.get_text()[:1500])

def debug_caredge():
    url = "https://caredge.com/acura/integra/maintenance"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("=== CarEdge Acura Integra Status ===", res.status_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Print the content of section#maintenance-outlook or any p containing maintenance
    print("=== CarEdge body text snippet ===")
    text = soup.get_text()
    for line in text.split('\n'):
        if 'maintenance' in line.lower() or 'repair' in line.lower():
            if len(line.strip()) > 10:
                print(line.strip()[:120])

def debug_fueleconomy():
    url = "https://www.fueleconomy.gov/ws/rest/vehicle/menu/options"
    params = {'year': 2006, 'make': 'Mercury', 'model': 'Montego'}
    headers = {'Accept': 'application/json'}
    res = requests.get(url, params=params, headers=headers)
    print("=== Fuel Economy raw response text ===")
    print(repr(res.text))
    print("Response status code:", res.status_code)

if __name__ == "__main__":
    debug_carcomplaints()
    debug_caredge()
    debug_fueleconomy()
