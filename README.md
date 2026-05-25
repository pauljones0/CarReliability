# CarReliability Aggregator

A powerful tool that aggregates car reliability data from multiple authoritative sources to provide a comprehensive view of vehicle dependability and ownership costs.

## Data Sources

1.  **Dashboard Light:** Historical reliability percentages (1993-2018) extracted via image processing of their quality graphs.
2.  **RepairPal:** Average annual repair costs and overall reliability ratings (out of 5.0).
3.  **NHTSA (National Highway Traffic Safety Administration):** Official recall counts and consumer complaint counts via their public API. Supports models up to **2023/2024**.
4.  **CarComplaints.com:** Identification of the "Worst Model Year" and the most common problem categories.
5.  **BYD (2026 Canadian Entry):** Specialized data for rumored BYD models arriving in Canada in late 2026, synthesized from European and Australian reliability reports.
6.  **FuelEconomy.gov (EPA):** Official City, Highway, and Combined MPG estimates.
7.  **VMR Canada:** Canadian used car price estimates (Wholesale and Retail) by trim.
8.  **CarEdge:** 10-year projected maintenance costs and probability of major repairs.
9.  **Safety Ratings:** Combined official NHTSA 5-star ratings and IIHS crashworthiness awards.

## BYD 2026 Canadian Entry

The tool includes projected data for the following BYD models rumored for the Canadian market:
- **Seagull (Dolphin Mini):** Estimated sub-$25,000 price; expected to be Canada's most affordable EV.
- **Atto 3:** Global bestseller; 5-star Euro NCAP safety rating.
- **Seal:** High-performance sport sedan; Tesla Model 3 rival.
- **Shark:** PHEV Pickup; 800km+ total range; V2L capability for cold-weather utility.

## Project Structure

- `src/`: Source code
  - `sources/`: Modular data source implementations.
    - `dashboard_light.py`: Processes local graph images.
    - `repairpal.py`: Scrapes RepairPal for costs and ratings.
    - `nhtsa.py`: Queries NHTSA API for recalls and complaints.
    - `carcomplaints.py`: Scrapes CarComplaints for model-wide issues.
  - `image_processor.py`: Core image processing logic (OpenCV).
  - `constants.py`: Centralized configuration.
  - `main.py`: Interactive CLI aggregator.
- `data/`: Extracted data and input JSON files.
- `images/`: Raw graph images for Dashboard Light processing.
- `tests/`: Unit tests for core logic.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Query a Specific Car
Get a full reliability profile for a specific make, model, and year. You can also provide the odometer reading (in KM) and your province for localized price adjustments:
```bash
python3 src/main.py --make Honda --model Accord --year 2018 --km 100000 --province BC
```
**Supported Province Codes:** BC, AB, SK, MB, ON_SOUTH, ON_NORTH, QC, NB, NS, PE, NL, YT, NT, NU.

### Batch Process All Images
Aggregate data for all models that have images in the `images/` directory:
```bash
python3 src/main.py --all
```
Results will be saved to `aggregated_reliability.json`.

## Testing
```bash
pytest tests/
```
