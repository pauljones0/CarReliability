import os
import re
import time

import requests
from bs4 import BeautifulSoup

# Define the starting URL
start_url = "https://www.dashboard-light.com"

# Define a variable to control the delay between requests
request_delay = 1  # in seconds

# Define a variable to store the folder path where the images will be saved
image_folder = '../images'


def get_html(url):
    time.sleep(request_delay)
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def extract_model_hrefs(soup):
    a_elements = soup.find_all('a', href=re.compile(r'^\.\./vehicles/(.*)\.html$'))
    return [re.search(r'^\.\./vehicles/(.*)\.html$', a['href']).group(1) for a in a_elements]


def extract_img_srcs(soup):
    img_elements = soup.find_all('img')
    return [img['src'] for img in img_elements if 'QIRRate.png' in img['src']]


def download_image(img_src, model):
    img_url = f"{start_url}/vehicles/{img_src}"
    img_file = f"{image_folder}/{model}.png"
    with open(img_file, 'wb') as f:
        f.write(requests.get(img_url).content)


def get_model_hrefs(make):
    url = f"{start_url}/reports/{make}.html"
    soup = get_html(url)
    return extract_model_hrefs(soup)


def download_images(model_hrefs):
    for model in model_hrefs:
        try:
            url = f"{start_url}/vehicles/{model}.html"
            soup = get_html(url)
            img_srcs = extract_img_srcs(soup)
            for img_src in img_srcs:
                download_image(img_src, model)
        except Exception as e:
            print(f"Error downloading image: {e} for model {model}")


def main():
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    makes = ["Acura", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ford", "GMC", "Honda",
             "Hummer", "Hyundai", "Infiniti", "ISUZU", "Jaguar", "Jeep", "Kia", "Land_Rover", "Lexus", "Lincoln",
             "Mazda", "Mercedes-Benz", "Mercury", "MINI", "Mitsubishi", "Nissan", "Oldsmobile", "Pontiac",
             "Porsche", "Saab", "Saturn", "Scion", "Subaru", "Suzuki", "Toyota", "Volkswagen", "Volvo"]
    all_model_hrefs = []
    for make in makes:
        all_model_hrefs.extend(get_model_hrefs(make))

    download_images(all_model_hrefs)


if __name__ == "__main__":
    main()
