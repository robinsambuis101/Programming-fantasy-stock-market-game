#!/usr/bin/env python3
"""
Test script to verify dynamic content is working
"""

from claude_api import ClaudeAPI

def test_dynamic_content():
    """Test that news and events are now dynamic"""
    claude = ClaudeAPI()
    
    print("Testing Dynamic Content Generation")
    print("=" * 40)
    
    # Get companies
    companies = claude._generate_fallback_companies()
    company_symbols = [c['symbol'] for c in companies]
    sectors = list(set(c['sector'] for c in companies))
    
    print(f"Testing with {len(companies)} companies across {len(sectors)} sectors")
    print()
    
    # Test news generation multiple times
    print("Testing News Generation (3 rounds):")
    print("-" * 30)
    
    for i in range(3):
        print(f"\nRound {i+1} News:")
        news = claude._generate_fallback_news(company_symbols, sectors)
        for j, news_item in enumerate(news, 1):
            print(f"  {j}. {news_item['headline']} ({news_item['category']})")
    
    # Test special events multiple times
    print("\n\nTesting Special Events (5 rounds):")
    print("-" * 30)
    
    for i in range(5):
        event = claude._generate_fallback_event(company_symbols)
        print(f"\nEvent {i+1}:")
        print(f"  Type: {event['event_type']}")
        print(f"  Title: {event['title']}")
        print(f"  Description: {event['description']}")
        print(f"  Effects: {event['effects']}")
    
    print("\n" + "=" * 40)
    print("Dynamic content test complete!")
    print("Each round should show different news and events.")

if __name__ == "__main__":
    test_dynamic_content()
