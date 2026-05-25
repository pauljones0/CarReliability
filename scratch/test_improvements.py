
from src.main import ReliabilityAggregator
import json

def test_improvements():
    aggregator = ReliabilityAggregator()
    
    test_cases = [
        ("Chevrolet", "Silverado"),
        ("Mercedes-Benz", "E-Class"),
        ("BMW", "3 Series")
    ]
    
    results = {}
    for make, model in test_cases:
        print(f"\n--- Aggregating {make} {model} ---")
        data = aggregator.aggregate(make, model)
        results[f"{make}_{model}"] = data
        
        # Check specific fields that were problematic
        print(f"  Ten Year Maintenance: {data.get('ten_year_maintenance_cost')}")
        print(f"  Annual Repair Cost: {data.get('annual_repair_cost')}")
        print(f"  City MPG: {data.get('city_mpg')}")
        print(f"  Price Estimates: {bool(data.get('canadian_price_estimates'))}")

if __name__ == "__main__":
    test_improvements()
