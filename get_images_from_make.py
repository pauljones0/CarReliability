import requests
from bs4 import BeautifulSoup
import os
import time


class ImageDownloader:
    BASE_URL = "https://www.dashboard-light.com"
    VEHICLE_URL = BASE_URL + "/vehicles/{}.html"
    IMG_URL = BASE_URL + "/vehicles/{}"
    IMG_PATH = '../images'
    IMG_NAME = "{}.png"
    DELAY = 1  # in seconds

    def __init__(self, model_hrefs):
        self.model_hrefs = model_hrefs
        self.check_and_create_image_folder()

    def check_and_create_image_folder(self):
        if not os.path.exists(self.IMG_PATH):
            os.makedirs(self.IMG_PATH)

    def get_model_page(self, model):
        url = self.VEHICLE_URL.format(model)
        time.sleep(self.DELAY)
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')

    def get_img_elements(self, model):
        return self.get_model_page(model).find_all('img')

    def get_img_file(self, model):
        return os.path.join(self.IMG_PATH, self.IMG_NAME.format(model))

    def download_image(self, img_element, model):
        if 'QIRRate.png' in img_element['src']:
            img_path = img_element['src']
            img_url = self.IMG_URL.format(img_path)
            img_file = self.get_img_file(model)
            with open(img_file, 'wb') as f:
                f.write(requests.get(img_url).content)

    def download_images(self):
        for model in self.model_hrefs:
            try:
                img_elements = self.get_img_elements(model)
                for element in img_elements:
                    self.download_image(element, model)
            except Exception as e:
                print(f"Error downloading image: {e} for model {model}")


