import os
import re
import time
import requests
from bs4 import BeautifulSoup
from src.constants import Constants

class ImageDownloader:
    BASE_URL = "https://www.dashboard-light.com"
    REPORTS_URL = f"{BASE_URL}/reports/{{}}.html"
    VEHICLES_URL = f"{BASE_URL}/vehicles/{{}}.html"
    IMG_SRC_PATTERN = r'QIRRate\.png'
    
    def __init__(self, request_delay=1):
        self.request_delay = request_delay
        self._ensure_image_dir()

    def _ensure_image_dir(self):
        if not Constants.IMAGE_DIR.exists():
            Constants.IMAGE_DIR.mkdir(parents=True)

    def _get_soup(self, url):
        time.sleep(self.request_delay)
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')

    def get_model_hrefs_for_make(self, make):
        url = self.REPORTS_URL.format(make)
        soup = self._get_soup(url)
        a_elements = soup.find_all('a', href=re.compile(r'^\.\./vehicles/(.*)\.html$'))
        return [re.search(r'^\.\./vehicles/(.*)\.html$', a['href']).group(1) for a in a_elements]

    def download_image_for_model(self, model):
        url = self.VEHICLES_URL.format(model)
        try:
            soup = self._get_soup(url)
            img_elements = soup.find_all('img')
            for img in img_elements:
                if re.search(self.IMG_SRC_PATTERN, img['src']):
                    self._save_image(img['src'], model)
                    return True
        except Exception as e:
            print(f"Error downloading image for {model}: {e}")
        return False

    def _save_image(self, img_src, model):
        img_url = f"{self.BASE_URL}/vehicles/{img_src}"
        img_file = Constants.IMAGE_DIR / f"{model}.png"
        with open(img_file, 'wb') as f:
            f.write(requests.get(img_url).content)
        print(f"Downloaded: {img_file}")

def download_all_images():
    makes = [
        "Acura", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ford", "GMC", "Honda",
        "Hummer", "Hyundai", "Infiniti", "ISUZU", "Jaguar", "Jeep", "Kia", "Land_Rover", "Lexus", "Lincoln",
        "Mazda", "Mercedes-Benz", "Mercury", "MINI", "Mitsubishi", "Nissan", "Oldsmobile", "Pontiac",
        "Porsche", "Saab", "Saturn", "Scion", "Subaru", "Suzuki", "Toyota", "Volkswagen", "Volvo"
    ]
    downloader = ImageDownloader()
    for make in makes:
        print(f"Fetching models for {make}...")
        models = downloader.get_model_hrefs_for_make(make)
        for model in models:
            if not (Constants.IMAGE_DIR / f"{model}.png").exists():
                downloader.download_image_for_model(model)
            else:
                print(f"Skipping {model}, already exists.")

if __name__ == "__main__":
    download_all_images()
