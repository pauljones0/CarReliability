
from src.main import ReliabilityAggregator
import json

def test_missing_cars():
    aggregator = ReliabilityAggregator()
    
    test_cases = [
        ("BMW", "8 Series"),
        ("Saturn", "S Series"),
        ("Dodge", "Ram"),
        ("Land Rover", "Defender"),
        ("Mercedes-Benz", "SL Class"),
        ("GMC", "Suburban")
    ]
    
    for make, model in test_cases:
        print(f"\n--- Testing {make} {model} ---")
        data = aggregator.aggregate(make, model)
        print(f"Data fields found: {list(data.keys())}")
        if 'annual_repair_cost' not in data:
            print("  RepairPal failed")
        if 'carcomplaints_count' not in data:
            print("  CarComplaints failed")
        if 'city_mpg' not in data:
            print("  FuelEconomy failed")
        if 'recall_count' not in data:
            print("  NHTSA failed")

if __name__ == "__main__":
    test_missing_cars()
