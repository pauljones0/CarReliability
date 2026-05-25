import pytest
import numpy as np
from src.image_processor import YearQualityMapper
from src.constants import Constants

def test_year_quality_mapper_horizontal_line():
    # Create a dummy image (height=100, width=900)
    height, width = 100, 900
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # A horizontal line at y=50 (which should be 50% quality if height is 100)
    # Actually, the logic is: percentage = round(((height - y1) / height) * 100)
    # So if y=50, height=100, percentage = round((50/100)*100) = 50.
    
    # Let's pick a year, say 2010. 
    # generate_midpoints_to_year_mapping includes (midpoint, 2010)
    midpoint_2010 = next(m for m, y in Constants.generate_midpoints_to_year_mapping() if y == 2010)
    
    lines = [np.array([[midpoint_2010 - 10, 50, midpoint_2010 + 10, 50]])]
    
    mapper = YearQualityMapper(image, lines)
    mapping = mapper.create_year_quality_mapping()
    
    assert (2010, 50) in mapping

def test_year_quality_mapper_top_pixel():
    height, width = 100, 900
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    midpoint_2015 = next(m for m, y in Constants.generate_midpoints_to_year_mapping() if y == 2015)
    
    # Top pixel at (30, midpoint) should be Constants.COLOR_TOP_PIXEL
    image[30, midpoint_2015] = Constants.COLOR_TOP_PIXEL
    
    mapper = YearQualityMapper(image, [])
    mapping = mapper.create_year_quality_mapping()
    
    assert (2015, 100) in mapping

def test_year_quality_mapper_bottom_pixel():
    height, width = 100, 900
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    midpoint_2005 = next(m for m, y in Constants.generate_midpoints_to_year_mapping() if y == 2005)
    
    # Bottom pixel at (height-30, midpoint) should be Constants.COLOR_BOTTOM_PIXEL
    image[height - 30, midpoint_2005] = Constants.COLOR_BOTTOM_PIXEL
    
    mapper = YearQualityMapper(image, [])
    mapping = mapper.create_year_quality_mapping()
    
    assert (2005, 0) in mapping
