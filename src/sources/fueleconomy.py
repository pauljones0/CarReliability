import requests
import time
import re
from src.sources.base_source import BaseSource

class FuelEconomySource(BaseSource):
    BASE_URL = "https://www.fueleconomy.gov/ws/rest"
    
    def __init__(self, delay=0.5):
        self.delay = delay

    def get_data(self, make, model, year=None):
        if not year:
            return None
            
        # Model Aliasing for FuelEconomy
        model_lower = model.lower().strip()
        fe_aliases = {
            '8 series': '850i',
            '3 series': '328i',
            '5 series': '528i',
            's series': 'sl2',
            'l series': 'l300',
            'sl class': 'sl500',
            'slk class': 'slk280'
        }
        if model_lower in fe_aliases:
            model = fe_aliases[model_lower]

        try:
            headers = {'Accept': 'application/json'}
            
            # Step 1: Get options (Vehicle IDs) for Year + Make + Model
            options_url = f"{self.BASE_URL}/vehicle/menu/options"
            params = {'year': year, 'make': make, 'model': model}
            
            time.sleep(self.delay)
            response = self._request(options_url, params=params, headers=headers)
            
            menu_items = []
            if response and response.status_code == 200:
                options_data = response.json()
                if options_data and isinstance(options_data, dict):
                    menu_items = options_data.get('menuItem', [])
                    if isinstance(menu_items, dict): # Single item comes as dict
                        menu_items = [menu_items]
                    elif menu_items is None:
                        menu_items = []
            
            # Fallback search if direct search yielded no options
            if not menu_items:
                all_models_url = f"{self.BASE_URL}/vehicle/menu/model"
                all_models_params = {'year': year, 'make': make}
                time.sleep(self.delay)
                all_res = self._request(all_models_url, params=all_models_params, headers=headers)
                
                if all_res and all_res.status_code == 200:
                    all_data = all_res.json()
                    if all_data and isinstance(all_data, dict):
                        items = all_data.get('menuItem', [])
                        if isinstance(items, dict):
                            items = [items]
                        elif items is None:
                            items = []
                        
                        matched_values = []
                        q_lower = model.lower().replace(' ', '').replace('-', '').replace('_', '')
                        
                        # Match rules for series/classes
                        is_series = re.match(r'(\d+)series', q_lower)
                        is_class = re.match(r'([a-z])class', q_lower)
                        is_f_series = q_lower in ['fseries', 'f']
                        
                        for item in items:
                            if not item or not isinstance(item, dict):
                                continue
                            m_text = item.get('text', '')
                            if not m_text:
                                continue
                            m_text_lower = m_text.lower().replace(' ', '').replace('-', '').replace('_', '')
                            
                            matched = False
                            if q_lower in m_text_lower:
                                matched = True
                            elif is_series:
                                digit = is_series.group(1)
                                if m_text_lower.startswith(digit) and len(m_text_lower) >= 3 and m_text_lower[1:3].isdigit():
                                    matched = True
                            elif is_class:
                                letter = is_class.group(1)
                                if m_text_lower.startswith(letter) and len(m_text_lower) >= 2 and m_text_lower[1].isdigit():
                                    matched = True
                            elif is_f_series:
                                if m_text_lower.startswith('f150') or m_text_lower.startswith('f250') or m_text_lower.startswith('f350') or m_text_lower.startswith('f-150'):
                                    matched = True
                            
                            if matched:
                                val = item.get('value')
                                if val:
                                    matched_values.append(val)
                        
                        for val in matched_values:
                            opt_url = f"{self.BASE_URL}/vehicle/menu/options"
                            opt_params = {'year': year, 'make': make, 'model': val}
                            time.sleep(self.delay)
                            opt_res = self._request(opt_url, params=opt_params, headers=headers)
                            if opt_res and opt_res.status_code == 200:
                                opt_data = opt_res.json()
                                if opt_data and isinstance(opt_data, dict):
                                    opt_items = opt_data.get('menuItem', [])
                                    if isinstance(opt_items, dict):
                                        opt_items = [opt_items]
                                    if opt_items:
                                        menu_items.extend(opt_items)
                
            total_city = 0
            total_hwy = 0
            total_comb = 0
            count = 0
            
            for item in menu_items:
                if not item or not isinstance(item, dict):
                    continue
                vehicle_id = item.get('value')
                if not vehicle_id:
                    continue
                    
                vehicle_url = f"{self.BASE_URL}/vehicle/{vehicle_id}"
                time.sleep(self.delay)
                v_res = self._request(vehicle_url, headers=headers)
                
                if v_res and v_res.status_code == 200:
                    v_data = v_res.json()
                    if v_data and isinstance(v_data, dict):
                        try:
                            total_city += float(v_data.get('city08', 0))
                            total_hwy += float(v_data.get('highway08', 0))
                            total_comb += float(v_data.get('comb08', 0))
                            count += 1
                        except (ValueError, TypeError):
                            continue
            
            if count > 0:
                return {
                    "city_mpg": round(total_city / count, 1),
                    "highway_mpg": round(total_hwy / count, 1),
                    "combined_mpg": round(total_comb / count, 1)
                }
                
            return None
            
        except Exception as e:
            print(f"Error fetching FuelEconomy data for {year} {make} {model}: {e}")
            return None
            
            if count > 0:
                return {
                    "city_mpg": round(total_city / count, 1),
                    "highway_mpg": round(total_hwy / count, 1),
                    "combined_mpg": round(total_comb / count, 1)
                }
                
            return None
            
        except Exception as e:
            print(f"Error fetching FuelEconomy data for {year} {make} {model}: {e}")
            return None
