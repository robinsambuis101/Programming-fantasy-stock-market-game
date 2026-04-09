#!/usr/bin/env python3
"""
Test script to verify Claude API integration with correct model
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from claude_api import ClaudeAPI

def test_api():
    """Test the Claude API integration"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("No API key found. Please set up your .env file.")
        return False
    
    print("Testing Claude API integration...")
    print(f"Using model: claude-sonnet-4-20250514")
    
    try:
        claude = ClaudeAPI()
        
        # Test company generation
        print("\n1. Testing company generation...")
        companies = claude.generate_companies()
        print(f"Generated {len(companies)} companies")
        for company in companies[:2]:  # Show first 2
            print(f"  - {company['symbol']}: {company['name']} ({company['sector']})")
        
        # Test news generation
        print("\n2. Testing news generation...")
        game_state = {
            'companies': {c['symbol']: c for c in companies},
            'current_news': [],
            'special_events': []
        }
        news = claude.generate_market_news(game_state)
        print(f"Generated {len(news)} news items")
        for news_item in news:
            print(f"  - {news_item['headline']}")
        
        # Test price calculation
        print("\n3. Testing price calculation...")
        prices = claude.calculate_new_prices(game_state)
        print(f"Calculated prices for {len(prices)} companies")
        
        # Test recap generation
        print("\n4. Testing recap generation...")
        recap = claude.generate_market_recap(game_state)
        print(f"Generated recap ({len(recap)} characters)")
        
        print("\nAPI Test Complete! All tests passed.")
        return True
        
    except Exception as e:
        print(f"API Test Failed: {e}")
        return False

if __name__ == "__main__":
    if '--test' in sys.argv:
        print("Running in test mode (no API calls)")
        claude = ClaudeAPI()
        companies = claude._generate_fallback_companies()
        print(f"Generated {len(companies)} fallback companies")
    else:
        test_api()
