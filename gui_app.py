#!/usr/bin/env python3
"""
Fantasy Stock Market Game - GUI Version
A desktop application with modern GUI using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from game_state import GameState
from claude_api import ClaudeAPI
from portfolio_chart import PortfolioChart

class StockMarketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Stock Market Game")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Game state
        self.test_mode = '--test' in sys.argv
        self.claude = ClaudeAPI()
        self.game_state = GameState()
        self.chart = PortfolioChart()
        
        # Style configuration
        self.setup_styles()
        
        # Get starting net worth from user
        self.get_starting_net_worth()
        
        # Initialize game
        self.initialize_game()
        
        # Create GUI components
        self.create_widgets()
        
        # Start first round
        self.start_new_round()
    
    def get_starting_net_worth(self):
        """Get starting net worth from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Starting Capital")
        dialog.geometry("400x250")
        dialog.configure(bg='#2d2d30')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text="Choose Your Starting Capital", 
                              font=('Segoe UI', 14, 'bold'), bg='#2d2d30', fg='#ffffff')
        title_label.pack(pady=20)
        
        # Amount selection
        amount_frame = tk.Frame(dialog, bg='#2d2d30')
        amount_frame.pack(pady=20)
        
        tk.Label(amount_frame, text="Starting Amount ($):", bg='#2d2d30', fg='#ffffff').pack(side=tk.LEFT)
        
        self.starting_amount_var = tk.StringVar(value="10000")
        amount_entry = tk.Entry(amount_frame, textvariable=self.starting_amount_var, 
                               font=('Segoe UI', 12), width=15)
        amount_entry.pack(side=tk.LEFT, padx=10)
        
        # Preset buttons
        preset_frame = tk.Frame(dialog, bg='#2d2d30')
        preset_frame.pack(pady=10)
        
        presets = [5000, 10000, 25000, 50000, 100000]
        for amount in presets:
            btn = tk.Button(preset_frame, text=f"${amount:,}", 
                          command=lambda a=amount: self.starting_amount_var.set(str(a)),
                          bg='#0e639c', fg='#ffffff', font=('Segoe UI', 10))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Confirm button
        def confirm():
            try:
                amount = float(self.starting_amount_var.get())
                if amount < 1000:
                    messagebox.showerror("Error", "Minimum starting amount is $1,000")
                    return
                if amount > 1000000:
                    messagebox.showerror("Error", "Maximum starting amount is $1,000,000")
                    return
                self.starting_net_worth = amount
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        confirm_btn = tk.Button(dialog, text="Start Game", command=confirm,
                               bg='#007acc', fg='#ffffff', font=('Segoe UI', 12, 'bold'))
        confirm_btn.pack(pady=20)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
    
    def setup_styles(self):
        """Configure modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#2d2d30'
        fg_color = '#ffffff'
        select_color = '#007acc'
        button_color = '#0e639c'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=button_color, foreground=fg_color)
        style.map('TButton', background=[('active', '#1177bb')])
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Treeview', background='#252526', foreground=fg_color, 
                       fieldbackground='#252526', selectbackground=select_color)
        style.configure('Treeview.Heading', background='#3c3c3c', foreground=fg_color)
    
    def initialize_game(self):
        """Initialize the game with companies"""
        if self.test_mode:
            companies = self.claude._generate_fallback_companies()
        else:
            companies = self.claude.generate_companies()
        
        self.game_state.initialize_companies(companies)
        # Set custom starting cash
        self.game_state.cash = self.starting_net_worth
        self.game_state.net_worth_history = [self.starting_net_worth]
        
        self.current_round = 1
        self.phase = "news"
    
    def create_widgets(self):
        """Create all GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Companies and Trading
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.create_companies_panel(left_panel)
        self.create_trading_panel(left_panel)
        
        # Right panel - Portfolio and News
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_portfolio_panel(right_panel)
        self.create_news_panel(right_panel)
        
        # Bottom control panel
        self.create_control_panel(main_frame)
    
    def create_header(self, parent):
        """Create header with round info"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.round_label = ttk.Label(header_frame, text=f"Trading Day {self.current_round} of 10", 
                                     style='Header.TLabel')
        self.round_label.pack(side=tk.LEFT)
        
        self.phase_label = ttk.Label(header_frame, text="Phase: Market News", style='Title.TLabel')
        self.phase_label.pack(side=tk.RIGHT)
    
    def create_companies_panel(self, parent):
        """Create companies list panel"""
        companies_frame = ttk.LabelFrame(parent, text="Market Overview", style='TFrame')
        companies_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Search bar
        search_frame = ttk.Frame(companies_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_companies)
        
        # Sector filter
        ttk.Label(search_frame, text="Sector:").pack(side=tk.LEFT)
        self.sector_var = tk.StringVar(value="All")
        self.sector_combo = ttk.Combobox(search_frame, textvariable=self.sector_var, 
                                         values=["All"], state='readonly', width=15)
        self.sector_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.sector_combo.bind('<<ComboboxSelected>>', self.filter_companies)
        
        # Create treeview for companies
        columns = ('Symbol', 'Name', 'Sector', 'Price', 'Change', 'Volatility')
        self.companies_tree = ttk.Treeview(companies_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.companies_tree.heading('Symbol', text='Symbol')
        self.companies_tree.heading('Name', text='Company Name')
        self.companies_tree.heading('Sector', text='Sector')
        self.companies_tree.heading('Price', text='Price')
        self.companies_tree.heading('Change', text='Change')
        self.companies_tree.heading('Volatility', text='Volatility')
        
        self.companies_tree.column('Symbol', width=70)
        self.companies_tree.column('Name', width=180)
        self.companies_tree.column('Sector', width=90)
        self.companies_tree.column('Price', width=70)
        self.companies_tree.column('Change', width=70)
        self.companies_tree.column('Volatility', width=70)
        
        self.companies_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(companies_frame, orient=tk.VERTICAL, command=self.companies_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.companies_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_trading_panel(self, parent):
        """Create trading interface panel"""
        trading_frame = ttk.LabelFrame(parent, text="Trading", style='TFrame')
        trading_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Stock selection
        select_frame = ttk.Frame(trading_frame)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Select Stock:").pack(side=tk.LEFT)
        self.stock_var = tk.StringVar()
        self.stock_combo = ttk.Combobox(select_frame, textvariable=self.stock_var, state='readonly')
        self.stock_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buy/Sell controls
        controls_frame = ttk.Frame(trading_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Shares:").pack(side=tk.LEFT)
        self.shares_var = tk.IntVar(value=1)
        shares_spin = ttk.Spinbox(controls_frame, from_=1, to=1000, textvariable=self.shares_var, width=10)
        shares_spin.pack(side=tk.LEFT, padx=(10, 20))
        
        self.buy_button = ttk.Button(controls_frame, text="BUY", command=self.buy_stock)
        self.buy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.sell_button = ttk.Button(controls_frame, text="SELL", command=self.sell_stock)
        self.sell_button.pack(side=tk.LEFT)
        
        # Transaction log
        log_frame = ttk.LabelFrame(trading_frame, text="Transaction Log", style='TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.transaction_text = tk.Text(log_frame, height=6, bg='#252526', fg='#ffffff', 
                                      font=('Consolas', 9))
        self.transaction_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_portfolio_panel(self, parent):
        """Create portfolio panel"""
        portfolio_frame = ttk.LabelFrame(parent, text="Your Portfolio", style='TFrame')
        portfolio_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Portfolio summary
        summary_frame = ttk.Frame(portfolio_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cash_label = ttk.Label(summary_frame, text="Cash: $10,000.00")
        self.cash_label.pack(anchor=tk.W)
        
        self.portfolio_value_label = ttk.Label(summary_frame, text="Portfolio Value: $0.00")
        self.portfolio_value_label.pack(anchor=tk.W)
        
        self.net_worth_label = ttk.Label(summary_frame, text="Net Worth: $10,000.00", 
                                        style='Title.TLabel')
        self.net_worth_label.pack(anchor=tk.W)
        
        # Holdings list
        holdings_frame = ttk.LabelFrame(portfolio_frame, text="Holdings", style='TFrame')
        holdings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Symbol', 'Shares', 'Price', 'Value')
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=columns, show='headings', height=6)
        
        self.holdings_tree.heading('Symbol', text='Symbol')
        self.holdings_tree.heading('Shares', text='Shares')
        self.holdings_tree.heading('Price', text='Price')
        self.holdings_tree.heading('Value', text='Value')
        
        self.holdings_tree.column('Symbol', width=80)
        self.holdings_tree.column('Shares', width=80)
        self.holdings_tree.column('Price', width=80)
        self.holdings_tree.column('Value', width=80)
        
        self.holdings_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_news_panel(self, parent):
        """Create news panel"""
        news_frame = ttk.LabelFrame(parent, text="Market News", style='TFrame')
        news_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.news_text = tk.Text(news_frame, height=12, bg='#252526', fg='#ffffff', 
                                 font=('Segoe UI', 10), wrap=tk.WORD)
        self.news_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for different news types
        self.news_text.tag_configure('global', foreground='#ff6b6b')
        self.news_text.tag_configure('sector', foreground='#4ecdc4')
        self.news_text.tag_configure('company', foreground='#45b7d1')
    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.next_phase_button = ttk.Button(control_frame, text="Next Phase", 
                                           command=self.next_phase, state=tk.DISABLED)
        self.next_phase_button.pack(side=tk.LEFT)
        
        self.chart_button = ttk.Button(control_frame, text="Show Chart", 
                                       command=self.show_chart)
        self.chart_button.pack(side=tk.LEFT, padx=(10, 0))
        
        self.save_button = ttk.Button(control_frame, text="Save Game", 
                                      command=self.save_game)
        self.save_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.IntVar(value=1)
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                           maximum=10, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(control_frame, text="Round Progress:").pack(side=tk.RIGHT)
    
    def filter_companies(self, event=None):
        """Filter companies based on search and sector"""
        search_term = self.search_var.get().lower()
        selected_sector = self.sector_var.get()
        
        # Clear existing items
        for item in self.companies_tree.get_children():
            self.companies_tree.delete(item)
        
        # Add filtered companies
        symbols = []
        for symbol, company in self.game_state.companies.items():
            # Apply filters
            name_match = search_term in company.name.lower() or search_term in symbol.lower()
            sector_match = selected_sector == "All" or company.sector == selected_sector
            
            if name_match and sector_match:
                change = self.game_state.get_price_change(symbol)
                change_str = f"{change:+.1f}%" if change != 0 else "0.0%"
                
                self.companies_tree.insert('', tk.END, values=(
                    symbol,
                    company.name[:25] + "..." if len(company.name) > 25 else company.name,
                    company.sector,
                    f"${company.current_price:.2f}",
                    change_str,
                    company.volatility
                ))
                symbols.append(symbol)
        
        # Update stock combo box with filtered results
        self.stock_combo['values'] = symbols
        if symbols and not self.stock_var.get():
            self.stock_var.set(symbols[0])
    
    def update_companies_list(self):
        """Update the companies treeview and sector filter"""
        # Update sector filter options
        sectors = ["All"] + sorted(set(company.sector for company in self.game_state.companies.values()))
        self.sector_combo['values'] = sectors
        
        # Apply current filters
        self.filter_companies()
    
    def update_portfolio_display(self):
        """Update portfolio information"""
        cash = self.game_state.cash
        portfolio_value = self.game_state.get_portfolio_value()
        net_worth = self.game_state.calculate_net_worth()
        
        self.cash_label.config(text=f"Cash: ${cash:,.2f}")
        self.portfolio_value_label.config(text=f"Portfolio Value: ${portfolio_value:,.2f}")
        self.net_worth_label.config(text=f"Net Worth: ${net_worth:,.2f}")
        
        # Update holdings
        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)
        
        for symbol, shares in self.game_state.portfolio.items():
            company = self.game_state.companies[symbol]
            value = shares * company.current_price
            
            self.holdings_tree.insert('', tk.END, values=(
                symbol,
                shares,
                f"${company.current_price:.2f}",
                f"${value:.2f}"
            ))
    
    def start_new_round(self):
        """Start a new trading round"""
        self.round_label.config(text=f"Trading Day {self.current_round} of 10")
        self.phase = "news"
        self.phase_label.config(text="Phase: Market News")
        self.next_phase_button.config(state=tk.DISABLED)
        
        # Generate news
        self.generate_news()
        
        # Update displays
        self.update_companies_list()
        self.update_portfolio_display()
        
        # Enable trading after news
        self.root.after(2000, self.enable_trading)
    
    def generate_news(self):
        """Generate market news"""
        if self.test_mode:
            companies = list(self.game_state.companies.keys())
            sectors = list(set(company.sector for company in self.game_state.companies.values()))
            news = self.claude._generate_fallback_news(companies, sectors)
        else:
            news = self.claude.generate_market_news(self.game_state.to_dict())
        
        self.game_state.current_news = news
        self.display_news(news)
    
    def display_news(self, news):
        """Display news in the news panel"""
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, "BREAKING NEWS:\n\n", 'global')
        
        for i, news_item in enumerate(news, 1):
            tag = news_item.get('category', 'global')
            headline = news_item['headline'].upper()
            
            self.news_text.insert(tk.END, f"{i}. {headline}\n", tag)
            
            # Add impact hints
            if news_item.get('affected_companies') and news_item['affected_companies'] != ['all']:
                self.news_text.insert(tk.END, f"   Impact: Could affect {', '.join(news_item['affected_companies'])}\n\n")
            elif news_item.get('sector'):
                self.news_text.insert(tk.END, f"   Impact: {news_item['sector'].title()} sector may be affected\n\n")
            else:
                self.news_text.insert(tk.END, "\n")
    
    def enable_trading(self):
        """Enable trading phase"""
        self.phase = "trading"
        self.phase_label.config(text="Phase: Trading Window")
        self.next_phase_button.config(state=tk.NORMAL)
        self.buy_button.config(state=tk.NORMAL)
        self.sell_button.config(state=tk.NORMAL)
    
    def buy_stock(self):
        """Handle buy stock action"""
        symbol = self.stock_var.get()
        if not symbol:
            messagebox.showwarning("Warning", "Please select a stock to buy.")
            return
        
        shares = self.shares_var.get()
        success = self.game_state.buy_shares(symbol, shares)
        
        if success:
            company = self.game_state.companies[symbol]
            cost = shares * company.current_price
            self.log_transaction(f"Bought {shares} shares of {symbol} for ${cost:.2f}")
            self.update_portfolio_display()
        else:
            messagebox.showerror("Error", "Failed to buy shares. Check your cash balance.")
    
    def sell_stock(self):
        """Handle sell stock action"""
        symbol = self.stock_var.get()
        if not symbol:
            messagebox.showwarning("Warning", "Please select a stock to sell.")
            return
        
        if symbol not in self.game_state.portfolio:
            messagebox.showerror("Error", "You don't own any shares of this stock.")
            return
        
        shares = self.shares_var.get()
        max_shares = self.game_state.portfolio[symbol]
        
        if shares > max_shares:
            messagebox.showerror("Error", f"You only own {max_shares} shares of {symbol}.")
            return
        
        success = self.game_state.sell_shares(symbol, shares)
        
        if success:
            company = self.game_state.companies[symbol]
            revenue = shares * company.current_price
            self.log_transaction(f"Sold {shares} shares of {symbol} for ${revenue:.2f}")
            self.update_portfolio_display()
        else:
            messagebox.showerror("Error", "Failed to sell shares.")
    
    def log_transaction(self, message):
        """Log a transaction"""
        self.transaction_text.insert(tk.END, f"{message}\n")
        self.transaction_text.see(tk.END)
    
    def next_phase(self):
        """Move to next phase"""
        if self.phase == "trading":
            self.resolve_prices()
        elif self.phase == "resolution":
            self.show_recap()
        elif self.phase == "recap":
            self.next_round()
    
    def resolve_prices(self):
        """Resolve stock prices"""
        self.phase = "resolution"
        self.phase_label.config(text="Phase: Price Resolution")
        self.next_phase_button.config(state=tk.DISABLED)
        self.buy_button.config(state=tk.DISABLED)
        self.sell_button.config(state=tk.DISABLED)
        
        # Calculate new prices
        if self.test_mode:
            new_prices = self.claude._generate_fallback_prices(self.game_state.to_dict())
        else:
            new_prices = self.claude.calculate_new_prices(self.game_state.to_dict())
        
        self.game_state.update_prices(new_prices)
        
        # Update display
        self.update_companies_list()
        self.update_portfolio_display()
        
        # Show price changes
        self.show_price_changes()
        
        # Enable recap after delay
        self.root.after(2000, self.enable_recap)
    
    def show_price_changes(self):
        """Show price changes in transaction log"""
        self.log_transaction("\n=== PRICE MOVEMENTS ===")
        
        movers = []
        for symbol, company in self.game_state.companies.items():
            change = self.game_state.get_price_change(symbol)
            movers.append((symbol, change, company.current_price))
        
        movers.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for symbol, change, price in movers[:5]:  # Top 5 movers
            direction = "UP" if change > 0 else "DOWN" if change < 0 else "FLAT"
            self.log_transaction(f"{symbol}: {direction} {change:+.1f}% (${price:.2f})")
    
    def enable_recap(self):
        """Enable recap phase"""
        self.phase = "recap"
        self.phase_label.config(text="Phase: Market Recap")
        self.next_phase_button.config(state=tk.NORMAL)
        
        # Generate recap
        if self.test_mode:
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
            recap = self.claude.generate_market_recap(self.game_state.to_dict())
        
        self.display_recap(recap)
    
    def display_recap(self, recap):
        """Display market recap"""
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, "MARKET RECAP:\n\n", 'global')
        self.news_text.insert(tk.END, recap)
    
    def next_round(self):
        """Move to next round"""
        self.current_round += 1
        self.progress_var.set(self.current_round)
        
        if self.current_round > 10:
            self.end_game()
        else:
            # Check for special events
            if self.current_round % 3 == 0:
                self.trigger_special_event()
            else:
                self.start_new_round()
    
    def trigger_special_event(self):
        """Trigger a special event"""
        if self.test_mode:
            companies = list(self.game_state.companies.keys())
            event = self.claude._generate_fallback_event(companies)
        else:
            event = self.claude.generate_special_event(self.game_state.to_dict())
        
        self.show_special_event(event)
        self.game_state.apply_special_event(event)
        
        # Continue to next round after showing event
        self.root.after(3000, self.start_new_round)
    
    def show_special_event(self, event):
        """Show special event"""
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, f"!!! SPECIAL EVENT !!!\n\n", 'global')
        self.news_text.insert(tk.END, f"{event.get('title', 'SPECIAL EVENT')}\n\n", 'sector')
        self.news_text.insert(tk.END, f"{event.get('description', '')}\n\n")
        self.news_text.insert(tk.END, f"{event.get('effects', '')}", 'company')
        
        self.log_transaction(f"\n!!! {event.get('title', 'SPECIAL EVENT')} !!!")
    
    def end_game(self):
        """End the game and show results"""
        # Disable all controls
        self.next_phase_button.config(state=tk.DISABLED)
        self.buy_button.config(state=tk.DISABLED)
        self.sell_button.config(state=tk.DISABLED)
        
        # Generate final analysis
        if self.test_mode:
            final_worth = self.game_state.calculate_net_worth()
            initial_worth = self.starting_net_worth
            final_analysis = f"FINAL ANALYSIS: You started with ${initial_worth:,.2f} and ended with ${final_worth:.2f}. {'Great job!' if final_worth >= initial_worth else 'Better luck next time!'} Your trading strategy was {'bold' if len(self.game_state.portfolio) > 0 else 'conservative'}. Remember: the market rewards those who read the news carefully!"
        else:
            # Update game state with starting net worth for analysis
            game_state_dict = self.game_state.to_dict()
            game_state_dict['starting_net_worth'] = self.starting_net_worth
            final_analysis = self.claude.generate_final_analysis(game_state_dict)
        
        # Show final results
        self.show_final_results(final_analysis)
    
    def show_final_results(self, analysis):
        """Show final game results"""
        final_worth = self.game_state.calculate_net_worth()
        initial_worth = self.starting_net_worth
        return_pct = ((final_worth - initial_worth) / initial_worth) * 100
        
        # Determine grade
        if return_pct >= 100:
            grade = "S"
            grade_color = "#FFD700"  # Gold
        elif return_pct >= 50:
            grade = "A"
            grade_color = "#00FF00"  # Green
        elif return_pct >= 20:
            grade = "B"
            grade_color = "#00CED1"  # Dark Turquoise
        elif return_pct >= 0:
            grade = "C"
            grade_color = "#FFFFFF"  # White
        else:
            grade = "D"
            grade_color = "#FF6B6B"  # Red
        
        # Update display for final results
        self.round_label.config(text="GAME OVER")
        self.phase_label.config(text="Final Results")
        
        # Show results in news panel
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, "GAME OVER - FINAL RESULTS\n\n", 'global')
        self.news_text.insert(tk.END, f"Initial Investment: ${initial_worth:,.2f}\n")
        self.news_text.insert(tk.END, f"Final Portfolio Value: ${final_worth:,.2f}\n")
        self.news_text.insert(tk.END, f"Total Return: {return_pct:+.1f}%\n\n")
        self.news_text.insert(tk.END, f"YOUR GRADE: {grade} TIER\n\n", 'sector')
        self.news_text.insert(tk.END, analysis)
        
        # Generate and show chart
        try:
            chart_path = self.chart.create_portfolio_history_chart(self.game_state.net_worth_history)
            self.log_transaction(f"\nChart saved to {chart_path}")
            self.chart.show_chart(chart_path)
        except Exception as e:
            self.log_transaction(f"Could not generate chart: {e}")
    
    def show_chart(self):
        """Show portfolio chart"""
        try:
            chart_path = self.chart.create_portfolio_history_chart(self.game_state.net_worth_history)
            self.chart.show_chart(chart_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate chart: {e}")
    
    def save_game(self):
        """Save game state"""
        try:
            filename = f"save_game_{self.current_round}.json"
            self.game_state.save_to_file(filename)
            messagebox.showinfo("Success", f"Game saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save game: {e}")

def main():
    """Main entry point for GUI application"""
    if not os.getenv("ANTHROPIC_API_KEY") and '--test' not in sys.argv:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set up your .env file with your Anthropic API key.")
        print("Or run in test mode: python gui_app.py --test")
        return
    
    root = tk.Tk()
    app = StockMarketGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
