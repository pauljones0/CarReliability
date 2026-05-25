import requests
from src.sources.base_source import BaseSource

import difflib

class NHTSASource(BaseSource):
    BASE_URL_RECALLS = "https://api.nhtsa.gov/recalls/recallsByVehicle"
    BASE_URL_COMPLAINTS = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
    BASE_URL_MODELS = "https://api.nhtsa.gov/products/vehicle/models"
    
    def _discover_nhtsa_model(self, make, model, year):
        """Fetch valid models for make/year and find the best fuzzy match."""
        try:
            params = {'issueType': 'c', 'make': make, 'modelYear': year}
            resp = self._request(self.BASE_URL_MODELS, params=params)
            if resp and resp.status_code == 200:
                results = resp.json().get('results', [])
                valid_models = [r['model'] for r in results]
                if not valid_models:
                    return None
                
                # Filter out obvious motorcycles/junk for car brands
                junk = ['MOTORCYCLE', 'R SERIES', 'K SERIES', 'F SERIES', 'G SERIES', 'BMW']
                if make.upper() == 'BMW':
                    valid_models = [m for m in valid_models if m.upper() not in junk]

                # Try 1: Substring match (prio longest match for specificity)
                q = model.upper().replace(' SERIES', '')
                matches = [m for m in valid_models if q in m.upper() or m.upper() in q]
                if matches:
                    # Pick the longest one (e.g. 850CSI over 850)
                    best_sub = max(matches, key=len)
                    print(f"  ℹ NHTSA: Remapped '{model}' to '{best_sub}' via substring match")
                    return best_sub
                
                # Try 2: Fuzzy match
                matches = difflib.get_close_matches(q, valid_models, n=1, cutoff=0.5)
                if matches:
                    print(f"  ℹ NHTSA: Remapped '{model}' to '{matches[0]}' via fuzzy match")
                    return matches[0]
        except:
            pass
        return None

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
        elif make.lower() == "mercedes-benz":
            nhtsa_make = "Mercedes-Benz"
            
        # First attempt
        params = {'make': nhtsa_make, 'model': nhtsa_model, 'modelYear': year}
        response = self._request(self.BASE_URL_RECALLS, params=params)
        
        # If 400, try to discover the real name
        if not response or response.status_code == 400:
            discovered = self._discover_nhtsa_model(nhtsa_make, nhtsa_model, year)
            if discovered:
                nhtsa_model = discovered
                params['model'] = nhtsa_model
                response = self._request(self.BASE_URL_RECALLS, params=params)

        # Recalls
        try:
            if response and response.status_code == 200:
                recalls = response.json().get('results', [])
                if recalls:
                    data['recall_count'] = len(recalls)
                    
                    detailed_recalls = []
                    for r in recalls:
                        if not r or not isinstance(r, dict):
                            continue
                        # Severity indicators: parkIt, parkOutSide
                        severity = "Standard"
                        if r.get('parkIt'):
                            severity = "URGENT: DO NOT DRIVE"
                        elif r.get('parkOutSide'):
                            severity = "URGENT: PARK OUTSIDE"
                        elif r.get('overTheAirUpdate'):
                            severity = "Software Update (OTA)"
                        
                        detailed_recalls.append({
                            "campaign": r.get('NHTSACampaignNumber'),
                            "component": r.get('Component'),
                            "severity": severity,
                            "consequence": r.get('Consequence'),
                            "remedy": r.get('Remedy'),
                            "notes": r.get('Notes')
                        })
                    data['recalls_detailed'] = detailed_recalls
                else:
                    data['recall_count'] = 0
        except Exception as e:
            print(f"Error fetching NHTSA recalls for {year} {make} {model}: {e}")
            
        # Complaints
        try:
            params = {'make': make, 'model': model, 'modelYear': year}
            response = self._request(self.BASE_URL_COMPLAINTS, params=params)
            if response and response.status_code == 200:
                complaints = response.json().get('results', [])
                if complaints:
                    data['complaint_count'] = len(complaints)
                else:
                    data['complaint_count'] = 0
        except Exception as e:
            print(f"Error fetching NHTSA complaints for {year} {make} {model}: {e}")
            
        return data
