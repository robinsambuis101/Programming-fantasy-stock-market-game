"""
Display Module
Handles all terminal output and user interface using colorama
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from colorama import init, Fore, Back, Style
import math

# Initialize colorama
init()

class Display:
    """Handles all terminal display and user interaction"""
    
    def __init__(self):
        self.terminal_width = 80
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_starting_net_worth(self):
        """Get starting net worth from user"""
        while True:
            self.clear_screen()
            print(f"{Fore.CYAN}{'=' * self.terminal_width}")
            print(f"{Fore.YELLOW}    CHOOSE YOUR STARTING CAPITAL")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}")
            print()
            print(f"{Fore.WHITE}Select your starting amount:")
            print(f"1. $5,000  (Beginner)")
            print(f"2. $10,000 (Standard)")
            print(f"3. $25,000 (Advanced)")
            print(f"4. $50,000 (Expert)")
            print(f"5. $100,000 (Whale)")
            print(f"6. Custom amount")
            print()
            
            choice = input(f"{Fore.GREEN}Enter choice (1-6): {Style.RESET_ALL}").strip()
            
            amounts = {
                '1': 5000,
                '2': 10000,
                '3': 25000,
                '4': 50000,
                '5': 100000
            }
            
            if choice in amounts:
                return amounts[choice]
            elif choice == '6':
                while True:
                    try:
                        amount = float(input(f"{Fore.GREEN}Enter custom amount ($1,000 - $1,000,000): {Style.RESET_ALL}"))
                        if 1000 <= amount <= 1000000:
                            return amount
                        else:
                            print(f"{Fore.RED}Amount must be between $1,000 and $1,000,000{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
    
    def show_welcome(self):
        """Display welcome screen"""
        self.clear_screen()
        welcome_text = f"""
{Fore.CYAN}{'=' * self.terminal_width}
{Fore.YELLOW}    FANTASY STOCK MARKET GAME
{Fore.CYAN}{'=' * self.terminal_width}

{Fore.WHITE}Welcome to the most chaotic stock market simulation ever created!
You start with ${Fore.GREEN}10,000{Fore.WHITE} in cash and 10 trading days to make your fortune.

{Fore.YELLOW}HOW TO PLAY:
{Fore.WHITE}1. Read the market news carefully
2. Buy, sell, or hold stocks based on your analysis
3. Watch prices move based on news and market sentiment
4. Survive special events every 3 rounds
5. Try to beat the market and earn your grade!

