import requests
from bs4 import BeautifulSoup
import time
import re
from src.sources.base_source import BaseSource

class CarEdgeSource(BaseSource):
    BASE_URL = "https://caredge.com/{}/{}/maintenance"
    
    def __init__(self, delay=1):
        self.delay = delay

    def get_data(self, make, model, year=None):
        formatted_make = make.lower().replace(' ', '-')
        
        model_lower = model.lower().strip()
        aliases = {
            'silverado': 'silverado-1500',
            'sierra': 'sierra-1500',
            'ram': 'ram-1500',
            'f series': 'f-150',
            'e series': 'e-150',
            'c/k': 'silverado-1500',
            '3 series': '3-series',
            '5 series': '5-series',
            '7 series': '7-series',
            'c class': 'c-class',
            'e class': 'e-class',
            's class': 's-class',
            'm class': 'm-class',
            'gl class': 'gl-class',
            'sl class': 'sl-class',
            'slk class': 'slk-class',
            '8 series': '8-series',
            'm35h': 'q70',
            'qx': 'qx80',
            'hs': 'hs-250h',
            'defender': 'defender',
            'suburban': 'suburban',
            'rx': 'rx-350',
            'es': 'es-350',
            'gs': 'gs-350',
            'lx': 'lx-570',
            'is': 'is-250',
            'ct': 'ct-200h',
            '370z': 'z',
            '350z': 'z',
            'matrix': 'corolla', # approximation
            'integra': 'ilx',    # approximation for maintenance
            'tsx': 'tlx'         # approximation
        }
        
        if model_lower in aliases:
            formatted_model = aliases[model_lower]
        else:
            formatted_model = model_lower.replace(' ', '-')
            
        url = self.BASE_URL.format(formatted_make, formatted_model)
        
        try:
            time.sleep(self.delay)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            response = self._request(url, headers=headers)
            
            if not response or response.status_code != 200:
                # Try one fallback: sometimes they don't use the dash
                if '-' in formatted_model:
                    fallback_model = formatted_model.replace('-', '')
                    url = self.BASE_URL.format(formatted_make, fallback_model)
                    response = self._request(url, headers=headers)
                
            if not response or response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            if len(text) < 1000:
                # Likely blocked or empty page
                return None

            data = {}
            
            # Maintenance Cost - more flexible regex
            # Look for the pattern: "$X,XXX for maintenance"
            cost_match = re.search(r'(\$[\d,]+).*?for maintenance', text, re.I | re.S)
            if cost_match:
                data['ten_year_maintenance_cost'] = cost_match.group(1)
                
            # Major Repair Probability - more flexible regex
            # Look for the pattern: "XX.XX% chance"
            prob_match = re.search(r'([\d\.]+%)\s+chance.*?major repair', text, re.I | re.S)
            if prob_match:
                data['major_repair_probability'] = prob_match.group(1)
            
            # If regex fails, try selectors again as backup
            if not data:
                cost_elem = soup.select_one('section#maintenance-outlook p strong:nth-of-type(1)')
                if cost_elem:
                    data['ten_year_maintenance_cost'] = cost_elem.get_text(strip=True)
                prob_elem = soup.select_one('section#maintenance-outlook p strong:nth-of-type(2)')
                if prob_elem:
                    data['major_repair_probability'] = prob_elem.get_text(strip=True)
                
            return data
            
        except Exception as e:
            print(f"Error fetching CarEdge for {make} {model}: {e}")
            return None
