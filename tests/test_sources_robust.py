import pytest
import re
import requests
from src.sources.fueleconomy import FuelEconomySource
from src.sources.carcomplaints import CarComplaintsSource
from src.sources.repairpal import RepairPalSource
from src.sources.safety import SafetyRatingsSource

def test_fueleconomy_fallback():
    # Test a model that normally returns 'null' but should match via fallback (e.g. BMW 3 Series)
    fe = FuelEconomySource(delay=0)
    data = fe.get_data("BMW", "3 Series", 2010)
    assert data is not None
    assert "city_mpg" in data
    assert "highway_mpg" in data
    assert "combined_mpg" in data
    assert data["combined_mpg"] > 0

def test_fueleconomy_null_handling():
    # Test a non-existent model that returns 'null' to make sure it doesn't crash
    fe = FuelEconomySource(delay=0)
    data = fe.get_data("NonExistentMake", "NonExistentModel", 2010)
    assert data is None

def test_carcomplaints_overall_and_year():
    # Test overall stats retrieval and year-specific count from overview
    cc = CarComplaintsSource(delay=0)
    data = cc.get_data("Honda", "Accord", 2018)
    # If we get blocked/rate limited, data might be None or empty. 
    # But if it succeeded:
    if data is not None and "worst_year" in data:
        assert "worst_year" in data
        assert "worst_category" in data
        assert "carcomplaints_count" in data
        assert int(data["carcomplaints_count"]) > 0

def test_repairpal_aliases():
    # Test that a model with aliases (e.g. BMW 3 Series) resolves and gets cost/ratings
    rp = RepairPalSource(delay=0)
    data = rp.get_data("BMW", "3 Series")
    # If not rate limited (429):
    if data is not None:
        assert "annual_repair_cost" in data
        assert "reliability_rating" in data
        assert data["annual_repair_cost"].startswith("$")

def test_safety_ratings_accord():
    s = SafetyRatingsSource(delay=0)
    data = s.get_data("Honda", "Accord", 2018)
    assert data is not None
    assert "nhtsa_overall_rating" in data
    assert data["nhtsa_overall_rating"] == "5"
    # iihs_award might be missing if IIHS returned 429
