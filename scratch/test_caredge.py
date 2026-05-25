
from src.sources.caredge import CarEdgeSource
import json

def test_caredge():
    ce = CarEdgeSource()
    test_cases = [
        ("Honda", "Accord"),
        ("Toyota", "Camry"),
        ("Ford", "F-150"),
        ("Chevrolet", "Silverado"),
        ("BMW", "3 Series"),
        ("Mercedes-Benz", "E-Class")
    ]
    
    for make, model in test_cases:
        print(f"--- Testing {make} {model} ---")
        data = ce.get_data(make, model)
        print(f"Result: {data}")

if __name__ == "__main__":
    test_caredge()
