import requests
from bs4 import BeautifulSoup
import re

def inspect_caredge():
    print("=== Inspecting CarEdge Acura Integra HTML ===")
    url = "https://caredge.com/acura/integra/maintenance"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Print the title, meta tags, and main content area if possible
    print("Title:", soup.title)
    # Print headings
    for h in soup.find_all(['h1', 'h2', 'h3']):
        print(f"  {h.name}: {repr(h.text.strip())}")
    
    # If there's an article or main tag, print its id/classes
    for tag in soup.find_all(['main', 'article', 'div']):
        if tag.get('id') or (tag.get('class') and 'content' in ''.join(tag.get('class'))):
            print(f"  {tag.name} (id={tag.get('id')}, class={tag.get('class')})")

def inspect_carcomplaints():
    print("=== Inspecting CarComplaints Honda Accord 2018 HTML ===")
    url = "https://www.carcomplaints.com/Honda/Accord/2018/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Find all <a> tags containing "Complaints"
    print("a tags containing Complaints:")
    for a in soup.find_all('a'):
        if 'complaint' in a.text.lower():
            print(f"  {a} -> text: {repr(a.text)}")

    # Let's find any text matching "complaints on file" or similar, case-insensitive
    text = soup.get_text()
    for line in text.split('\n'):
        if 'complaints' in line.lower() and ('file' in line.lower() or 'total' in line.lower() or 'number' in line.lower()):
            print("  Line:", repr(line.strip()))

if __name__ == "__main__":
    inspect_caredge()
    inspect_carcomplaints()
