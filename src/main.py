import argparse
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.constants import Constants
from src.sources.dashboard_light import DashboardLightSource
from src.sources.repairpal import RepairPalSource
from src.sources.nhtsa import NHTSASource
from src.sources.carcomplaints import CarComplaintsSource
from src.sources.byd import BYDSource
from src.sources.fueleconomy import FuelEconomySource
from src.sources.vmrcanada import VMRCanadaSource
from src.sources.caredge import CarEdgeSource
from src.sources.safety import SafetyRatingsSource
from src.file_handler import FileHandler

class ReliabilityAggregator:
    def __init__(self):
        self.sources = {
            'dashboard_light': DashboardLightSource(),
            'repairpal': RepairPalSource(),
            'nhtsa': NHTSASource(),
            'carcomplaints': CarComplaintsSource(),
            'byd': BYDSource(),
            'fueleconomy': FuelEconomySource(),
            'vmrcanada': VMRCanadaSource(),
            'caredge': CarEdgeSource(),
            'safety': SafetyRatingsSource()
        }

    def _discover_year(self, make, model):
        """Discover the most recent valid model year using real data sources."""
        # --- Source 1: CarComplaints overview ---
        cc_overview = self.sources['carcomplaints'].get_data(make, model)
        if cc_overview:
            available = cc_overview.get('available_years', [])
            if available:
                return max(available), cc_overview
        
        # --- Source 2: NHTSA model-years API ---
        try:
            url = f"https://api.nhtsa.gov/products/vehicle/modelYears?issueType=c&make={make}&model={model}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                years = [int(r['modelYear']) for r in results if str(r.get('modelYear', '')).isdigit()]
                if years:
                    return max(years), cc_overview
        except Exception:
            pass

        return None, cc_overview

    def aggregate(self, make, model, year=None, km=None, province="ON_SOUTH"):
        # Global Normalization / Brand Aliasing
        original_make = make
        original_model = model
        
        # Brand redirects
        if make.upper() == "GMC" and "SUBURBAN" in model.upper():
            make = "Chevrolet"
        elif make.upper() == "SCION":
            make = "Toyota"
            
        print(f"Aggregating data for {year or 'latest'} {make} {model}...")
        results = {}

        # BYD Specific Check
        if make.upper() == "BYD":
            byd_data = self.sources['byd'].get_data(make, model, year)
            if byd_data:
                results.update(byd_data)
            return results

        # 1. Dashboard Light (Historical) — year-independent, always fetch
        dl_data = self.sources['dashboard_light'].get_data(make, model)
        if dl_data:
            results['historical_reliability'] = dl_data

        # Determine the year to use for all year-dependent API queries.
        query_year = year
        prefetched_cc = None

        if not query_year:
            # Try Dashboard Light years first (already in memory, zero extra cost)
            if dl_data:
                dl_years = sorted([int(y) for y in dl_data.keys()])
                if dl_years:
                    query_year = dl_years[-1]

        # Hit CarComplaints + NHTSA to find the real latest year
        discovered_year, prefetched_cc = self._discover_year(make, model)
        if not query_year and discovered_year:
            query_year = discovered_year
            
        # Prio 3: Default for older/discontinued cars if still unknown
        if not query_year:
            query_year = 2015 # A safe modern default for pricing/recalls if all discovery fails

        results['data_year'] = query_year

        # 2. RepairPal (Costs/Ratings) — year-independent
        rp_data = self.sources['repairpal'].get_data(make, model)
        if rp_data:
            results.update(rp_data)

        # 3. CarComplaints (Issues)
        # Re-use pre-fetched overview data if we already called it during year discovery
        if prefetched_cc is not None:
            cc_data = prefetched_cc
            # Now enrich with the year-specific complaint count if we have a year
            if query_year and 'carcomplaints_count' not in cc_data:
                cc_extra = self.sources['carcomplaints'].get_data(make, model, query_year)
                if cc_extra:
                    cc_data.update(cc_extra)
        else:
            cc_data = self.sources['carcomplaints'].get_data(make, model, query_year)
        if cc_data:
            # Remove internal available_years from the final output
            cc_data.pop('available_years', None)
            results.update(cc_data)

        # 4. NHTSA (Recalls/Complaints)
        nhtsa_data = self.sources['nhtsa'].get_data(make, model, query_year)
        if nhtsa_data:
            results.update(nhtsa_data)

        # 5. Fuel Economy (MPG)
        mpg_data = self.sources['fueleconomy'].get_data(make, model, query_year)
        if mpg_data:
            results.update(mpg_data)

        # 6. VMR Canada (Pricing)
        vmr_data = self.sources['vmrcanada'].get_data(make, model, query_year, km, province)
        if vmr_data:
            results.update(vmr_data)

        # 7. CarEdge (Maintenance Projections) — year-independent
        ce_data = self.sources['caredge'].get_data(make, model)
        if ce_data:
            results.update(ce_data)

        # 8. Safety Ratings (NHTSA/IIHS)
        safety_data = self.sources['safety'].get_data(make, model, query_year)
        if safety_data:
            results.update(safety_data)

        return results

def main():
    parser = argparse.ArgumentParser(description="Car Reliability Aggregator")
    parser.add_argument("--make", help="Car make (e.g., Honda)")
    parser.add_argument("--model", help="Car model (e.g., Accord)")
    parser.add_argument("--year", type=int, help="Car year (e.g., 2018)")
    parser.add_argument("--km", type=int, help="Odometer reading in KM for price adjustment")
    parser.add_argument("--province", default="ON_SOUTH", help="Province code (e.g., BC, AB, QC) for price adjustment")
    parser.add_argument("--all", action="store_true", help="Process all images in the image directory")
    parser.add_argument("--limit", type=int, help="Limit the number of models processed in batch mode")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers for batch processing")
    
    args = parser.parse_args()
    aggregator = ReliabilityAggregator()

    if args.all:
        result_dict = {}
        filenames = [f for f in os.listdir(Constants.IMAGE_DIR) if f.endswith(".png")]
        if args.limit:
            filenames = filenames[:args.limit]

        print(f"Starting batch processing of {len(filenames)} models with {args.workers} workers...")

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_model = {}
            for filename in filenames:
                if filename.startswith("Land_Rover_"):
                    make = "Land Rover"
                    model = filename[len("Land_Rover_"):-4].replace('_', ' ')
                else:
                    parts = filename[:-4].split('_', 1)
                    if len(parts) == 2:
                        make, model = parts
                        model = model.replace('_', ' ')
                    else:
                        continue
                
                # In batch mode, we use default km/province
                future = executor.submit(aggregator.aggregate, make, model)
                future_to_model[future] = f"{make}_{model}"
            
            processed_count = 0
            for future in as_completed(future_to_model):
                model_key = future_to_model[future]
                try:
                    data = future.result()
                    result_dict[model_key] = data
                except Exception as e:
                    print(f"Error processing {model_key}: {e}")
                
                processed_count += 1
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count}/{len(filenames)} models...")
                    FileHandler.write_to_json('aggregated_reliability.json', result_dict)
        
        FileHandler.write_to_json('aggregated_reliability.json', result_dict)
        print("Batch processing complete. Results saved to aggregated_reliability.json")
        
    elif args.make and args.model:
        data = aggregator.aggregate(args.make, args.model, args.year, args.km, args.province)
        print(json.dumps(data, indent=4))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
