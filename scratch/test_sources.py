
from src.sources.fueleconomy import FuelEconomySource
from src.sources.vmrcanada import VMRCanadaSource
import json

def test_sources():
    fe = FuelEconomySource()
    vmr = VMRCanadaSource()
    
    test_cases = [
        ("Honda", "Accord", 2018),
        ("Mercury", "Montego", 2006),
        ("Chrysler", "LHS", 2000)
    ]
    
    for make, model, year in test_cases:
        print(f"--- Testing {year} {make} {model} ---")
        fe_data = fe.get_data(make, model, year)
        print(f"FuelEconomy: {fe_data}")
        
        vmr_data = vmr.get_data(make, model, year)
        print(f"VMR Canada: {vmr_data}")

if __name__ == "__main__":
    test_sources()
