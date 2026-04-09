"""
Game State Management
Handles all game data and player portfolio state
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import random

@dataclass
class Company:
    """Represents a fictional company"""
    symbol: str
    name: str
    sector: str
    backstory: str
    current_price: float
    ipo_price: float
    volatility: str  # low, medium, high
    stability_score: int  # 1-10
    
@dataclass
class NewsItem:
    """Represents a news item"""
    headline: str
    category: str  # global, sector, company
    affected_companies: List[str]
    sentiment: str  # positive, negative, neutral

class GameState:
    """Manages the complete game state"""
    
    def __init__(self):
        self.current_round = 1
        self.cash = 10000.0
        self.portfolio = {}  # symbol: shares
        self.companies = {}  # symbol: Company
        self.price_history = {}  # symbol: [prices]
        self.net_worth_history = [10000.0]
        self.current_news = []
        self.special_events = []
        
    def initialize_companies(self, companies_data: List[Dict[str, Any]]):
        """Initialize companies from Claude-generated data"""
        for company_data in companies_data:
            company = Company(
                symbol=company_data['symbol'],
                name=company_data['name'],
                sector=company_data['sector'],
                backstory=company_data['backstory'],
                current_price=company_data['ipo_price'],
                ipo_price=company_data['ipo_price'],
                volatility=company_data['volatility'],
                stability_score=company_data['stability_score']
            )
            self.companies[company.symbol] = company
            self.price_history[company.symbol] = [company.current_price]
    
    def buy_shares(self, symbol: str, shares: int) -> bool:
        """Buy shares of a company"""
        if symbol not in self.companies:
            return False
        
        cost = self.companies[symbol].current_price * shares
        if cost > self.cash:
            return False
        
        self.cash -= cost
        if symbol in self.portfolio:
            self.portfolio[symbol] += shares
        else:
            self.portfolio[symbol] = shares
        return True
    
    def sell_shares(self, symbol: str, shares: int) -> bool:
        """Sell shares of a company"""
        if symbol not in self.portfolio or self.portfolio[symbol] < shares:
            return False
        
        revenue = self.companies[symbol].current_price * shares
        self.cash += revenue
        self.portfolio[symbol] -= shares
        
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        return True
    
    def update_prices(self, new_prices: Dict[str, float]):
        """Update all company prices"""
        for symbol, new_price in new_prices.items():
            if symbol in self.companies:
                self.companies[symbol].current_price = new_price
                self.price_history[symbol].append(new_price)
        
        # Update net worth history
        self.net_worth_history.append(self.calculate_net_worth())
    
    def calculate_net_worth(self) -> float:
        """Calculate total portfolio value"""
        total = self.cash
        for symbol, shares in self.portfolio.items():
            total += self.companies[symbol].current_price * shares
        return total
    
    def get_portfolio_value(self) -> float:
        """Get current portfolio value (excluding cash)"""
        total = 0.0
        for symbol, shares in self.portfolio.items():
            total += self.companies[symbol].current_price * shares
        return total
    
    def get_price_change(self, symbol: str) -> float:
        """Get price change percentage from previous round"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return 0.0
        
        old_price = self.price_history[symbol][-2]
        new_price = self.price_history[symbol][-1]
        
        if old_price == 0:
            return 0.0
        
        return ((new_price - old_price) / old_price) * 100
    
    def apply_special_event(self, event: Dict[str, Any]):
        """Apply special event effects to the game state"""
        self.special_events.append(event)
        # Special event logic will be handled in Claude API
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        return {
            'current_round': self.current_round,
            'cash': self.cash,
            'portfolio': self.portfolio,
            'companies': {symbol: asdict(company) for symbol, company in self.companies.items()},
            'price_history': self.price_history,
            'net_worth_history': self.net_worth_history,
            'current_news': self.current_news,
            'special_events': self.special_events
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load game state from dictionary"""
        self.current_round = data['current_round']
        self.cash = data['cash']
        self.portfolio = data['portfolio']
        self.companies = {symbol: Company(**company_data) for symbol, company_data in data['companies'].items()}
        self.price_history = data['price_history']
        self.net_worth_history = data['net_worth_history']
        self.current_news = data['current_news']
        self.special_events = data['special_events']
    
    def save_to_file(self, filename: str):
        """Save game state to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load game state from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        self.from_dict(data)
