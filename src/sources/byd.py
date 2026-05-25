from src.sources.base_source import BaseSource

class BYDSource(BaseSource):
    # Data derived from European (OCU) and Australian (ANCAP/CarExpert) 2025/2026 reports
    BYD_MODELS = {
        "Seagull": {
            "type": "City Hatchback (EV)",
            "est_price": "$22,000 - $30,000 CAD",
            "reliability_blurb": "Ranked highly in China for build quality relative to price. Features the 'Blade' LFP battery, known for longevity and safety. Software is the primary variable for North American compliance.",
            "market_note": "Expected to be Canada's most affordable EV."
        },
        "Atto 3": {
            "type": "Compact SUV (EV)",
            "est_price": "$43,000 - $48,000 CAD",
            "reliability_blurb": "Top 10 most reliable brand in Europe (OCU 2026). Global bestseller with mature hardware. Australian owners report robust mechanicals but minor software ADAS sensitivity.",
            "safety_rating": "5-star Euro NCAP"
        },
        "Seal": {
            "type": "Sport Sedan (EV)",
            "est_price": "$55,000 - $62,000 CAD",
            "reliability_blurb": "Tesla Model 3 rival. 2024 J.D. Power China study suggests refined build quality. Minimal battery degradation reported in Australian multi-year fleets.",
            "safety_rating": "5-star ANCAP"
        },
        "Shark": {
            "type": "PHEV Pickup",
            "est_price": "$55,000 - $60,000 CAD",
            "reliability_blurb": "New platform (DMO). Plug-in hybrid setup offers cold-weather resilience for Canada. High torque and towing specs, but long-term reliability of the complex PHEV system is still being established.",
            "utility": "V2L capability (powers external tools)"
        }
    }

    def get_data(self, make, model, year=None):
        if make.upper() != "BYD":
            return None
            
        # Try to match model name
        for model_name, info in self.BYD_MODELS.items():
            if model_name.lower() in model.lower():
                data = info.copy()
                data['source'] = "2026 Canadian Market Rumors & International Data"
                return data
        
        return {
            "note": "General BYD data: Ranked 6th most reliable brand in Europe (2026) by OCU (89/100 score).",
            "source": "OCU Europe 2026"
        }
