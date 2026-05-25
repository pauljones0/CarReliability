import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from src.sources.base_source import BaseSource

class VMRCanadaSource(BaseSource):
    BASE_URL = "https://www.vmrcanada.com/used-car/values/{}-{}-{}.html"
    
    # EXACT VMR Canada Provincial Adjustment Factors
    PROVINCIAL_ADJUSTMENTS = {
        "AB": 1.03,
        "BC": 1.06,
        "MB": 1.03,
        "NB": 1.04,
        "NL": 1.08,
        "NT": 1.10,
        "NS": 1.05,
        "NU": 1.10,
        "ON_NORTH": 1.02,
        "ON_SOUTH": 1.00,
        "PE": 1.08,
        "QC": 1.02,
        "SK": 1.03,
        "YT": 1.10
    }
    
    # VMR Canada Standard Mileage increments and values
    KM_INCREMENT = 7500
    WS_RATE = 225
    RET_RATE = 250

    def __init__(self, delay=1):
        self.delay = delay

    def get_data(self, make, model, year=None, km=None, province="ON_SOUTH"):
        if not year:
            return None
            
        # VMR Canada Normalization
        formatted_make = make.lower().replace(' ', '-')
        model_lower = model.lower().strip()
        
        vmr_aliases = {
            '3 series': '3-series',
            '5 series': '5-series',
            'c class': 'c-class',
            'e class': 'e-class',
            'f series': 'f-150',
            'suburban': 'suburban',
            'grand cherokee': 'grand-cherokee',
            'range rover': 'range-rover',
            's-10': 's10-pickup'
        }
        
        if model_lower in vmr_aliases:
            formatted_model = vmr_aliases[model_lower]
        else:
            formatted_model = model_lower.replace(' ', '-')
            
        url = self.BASE_URL.format(year, formatted_make, formatted_model)
        
        try:
            time.sleep(self.delay)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = self._request(url, headers=headers)
            
            # If primary URL fails, try a few common VMR patterns
            if not response or response.status_code != 200:
                # Fallback 1: Add/Remove '-sedan'
                alt_model = formatted_model + "-sedan" if "-sedan" not in formatted_model else formatted_model.replace("-sedan", "")
                url = self.BASE_URL.format(year, formatted_make, alt_model)
                response = self._request(url, headers=headers)
                
            if not response or response.status_code != 200:
                # Fallback 2: Try without any dashes if it had them
                if '-' in formatted_model:
                    alt_model = formatted_model.replace('-', '')
                    url = self.BASE_URL.format(year, formatted_make, alt_model)
                    response = self._request(url, headers=headers)

            if not response or response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {}
            
            # 1. Find the "Zero Point" (Average KM) from the page if possible
            zero_point_km = self._find_zero_point_km(soup, year)
            
            # 2. Calculate Mileage Adjustment
            ws_adj = 0
            ret_adj = 0
            if km is not None:
                diff = int(km) - zero_point_km
                num_increments = diff / self.KM_INCREMENT
                ws_adj = - (num_increments * self.WS_RATE)
                ret_adj = - (num_increments * self.RET_RATE)

            # 3. Get Regional Factor
            region_factor = self.PROVINCIAL_ADJUSTMENTS.get(province.upper(), 1.00)

            # 4. Extract Base Prices and Apply Math
            estimates = []
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    trim = cols[0].get_text(strip=True)
                    ws_text = cols[1].get_text(" ", strip=True)
                    ret_text = cols[2].get_text(" ", strip=True)
                    
                    ws_match = re.search(r'(\d+)', ws_text.replace(',', ''))
                    ret_match = re.search(r'(\d+)', ret_text.replace(',', ''))
                    
                    if ws_match and ret_match:
                        ws_val = int(ws_match.group(1))
                        ret_val = int(ret_match.group(1))
                        
                        if ws_val > 100 and ret_val > 100 and "Trim" not in trim:
                            # Apply adjustments
                            # VMR math: (Base + Mileage Adj) * Region %
                            adjusted_ws = round((ws_val + ws_adj) * region_factor)
                            adjusted_ret = round((ret_val + ret_adj) * region_factor)
                            
                            estimates.append({
                                "trim": trim,
                                "base_wholesale": f"${ws_val:,}",
                                "base_retail": f"${ret_val:,}",
                                "adjusted_wholesale": f"${max(0, adjusted_ws):,}",
                                "adjusted_retail": f"${max(0, adjusted_ret):,}"
                            })
            
            if estimates:
                data['canadian_price_estimates'] = estimates[:8]
                data['mileage_adjustment_calculated'] = {
                    "wholesale": f"${round(ws_adj):,}",
                    "retail": f"${round(ret_adj):,}",
                    "assumed_average_km": f"{zero_point_km:,} km"
                }
                data['regional_factor_applied'] = f"{round((region_factor-1)*100)}% ({province.upper()})"
                    
            return data
            
        except Exception as e:
            print(f"Error fetching VMR Canada for {year} {make} {model}: {e}")
            return None

    def _find_zero_point_km(self, soup, year):
        # Fallback: Assume 18k km per year if page scraping fails
        # But try to find the row with $0 or 0 in the table
        try:
            rows = soup.find_all('tr')
            for row in rows:
                text = row.get_text()
                if (" 0" in text or "$0" in text) and ("km" in text or "-" in text):
                    # Found the neutral row, e.g. "67,501 - 75,000 $0 $0"
                    match = re.search(r'(\d[\d,]+)\s*-\s*(\d[\d,]+)', text)
                    if match:
                        low = int(match.group(1).replace(',', ''))
                        high = int(match.group(2).replace(',', ''))
                        return (low + high) // 2
        except:
            pass
            
        # Hard fallback based on VMR's static benchmark logic
        current_year = 2024 # Benchmark year for VMR's current tables
        age = max(1, current_year - int(year))
        return age * 18000
