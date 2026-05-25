import requests
import time
import re
from bs4 import BeautifulSoup
from src.sources.base_source import BaseSource

class SafetyRatingsSource(BaseSource):
    NHTSA_LIST_URL = "https://api.nhtsa.gov/SafetyRatings/modelyear/{}/make/{}/model/{}"
    NHTSA_DETAIL_URL = "https://api.nhtsa.gov/SafetyRatings/VehicleId/{}"
    IIHS_BASE_URL = "https://www.iihs.org/ratings/vehicle/{}/{}/{}"
    
    def __init__(self, delay=1):
        self.delay = delay

    def get_data(self, make, model, year=None):
        if not year:
            return None
            
        data = {}
        
        # NHTSA specific normalization
        nhtsa_make = make
        nhtsa_model = model
        
        model_lower = model.lower().strip()
        if "silverado" in model_lower and "1500" not in model_lower:
            nhtsa_model = "Silverado 1500"
        elif "sierra" in model_lower and "1500" not in model_lower:
            nhtsa_model = "Sierra 1500"
        elif model_lower == "ram" or (make.lower() == "dodge" and model_lower == "ram"):
            nhtsa_model = "1500"
            nhtsa_make = "RAM"
            
        # 1. NHTSA Star Ratings
        try:
            list_url = self.NHTSA_LIST_URL.format(year, nhtsa_make, nhtsa_model)
            list_res = self._request(list_url)
            if list_res and list_res.status_code == 200:
                variants = list_res.json().get('Results', [])
                if variants:
                    vehicle_id = variants[0].get('VehicleId')
                    detail_url = self.NHTSA_DETAIL_URL.format(vehicle_id)
                    detail_res = self._request(detail_url)
                    if detail_res and detail_res.status_code == 200:
                        details = detail_res.json().get('Results', [])
                        if details:
                            d = details[0]
                            data['nhtsa_overall_rating'] = d.get('OverallRating')
                            data['nhtsa_front_rating'] = d.get('OverallFrontCrashRating')
                            data['nhtsa_side_rating'] = d.get('OverallSideCrashRating')
                            data['nhtsa_rollover_rating'] = d.get('RolloverRating')
        except Exception as e:
            print(f"Error fetching NHTSA safety for {year} {make} {model}: {e}")
            
        # 2. IIHS Ratings (Scraping)
        try:
            formatted_make = make.lower().replace(' ', '-')
            formatted_model = model.lower().replace(' ', '-')
            url = self.IIHS_BASE_URL.format(formatted_make, formatted_model, year)
            
            time.sleep(self.delay)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self._request(url, headers=headers)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                tsp = soup.find(string=re.compile(r'Top Safety Pick', re.I))
                if tsp:
                    data['iihs_award'] = tsp.strip()
                
                overall = soup.select_one('.rating-label')
                if overall:
                    data['iihs_overall'] = overall.get_text(strip=True)
        except Exception as e:
            pass
            
        return data
