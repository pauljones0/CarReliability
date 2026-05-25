import json
from src.constants import Constants

class FileHandler:
    @staticmethod
    def write_to_json(file_path, data):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def write_to_txt(file_path, data, threshold=Constants.DESIRED_RELIABILITY_PERCENTAGE):
        with open(file_path, 'w') as file:
            for car, year_data in data.items():
                for year, percentage in year_data.items():
                    if percentage >= threshold:
                        file.write(f'{car} {year}\n')
