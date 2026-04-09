#!/usr/bin/env python3
"""
Fantasy Stock Market Game
A terminal-based stock trading game powered by Claude AI
"""

import os
import sys
from dotenv import load_dotenv
from colorama import Fore

# Load environment variables
load_dotenv()

from game_state import GameState
from claude_api import ClaudeAPI
from display import Display
from portfolio_chart import PortfolioChart

def main():
    """Main game loop"""
    # Check for test mode
    test_mode = len(sys.argv) > 1 and sys.argv[1] == '--test'
    
    # Initialize game components
    claude = ClaudeAPI()
    display = Display()
    game_state = GameState()
    
    # Start the game
    display.show_welcome()
    
    # Get starting net worth
    starting_net_worth = display.get_starting_net_worth()
    
    # Generate initial companies
    if test_mode:
        display.show_message("Using test mode with mock data...")
        companies = claude._generate_fallback_companies()
    else:
        display.show_message("Generating fictional companies...")
        companies = claude.generate_companies()
    
    game_state.initialize_companies(companies)
    game_state.cash = starting_net_worth
    game_state.net_worth_history = [starting_net_worth]
    
    # Main game loop (10 rounds)
    for round_num in range(1, 11):
        game_state.current_round = round_num
        display.show_round_header(round_num)
        
        # Phase 1: Market News
        display.show_phase_header("Market News")
        if test_mode:
            companies = list(game_state.companies.keys())
            sectors = list(set(company.sector for company in game_state.companies.values()))
            news = claude._generate_fallback_news(companies, sectors)
        else:
            news = claude.generate_market_news(game_state)
        game_state.current_news = news
        display.show_news(news)
        
        # Phase 2: Trading Window
        display.show_phase_header("Trading Window")
        while True:
            display.show_portfolio(game_state)
            display.show_market_table(game_state)
            
            action = display.get_trading_action()
            if action == 'hold':
                break
            elif action == 'buy':
                symbol, shares = display.get_buy_order(game_state)
                if symbol and shares:
                    success = game_state.buy_shares(symbol, shares)
                    if success:
                        display.show_message(f"Bought {shares} shares of {symbol}")
                    else:
                        display.show_message("Failed to buy shares", Fore.RED)
            elif action == 'sell':
                symbol, shares = display.get_sell_order(game_state)
                if symbol and shares:
                    success = game_state.sell_shares(symbol, shares)
                    if success:
                        display.show_message(f"Sold {shares} shares of {symbol}")
                    else:
                        display.show_message("Failed to sell shares", Fore.RED)
        
        # Phase 3: Price Resolution
        display.show_phase_header("Price Resolution")
        if test_mode:
            new_prices = claude._generate_fallback_prices(game_state.to_dict())
        else:
            new_prices = claude.calculate_new_prices(game_state.to_dict())
        game_state.update_prices(new_prices)
        display.show_price_changes(game_state)
        
        # Phase 4: Market Recap
        display.show_phase_header("Market Recap")
        if test_mode:
            import random
            recap_options = [
                "MARKET RECAP: What a wild ride on Wall Street today! The market swung dramatically as investors reacted to breaking news. Some stocks soared while others took a beating. Tomorrow promises more excitement in this unpredictable market!",
                "MARKET RECAP: Trading floors were buzzing today as volatility returned to the market. Winners celebrated big gains while losers licked their wounds. The only certainty in this market? More uncertainty ahead!",
                "MARKET RECAP: Another chaotic trading day comes to a close! Bulls and bears battled it out, leaving some stocks flying high and others deep in the red. Fasten your seatbelts - tomorrow could be even wilder!",
                "MARKET RECAP: Market madness today as stocks seesawed on mixed signals. Traders scrambled to adjust positions amid the chaos. One thing's for sure - this market never sleeps!",
                "MARKET RECAP: Whiplash trading today as investors whipsawed between fear and greed. Some stocks emerged as clear winners while others got crushed. The drama continues tomorrow in this wild market!"
            ]
            recap = random.choice(recap_options)
        else:
            recap = claude.generate_market_recap(game_state.to_dict())
        display.show_recap(recap)
        
        # Special events every 3 rounds
        if round_num % 3 == 0:
            if test_mode:
                companies = list(game_state.companies.keys())
                special_event = claude._generate_fallback_event(companies)
            else:
                special_event = claude.generate_special_event(game_state.to_dict())
            display.show_special_event(special_event)
            game_state.apply_special_event(special_event)
        
        # Continue prompt
        if round_num < 10:
            display.continue_prompt()
    
    # Game Over
    display.show_game_over(game_state, starting_net_worth)
    
    # Generate portfolio chart
    try:
        chart = PortfolioChart()
        chart_path = chart.create_portfolio_history_chart(game_state.net_worth_history)
        display.show_message(f"Portfolio chart saved to {chart_path}", Fore.CYAN)
        
        # Try to show the chart
        chart.show_chart(chart_path)
    except Exception as e:
        display.show_message(f"Could not generate chart: {e}", Fore.RED)
    
    if test_mode:
        final_analysis = f"FINAL ANALYSIS: You started with ${starting_net_worth:,.2f} and ended with ${game_state.calculate_net_worth():.2f}. {'Great job!' if game_state.calculate_net_worth() >= starting_net_worth else 'Better luck next time!'} Your trading strategy was {'bold' if len(game_state.portfolio) > 0 else 'conservative'}. Remember: the market rewards those who read the news carefully!"
    else:
        # Update game state with starting net worth for analysis
        game_state_dict = game_state.to_dict()
        game_state_dict['starting_net_worth'] = starting_net_worth
        final_analysis = claude.generate_final_analysis(game_state_dict)
    display.show_final_analysis(final_analysis)

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY") and '--test' not in sys.argv:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set up your .env file with your Anthropic API key.")
        print("Or run in test mode: python main.py --test")
        sys.exit(1)
    
    main()
