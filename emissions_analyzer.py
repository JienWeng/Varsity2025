import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class EmissionsAnalyzer:
    """Class to read and analyze CodeCarbon emissions logs."""
    
    def __init__(self, emissions_dir="./emissions"):
        self.emissions_dir = Path(emissions_dir)
        self.ensure_emissions_dir()
        self.emissions_data = self.load_emissions_data()
    
    def ensure_emissions_dir(self):
        """Ensure the emissions directory exists."""
        os.makedirs(self.emissions_dir, exist_ok=True)
    
    def load_emissions_data(self):
        """Load all emissions CSV files into a single DataFrame."""
        csv_files = list(self.emissions_dir.glob("*.csv"))
        
        if not csv_files:
            return pd.DataFrame()  # Return empty if no data
        
        df_list = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                df['source_file'] = file.name
                df_list.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        if df_list:
            all_data = pd.concat(df_list, ignore_index=True)
            all_data['timestamp'] = pd.to_datetime(all_data['timestamp'], errors='coerce')
            return all_data
        else:
            return pd.DataFrame()
    
    def get_emissions_over_time(self):
        """Get emissions and energy consumption over time."""
        if self.emissions_data.empty:
            return pd.DataFrame()
        
        # Group by timestamp if needed or just return full data
        return self.emissions_data[['timestamp', 'emissions', 'energy_consumed']]
    
    def generate_emissions_report(self):
        """Generate a simple report about emissions data."""
        if self.emissions_data.empty:
            return {
                "last_updated": "No Data",
                "total_emissions_kg": 0.0,
                "total_energy_kwh": 0.0,
                "call_count": 0,
                "average_emissions_per_call_kg": 0.0
            }
        
        total_emissions = self.emissions_data['emissions'].sum()
        total_energy = self.emissions_data['energy_consumed'].sum()
        call_count = len(self.emissions_data)
        avg_emissions_per_call = total_emissions / call_count if call_count else 0.0
        
        last_updated = self.emissions_data['timestamp'].max()
        
        return {
            "last_updated": last_updated.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(last_updated) else "Unknown",
            "total_emissions_kg": total_emissions,
            "total_energy_kwh": total_energy,
            "call_count": call_count,
            "average_emissions_per_call_kg": avg_emissions_per_call
        }
