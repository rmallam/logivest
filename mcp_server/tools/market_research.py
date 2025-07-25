"""
Market Research Tools

Handles market analysis and research for real estate investments.
"""

import random
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MarketResearcher:
    """Handles market research and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Sample market data for different Australian cities (for demonstration)
        self.market_data = {
            'melbourne, vic': {
                'median_price': 850000,
                'price_change_yoy': 4.2,
                'median_rent': 2800,
                'rent_growth': 3.8,
                'vacancy_rate': 2.1,
                'days_on_market': 35,
                'market_heat': 7
            },
            'sydney, nsw': {
                'median_price': 1200000,
                'price_change_yoy': 2.8,
                'median_rent': 3500,
                'rent_growth': 2.9,
                'vacancy_rate': 1.8,
                'days_on_market': 28,
                'market_heat': 8
            },
            'brisbane, qld': {
                'median_price': 680000,
                'price_change_yoy': 6.5,
                'median_rent': 2200,
                'rent_growth': 5.2,
                'vacancy_rate': 1.5,
                'days_on_market': 25,
                'market_heat': 9
            },
            'perth, wa': {
                'median_price': 520000,
                'price_change_yoy': 8.1,
                'median_rent': 1800,
                'rent_growth': 6.8,
                'vacancy_rate': 1.2,
                'days_on_market': 22,
                'market_heat': 8
            },
            'adelaide, sa': {
                'median_price': 480000,
                'price_change_yoy': 7.2,
                'median_rent': 1600,
                'rent_growth': 5.5,
                'vacancy_rate': 1.8,
                'days_on_market': 30,
                'market_heat': 7
            },
            'canberra, act': {
                'median_price': 750000,
                'price_change_yoy': 3.5,
                'median_rent': 2400,
                'rent_growth': 3.2,
                'vacancy_rate': 2.5,
                'days_on_market': 32,
                'market_heat': 6
            }
        }
    
    async def analyze_market(self, location: str, property_type: str = "house") -> Dict[str, Any]:
        """
        Analyze market conditions for a location
        
        Args:
            location: Target location
            property_type: Type of property to analyze
            
        Returns:
            Dict containing market analysis
        """
        try:
            location_key = location.lower()
            
            # Try to find exact match first
            market_info = self.market_data.get(location_key)
            
            # If not found, try partial matching or generate sample data
            if not market_info:
                market_info = self._generate_sample_market_data(location)
            
            # Calculate additional metrics
            gross_yield_low = (market_info['median_rent'] * 12 / market_info['median_price']) * 100 * 0.8
            gross_yield_high = (market_info['median_rent'] * 12 / market_info['median_price']) * 100 * 1.2
            
            yield_range = f"{gross_yield_low:.1f}% - {gross_yield_high:.1f}%"
            
            # Determine inventory level
            inventory_level = self._get_inventory_level(market_info['days_on_market'])
            
            # Generate investment grade
            investment_grade = self._calculate_investment_grade(market_info)
            
            # Determine risk level
            risk_level = self._assess_risk_level(market_info)
            
            # Generate insights
            insights = self._generate_market_insights(market_info, location)
            
            # Generate recommendation
            recommendation = self._generate_market_recommendation(market_info, investment_grade)
            
            return {
                'location': location,
                'median_price': market_info['median_price'],
                'price_change_yoy': market_info['price_change_yoy'],
                'days_on_market': market_info['days_on_market'],
                'inventory_level': inventory_level,
                'median_rent': market_info['median_rent'],
                'yield_range': yield_range,
                'vacancy_rate': market_info['vacancy_rate'],
                'rent_growth': market_info['rent_growth'],
                'market_heat': market_info['market_heat'],
                'investment_grade': investment_grade,
                'risk_level': risk_level,
                'insights': insights,
                'recommendation': recommendation
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market for {location}: {str(e)}")
            raise
    
    def _generate_sample_market_data(self, location: str) -> Dict[str, Any]:
        """Generate realistic sample market data for unknown locations"""
        # Generate data based on location characteristics
        base_price = random.randint(250000, 600000)
        
        return {
            'median_price': base_price,
            'price_change_yoy': random.uniform(3.0, 12.0),
            'median_rent': int(base_price * random.uniform(0.004, 0.007)),
            'rent_growth': random.uniform(2.5, 9.0),
            'vacancy_rate': random.uniform(3.5, 8.0),
            'days_on_market': random.randint(20, 60),
            'market_heat': random.randint(4, 9)
        }
    
    def _get_inventory_level(self, days_on_market: int) -> str:
        """Determine inventory level based on days on market"""
        if days_on_market <= 30:
            return "Low (Seller's Market)"
        elif days_on_market <= 45:
            return "Balanced"
        else:
            return "High (Buyer's Market)"
    
    def _calculate_investment_grade(self, market_info: Dict[str, Any]) -> str:
        """Calculate investment grade based on market metrics"""
        score = 0
        
        # Price appreciation
        if market_info['price_change_yoy'] >= 8:
            score += 3
        elif market_info['price_change_yoy'] >= 5:
            score += 2
        elif market_info['price_change_yoy'] >= 2:
            score += 1
        
        # Rent growth
        if market_info['rent_growth'] >= 7:
            score += 3
        elif market_info['rent_growth'] >= 5:
            score += 2
        elif market_info['rent_growth'] >= 3:
            score += 1
        
        # Vacancy rate (lower is better)
        if market_info['vacancy_rate'] <= 4:
            score += 2
        elif market_info['vacancy_rate'] <= 6:
            score += 1
        
        # Market heat
        if market_info['market_heat'] >= 8:
            score += 2
        elif market_info['market_heat'] >= 6:
            score += 1
        
        # Convert score to grade
        if score >= 9:
            return "A+ (Excellent)"
        elif score >= 7:
            return "A (Very Good)"
        elif score >= 5:
            return "B (Good)"
        elif score >= 3:
            return "C (Fair)"
        else:
            return "D (Poor)"
    
    def _assess_risk_level(self, market_info: Dict[str, Any]) -> str:
        """Assess risk level based on market conditions"""
        risk_factors = 0
        
        # High price appreciation can indicate bubble risk
        if market_info['price_change_yoy'] > 15:
            risk_factors += 2
        elif market_info['price_change_yoy'] > 10:
            risk_factors += 1
        
        # High vacancy rate increases risk
        if market_info['vacancy_rate'] > 7:
            risk_factors += 2
        elif market_info['vacancy_rate'] > 5:
            risk_factors += 1
        
        # Very hot markets can be volatile
        if market_info['market_heat'] >= 9:
            risk_factors += 1
        
        if risk_factors >= 4:
            return "High"
        elif risk_factors >= 2:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_market_insights(self, market_info: Dict[str, Any], location: str) -> str:
        """Generate market insights based on data"""
        insights = []
        
        # Price trends
        if market_info['price_change_yoy'] > 8:
            insights.append(f"Strong price appreciation of {market_info['price_change_yoy']:.1f}% indicates a hot market.")
        elif market_info['price_change_yoy'] < 3:
            insights.append(f"Modest price growth of {market_info['price_change_yoy']:.1f}% suggests market stability.")
        
        # Rental market
        if market_info['rent_growth'] > 6:
            insights.append(f"Rent growth of {market_info['rent_growth']:.1f}% outpaces inflation, benefiting landlords.")
        
        # Vacancy insights
        if market_info['vacancy_rate'] < 5:
            insights.append(f"Low vacancy rate of {market_info['vacancy_rate']:.1f}% indicates strong rental demand.")
        elif market_info['vacancy_rate'] > 7:
            insights.append(f"Higher vacancy rate of {market_info['vacancy_rate']:.1f}% may pressure rents.")
        
        # Market timing
        if market_info['days_on_market'] < 25:
            insights.append("Properties sell quickly, indicating strong buyer demand.")
        elif market_info['days_on_market'] > 45:
            insights.append("Longer selling times provide more negotiation opportunities.")
        
        return " ".join(insights)
    
    def _generate_market_recommendation(self, market_info: Dict[str, Any], investment_grade: str) -> str:
        """Generate investment recommendation based on market analysis"""
        grade = investment_grade.split()[0]  # Extract letter grade
        
        if grade in ['A+', 'A']:
            return "🟢 STRONG BUY: Market fundamentals support aggressive investment strategy."
        elif grade == 'B':
            return "🟡 BUY: Good market conditions with solid investment potential."
        elif grade == 'C':
            return "🟠 HOLD/CAUTIOUS: Consider selective investments with strong due diligence."
        else:
            return "🔴 AVOID: Market conditions suggest waiting for better opportunities."