{Fore.RED}WARNING: This game is powered by AI chaos. No two playthroughs are identical.
{Fore.CYAN}{'=' * self.terminal_width}
{Style.RESET_ALL}"""
        
        print(welcome_text)
        input(f"{Fore.GREEN}Press Enter to begin your trading career...{Style.RESET_ALL}")
    
    def show_round_header(self, round_num: int):
        """Display round header"""
        self.clear_screen()
        header = f"""
{Fore.CYAN}{'=' * self.terminal_width}
{Fore.YELLOW}    TRADING DAY {round_num} of 10
{Fore.CYAN}{'=' * self.terminal_width}
{Style.RESET_ALL}"""
        print(header)
    
    def show_phase_header(self, phase_name: str):
        """Display phase header"""
        print(f"\n{Fore.MAGENTA}--- {phase_name.upper()} ---{Style.RESET_ALL}\n")
    
    def show_message(self, message: str, color: str = Fore.WHITE):
        """Show a simple message"""
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def show_news(self, news: List[Dict[str, Any]]):
        """Display market news"""
        print(f"{Fore.YELLOW}BREAKING NEWS:{Style.RESET_ALL}\n")
        
        for i, news_item in enumerate(news, 1):
            category_color = {
                'global': Fore.RED,
                'sector': Fore.BLUE,
                'company': Fore.GREEN
            }.get(news_item.get('category', ''), Fore.WHITE)
            
            print(f"{i}. {category_color}{news_item['headline'].upper()}{Style.RESET_ALL}")
            
            # Add subtle hints about affected companies
            if news_item.get('affected_companies') and news_item['affected_companies'] != ['all']:
                print(f"   {Fore.CYAN}Impact: This could affect {', '.join(news_item['affected_companies'])}{Style.RESET_ALL}")
            elif news_item.get('sector'):
                print(f"   {Fore.CYAN}Impact: {news_item['sector'].title()} sector may be affected{Style.RESET_ALL}")
            
            print()
    
    def show_portfolio(self, game_state):
        """Display player's current portfolio"""
        print(f"{Fore.GREEN}YOUR PORTFOLIO:{Style.RESET_ALL}")
        print(f"Cash: ${Fore.GREEN}{game_state.cash:,.2f}{Style.RESET_ALL}")
        print(f"Portfolio Value: ${Fore.GREEN}{game_state.get_portfolio_value():,.2f}{Style.RESET_ALL}")
        print(f"Total Net Worth: ${Fore.YELLOW}{game_state.calculate_net_worth():,.2f}{Style.RESET_ALL}")
        
        if game_state.portfolio:
            print(f"\n{Fore.CYAN}Holdings:{Style.RESET_ALL}")
            for symbol, shares in game_state.portfolio.items():
                company = game_state.companies[symbol]
                value = shares * company.current_price
                print(f"  {symbol}: {shares} shares @ ${company.current_price:.2f} = ${value:.2f}")
        
        print()
    
    def show_market_table(self, game_state):
        """Display market table with all companies and prices"""
        print(f"{Fore.CYAN}MARKET OVERVIEW:{Style.RESET_ALL}")
        print(f"{'Symbol':<6} {'Name':<20} {'Sector':<12} {'Price':<10} {'Change':<10}")
        print("-" * 65)
        
        for symbol, company in game_state.companies.items():
            price_change = game_state.get_price_change(symbol)
            
            # Color code the price change
            if price_change > 0:
                change_color = Fore.GREEN
                change_symbol = "+"
            elif price_change < 0:
                change_color = Fore.RED
                change_symbol = ""
            else:
                change_color = Fore.WHITE
                change_symbol = ""
            
            # Truncate name if too long
            name = company.name[:18] + ".." if len(company.name) > 20 else company.name
            
            print(f"{symbol:<6} {name:<20} {company.sector:<12} "
                  f"${company.current_price:<9.2f} "
                  f"{change_color}{change_symbol}{price_change:+.1f}%{Style.RESET_ALL}")
        
        print()
    
    def get_trading_action(self) -> str:
        """Get trading action from user"""
        while True:
            print(f"{Fore.YELLOW}Choose your action:{Style.RESET_ALL}")
            print("1. BUY shares")
            print("2. SELL shares") 
            print("3. HOLD (skip trading)")
            
            choice = input(f"\n{Fore.GREEN}Enter choice (1-3): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                return 'buy'
            elif choice == '2':
                return 'sell'
            elif choice == '3':
                return 'hold'
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
    
    def get_buy_order(self, game_state) -> Tuple[Optional[str], Optional[int]]:
        """Get buy order from user"""
        print(f"\n{Fore.GREEN}BUY ORDER{Style.RESET_ALL}")
        
        # Show available companies
        available = []
        for symbol, company in game_state.companies.items():
            max_shares = int(game_state.cash / company.current_price)
            if max_shares > 0:
                available.append((symbol, company, max_shares))
        
        if not available:
            print(f"{Fore.RED}You don't have enough cash to buy any shares!{Style.RESET_ALL}")
            return None, None
        
        print("Available companies:")
        for symbol, company, max_shares in available:
            print(f"  {symbol}: {company.name} - ${company.current_price:.2f} (max {max_shares} shares)")
        
        symbol = input(f"\n{Fore.GREEN}Enter company symbol: {Style.RESET_ALL}").strip().upper()
        
        if symbol not in game_state.companies:
            print(f"{Fore.RED}Invalid company symbol!{Style.RESET_ALL}")
            return None, None
        
        max_shares = int(game_state.cash / game_state.companies[symbol].current_price)
        if max_shares == 0:
            print(f"{Fore.RED}Not enough cash to buy {symbol}!{Style.RESET_ALL}")
            return None, None
        
        while True:
            try:
                shares = int(input(f"{Fore.GREEN}Enter number of shares (1-{max_shares}): {Style.RESET_ALL}"))
                if 1 <= shares <= max_shares:
                    return symbol, shares
                else:
                    print(f"{Fore.RED}Please enter a number between 1 and {max_shares}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
    
    def get_sell_order(self, game_state) -> Tuple[Optional[str], Optional[int]]:
        """Get sell order from user"""
        print(f"\n{Fore.RED}SELL ORDER{Style.RESET_ALL}")
        
        if not game_state.portfolio:
            print(f"{Fore.RED}You don't own any shares to sell!{Style.RESET_ALL}")
            return None, None
        
        print("Your holdings:")
        for symbol, shares in game_state.portfolio.items():
            company = game_state.companies[symbol]
            value = shares * company.current_price
            print(f"  {symbol}: {shares} shares @ ${company.current_price:.2f} = ${value:.2f}")
        
        symbol = input(f"\n{Fore.GREEN}Enter company symbol: {Style.RESET_ALL}").strip().upper()
        
        if symbol not in game_state.portfolio:
            print(f"{Fore.RED}You don't own any shares of {symbol}!{Style.RESET_ALL}")
            return None, None
        
        max_shares = game_state.portfolio[symbol]
        
        while True:
            try:
                shares = int(input(f"{Fore.GREEN}Enter number of shares (1-{max_shares}): {Style.RESET_ALL}"))
                if 1 <= shares <= max_shares:
                    return symbol, shares
                else:
                    print(f"{Fore.RED}Please enter a number between 1 and {max_shares}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
    
    def show_price_changes(self, game_state):
        """Show price changes after resolution"""
        print(f"{Fore.YELLOW}PRICE MOVEMENTS:{Style.RESET_ALL}\n")
        
        movers = []
        for symbol, company in game_state.companies.items():
            change = game_state.get_price_change(symbol)
            movers.append((symbol, company.name, change, company.current_price))
        
        # Sort by biggest movers
        movers.sort(key=lambda x: abs(x[2]), reverse=True)
        
        for symbol, name, change, price in movers:
            if change > 0:
                color = Fore.GREEN
                arrow = "UP"
            elif change < 0:
                color = Fore.RED
                arrow = "DOWN"
            else:
                color = Fore.WHITE
                arrow = "FLAT"
            
            print(f"{symbol}: {color}{arrow} {change:+.1f}% (${price:.2f}){Style.RESET_ALL}")
        
        print()
    
    def show_recap(self, recap: str):
        """Display market recap"""
        print(f"{Fore.MAGENTA}MARKET RECAP:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{recap}{Style.RESET_ALL}\n")
    
    def show_special_event(self, event: Dict[str, Any]):
        """Display special event"""
        print(f"{Fore.RED}{'!' * 20} SPECIAL EVENT {'!' * 20}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{event.get('title', 'SPECIAL EVENT')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{event.get('description', '')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{event.get('effects', '')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{'!' * 55}{Style.RESET_ALL}\n")
    
    def show_game_over(self, game_state, initial_worth):
        """Display game over screen"""
        self.clear_screen()
        
        final_worth = game_state.calculate_net_worth()
        return_pct = ((final_worth - initial_worth) / initial_worth) * 100
        
        # Determine grade
        if return_pct >= 100:
            grade = "S"
            grade_color = Fore.YELLOW
        elif return_pct >= 50:
            grade = "A"
            grade_color = Fore.GREEN
        elif return_pct >= 20:
            grade = "B"
            grade_color = Fore.CYAN
        elif return_pct >= 0:
            grade = "C"
            grade_color = Fore.WHITE
        else:
            grade = "D"
            grade_color = Fore.RED
        
        game_over_text = f"""
{Fore.RED}{'=' * self.terminal_width}
{Fore.YELLOW}    GAME OVER - TRADING COMPLETE
{Fore.RED}{'=' * self.terminal_width}

{Fore.WHITE}FINAL RESULTS:
Initial Investment: ${Fore.GREEN}{initial_worth:,.2f}{Fore.WHITE}
Final Portfolio Value: ${Fore.GREEN}{final_worth:,.2f}{Fore.WHITE}
Total Return: {Fore.GREEN if return_pct >= 0 else Fore.RED}{return_pct:+.1f}%{Fore.WHITE}

{Fore.WHITE}YOUR GRADE: {grade_color}{grade} TIER{Fore.WHITE}

{Fore.CYAN}{'=' * self.terminal_width}
{Style.RESET_ALL}"""
        
        print(game_over_text)
    
    def show_final_analysis(self, analysis: str):
        """Display final analyst report"""
        print(f"\n{Fore.MAGENTA}FINAL ANALYST REPORT:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{analysis}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to exit...{Style.RESET_ALL}")
