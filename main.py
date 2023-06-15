import cv2
import numpy as np
from bisect import bisect

IMAGE_PATH = 'images/Acura_TL.png'
MIDPOINTS = [31.5, 63, 94.5, 125.5, 157, 188.5, 220, 251.5, 282.5, 314, 345.5, 377, 408.5, 439.5, 471, 502.5, 534,
             565.5, 597, 628.5, 659.5, 691, 722.5, 754, 785.5, 816.5]
YEARS = [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
         2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]


class Graph:
    def __init__(self, top=34, bottom=556, left=59, right=907):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right


class YearMapper:
    @staticmethod
    def map_number_to_year(num):
        return YEARS[bisect(MIDPOINTS, num)]


class ImageProcessor:
    def __init__(self, path, graph, rho=0.5, theta=np.pi / 180, threshold=10, min_line_length=25, max_line_gap=10):
        self.image = self._crop_image(cv2.imread(path), graph)
        self.lines = None
        self.year_to_quality = None
        self.rho = rho
        self.theta = theta
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def _crop_image(self, img, graph):
        return img[graph.top:graph.bottom, graph.left:graph.right]

    def detect_lines(self):
        # Create a binary mask for near-black color
        mask = cv2.inRange(self.image, 0, 0)
        self.lines = cv2.HoughLinesP(mask, rho=self.rho, theta=self.theta, threshold=self.threshold,
                                     minLineLength=self.min_line_length, maxLineGap=self.max_line_gap)

    def draw_lines(self):
        year_mapping = set()
        height, _, _ = self.image.shape
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                if y1 == y2:  # horizontal line
                    percentage = round(((height - y1) / height) * 100)
                    year_mapping.add((YearMapper.map_number_to_year(x2), percentage))  # add year and percentage
        self.year_to_quality = year_mapping


def show_image(window_name, img):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)


def main():
    img_processor = ImageProcessor(IMAGE_PATH, Graph())
    img_processor.detect_lines()
    show_image("Black Grayscale Image", img_processor.image)
    img_processor.draw_lines()
    show_image('Detected Lines', img_processor.image)
    if img_processor.year_to_quality:
        print(f"List of horizontal line y-locations: {sorted(img_processor.year_to_quality, key=lambda x: x[0])}")
    else:
        print("No horizontal lines detected")


if __name__ == "__main__":
    main()
