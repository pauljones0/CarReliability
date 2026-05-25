import numpy as np
from pathlib import Path

class Constants:
    # Directories
    BASE_DIR = Path(__file__).parent.parent
    IMAGE_DIR = BASE_DIR / 'images'
    DATA_DIR = BASE_DIR / 'data'
    
    # Reliability Settings
    DESIRED_RELIABILITY_PERCENTAGE = 90
    START_YEAR = 1993
    END_YEAR = 2018
    
    # Graph Coordinates (Clipped Image)
    GRAPH_TOP = 34
    GRAPH_BOTTOM = 556
    GRAPH_LEFT = 59
    GRAPH_RIGHT = 907
    
    # Line Detection Midpoints
    FIRST_FULL_LINE = 32
    LAST_FULL_LINE = 816
    
    # Colors (BGR for OpenCV)
    COLOR_BOTTOM_PIXEL = np.array([217, 217, 255])  # FFD9D9 in RGB -> BGR
    COLOR_TOP_PIXEL = np.array([255, 240, 222])     # DEF0FF in RGB -> BGR
    
    # Line Detection Parameters
    RHO = 0.5
    THETA = np.pi / 180
    THRESHOLD = 10
    MIN_LINE_LENGTH = 25
    MAX_LINE_GAP = 10

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
        # Specific corrections for non-linear year spacing in the graphs
        for midpoint, year in midpoints_to_year_mapping:
            if year in [2000, 2003, 2004, 2006, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
                midpoint += 1
            elif year == 2017:
                midpoint += 2
            corrected_mapping.append((midpoint, year))
        return corrected_mapping
