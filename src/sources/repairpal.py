import requests
from bs4 import BeautifulSoup
import time
import re
from src.sources.base_source import BaseSource

class RepairPalSource(BaseSource):
    BASE_URL = "https://repairpal.com/reliability/{}/{}"
    
    def __init__(self, delay=1):
        self.delay = delay

    def get_data(self, make, model, year=None):
        formatted_make = make.lower().replace(' ', '-')
        
        model_lower = model.lower().strip()
        aliases = {
            '1 series': '128i',
            '3 series': '328i',
            '5 series': '528i',
            '6 series': '650i',
            '7 series': '750i',
            '8 series': '850i',
            'c class': 'c300',
            'c-class': 'c300',
            'e class': 'e350',
            'e-class': 'e350',
            's class': 's550',
            's-class': 's550',
            'm class': 'ml350',
            'm-class': 'ml350',
            'gl class': 'gl450',
            'gl-class': 'gl450',
            'sl class': 'sl500',
            'sl-class': 'sl500',
            'slk class': 'slk280',
            'slk-class': 'slk280',
            'f series': 'f-150',
            'f-series': 'f-150',
            'e series': 'e-150',
            'e-series': 'e-150',
            'g series': 'g20',       # Chevrolet G Series van -> G20
            '900 series': '940',
            'm35h': 'm35',
            'qx': 'qx56',
            'hs': 'hs250h',          # Lexus HS -> HS250h
            'defender': 'defender-90',
            'suburban': 'suburban-1500',
            'c/k': 'c1500',          # Chevrolet C/K -> c1500
            'rx': 'rx350',           # Lexus RX -> rx350
            'es': 'es350',           # Lexus ES -> es350
            'gs': 'gs350',           # Lexus GS -> gs350
            'lx': 'lx570',           # Lexus LX -> lx570
            'is': 'is250',           # Lexus IS -> is250
            'ct': 'ct200h',          # Lexus CT -> ct200h
            'transit': 'transit-connect',
            'eighty eight': '88',    # Oldsmobile Eighty Eight -> 88
            'eighty-eight': '88',
            'ninety eight': '98',    # Oldsmobile Ninety Eight -> 98
            'ninety-eight': '98',
            'xv': 'xv-crosstrek',    # Subaru XV -> xv-crosstrek
            'silverado': 'silverado-1500',
            'sierra': 'sierra-1500',
            'ram': 'ram-1500',
            's series': 'sl2',       # Saturn S-Series -> SL2 (common)
            'l series': 'l300',      # Saturn L-Series -> L300
            'lr2': 'lr2',
            'lr3': 'lr3',
            'lr4': 'lr4',
            '3000gt': '3000gt',
            'fiero': 'fiero',
            'g-wagen': 'g550',
            'g-class': 'g550',
            'mark': 'mark-viii'
        }
        
        # GMC Suburban -> Chevrolet Suburban
        if formatted_make == "gmc" and model_lower == "suburban":
            formatted_make = "chevrolet"
            formatted_model = "suburban-1500"
        elif model_lower in aliases:
            formatted_model = aliases[model_lower]
        else:
            formatted_model = model_lower.replace(' ', '-')

            
        url = self.BASE_URL.format(formatted_make, formatted_model)
        
        try:
            time.sleep(self.delay)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = self._request(url, headers=headers)
            
            if not response or response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {}
            
            # Annual Repair Cost - looking for the text directly if classes fail
            cost_text = soup.find(string=re.compile(r'average annual repair cost is'))
            if cost_text:
                match = re.search(r'\$(\d+)', cost_text)
                if match:
                    data['annual_repair_cost'] = f"${match.group(1)}"
            
            if 'annual_repair_cost' not in data:
                # Try slider handle
                cost_handle = soup.select_one('.slider-chart.cost .slider-handle-text')
                if cost_handle:
                    data['annual_repair_cost'] = cost_handle.get_text(strip=True)

            # Reliability Rating
            rating_elem = soup.find('span', class_='body-bold', string=re.compile(r'\d\.\d out of 5\.0'))
            if rating_elem:
                data['reliability_rating'] = rating_elem.get_text(strip=True)
            else:
                # Fallback to general search
                rating_text = soup.find(string=re.compile(r'Reliability Rating is'))
                if rating_text:
                    match = re.search(r'(\d\.\d out of 5\.0)', rating_text)
                    if match:
                        data['reliability_rating'] = match.group(1)
                
            return data
            
        except Exception as e:
            print(f"Error fetching RepairPal data for {make} {model}: {e}")
            return None
