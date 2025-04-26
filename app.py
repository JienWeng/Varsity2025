import gradio as gr
from services.chat_service import ChatService
from emissions_analyzer import EmissionsAnalyzer
import matplotlib.pyplot as plt
import io
from PIL import Image

chat_service = ChatService()
emissions_analyzer = EmissionsAnalyzer()

def respond(
    message: str, 
    history: list[tuple[str, str]], 
    system_message: str, 
    max_tokens: int, 
    temperature: float, 
    top_p: float,
):
    result = chat_service.generate_response(
        message, history, system_message, max_tokens, temperature, top_p
    )
    
    # Add carbon information
    if result["from_cache"]:
        carbon_info = f"(Response from cache. Saved {result['emissions_saved']:.6f} kg CO2eq)"
    else:
        carbon_info = f"(Generated new response. Used {result['emissions']:.6f} kg CO2eq)"
    
    return result["response"] + "\n\n" + carbon_info

def get_carbon_stats():
    """Get and format carbon emission statistics."""
    try:
        stats = chat_service.emissions_stats
        
        # Avoid division by zero
        calls = max(1, stats.get("calls", 0))
        total_calls = max(1, stats.get("calls", 0) + stats.get("cached_calls", 0))
        cache_efficiency = stats.get("cached_calls", 0) / total_calls * 100
        avg_emissions = stats.get("total_emissions", 0.0) / calls
        
        markdown = f"""
        ## Carbon Emission Stats
        
        ### Current Session
        - Total CO2 Emissions: {stats.get("total_emissions", 0.0):.6f} kg CO2eq
        - Total Energy Consumed: {stats.get("total_energy", 0.0):.6f} kWh
        - Total API Calls: {stats.get("calls", 0)}
        - Cached Responses Used: {stats.get("cached_calls", 0)}
        
        ### Savings from Cache
        - CO2 Emissions Saved: {stats.get("emissions_saved", 0.0):.6f} kg CO2eq
        - Energy Saved: {stats.get("energy_saved", 0.0):.6f} kWh
        - Total Cache Hits: {stats.get("cache_hits", 0)}
        
        ### Efficiency Metrics
        - Average Emissions per Call: {avg_emissions:.6f} kg CO2eq
        - Cache Efficiency: {cache_efficiency:.2f}%
        """
        
        return markdown
    except Exception as e:
        return f"Error retrieving carbon stats: {str(e)}"

def create_emissions_plot():
    """Create a plot of emissions over time."""
    emissions_over_time = emissions_analyzer.get_emissions_over_time()
    
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
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    return Image.open(buf)

def create_energy_plot():
    """Create a plot of energy consumption over time."""
    emissions_over_time = emissions_analyzer.get_emissions_over_time()
    
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
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    return Image.open(buf)

# ✅ New function to refresh dashboard
def refresh_dashboard():
    emissions_analyzer.load_emissions_data()
    return get_carbon_stats(), create_emissions_plot(), create_energy_plot()

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("EcoChat"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.ChatInterface(
                        respond,
                        additional_inputs=[
                            gr.Textbox(
                                value="You are a friendly EcoChat bot. You provide information about environmental topics and also track your own carbon footprint.", 
                                label="System message"
                            ),
                            gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens"),
                            gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
                            gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)"),
                        ],
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("## Carbon Tracker")
                    carbon_stats = gr.Markdown("Click the button to see carbon stats")
                    carbon_button = gr.Button("Show Carbon Stats", variant="primary")
                    carbon_button.click(get_carbon_stats, outputs=carbon_stats)
                    
                    gr.Markdown("### What is this?")
                    gr.Markdown("""
                    This panel shows the carbon footprint of your conversation with the EcoChat bot.
                    
                    Each new response generates CO2 emissions from computing resources.
                    By caching responses, we can reduce our carbon footprint when the same 
                    questions are asked multiple times.
                    """)

        with gr.Tab("Carbon Dashboard"):
            with gr.Row():
                refresh_button = gr.Button("Refresh Dashboard Data")
            
            with gr.Row():
                dashboard_stats = gr.Markdown()
            
            with gr.Row():
                with gr.Column():
                    emissions_plot = gr.Image(label="Emissions Over Time")
                with gr.Column():
                    energy_plot = gr.Image(label="Energy Consumption Over Time")
            
            refresh_button.click(
                fn=refresh_dashboard,
                outputs=[dashboard_stats, emissions_plot, energy_plot]
            )

if __name__ == "__main__":
    demo.launch()
