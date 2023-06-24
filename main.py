import os
import json
import cv2
import numpy as np

class Constants:
    IMAGE_DIR = 'images'
    DEBUG_FLAG = False
    START_YEAR = 1993
    END_YEAR = 2018
    FIRST_FULL_LINE, LAST_FULL_LINE = 32, 816

    @staticmethod
    def generate_midpoints_to_year_mapping():
        years = range(Constants.START_YEAR, Constants.END_YEAR + 1)
        midpoints = np.linspace(Constants.FIRST_FULL_LINE, Constants.LAST_FULL_LINE, len(years)).astype(int)
        midpoints_to_year_mapping = list(zip(midpoints, years))
        midpoints_to_year_mapping = Constants.correct_midpoints(midpoints_to_year_mapping)
        midpoints_to_year_mapping.insert(0, (12, 1992))
        midpoints_to_year_mapping.append((836, 2019))
        return midpoints_to_year_mapping

    @staticmethod
    def correct_midpoints(midpoints_to_year_mapping):
        corrected_mapping = []
        for midpoint, year in midpoints_to_year_mapping:
            if year in [2000,2003,2004,2006,2009,2010,2011,2012,2013,2014,2015,2016]:
                midpoint += 1
            elif year == 2017:
                midpoint += 2
            corrected_mapping.append((midpoint, year))
        return corrected_mapping

class Graph:
    def __init__(self, top=34, bottom=556, left=59, right=907):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

class Image:
    def __init__(self, path, graph):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Image at {path} could not be read.")
        self.image = self._crop_image(img, graph)


    @staticmethod
    def _crop_image(img, graph):
        return img[graph.top:graph.bottom, graph.left:graph.right]

class LineDetector:
    def __init__(self, image, rho=0.5, theta=np.pi / 180, threshold=10,
                 min_line_length=25, max_line_gap=10):
        self.image = image
        self.lines = None
        self.rho = rho
        self.theta = theta
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def detect_lines(self):
        mask = cv2.inRange(self.image, 0, 0)
        lines = cv2.HoughLinesP(mask, rho=self.rho, theta=self.theta, threshold=self.threshold,
                                minLineLength=self.min_line_length, maxLineGap=self.max_line_gap)
        self.lines = lines if lines is not None else []
        return self.lines


class YearQualityMapper:
    def __init__(self, image, lines):
        self.image = image
        self.lines = lines
        self.year_to_quality = None

    def create_year_quality_mapping(self):
        self.year_to_quality = self._map_to_year_quality()

    def _map_to_year_quality(self):
        year_mapping = set()
        height, _, _ = self.image.shape
        for midpoint, year in Constants.generate_midpoints_to_year_mapping():
            year_mapping = self._evaluate_midpoints(midpoint, year, year_mapping, height)
        return year_mapping

    def _evaluate_midpoints(self, midpoint, year, year_mapping, height):
        applicable_line = next((line for line in self.lines if line[0][0] <= midpoint <= line[0][2]), None)
        if applicable_line is not None:
            year_mapping = self._evaluate_applicable_line(applicable_line, year, year_mapping, height)
        else:
            year_mapping = self._evaluate_pixels(midpoint, year, year_mapping, height)
        return year_mapping

    def _evaluate_applicable_line(self, applicable_line, year, year_mapping, height):
        x1, y1, x2, y2 = applicable_line[0]
        cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        if y1 == y2:  # horizontal line
            percentage = round(((height - y1) / height) * 100)
            year_mapping.add((year, percentage))  # add year and percentage
        return year_mapping

    def _evaluate_pixels(self, midpoint, year, year_mapping, height):
        bottom_pixel = self.image[height - 30, midpoint]
        if np.array_equal(bottom_pixel, np.array([217, 217, 255])):  # FFD9D9 in RGB
            year_mapping.add((year, 0))  # add year and percentage == 0

        top_pixel = self.image[30, midpoint]
        if np.array_equal(top_pixel, np.array([255, 240, 222])):  # DEF0FF in RGB
            year_mapping.add((year, 100))  # add year and percentage == 100
        return year_mapping

class FileWriter:
    @staticmethod
    def write_to_json(file_name, data):
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file)

    @staticmethod
    def write_to_txt(file_name, data):
        with open(file_name, 'w') as file:
            for car, year_data in data.items():
                for year, percentage in year_data.items():
                    if percentage >= 90:
                        file.write(f'{car} {year}\n')

def main():
    result_dict = {}
    for filename in os.listdir(Constants.IMAGE_DIR):
        if filename.endswith(".png"):
            file_path = os.path.join(Constants.IMAGE_DIR, filename)
            image = Image(file_path, Graph())
            line_detector = LineDetector(image.image)
            lines = line_detector.detect_lines()
            mapper = YearQualityMapper(image.image, lines)
            mapper.create_year_quality_mapping()
            if mapper.year_to_quality:
                result_dict[filename[:-4]] = {year: percent for year, percent in sorted(mapper.year_to_quality)}

    FileWriter.write_to_json('result.json', result_dict)
    FileWriter.write_to_txt('cars_above_90.txt', result_dict)

if __name__ == "__main__":
    main()