def main():
    all_model_hrefs = [
        ['Acura_CL', 'Acura_ILX', 'Acura_Integra', 'Acura_MDX', 'Acura_RDX', 'Acura_RL', 'Acura_RSX', 'Acura_TL',
         'Acura_TSX'],
        ['Audi_A3', 'Audi_A4', 'Audi_A5', 'Audi_A6', 'Audi_A8', 'Audi_Allroad', 'Audi_Q5', 'Audi_Q7', 'Audi_S4',
         'Audi_S5', 'Audi_TT'],
        ['BMW_1_Series', 'BMW_3_Series', 'BMW_5_Series', 'BMW_6_Series', 'BMW_7_Series', 'BMW_8_Series', 'BMW_M3',
         'BMW_M5', 'BMW_M6', 'BMW_X3', 'BMW_X5', 'BMW_X6', 'BMW_Z3', 'BMW_Z4'],
        ['Buick_Century', 'Buick_Enclave', 'Buick_Encore', 'Buick_LaCrosse', 'Buick_LeSabre', 'Buick_Lucerne',
         'Buick_Park_Avenue', 'Buick_Rainier', 'Buick_Regal', 'Buick_Rendezvous', 'Buick_Riviera', 'Buick_Skylark',
         'Buick_Terraza', 'Buick_Verano'],
        ['Cadillac_ATS', 'Cadillac_Catera', 'Cadillac_CTS', 'Cadillac_DeVille', 'Cadillac_DTS',
         'Cadillac_Eldorado', 'Cadillac_Escalade', 'Cadillac_Seville', 'Cadillac_SRX', 'Cadillac_STS',
         'Cadillac_XLR', 'Cadillac_XTS'],
        ['Chevrolet_Astro', 'Chevrolet_Avalanche', 'Chevrolet_Aveo', 'Chevrolet_Blazer', 'Chevrolet_Camaro',
         'Chevrolet_Cavalier', 'Chevrolet_C_K', 'Chevrolet_Cobalt', 'Chevrolet_Colorado', 'Chevrolet_Corvette',
         'Chevrolet_Cruze', 'Chevrolet_Equinox', 'Chevrolet_Express', 'Chevrolet_G_Series', 'Chevrolet_HHR',
         'Chevrolet_Impala', 'Chevrolet_Lumina', 'Chevrolet_Malibu', 'Chevrolet_Metro', 'Chevrolet_Monte_Carlo',
         'Chevrolet_Prizm', 'Chevrolet_S-10', 'Chevrolet_Silverado', 'Chevrolet_Sonic', 'Chevrolet_Spark',
         'Chevrolet_SSR', 'Chevrolet_Suburban', 'Chevrolet_Tahoe', 'Chevrolet_Tracker', 'Chevrolet_TrailBlazer',
         'Chevrolet_Traverse', 'Chevrolet_Uplander', 'Chevrolet_Venture'],
        ['Chrysler_300', 'Chrysler_300M', 'Chrysler_Aspen', 'Chrysler_Cirrus', 'Chrysler_Concorde',
         'Chrysler_Crossfire', 'Chrysler_Grand_Voyager', 'Chrysler_LHS', 'Chrysler_Pacifica',
         'Chrysler_PT_Cruiser', 'Chrysler_Sebring', 'Chrysler_Town_and_Country', 'Chrysler_Voyager'],
        ['Dodge_Avenger', 'Dodge_Caliber', 'Dodge_Caravan', 'Dodge_Challenger', 'Dodge_Charger', 'Dodge_Dakota',
         'Dodge_Dart', 'Dodge_Durango', 'Dodge_Grand_Caravan', 'Dodge_Intrepid', 'Dodge_Journey', 'Dodge_Magnum',
         'Dodge_Neon', 'Dodge_Nitro', 'Dodge_Ram', 'Dodge_Sprinter', 'Dodge_Stratus', 'Dodge_Viper'],
        ['Ford_Aerostar', 'Ford_C-MAX', 'Ford_Contour', 'Ford_Crown_Victoria', 'Ford_Edge', 'Ford_Escape',
         'Ford_Escort', 'Ford_E_Series', 'Ford_Excursion', 'Ford_Expedition', 'Ford_Explorer', 'Ford_Fiesta',
         'Ford_Five_Hundred', 'Ford_Flex', 'Ford_Focus', 'Ford_Freestar', 'Ford_Freestyle', 'Ford_F_Series',
         'Ford_Fusion', 'Ford_Mustang', 'Ford_Ranger', 'Ford_Taurus', 'Ford_Thunderbird', 'Ford_Transit',
         'Ford_Windstar'],
        ['GMC_Acadia', 'GMC_Canyon', 'GMC_Envoy', 'GMC_Jimmy', 'GMC_Safari', 'GMC_Savana', 'GMC_Sierra',
         'GMC_Sonoma', 'GMC_Suburban', 'GMC_Terrain', 'GMC_Yukon'],
        ['Honda_Accord', 'Honda_Civic', 'Honda_CR-V', 'Honda_CR-Z', 'Honda_Element', 'Honda_Fit', 'Honda_Insight',
         'Honda_Odyssey', 'Honda_Passport', 'Honda_Pilot', 'Honda_Prelude', 'Honda_Ridgeline', 'Honda_S2000'],
        ['Hummer_H1', 'Hummer_H2', 'Hummer_H3'],
        ['Hyundai_Accent', 'Hyundai_Azera', 'Hyundai_Elantra', 'Hyundai_Entourage', 'Hyundai_Equus',
         'Hyundai_Genesis', 'Hyundai_Santa_Fe', 'Hyundai_Sonata', 'Hyundai_Tiburon', 'Hyundai_Tucson',
         'Hyundai_Veloster', 'Hyundai_Veracruz', 'Hyundai_XG'],
        ['Infiniti_EX', 'Infiniti_FX', 'Infiniti_G', 'Infiniti_I', 'Infiniti_J30', 'Infiniti_JX35', 'Infiniti_M',
         'Infiniti_M35H', 'Infiniti_Q45', 'Infiniti_Q50', 'Infiniti_QX', 'Infiniti_QX60', 'Infiniti_QX70'],
        ['ISUZU_Amigo', 'ISUZU_Ascender', 'ISUZU_Axiom', 'ISUZU_Hombre', 'ISUZU_i_Series', 'ISUZU_Npr',
         'ISUZU_Oasis', 'ISUZU_Pickup', 'ISUZU_Rodeo', 'ISUZU_Spacecab', 'ISUZU_Trooper', 'ISUZU_VehiCROSS'],
        ['Jaguar_S-Type', 'Jaguar_XF', 'Jaguar_XJ', 'Jaguar_XK', 'Jaguar_X-Type'],
        ['Jeep_Cherokee', 'Jeep_Commander', 'Jeep_Compass', 'Jeep_Grand_Cherokee', 'Jeep_Liberty', 'Jeep_Patriot',
         'Jeep_Wrangler'],
        ['Kia_Amanti', 'Kia_Borrego', 'Kia_Forte', 'Kia_Optima', 'Kia_Rio', 'Kia_Rondo', 'Kia_Sedona',
         'Kia_Sephia', 'Kia_Sorento', 'Kia_Soul', 'Kia_Spectra', 'Kia_Sportage'],
        ['Land_Rover_Defender', 'Land_Rover_Discovery', 'Land_Rover_Freelander', 'Land_Rover_LR2',
         'Land_Rover_LR3', 'Land_Rover_LR4', 'Land_Rover_Range_Rover'],
        ['Lexus_CT', 'Lexus_ES', 'Lexus_GS', 'Lexus_GX', 'Lexus_HS', 'Lexus_IS', 'Lexus_LS', 'Lexus_LX',
         'Lexus_RX', 'Lexus_SC'],
        ['Lincoln_Aviator', 'Lincoln_Blackwood', 'Lincoln_Continental', 'Lincoln_LS', 'Lincoln_Mark',
         'Lincoln_Mark_LT', 'Lincoln_MKS', 'Lincoln_MKT', 'Lincoln_MKX', 'Lincoln_MKZ', 'Lincoln_Navigator',
         'Lincoln_Town_Car', 'Lincoln_Zephyr'],
        ['Mazda_626', 'Mazda_B_Series', 'Mazda_CX-5', 'Mazda_CX-7', 'Mazda_CX-9', 'Mazda_Mazda2', 'Mazda_Mazda3',
         'Mazda_Mazda5', 'Mazda_Mazda6', 'Mazda_Millenia', 'Mazda_MPV', 'Mazda_MX-5', 'Mazda_Protege',
         'Mazda_RX-8', 'Mazda_Tribute'],
        ['Mercedes-Benz_C_Class', 'Mercedes-Benz_CL', 'Mercedes-Benz_CLK', 'Mercedes-Benz_CLS',
         'Mercedes-Benz_E_Class', 'Mercedes-Benz_GL_Class', 'Mercedes-Benz_G-Wagen', 'Mercedes-Benz_M_Class',
         'Mercedes-Benz_R_Class', 'Mercedes-Benz_S_Class', 'Mercedes-Benz_SL_Class', 'Mercedes-Benz_SLK_Class'],
        ['Mercury_Cougar', 'Mercury_Grand_Marquis', 'Mercury_Marauder', 'Mercury_Mariner', 'Mercury_Milan',
         'Mercury_Montego', 'Mercury_Monterey', 'Mercury_Mountaineer', 'Mercury_Mystique', 'Mercury_Sable',
         'Mercury_Tracer', 'Mercury_Villager'], ['MINI_Cooper'],
        ['Mitsubishi_3000GT', 'Mitsubishi_Diamante', 'Mitsubishi_Eclipse', 'Mitsubishi_Endeavor',
         'Mitsubishi_Galant', 'Mitsubishi_Lancer', 'Mitsubishi_Mirage', 'Mitsubishi_Montero',
         'Mitsubishi_Outlander', 'Mitsubishi_Raider'],
        ['Nissan_200SX', 'Nissan_350Z', 'Nissan_370Z', 'Nissan_Altima', 'Nissan_Armada', 'Nissan_Cube',
         'Nissan_Frontier', 'Nissan_Juke', 'Nissan_Leaf', 'Nissan_Maxima', 'Nissan_Murano', 'Nissan_NV',
         'Nissan_Pathfinder', 'Nissan_Pickup', 'Nissan_Quest', 'Nissan_Rogue', 'Nissan_Sentra', 'Nissan_Titan',
         'Nissan_Versa', 'Nissan_Xterra'],
        ['Oldsmobile_Achieva', 'Oldsmobile_Alero', 'Oldsmobile_Aurora', 'Oldsmobile_Bravada', 'Oldsmobile_Cutlass',
         'Oldsmobile_Eighty_Eight', 'Oldsmobile_Intrigue', 'Oldsmobile_Ninety_Eight', 'Oldsmobile_Silhouette'],
        ['Pontiac_Aztek', 'Pontiac_Bonneville', 'Pontiac_Fiero', 'Pontiac_Firebird', 'Pontiac_G3', 'Pontiac_G5',
         'Pontiac_G6', 'Pontiac_G8', 'Pontiac_Grand_Am', 'Pontiac_Grand_Prix', 'Pontiac_GTO', 'Pontiac_Montana',
         'Pontiac_Solstice', 'Pontiac_Sunfire', 'Pontiac_Torrent', 'Pontiac_Vibe'],
        ['Porsche_911', 'Porsche_Boxster', 'Porsche_Cayenne', 'Porsche_Cayman'],
        ['Saab_900', 'Saab_9-2X', 'Saab_9-3', 'Saab_9-5', 'Saab_9-7X'],
        ['Saturn_Astra', 'Saturn_Aura', 'Saturn_Ion', 'Saturn_L_Series', 'Saturn_Outlook', 'Saturn_Relay',
         'Saturn_Sky', 'Saturn_S_Series', 'Saturn_Vue'],
        ['Scion_FR-S', 'Scion_iQ', 'Scion_tC', 'Scion_xA', 'Scion_xB', 'Scion_xD'],
        ['Subaru_B9', 'Subaru_Baja', 'Subaru_BRZ', 'Subaru_Forester', 'Subaru_Impreza', 'Subaru_Legacy',
         'Subaru_Outback', 'Subaru_Tribeca', 'Subaru_XV'],
        ['Suzuki_Aerio', 'Suzuki_Esteem', 'Suzuki_Forenza', 'Suzuki_Grand_Vitara', 'Suzuki_Kizashi', 'Suzuki_Reno',
         'Suzuki_SX4', 'Suzuki_Verona', 'Suzuki_Vitara', 'Suzuki_XL-7'],
        ['Toyota_4Runner', 'Toyota_Avalon', 'Toyota_Camry', 'Toyota_Celica', 'Toyota_Corolla', 'Toyota_ECHO',
         'Toyota_FJ', 'Toyota_Highlander', 'Toyota_Land_Cruiser', 'Toyota_Matrix', 'Toyota_Mr2', 'Toyota_MR2',
         'Toyota_Prius', 'Toyota_RAV4', 'Toyota_Sequoia', 'Toyota_Sienna', 'Toyota_Solara', 'Toyota_T100',
         'Toyota_Tacoma', 'Toyota_Tercel', 'Toyota_Tundra', 'Toyota_Venza', 'Toyota_Yaris'],
        ['Volkswagen_Beetle', 'Volkswagen_Cabrio', 'Volkswagen_CC', 'Volkswagen_Eos', 'Volkswagen_Eurovan',
         'Volkswagen_Golf', 'Volkswagen_GTI', 'Volkswagen_Jetta', 'Volkswagen_Passat', 'Volkswagen_R32',
         'Volkswagen_Rabbit', 'Volkswagen_Routan', 'Volkswagen_Tiguan', 'Volkswagen_Touareg'],
        ['Volvo_850', 'Volvo_900_Series', 'Volvo_C30', 'Volvo_C70', 'Volvo_S40', 'Volvo_S60', 'Volvo_S70',
         'Volvo_S80', 'Volvo_V40', 'Volvo_V50', 'Volvo_V70', 'Volvo_XC60', 'Volvo_XC70', 'Volvo_XC90']]
    downloader = ImageDownloader(all_model_hrefs)
    downloader.download_images()


if __name__ == "__main__":
    main()
