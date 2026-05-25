import cv2
import numpy as np
from src.constants import Constants
from src.image_processor import Image, LineDetector, YearQualityMapper

# Pick an image for testing
IMAGE_PATH = Constants.IMAGE_DIR / 'Acura_TL.png'

def show_image(window_name, img):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    if not IMAGE_PATH.exists():
        print(f"Image not found: {IMAGE_PATH}")
        return

    # Load and crop image
    image_obj = Image(IMAGE_PATH)
    
    # Detect lines
    line_detector = LineDetector(image_obj.image)
    lines = line_detector.detect_lines()
    
    # Draw detected lines for visualization
    vis_img = image_obj.image.copy()
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    show_image('Detected Lines', vis_img)
    
    # Map to year/quality
    mapper = YearQualityMapper(image_obj.image, lines)
    year_to_quality = mapper.create_year_quality_mapping()
    
    if year_to_quality:
        print("Year Quality Mapping:")
        for year, percent in sorted(year_to_quality):
            print(f"{year}: {percent}%")
    else:
        print("No mapping generated.")

if __name__ == "__main__":
    main()
