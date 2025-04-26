import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import io
from PIL import Image
import os
from pathlib import Path
from emissions_analyzer import EmissionsAnalyzer

def create_carbon_dashboard():
    """Create a Gradio interface for the carbon emissions dashboard."""
    
    analyzer = EmissionsAnalyzer()
    
    def refresh_stats():
        """Refresh the emissions statistics."""
        analyzer.emissions_data = analyzer.load_emissions_data()
        report = analyzer.generate_emissions_report()
        
        markdown = f"""
        ## Carbon Emissions Dashboard
        
        **Last Updated:** {report['last_updated']}
        
        ### Emissions Summary
        - **Total CO2 Emissions:** {report['total_emissions_kg']:.8f} kg CO2eq
        - **Total Energy Consumed:** {report['total_energy_kwh']:.8f} kWh
        - **Number of API Calls:** {report['call_count']}
        - **Average Emissions per Call:** {report['average_emissions_per_call_kg']:.8f} kg CO2eq
        
        ### Environmental Impact Context
        To put these numbers in perspective:
        - The average car emits about 0.2 kg CO2eq per kilometer
        - A tree absorbs about 22 kg of CO2 per year
        
        ### Improvement Suggestions
        - Keep using the cache system to avoid regenerating responses
        - Consider batching multiple queries together when possible
        - Run the model on more energy-efficient hardware when available
        """
        
        return markdown
    
    def create_emissions_plot():
        """Create and return a plot of emissions over time."""
        emissions_over_time = analyzer.get_emissions_over_time()
        
        if emissions_over_time.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.plot(emissions_over_time['timestamp'], emissions_over_time['emissions'], marker='o', color='green')
        plt.title('CO2 Emissions Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('Emissions (kg CO2eq)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return Image.open(buf)
    
    def create_energy_plot():
        """Create and return a plot of energy consumption over time."""
        emissions_over_time = analyzer.get_emissions_over_time()
        
        if emissions_over_time.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.plot(emissions_over_time['timestamp'], emissions_over_time['energy_consumed'], marker='o', color='blue')
        plt.title('Energy Consumption Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('Energy (kWh)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return Image.open(buf)
    
    with gr.Blocks() as dashboard:
        gr.Markdown("# EcoChat Carbon Emissions Dashboard")
        
        with gr.Row():
            refresh_button = gr.Button("Refresh Data")
        
        with gr.Row():
            stats_md = gr.Markdown()
        
        with gr.Row():
            with gr.Column():
                emissions_plot = gr.Image(label="Emissions Over Time")
            with gr.Column():
                energy_plot = gr.Image(label="Energy Consumption Over Time")
        
        refresh_button.click(
            fn=lambda: (refresh_stats(), create_emissions_plot(), create_energy_plot()),
            outputs=[stats_md, emissions_plot, energy_plot]
        )
        
        # Initialize with data
        dashboard.load(
            fn=lambda: (refresh_stats(), create_emissions_plot(), create_energy_plot()),
            outputs=[stats_md, emissions_plot, energy_plot]
        )
    
    return dashboard

if __name__ == "__main__":
    dashboard = create_carbon_dashboard()
    dashboard.launch()