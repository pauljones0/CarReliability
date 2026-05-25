import requests
import time
from abc import ABC, abstractmethod

class BaseSource(ABC):
    @abstractmethod
    def get_data(self, make, model, year=None):
        """
        Fetch data for a specific car.
        :param make: Car make (e.g., 'Honda')
        :param model: Car model (e.g., 'Accord')
        :param year: Car year (optional, e.g., 2018)
        :return: A dictionary of reliability data.
        """
        pass

    def _request(self, url, params=None, headers=None, timeout=10, max_retries=3, initial_delay=1):
        """
        Make a robust HTTP request with retries and 429 handling.
        """
        delay = initial_delay
        for i in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    return response
                
                if response.status_code == 429:
                    # Aggressive backoff for rate limits: 10s, 30s, 90s
                    wait_time = [10, 30, 90][i] if i < 3 else 120
                    print(f"  ⚠ Rate limited (429) for {url}. Waiting {wait_time}s (Attempt {i+1})...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 400:
                    # Log 400 body to help diagnose naming/param issues
                    try:
                        error_detail = response.text[:200]
                        # NHTSA Special Case: 400 status but successful zero-result body
                        if "Results returned successfully" in error_detail:
                            return response # Treat as valid
                    except:
                        error_detail = "Could not read body"
                    
                    with open('naming_audit.log', 'a') as f:
                        f.write(f"400_ERROR|{self.__class__.__name__}|{url}|{error_detail}\n")
                    return response
                
                if response.status_code == 404:
                    # Log 404 specifically as it might be a naming mismatch
                    # We can use a dedicated file or just a specific prefix for grep
                    with open('naming_audit.log', 'a') as f:
                        f.write(f"404_FAILURE|{self.__class__.__name__}|{url}\n")
                    return response
                
                time.sleep(delay)
                
            except Exception as e:
                time.sleep(delay)
        
        return None
