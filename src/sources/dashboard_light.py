import os
from src.sources.base_source import BaseSource
from src.image_processor import Image, LineDetector, YearQualityMapper
from src.constants import Constants

class DashboardLightSource(BaseSource):
    def __init__(self):
        self.image_dir = Constants.IMAGE_DIR

    def get_data(self, make, model, year=None):
        # Dashboard Light files are named 'Make_Model.png'
        filename = f"{make}_{model.replace(' ', '_')}.png"
        file_path = self.image_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            image = Image(file_path)
            line_detector = LineDetector(image.image)
            lines = line_detector.detect_lines()
            
            mapper = YearQualityMapper(image.image, lines)
            year_to_quality = mapper.create_year_quality_mapping()
            
            data = {str(y): int(p) for y, p in year_to_quality}
            
            if year:
                return data.get(str(year))
            return data
        except Exception as e:
            print(f"Error processing DashboardLight for {make} {model}: {e}")
            return None
