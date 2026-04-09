"""
Claude API Integration
Handles all communication with Anthropic Claude API
"""

import os
import json
import random
from typing import Dict, List, Any
from anthropic import Anthropic

class ClaudeAPI:
    """Interface to Claude API for generating game content"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def generate_companies(self) -> List[Dict[str, Any]]:
        """Generate 75 fictional companies with their attributes"""
        prompt = """
        Generate 75 fictional companies for a stock market game. For each company, provide:
        - A ridiculous but believable company name (like "QuantumBurger Inc", "MoonRock Energy")
        - A 3-4 letter stock ticker symbol
        - A sector from these options: Tech, Energy, Food, Entertainment, Healthcare, Defense, Finance, Retail, Automotive, Aerospace, Real Estate, Biotech, Consumer Goods, Industrial, Telecom, Utilities, Materials, Transportation
        - A short 2-sentence backstory
        - An IPO price between $10-$200
        - Volatility rating (low, medium, high)
        - Stability score (1-10, where 10 is most stable)
        
        Return as a JSON array of objects with this exact structure:
        [
            {
                "symbol": "QBI",
                "name": "QuantumBurger Inc",
                "sector": "Food",
                "backstory": "Revolutionary fast-food chain using quantum-entangled patties. Their burgers exist in multiple states until you bite them.",
                "ipo_price": 45.50,
                "volatility": "high",
                "stability_score": 3
            }
        ]
        
        Make the companies creative and memorable. Ensure good distribution across all sectors - aim for 3-5 companies per sector.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            companies_data = json.loads(response.content[0].text)
            # Ensure we have exactly 75 companies
            if len(companies_data) != 75:
                print(f"Warning: Claude generated {len(companies_data)} companies, expected 75. Using fallback.")
                return self._generate_fallback_companies()
            return companies_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._generate_fallback_companies()
    
    def generate_market_news(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate 3 news headlines for the round"""
        companies = list(game_state['companies'].keys())
        sectors = list(set(company['sector'] for company in game_state['companies'].values()))
        
        prompt = f"""
        Generate 3 news headlines for a stock market game round. The available companies are: {', '.join(companies)}.
        The sectors represented are: {', '.join(sectors)}.
        
        Create exactly:
        1. One global macro event (affects all markets)
        2. One sector-specific event (affects one of these sectors: {', '.join(sectors)})
        3. One company-specific event (targets one specific company from the list)
        
        Each headline should hint at potential stock movements without being obvious. Make them witty and slightly absurd.
        
        Return as a JSON array with this structure:
        [
            {
                "headline": "Central bank raises interest rates to combat inflation",
                "category": "global",
                "affected_companies": ["all"],
                "sentiment": "negative"
            }
        ]
        
        For company-specific events, list the specific company symbol. For sector events, list "all" in affected_companies but specify the sector in a "sector" field.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            news_data = json.loads(response.content[0].text)
            return news_data
        except json.JSONDecodeError:
            return self._generate_fallback_news(companies, sectors)
    
    def calculate_new_prices(self, game_state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate new stock prices based on news and company attributes"""
        prompt = f"""
        Calculate new stock prices based on market news and company attributes. Here's the current situation:
        
        Current companies and prices:
        {json.dumps([{symbol: {'price': company['current_price'], 'volatility': company['volatility'], 'stability': company['stability_score'], 'sector': company['sector']}} for symbol, company in game_state['companies'].items()], indent=2)}
        
        Current news events:
        {json.dumps(game_state.get('current_news', []), indent=2)}
        
        Calculate new prices considering:
        - News impact (positive news should raise prices, negative should lower them)
        - Company volatility (high volatility = bigger price swings)
        - Company stability (higher stability = less extreme movements)
        - Sector effects (sector news affects all companies in that sector)
        - Add ±5% random variance for unpredictability
        
        Price movement range: -30% to +40% per round depending on news severity.
        
        Return as a JSON object with symbol as key and new price as value:
        {{
            "QBI": 52.30,
            "MRE": 38.75
        }}
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            prices_data = json.loads(response.content[0].text)
            return prices_data
        except json.JSONDecodeError:
            return self._generate_fallback_prices(game_state)
    
    def generate_market_recap(self, game_state: Dict[str, Any]) -> str:
        """Generate a dramatic market recap in CNBC style"""
        prompt = f"""
        Write a dramatic, funny CNBC-style market recap for this trading round. Include:
        
        - Reference actual price movements that happened
        - Call out the biggest winner and biggest loser
        - Use dramatic, slightly unhinged financial news language
        - Tease what might happen next round (vague, not spoilers)
        
        Here's what happened this round:
        Companies and their price changes:
        {self._format_price_changes(game_state)}
        
        News events:
        {json.dumps(game_state.get('current_news', []), indent=2)}
        
        Make it sound like a mix of Wall Street Bets chaos and Bloomberg terminal. Be witty and entertaining.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_special_event(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a special event that happens every 3 rounds"""
        events = ["merger_rumor", "bubble_warning", "insider_tip", "market_crash", "meme_stock_frenzy"]
        chosen_event = random.choice(events)
        companies = list(game_state['companies'].keys())
        sectors = list(set(company['sector'] for company in game_state['companies'].values()))
        
        prompt = f"""
        Generate a special event for the stock market game. Event type: {chosen_event}
        Available companies: {', '.join(companies)}
        Available sectors: {', '.join(sectors)}
        
        Create an event with these details:
        - event_type: "{chosen_event}"
        - title: Catchy event title
        - description: What's happening
        - affected_companies: List of company symbols affected
        - effects: Description of how this will impact prices
        
        Return as JSON:
        {{
            "event_type": "merger_rumor",
            "title": "Merger Mania!",
            "description": "Rumors swirl about a potential merger...",
            "affected_companies": ["QBI", "MRE"],
            "effects": "One company spikes, one dips"
        }}
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            event_data = json.loads(response.content[0].text)
            return event_data
        except json.JSONDecodeError:
            return self._generate_fallback_event(companies)
    
    def generate_final_analysis(self, game_state: Dict[str, Any]) -> str:
        """Generate final analyst report reviewing player's strategy"""
        initial_worth = game_state.get('starting_net_worth', 10000.0)
        final_worth = game_state['net_worth_history'][-1]
        return_percentage = ((final_worth - initial_worth) / initial_worth) * 100
        
        prompt = f"""
        Write a final analyst report reviewing the player's investment strategy. Include:
        
        - Overall performance: Started with ${initial_worth:,.2f}, ended with ${final_worth:.2f} ({return_percentage:+.1f}% return)
        - Grade their performance (S Tier: +100%+, A: +50-99%, B: +20-49%, C: 0-19%, D: negative)
        - Comment on their trading patterns (panic selling, diamond hands, etc.)
        - Reference specific companies they did well or poorly with
        - Give witty, genuine observations about their investment style
        - End with advice for future trading
        
        Portfolio history:
        {json.dumps(game_state['net_worth_history'], indent=2)}
        
        Current portfolio:
        {json.dumps(game_state['portfolio'], indent=2)}
        
        Make it sound like a real but slightly unhinged financial analyst. Be specific and insightful.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _format_price_changes(self, game_state: Dict[str, Any]) -> str:
        """Format price changes for prompt"""
        changes = []
        for symbol, company in game_state['companies'].items():
            if 'price_history' in game_state and symbol in game_state['price_history']:
                history = game_state['price_history'][symbol]
                if len(history) >= 2:
                    old_price = history[-2]
                    new_price = history[-1]
                    change_pct = ((new_price - old_price) / old_price) * 100
                    changes.append(f"{symbol}: {old_price:.2f} -> {new_price:.2f} ({change_pct:+.1f}%)")
        return "\n".join(changes)
    
    def _generate_fallback_companies(self) -> List[Dict[str, Any]]:
        """Fallback companies if API fails"""
        return [
            {"symbol": "QBI", "name": "QuantumBurger Inc", "sector": "Food", "backstory": "Revolutionary fast-food using quantum physics.", "ipo_price": 45.50, "volatility": "high", "stability_score": 3},
            {"symbol": "MRE", "name": "MoonRock Energy", "sector": "Energy", "backstory": "Mining lunar resources for clean energy.", "ipo_price": 78.25, "volatility": "medium", "stability_score": 6},
            {"symbol": "CYB", "name": "CyberDream Tech", "sector": "Tech", "backstory": "AI-powered dream analysis technology.", "ipo_price": 125.00, "volatility": "high", "stability_score": 4},
            {"symbol": "GME", "name": "Galactic Medical", "sector": "Healthcare", "backstory": "Space-age medical breakthroughs.", "ipo_price": 92.75, "volatility": "medium", "stability_score": 7},
            {"symbol": "DEF", "name": "Defense Dynamics", "sector": "Defense", "backstory": "Advanced military robotics and AI systems.", "ipo_price": 156.00, "volatility": "low", "stability_score": 8},
            {"symbol": "FUN", "name": "FutureFun Entertainment", "sector": "Entertainment", "backstory": "Virtual reality entertainment experiences.", "ipo_price": 67.25, "volatility": "high", "stability_score": 3},
            {"symbol": "FIN", "name": "FinTech Fusion", "sector": "Finance", "backstory": "Blockchain-based financial solutions.", "ipo_price": 89.50, "volatility": "high", "stability_score": 5},
            {"symbol": "RTL", "name": "Retail Revolution", "sector": "Retail", "backstory": "AI-powered shopping assistant technology.", "ipo_price": 54.75, "volatility": "medium", "stability_score": 6},
            {"symbol": "AUTO", "name": "AutoFuture Motors", "sector": "Automotive", "backstory": "Self-driving electric vehicle technology.", "ipo_price": 112.00, "volatility": "high", "stability_score": 4},
            {"symbol": "AERO", "name": "AeroSpace Innovations", "sector": "Aerospace", "backstory": "Commercial space flight technology.", "ipo_price": 198.50, "volatility": "high", "stability_score": 2},
            {"symbol": "EST", "name": "EstateTech", "sector": "Real Estate", "backstory": "Smart property management systems.", "ipo_price": 73.25, "volatility": "low", "stability_score": 7},
            {"symbol": "BIO", "name": "BioGen Labs", "sector": "Biotech", "backstory": "Genetic engineering for medical treatments.", "ipo_price": 134.75, "volatility": "high", "stability_score": 3},
            {"symbol": "CGD", "name": "Consumer Goods Direct", "sector": "Consumer Goods", "backstory": "Direct-to-consumer product innovation.", "ipo_price": 61.50, "volatility": "medium", "stability_score": 6},
            {"symbol": "IND", "name": "Industrial Automation", "sector": "Industrial", "backstory": "Smart factory solutions and robotics.", "ipo_price": 87.00, "volatility": "low", "stability_score": 8},
            {"symbol": "TEL", "name": "Telecom Tomorrow", "sector": "Telecom", "backstory": "Next-generation communication networks.", "ipo_price": 95.25, "volatility": "medium", "stability_score": 7},
            {"symbol": "UTL", "name": "Utility Future", "sector": "Utilities", "backstory": "Renewable energy grid management.", "ipo_price": 71.50, "volatility": "low", "stability_score": 9},
            {"symbol": "MAT", "name": "Materials Science Co", "sector": "Materials", "backstory": "Advanced material development for industry.", "ipo_price": 68.75, "volatility": "medium", "stability_score": 6},
            {"symbol": "TRN", "name": "Transport Solutions", "sector": "Transportation", "backstory": "Autonomous logistics and delivery systems.", "ipo_price": 79.00, "volatility": "high", "stability_score": 4},
            {"symbol": "TEC", "name": "TechVision Systems", "sector": "Tech", "backstory": "Augmented reality glasses for everyday use.", "ipo_price": 143.25, "volatility": "high", "stability_score": 4},
            {"symbol": "ENR", "name": "Energy Revolution", "sector": "Energy", "backstory": "Fusion power breakthrough technology.", "ipo_price": 167.50, "volatility": "high", "stability_score": 2},
            {"symbol": "FOD", "name": "FoodFuture Labs", "sector": "Food", "backstory": "Lab-grown gourmet meat alternatives.", "ipo_price": 58.75, "volatility": "medium", "stability_score": 5},
            {"symbol": "HLT", "name": "HealthTech Plus", "sector": "Healthcare", "backstory": "Nano-robots for targeted drug delivery.", "ipo_price": 118.00, "volatility": "high", "stability_score": 3},
            {"symbol": "DFC", "name": "DefenseCorp", "sector": "Defense", "backstory": "Quantum encryption for military communications.", "ipo_price": 189.25, "volatility": "low", "stability_score": 8},
            {"symbol": "ENT", "name": "EntertainMax", "sector": "Entertainment", "backstory": "Holographic concerts and virtual celebrities.", "ipo_price": 76.50, "volatility": "high", "stability_score": 3},
            {"symbol": "BAN", "name": "BankChain", "sector": "Finance", "backstory": "Decentralized banking with smart contracts.", "ipo_price": 94.75, "volatility": "high", "stability_score": 4},
            {"symbol": "SHP", "name": "ShopSmart AI", "sector": "Retail", "backstory": "Personalized AI shopping assistants.", "ipo_price": 52.25, "volatility": "medium", "stability_score": 6},
            {"symbol": "CAR", "name": "CarFuture", "sector": "Automotive", "backstory": "Flying electric vehicles for urban transport.", "ipo_price": 176.00, "volatility": "high", "stability_score": 2},
            {"symbol": "SPC", "name": "SpaceCorp", "sector": "Aerospace", "backstory": "Asteroid mining and resource extraction.", "ipo_price": 145.75, "volatility": "high", "stability_score": 3},
            {"symbol": "PRO", "name": "PropertyTech", "sector": "Real Estate", "backstory": "AI-powered property valuation and management.", "ipo_price": 81.50, "volatility": "medium", "stability_score": 7},
            {"symbol": "GEN", "name": "GeneTherapy", "sector": "Biotech", "backstory": "CRISPR-based genetic disease cures.", "ipo_price": 156.25, "volatility": "high", "stability_score": 2},
            {"symbol": "CNS", "name": "ConsumerNet", "sector": "Consumer Goods", "backstory": "Smart home devices with AI integration.", "ipo_price": 64.00, "volatility": "medium", "stability_score": 6},
            {"symbol": "FAC", "name": "FactoryOne", "sector": "Industrial", "backstory": "Fully automated manufacturing facilities.", "ipo_price": 98.50, "volatility": "low", "stability_score": 8},
            {"symbol": "NET", "name": "NetworkNext", "sector": "Telecom", "backstory": "6G wireless communication infrastructure.", "ipo_price": 109.75, "volatility": "medium", "stability_score": 7},
            {"symbol": "PWR", "name": "PowerGrid", "sector": "Utilities", "backstory": "Smart grid with AI load balancing.", "ipo_price": 74.25, "volatility": "low", "stability_score": 9},
            {"symbol": "CMP", "name": "CompoundTech", "sector": "Materials", "backstory": "Graphene-based supermaterials.", "ipo_price": 91.00, "volatility": "medium", "stability_score": 6},
            {"symbol": "LOG", "name": "LogisticsAI", "sector": "Transportation", "backstory": "Autonomous trucking and delivery networks.", "ipo_price": 83.50, "volatility": "high", "stability_score": 4},
            {"symbol": "AIS", "name": "AI Squared", "sector": "Tech", "backstory": "Artificial general intelligence research.", "ipo_price": 195.00, "volatility": "high", "stability_score": 1},
            {"symbol": "SOL", "name": "SolarMax", "sector": "Energy", "backstory": "High-efficiency perovskite solar panels.", "ipo_price": 86.75, "volatility": "medium", "stability_score": 7},
            {"symbol": "BUR", "name": "BurgerBot", "sector": "Food", "backstory": "Robot-operated fast-food restaurants.", "ipo_price": 48.25, "volatility": "medium", "stability_score": 5},
            {"symbol": "MED", "name": "MediCore", "sector": "Healthcare", "backstory": "3D-printed organ replacement technology.", "ipo_price": 137.50, "volatility": "high", "stability_score": 3},
            {"symbol": "ARM", "name": "ArmorTech", "sector": "Defense", "backstory": "Exoskeleton suits for soldiers.", "ipo_price": 178.75, "volatility": "low", "stability_score": 8},
            {"symbol": "GAM", "name": "GameVerse", "sector": "Entertainment", "backstory": "Fully immersive virtual reality gaming.", "ipo_price": 69.50, "volatility": "high", "stability_score": 4},
            {"symbol": "PAY", "name": "PayChain", "sector": "Finance", "backstory": "Cryptocurrency payment processing systems.", "ipo_price": 102.25, "volatility": "high", "stability_score": 3},
            {"symbol": "MKT", "name": "MarketPlace", "sector": "Retail", "backstory": "AI-driven e-commerce optimization.", "ipo_price": 57.75, "volatility": "medium", "stability_score": 6},
            {"symbol": "ELE", "name": "ElectraAuto", "sector": "Automotive", "backstory": "Battery technology with 1000-mile range.", "ipo_price": 124.50, "volatility": "high", "stability_score": 3},
            {"symbol": "RKT", "name": "RocketLab", "sector": "Aerospace", "backstory": "Reusable rocket launch systems.", "ipo_price": 161.25, "volatility": "high", "stability_score": 2},
            {"symbol": "HOM", "name": "HomeSmart", "sector": "Real Estate", "backstory": "AI-integrated luxury apartment complexes.", "ipo_price": 88.00, "volatility": "medium", "stability_score": 7},
            {"symbol": "VAX", "name": "VaxTech", "sector": "Biotech", "backstory": "Rapid vaccine development platform.", "ipo_price": 147.75, "volatility": "high", "stability_score": 2},
            {"symbol": "WEA", "name": "WearTech", "sector": "Consumer Goods", "backstory": "Smart clothing with health monitoring.", "ipo_price": 55.50, "volatility": "medium", "stability_score": 5},
            {"symbol": "ROB", "name": "RobotWorks", "sector": "Industrial", "backstory": "Advanced manufacturing robotics.", "ipo_price": 96.25, "volatility": "low", "stability_score": 8},
            {"symbol": "BIO", "name": "BioFuture", "sector": "Biotech", "backstory": "Synthetic biology for sustainable agriculture.", "ipo_price": 112.75, "volatility": "high", "stability_score": 3},
            {"symbol": "FDT", "name": "FoodTech", "sector": "Food", "backstory": "Cellular agriculture and lab-grown meat alternatives.", "ipo_price": 67.50, "volatility": "medium", "stability_score": 5},
            {"symbol": "QTS", "name": "QuantumSoft", "sector": "Tech", "backstory": "Quantum computing software for enterprise solutions.", "ipo_price": 189.00, "volatility": "high", "stability_score": 2},
            {"symbol": "HYP", "name": "HydroPower", "sector": "Energy", "backstory": "Hydroelectric dam optimization and smart grid integration.", "ipo_price": 91.25, "volatility": "low", "stability_score": 9},
            {"symbol": "MDT", "name": "MediTech", "sector": "Healthcare", "backstory": "Telemedicine and remote patient monitoring systems.", "ipo_price": 78.50, "volatility": "medium", "stability_score": 6},
            {"symbol": "CYD", "name": "CyberDefense", "sector": "Defense", "backstory": "Cybersecurity solutions for government and military.", "ipo_price": 134.00, "volatility": "medium", "stability_score": 7},
            {"symbol": "STX", "name": "StreamFlix", "sector": "Entertainment", "backstory": "Streaming platform with AI-generated content.", "ipo_price": 143.75, "volatility": "high", "stability_score": 4},
            {"symbol": "CRB", "name": "CryptoBank", "sector": "Finance", "backstory": "Digital bank specializing in cryptocurrency services.", "ipo_price": 87.25, "volatility": "high", "stability_score": 3},
            {"symbol": "QSH", "name": "QuickShop", "sector": "Retail", "backstory": "AI-powered instant delivery and inventory management.", "ipo_price": 56.75, "volatility": "medium", "stability_score": 5},
            {"symbol": "EDR", "name": "ElectricDrive", "sector": "Automotive", "backstory": "Electric vehicle charging infrastructure network.", "ipo_price": 102.50, "volatility": "low", "stability_score": 8},
            {"symbol": "SPL", "name": "SpaceLogistics", "sector": "Aerospace", "backstory": "Space-based cargo transport and delivery services.", "ipo_price": 176.25, "volatility": "high", "stability_score": 2},
            {"symbol": "SMH", "name": "SmartHomes", "sector": "Real Estate", "backstory": "IoT-enabled home automation and energy management.", "ipo_price": 64.00, "volatility": "medium", "stability_score": 6},
            {"symbol": "PET", "name": "PersonalTech", "sector": "Consumer Goods", "backstory": "Wearable technology and personal electronics.", "ipo_price": 71.25, "volatility": "medium", "stability_score": 5},
            {"symbol": "SFT", "name": "SmartFactory", "sector": "Industrial", "backstory": "Industry 4.0 automation and IoT integration.", "ipo_price": 98.75, "volatility": "low", "stability_score": 8},
            {"symbol": "FBN", "name": "FiberNet", "sector": "Telecom", "backstory": "Fiber optic network infrastructure and 5G deployment.", "ipo_price": 105.50, "volatility": "medium", "stability_score": 7},
            {"symbol": "GER", "name": "GreenEnergy", "sector": "Utilities", "backstory": "Renewable energy integration and smart grid management.", "ipo_price": 82.75, "volatility": "low", "stability_score": 9},
            {"symbol": "NTC", "name": "NanoTech", "sector": "Materials", "backstory": "Nanomaterials and advanced composites manufacturing.", "ipo_price": 115.25, "volatility": "high", "stability_score": 3},
            {"symbol": "ASP", "name": "AutoShip", "sector": "Transportation", "backstory": "Autonomous shipping and maritime logistics.", "ipo_price": 124.00, "volatility": "medium", "stability_score": 6},
            {"symbol": "DPM", "name": "DeepMind", "sector": "Tech", "backstory": "Advanced neural networks and machine learning research.", "ipo_price": 167.50, "volatility": "high", "stability_score": 2},
            {"symbol": "WTC", "name": "WindTech", "sector": "Energy", "backstory": "Offshore wind turbine technology and maintenance.", "ipo_price": 93.75, "volatility": "medium", "stability_score": 7},
            {"symbol": "FFD", "name": "FastFood", "sector": "Food", "backstory": "Quick service restaurant chain with AI ordering.", "ipo_price": 51.25, "volatility": "medium", "stability_score": 5},
            {"symbol": "HAI", "name": "HealthAI", "sector": "Healthcare", "backstory": "AI-powered diagnostic tools and medical imaging.", "ipo_price": 145.25, "volatility": "high", "stability_score": 3},
            {"symbol": "DAI", "name": "DefenseAI", "sector": "Defense", "backstory": "AI-powered defense systems and autonomous weapons.", "ipo_price": 187.50, "volatility": "low", "stability_score": 8},
            {"symbol": "VRX", "name": "VirtualReality", "sector": "Entertainment", "backstory": "VR gaming and metaverse platform development.", "ipo_price": 74.75, "volatility": "high", "stability_score": 4},
            {"symbol": "DWT", "name": "DigitalWallet", "sector": "Finance", "backstory": "Mobile payment solutions and digital currency integration.", "ipo_price": 95.00, "volatility": "medium", "stability_score": 6},
        ]
    
    def _generate_fallback_news(self, companies: List[str], sectors: List[str]) -> List[Dict[str, Any]]:
        """Fallback news if API fails"""
        import random
        
        # Dynamic global news options
        global_news = [
            {"headline": "Federal Reserve announces interest rate changes", "category": "global", "affected_companies": ["all"], "sentiment": random.choice(["positive", "negative", "neutral"])},
            {"headline": "Stock market reaches record highs amid economic optimism", "category": "global", "affected_companies": ["all"], "sentiment": "positive"},
            {"headline": "Trade tensions rise between major economies", "category": "global", "affected_companies": ["all"], "sentiment": "negative"},
            {"headline": "Inflation data comes in better than expected", "category": "global", "affected_companies": ["all"], "sentiment": "positive"},
            {"headline": "Government announces new stimulus package", "category": "global", "affected_companies": ["all"], "sentiment": "positive"},
            {"headline": "Supply chain disruptions impact global markets", "category": "global", "affected_companies": ["all"], "sentiment": "negative"},
        ]
        
        # Dynamic sector news options
        sector_news = []
        for sector in random.sample(sectors, min(2, len(sectors))):
            if sector == "Tech":
                sector_news.extend([
                    {"headline": f"Breakthrough in AI technology boosts {sector} stocks", "category": "sector", "affected_companies": ["all"], "sentiment": "positive", "sector": sector},
                    {"headline": f"Major tech company faces antitrust lawsuit", "category": "sector", "affected_companies": ["all"], "sentiment": "negative", "sector": sector},
                    {"headline": f"New cybersecurity threats emerge in {sector}", "category": "sector", "affected_companies": ["all"], "sentiment": "negative", "sector": sector},
                ])
            elif sector == "Energy":
                sector_news.extend([
                    {"headline": f"Oil prices surge amid supply concerns", "category": "sector", "affected_companies": ["all"], "sentiment": "positive", "sector": sector},
                    {"headline": f"Renewable energy breakthrough threatens traditional {sector}", "category": "sector", "affected_companies": ["all"], "sentiment": "negative", "sector": sector},
                    {"headline": f"Government announces new {sector} policy", "category": "sector", "affected_companies": ["all"], "sentiment": random.choice(["positive", "negative"]), "sector": sector},
                ])
            elif sector == "Healthcare":
                sector_news.extend([
                    {"headline": f"FDA approves new breakthrough drug in {sector}", "category": "sector", "affected_companies": ["all"], "sentiment": "positive", "sector": sector},
                    {"headline": f"Healthcare reform debate impacts {sector} stocks", "category": "sector", "affected_companies": ["all"], "sentiment": "negative", "sector": sector},
                    {"headline": f"Medical device innovation drives {sector} growth", "category": "sector", "affected_companies": ["all"], "sentiment": "positive", "sector": sector},
                ])
            else:
                sector_news.extend([
                    {"headline": f"New regulations impact {sector} industry", "category": "sector", "affected_companies": ["all"], "sentiment": "negative", "sector": sector},
                    {"headline": f"{sector} sector shows strong growth", "category": "sector", "affected_companies": ["all"], "sentiment": "positive", "sector": sector},
                ])
        
        # Dynamic company news options
        company = random.choice(companies)
        company_news = [
            {"headline": f"{company} reports better than expected earnings", "category": "company", "affected_companies": [company], "sentiment": "positive"},
            {"headline": f"{company} CEO announces surprise resignation", "category": "company", "affected_companies": [company], "sentiment": "negative"},
            {"headline": f"{company} announces major acquisition", "category": "company", "affected_companies": [company], "sentiment": "positive"},
            {"headline": f"{company} faces regulatory investigation", "category": "company", "affected_companies": [company], "sentiment": "negative"},
            {"headline": f"{company} launches innovative new product", "category": "company", "affected_companies": [company], "sentiment": "positive"},
            {"headline": f"{company} stock surges on upgrade from analysts", "category": "company", "affected_companies": [company], "sentiment": "positive"},
        ]
        
        # Select one from each category
        selected_news = [
            random.choice(global_news),
            random.choice(sector_news) if sector_news else {"headline": f"Market uncertainty affects {sectors[0]} sector", "category": "sector", "affected_companies": ["all"], "sentiment": "neutral", "sector": sectors[0]},
            random.choice(company_news)
        ]
        
        return selected_news
    
    def _generate_fallback_prices(self, game_state: Dict[str, Any]) -> Dict[str, float]:
        """Fallback price calculation if API fails"""
        new_prices = {}
        for symbol, company in game_state['companies'].items():
            current_price = company['current_price']
            # Simple random movement between -10% and +10%
            change = random.uniform(-0.1, 0.1)
            new_prices[symbol] = current_price * (1 + change)
        return new_prices
    
    def _generate_fallback_event(self, companies: List[str]) -> Dict[str, Any]:
        """Fallback special event if API fails"""
        import random
        
        events = [
            {
                "event_type": "merger_rumor",
                "title": "Merger Mania!",
                "description": f"Rumors swirl about a potential merger between {random.choice(companies)} and {random.choice(companies)}.",
                "affected_companies": random.sample(companies, 2),
                "effects": "One company spikes, one dips"
            },
            {
                "event_type": "market_crash",
                "title": "Market Crash!",
                "description": "Unexpected market turbulence sends shockwaves through Wall Street.",
                "affected_companies": companies,
                "effects": "All stocks drop 15-25%"
            },
            {
                "event_type": "meme_stock_frenzy",
                "title": "Meme Stock Frenzy!",
                "description": f"Retail investors go wild over {random.choice(companies)}!",
                "affected_companies": [random.choice(companies)],
                "effects": "One stock goes parabolic then crashes"
            },
            {
                "event_type": "bubble_warning",
                "title": "Bubble Warning!",
                "description": f"Analysts warn that the {random.choice(['Tech', 'Energy', 'Healthcare', 'Finance'])} sector is overheated.",
                "affected_companies": companies,
                "effects": "Sector-specific volatility increases"
            },
            {
                "event_type": "insider_tip",
                "title": "Insider Tip!",
                "description": f"Anonymous source suggests {random.choice(companies)} is about to make a major announcement.",
                "affected_companies": [random.choice(companies)],
                "effects": "70% accurate tip - could be a trap!"
            },
            {
                "event_type": "regulatory_shock",
                "title": "Regulatory Shock!",
                "description": "New government regulations catch markets by surprise.",
                "affected_companies": companies,
                "effects": "Random sector impact"
            },
            {
                "event_type": "breakthrough_announcement",
                "title": "Scientific Breakthrough!",
                "description": f"Revolutionary discovery announced by {random.choice(companies)}.",
                "affected_companies": [random.choice(companies)],
                "effects": "Company stock soars on innovation news"
            },
            {
                "event_type": "supply_chain_crisis",
                "title": "Supply Chain Crisis!",
                "description": "Global supply chain disruptions impact multiple sectors.",
                "affected_companies": companies,
                "effects": "Manufacturing and transportation stocks hit hard"
            }
        ]
        
        return random.choice(events)
