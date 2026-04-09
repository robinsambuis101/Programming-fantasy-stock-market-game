"""
Portfolio Chart Module
Creates matplotlib charts showing portfolio performance over time
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict, Any

class PortfolioChart:
    """Handles portfolio visualization using matplotlib"""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def create_portfolio_history_chart(self, net_worth_history: List[float], 
                                     save_path: str = "portfolio_history.png"):
        """Create and save a portfolio value chart over time"""
        # Generate day numbers for x-axis (10 trading days)
        days = list(range(1, len(net_worth_history) + 1))
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the portfolio value
        ax.plot(days, net_worth_history, linewidth=3, marker='o', markersize=6, 
                color='#2E86AB', label='Portfolio Value')
        
        # Add initial investment line
        initial_value = net_worth_history[0]  # Use actual starting value
        ax.axhline(y=initial_value, color='red', linestyle='--', alpha=0.7, 
                  label=f'Initial Investment (${initial_value:,.0f})')
        
        # Fill area above/below initial investment
        ax.fill_between(days, net_worth_history, initial_value, 
                       where=[x >= initial_value for x in net_worth_history],
                       color='green', alpha=0.3, interpolate=True, label='Profit')
        ax.fill_between(days, net_worth_history, initial_value, 
                       where=[x < initial_value for x in net_worth_history],
                       color='red', alpha=0.3, interpolate=True, label='Loss')
        
        # Formatting
        ax.set_title('Portfolio Performance Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Trading Day', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        
        # Format y-axis to show dollar values
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Format x-axis to show trading days
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Day {int(x)}'))
        
        # Set x-axis ticks to show all days
        ax.set_xticks(days)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add legend
        ax.legend(loc='best')
        
        # Add final statistics
        final_value = net_worth_history[-1]
        return_pct = ((final_value - initial_value) / initial_value) * 100
        
        stats_text = f'Final Value: ${final_value:,.2f}\nReturn: {return_pct:+.1f}%'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_sector_performance_chart(self, game_state: Any, 
                                      save_path: str = "sector_performance.png"):
        """Create a sector performance comparison chart"""
        # Group companies by sector and calculate performance
        sector_performance = {}
        
        for symbol, company in game_state.companies.items():
            sector = company.sector
            initial_price = company.ipo_price
            current_price = company.current_price
            performance = ((current_price - initial_price) / initial_price) * 100
            
            if sector not in sector_performance:
                sector_performance[sector] = []
            sector_performance[sector].append(performance)
        
        # Calculate average performance per sector
        sector_avg = {sector: sum(perfs) / len(perfs) 
                     for sector, perfs in sector_performance.items()}
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sectors = list(sector_avg.keys())
        performances = list(sector_avg.values())
        
        # Color coding based on performance
        colors = ['green' if perf >= 0 else 'red' for perf in performances]
        
        bars = ax.bar(sectors, performances, color=colors, alpha=0.7)
        
        # Formatting
        ax.set_title('Sector Performance Comparison', fontsize=16, fontweight='bold')
        ax.set_xlabel('Sector', fontsize=12)
        ax.set_ylabel('Average Return (%)', fontsize=12)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Add value labels on bars
        for bar, perf in zip(bars, performances):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3),
                   f'{perf:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                   fontweight='bold')
        
        # Grid and layout
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def show_chart(self, image_path: str):
        """Display a chart image"""
        try:
            import PIL.Image
            from PIL import Image
            
            img = Image.open(image_path)
            img.show()
        except ImportError:
            print(f"Chart saved to {image_path}")
            print("Install Pillow to view charts automatically: pip install Pillow")
        except Exception as e:
            print(f"Could not display chart: {e}")
            print(f"Chart saved to {image_path}")
