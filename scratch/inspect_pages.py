import requests
from bs4 import BeautifulSoup
import re

def inspect_caredge_integra():
    print("=== Inspecting CarEdge Acura Integra ===")
    url = "https://caredge.com/acura/integra/maintenance"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    print("Status:", res.status_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    text = soup.get_text()
    
    print("Length of text:", len(text))
    # Let's see if we can find any numbers like $ or percentage
    dollars = re.findall(r'\$[\d,]+', text)
    print("Dollar amounts found:", dollars[:20])
    percentages = re.findall(r'\d+(?:\.\d+)?%', text)
    print("Percentages found:", percentages[:20])
    
    # Print some paragraphs containing 'cost'
    for p in soup.find_all('p'):
        p_text = p.get_text().strip()
        if 'cost' in p_text.lower() or 'maintenance' in p_text.lower():
            print("  P:", repr(p_text[:150]))

def inspect_carcomplaints_accord():
    print("=== Inspecting CarComplaints Honda Accord 2018 ===")
    url = "https://www.carcomplaints.com/Honda/Accord/2018/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Search for any paragraph or span containing 'complaint' or 'NHTSA'
    print("Searching text elements containing complaints:")
    count = 0
    for tag in soup.find_all(['p', 'span', 'h1', 'h2', 'h3', 'a', 'td', 'th', 'div']):
        text = tag.get_text().strip()
        if 'complaint' in text.lower():
            # If it's a short text or contains digits
            if len(text) < 150 and any(c.isdigit() for c in text):
                print(f"  {tag.name}: {repr(text)}")
                count += 1
                if count > 15:
                    break

if __name__ == "__main__":
    inspect_caredge_integra()
    inspect_carcomplaints_accord()
