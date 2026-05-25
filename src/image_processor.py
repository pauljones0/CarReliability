import cv2
import numpy as np
from src.constants import Constants

class Graph:
    def __init__(self, top=Constants.GRAPH_TOP, bottom=Constants.GRAPH_BOTTOM, 
                 left=Constants.GRAPH_LEFT, right=Constants.GRAPH_RIGHT):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

class Image:
    def __init__(self, path, graph=None):
        if graph is None:
            graph = Graph()
        
        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"Image at {path} could not be read.")
        self.image = self._crop_image(img, graph)

    @staticmethod
    def _crop_image(img, graph):
        return img[graph.top:graph.bottom, graph.left:graph.right]

class LineDetector:
    def __init__(self, image, rho=Constants.RHO, theta=Constants.THETA, 
                 threshold=Constants.THRESHOLD, min_line_length=Constants.MIN_LINE_LENGTH, 
                 max_line_gap=Constants.MAX_LINE_GAP):
        self.image = image
        self.lines = []
        self.rho = rho
        self.theta = theta
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def detect_lines(self):
        # Create a binary mask for near-black color
        mask = cv2.inRange(self.image, 0, 0)
        lines = cv2.HoughLinesP(mask, rho=self.rho, theta=self.theta, threshold=self.threshold,
                                minLineLength=self.min_line_length, maxLineGap=self.max_line_gap)
        self.lines = lines if lines is not None else []
        return self.lines

class YearQualityMapper:
    def __init__(self, image, lines):
        self.image = image
        self.lines = lines
        self.year_to_quality = set()

    def create_year_quality_mapping(self):
        height, _, _ = self.image.shape
        for midpoint, year in Constants.generate_midpoints_to_year_mapping():
            self._evaluate_midpoint(midpoint, year, height)
        return self.year_to_quality

    def _evaluate_midpoint(self, midpoint, year, height):
        applicable_line = next((line for line in self.lines if line[0][0] <= midpoint <= line[0][2]), None)
        if applicable_line is not None:
            self._evaluate_applicable_line(applicable_line, year, height)
        else:
            self._evaluate_pixels(midpoint, year, height)

    def _evaluate_applicable_line(self, applicable_line, year, height):
        x1, y1, x2, y2 = applicable_line[0]
        # Draw line for debugging/visualization if needed
        # cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        if y1 == y2:  # horizontal line
            percentage = round(((height - y1) / height) * 100)
            self.year_to_quality.add((year, percentage))

    def _evaluate_pixels(self, midpoint, year, height):
        # Check pixel color 30 pixels from the bottom
        bottom_pixel = self.image[height - 30, midpoint]
        if np.array_equal(bottom_pixel, Constants.COLOR_BOTTOM_PIXEL):
            self.year_to_quality.add((year, 0))

        # Check pixel color 30 pixels from the top
        top_pixel = self.image[30, midpoint]
        if np.array_equal(top_pixel, Constants.COLOR_TOP_PIXEL):
            self.year_to_quality.add((year, 100))
