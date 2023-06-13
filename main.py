from bisect import bisect

import cv2
import numpy as np

image_path = 'C:/Users/bethe/PycharmProjects/pythonProject/images/Acura_TL.png'

def map_number_to_year_using_bisection(num):
    midpoints = [90.5, 122, 153.5, 184.5, 216, 247.5, 279, 310.5, 341.5, 373, 404.5, 436, 467.5, 498.5,
                 530, 561.5, 593, 624.5, 656, 687.5, 718.5, 750, 781.5, 813, 844.5, 875.5]
    years = [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999,
             2000, 2001, 2002, 2003, 2004, 2005, 2006,
             2007, 2008, 2009, 2010, 2011, 2012, 2013,
             2014, 2015, 2016, 2017, 2018]
    return years[bisect(midpoints, num)]


class ImageProcessor:
    def __init__(self, path):
        self.image = cv2.imread(path)
        self.mask = None
        self.lines = None
        self.year_to_quality = None

    def create_mask(self):
        # Create a binary mask for near-black color
        self.mask = cv2.inRange(self.image, 0, 0)

    def detect_lines(self):
        self.lines = cv2.HoughLinesP(self.mask, rho=0.5, theta=np.pi / 180, threshold=10, minLineLength=25,
                                     maxLineGap=10)

    def draw_lines(self):
        year_mapping = set()
        height, _, _ = self.image.shape
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                if y1 == y2:  # horizontal line
                    year_mapping.add((map_number_to_year_using_bisection(x1), round(y1 / height * 100)))
        self.year_to_quality = year_mapping


def show_image(window_name, img):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)


def print_horizontal_lines(horizontal_lines):
    if horizontal_lines:
        print(f"List of horizontal line y-locations: {sorted(horizontal_lines, key=lambda x: x[0])}")
    else:
        print("No horizontal lines detected")


def main():
    img_processor = ImageProcessor(image_path)
    img_processor.create_mask()
    show_image("Black Grayscale Image", img_processor.mask)
    img_processor.detect_lines()
    img_processor.draw_lines()
    show_image('Detected Lines', img_processor.image)
    print_horizontal_lines(img_processor.year_to_quality)


if __name__ == "__main__":
    main()
