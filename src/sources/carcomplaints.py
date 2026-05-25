import requests
from bs4 import BeautifulSoup
import time
import re
from src.sources.base_source import BaseSource

class CarComplaintsSource(BaseSource):
    BASE_URL = "https://www.carcomplaints.com/{}/{}/"
    
    def __init__(self, delay=1):
        self.delay = delay

    def get_data(self, make, model, year=None):
        # Normalize make
        if make.upper() == "GMC":
            formatted_make = "GMC"
        elif make.upper() == "BMW":
            formatted_make = "BMW"
        elif make.lower() == "mercedes-benz":
            formatted_make = "Mercedes-Benz"
        else:
            formatted_make = make.replace(' ', '_').title()
            
        model_lower = model.lower().strip()
        aliases = {
            '1 series': '1_Series', '3 series': '3_Series', '5 series': '5_Series', '6 series': '6_Series', '7 series': '7_Series', '8 series': '8_Series',
            'c class': 'C-Class', 'c-class': 'C-Class', 'e class': 'E-Class', 'e-class': 'E-Class', 's class': 'S-Class', 's-class': 'S-Class',
            'm class': 'M-Class', 'm-class': 'M-Class', 'gl class': 'GL-Class', 'gl-class': 'GL-Class', 'sl class': 'SL-Class', 'sl-class': 'SL-Class',
            'slk class': 'SLK-Class', 'slk-class': 'SLK-Class', 'f series': 'F-150', 'f-series': 'F-150', 'e series': 'E-150', 'e-series': 'E-150',
            'g series': 'G20', '900 series': '940', 'm35h': 'M35', 'qx': 'QX56', 'hs': 'HS_250h', 'defender': 'Defender',
            'suburban': 'Suburban_1500', 'c/k': 'C/K_1500', 'rx': 'RX_350', 'es': 'ES_350', 'gs': 'GS_350', 'lx': 'LX_570', 'is': 'IS_250',
            'ct': 'CT_200h', 'transit': 'Transit_Connect', 'eighty eight': '88', 'eighty-eight': '88', 'ninety eight': '98', 'ninety-eight': '98',
            'xv': 'XV_Crosstrek', 'ram': 'Ram_1500', 's series': 'S-Series', 'l series': 'L-Series',
            'b9': 'B9_Tribeca', 'g': 'G35'
        }
        
        if model_lower in aliases:
            formatted_model = aliases[model_lower]
        else:
            formatted_model = model.replace(' ', '_')
            
        # GMC Suburban -> Chevrolet Suburban in CC
        if formatted_make == "Gmc" and formatted_model == "Suburban_1500":
            formatted_make = "Chevrolet"

            
        url = self.BASE_URL.format(formatted_make, formatted_model)
        
        try:
            time.sleep(self.delay)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self._request(url, headers=headers)
            
            if not response or response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {}
            
            # Worst Year
            worst_dt = soup.find('dt', string=re.compile(r'Worst Model Year'))
            if worst_dt:
                worst_dd = worst_dt.find_next_sibling('dd', class_='year')
                if worst_dd:
                    data['worst_year'] = worst_dd.get_text(strip=True)
            
            # Worst Category / Problem
            worst_cat_dt = soup.find('dt', string=re.compile(r'Worst Category'))
            if worst_cat_dt:
                worst_cat_dd = worst_cat_dt.find_next_sibling('dd', class_='complaint')
                if worst_cat_dd:
                    data['worst_category'] = worst_cat_dd.get_text(strip=True)
            
            # Extract available years on overview page
            available_years = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                match = re.search(r'/(\d{4})/', href)
                if match:
                    y_val = int(match.group(1))
                    if 1990 <= y_val <= 2025:
                        available_years.append(y_val)
            if available_years:
                data['available_years'] = sorted(list(set(available_years)), reverse=True)

            if year:
                # Try to extract the specific year's complaint count from the overview page
                year_suffix = f"/{year}/"
                found_count = False
                for a in soup.find_all('a'):
                    href = a.get('href', '')
                    if href.endswith(year_suffix) or f"/{formatted_make}/{formatted_model}/{year}/".lower() in href.lower():
                        count_span = a.find('span', class_='count')
                        if count_span:
                            data['carcomplaints_count'] = count_span.get_text(strip=True)
                            found_count = True
                            break
                
                # Fallback: request year-specific page if not found on overview
                if not found_count:
                    year_url = url + f"{year}/"
                    time.sleep(self.delay)
                    y_res = self._request(year_url, headers=headers)
                    if y_res and y_res.status_code == 200:
                        y_soup = BeautifulSoup(y_res.content, 'html.parser')
                        cnt_span = y_soup.find('span', class_='cnt')
                        if cnt_span and cnt_span.parent and 'Complaints' in cnt_span.parent.get_text():
                            data['carcomplaints_count'] = cnt_span.get_text(strip=True)
                        else:
                            summary_text = y_soup.find(string=re.compile(r'complaints on file for the'))
                            if summary_text:
                                match = re.search(r'([\d,]+) complaints', summary_text)
                                if match:
                                    data['carcomplaints_count'] = match.group(1).replace(',', '')
            
            return data
            
        except Exception as e:
            print(f"Error fetching CarComplaints for {make} {model}: {e}")
            return None
