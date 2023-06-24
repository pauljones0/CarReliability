import cv2
import numpy as np
from bisect import bisect

IMAGE_PATH = 'images/Acura_TL.png'
# IMAGE_PATH = 'images/Toyota_Highlander.png'

MIDPOINTS_TO_YEAR_MAPPING = [
    (12, 1992), (32, 1993), (63, 1994), (94, 1995), (126, 1996),
    (157, 1997), (188, 1998), (220, 1999), (252, 2000), (282, 2001),
    (314, 2002), (346, 2003), (377, 2004), (408, 2005), (440, 2006),
    (471, 2007), (502, 2008), (534, 2009), (566, 2010), (597, 2011),
    (628, 2012), (660, 2013), (691, 2014), (722, 2015), (754, 2016),
    (786, 2017), (816, 2018), (836, 2019)
]


class Graph:
    def __init__(self, top=32, bottom=557, left=59, right=907):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right


def _crop_image(img, graph):
    return img[graph.top:graph.bottom, graph.left:graph.right]


class ImageProcessor:
    def __init__(self, path, graph, rho=0.5, theta=np.pi / 180, threshold=10, min_line_length=25, max_line_gap=10):
        self.image = _crop_image(cv2.imread(path), graph)
        self.lines = None
        self.year_to_quality = None
        self.rho = rho
        self.theta = theta
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def detect_lines(self):
        # Create a binary mask for near-black color
        mask = cv2.inRange(self.image, 0, 0)
        self.lines = cv2.HoughLinesP(mask, rho=self.rho, theta=self.theta, threshold=self.threshold,
                                     minLineLength=self.min_line_length, maxLineGap=self.max_line_gap)

    def draw_lines(self):
        year_mapping = set()
        height, _, _ = self.image.shape
        for midpoint, year in MIDPOINTS_TO_YEAR_MAPPING:
            # Check for lines surrounding the midpoint
            applicable_line = next((line for line in self.lines if line[0][0] <= midpoint <= line[0][2]), None)
            if applicable_line is not None:
                x1, y1, x2, y2 = applicable_line[0]
                cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                if y1 == y2:  # horizontal line
                    percentage = round(((height - y1) / height) * 100)
                    year_mapping.add((year, percentage))  # add year and percentage
            else:
                # Check pixel color 30 pixels from the bottom
                bottom_pixel = self.image[height - 30, midpoint]
                if np.array_equal(bottom_pixel, np.array([217, 217, 255])):  # FFD9D9 in RGB
                    year_mapping.add((year, 0))  # add year and percentage == 0

                # Check pixel color 30 pixels from the top
                top_pixel = self.image[30, midpoint]
                if np.array_equal(top_pixel, np.array([255, 240, 222])):  # DEF0FF in RGB
                    year_mapping.add((year, 100))  # add year and percentage == 100

        self.year_to_quality = year_mapping


def show_image(window_name, img):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  # destroy all windows once you're done


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
