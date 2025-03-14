import cv2
import numpy as np


class LineDetector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img = None
        self.gray = None
        self.mask = None
        self.lines = None
        self.vertical_lines = []
        self.horizontal_lines = []

    def read_image(self):
        self.img = cv2.imread(self.image_path)
        self.display_image('Original Image', self.img)

    def convert_to_grayscale(self):
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def create_mask(self, lower_bound, upper_bound):
        self.mask = cv2.inRange(self.gray, lower_bound, upper_bound)
        self.display_image('Mask', self.mask)

    def detect_lines(self, rho, theta, threshold, min_line_length, max_line_gap):
        self.lines = cv2.HoughLinesP(self.mask, rho, theta, threshold, min_line_length, max_line_gap)

    def draw_and_classify_lines(self):
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(self.img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                if x1 == x2:  # vertical line
                    self.vertical_lines.append((x1, y1, x2, y2))
                elif y1 == y2:  # horizontal line
                    self.horizontal_lines.append((x1, y1, x2, y2))

            self.display_image('Detected Lines', self.img)

    def analyze_lines(self):
        self.analyze_specific_lines(self.vertical_lines, "vertical")
        self.analyze_specific_lines(self.horizontal_lines, "horizontal")

    @staticmethod
    def analyze_specific_lines(lines, line_type):
        if lines:
            first_line = min([x1 for x1, y1, x2, y2 in lines])
            last_line = max([x2 for x1, y1, x2, y2 in lines])
            average_distance_lines = (last_line - first_line) / len(lines)
            print(f"First {line_type} line at x = {first_line}")
            print(f"Last {line_type} line at x = {last_line}")
            print(f"Average distance between {line_type} lines = {average_distance_lines}")
            print(f"List of {line_type} line x-locations: {sorted([x1 for x1, y1, x2, y2 in lines])}")
        else:
            print(f"No {line_type} lines detected")

    @staticmethod
    def display_image(window_name, image):
        cv2.imshow(window_name, image)
        cv2.waitKey(0)

    def destroy_all_windows(self):
        cv2.destroyAllWindows()


if __name__ == "__main__":
    line_detector = LineDetector('C:/Users/bethe/PycharmProjects/pythonProject/images/Chrysler_Grand_Voyager.png')
    line_detector.read_image()
    line_detector.convert_to_grayscale()
    line_detector.create_mask(204, 205)
    line_detector.detect_lines(1, np.pi / 180, 10, 50, 10)
    line_detector.draw_and_classify_lines()
    line_detector.analyze_lines()
    line_detector.destroy_all_windows()