"""
Property Analysis Tools

Handles property valuation, analysis, and investment scoring.
"""

import random
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PropertyAnalyzer:
    """Analyzes properties for investment potential"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_property(self, property_data: Dict[str, Any], budget: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze a property for investment potential
        
        Args:
            property_data: Property information dict
            budget: Optional budget constraint
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Extract property details
            address = property_data.get('address', 'Unknown Address')
            property_type = property_data.get('type', 'house')
            bedrooms = property_data.get('bedrooms', 3)
            bathrooms = property_data.get('bathrooms', 2)
            
            # Handle both sqft and sqm (Australian properties use sqm)
            sqft = property_data.get('sqft', 0)
            sqm = property_data.get('sqm', 0)
            
            if sqm > 0 and sqft == 0:
                sqft = int(sqm * 10.764)  # Convert sqm to sqft for calculations
            elif sqft == 0 and sqm == 0:
                sqft = 1500  # Default
                
            price = property_data.get('price', 300000)
            
            # Calculate estimated rent (using a rent-to-price ratio)
            rent_ratio = self._get_rent_ratio(property_type, sqft)
            estimated_rent = price * rent_ratio
            
            # Calculate yields
            annual_rent = estimated_rent * 12
            annual_expenses = price * 0.025  # Assume 2.5% of price for expenses
            
            gross_yield = (annual_rent / price) * 100
            net_yield = ((annual_rent - annual_expenses) / price) * 100
            cap_rate = net_yield  # Simplified cap rate
            
            # Calculate financing metrics (assuming 20% down, 30-year loan at 7%)
            down_payment = price * 0.20
            loan_amount = price * 0.80
            monthly_payment = self._calculate_mortgage_payment(loan_amount, 0.07, 30)
            
            # Cash flow calculations
            monthly_expenses = annual_expenses / 12
            monthly_cashflow = estimated_rent - monthly_payment - monthly_expenses
            annual_cashflow = monthly_cashflow * 12
            
            # Cash-on-cash return
            total_cash_invested = down_payment + (price * 0.05)  # Add 5% for closing costs
            cash_return = (annual_cashflow / total_cash_invested) * 100 if total_cash_invested > 0 else 0
            
            # Break-even calculation
            breakeven_months = abs(total_cash_invested / monthly_cashflow) if monthly_cashflow > 0 else 999
            
            # Investment scoring (1-10 scale)
            investment_score = self._calculate_investment_score(
                gross_yield, net_yield, cash_return, monthly_cashflow
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                investment_score, gross_yield, cash_return, monthly_cashflow
            )
            
            return {
                'address': address,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'estimated_value': price,
                'estimated_rent': estimated_rent,
                'gross_yield': gross_yield,
                'net_yield': net_yield,
                'cap_rate': cap_rate,
                'cash_return': cash_return,
                'breakeven_months': int(breakeven_months),
                'annual_cashflow': annual_cashflow,
                'monthly_cashflow': monthly_cashflow,
                'investment_score': investment_score,
                'recommendation': recommendation
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing property: {str(e)}")
            raise
    
    def _get_rent_ratio(self, property_type: str, sqft: int) -> float:
        """Get monthly rent as a ratio of property price - updated for Australian market"""
        # Australian rental yield ratios (monthly rent as percentage of property price)
        base_ratios = {
            'house': 0.0040,        # ~4.8% annual yield
            'condo': 0.0042,        # ~5.0% annual yield  
            'townhouse': 0.0041,    # ~4.9% annual yield
            'apartment': 0.0043,    # ~5.2% annual yield
            'unit': 0.0043          # ~5.2% annual yield
        }
        
        ratio = base_ratios.get(property_type, 0.0041)
        
        # Adjust for size (smaller properties typically have higher yields in Australia)
        sqm = sqft * 0.092903 if sqft > 0 else 100  # Convert to square meters
        
        if sqm < 70:          # Small apartments
            ratio *= 1.3
        elif sqm < 100:       # Medium apartments
            ratio *= 1.1
        elif sqm > 200:       # Large houses
            ratio *= 0.9
            
        return ratio
    
    def _calculate_mortgage_payment(self, principal: float, annual_rate: float, years: int) -> float:
        """Calculate monthly mortgage payment"""
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return principal / num_payments
        
        payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                 ((1 + monthly_rate)**num_payments - 1)
        
        return payment
    
    def _calculate_investment_score(self, gross_yield: float, net_yield: float, 
                                  cash_return: float, monthly_cashflow: float) -> int:
        """Calculate investment score from 1-10"""
        score = 0
        
        # Gross yield scoring (0-3 points)
        if gross_yield >= 12:
            score += 3
        elif gross_yield >= 8:
            score += 2
        elif gross_yield >= 6:
            score += 1
        
        # Net yield scoring (0-2 points)
        if net_yield >= 8:
            score += 2
        elif net_yield >= 5:
            score += 1
        
        # Cash return scoring (0-3 points)
        if cash_return >= 15:
            score += 3
        elif cash_return >= 10:
            score += 2
        elif cash_return >= 5:
            score += 1
        
        # Cash flow scoring (0-2 points)
        if monthly_cashflow >= 500:
            score += 2
        elif monthly_cashflow >= 200:
            score += 1
        
        return min(score, 10)
    
    def _generate_recommendation(self, score: int, gross_yield: float, 
                               cash_return: float, monthly_cashflow: float) -> str:
        """Generate investment recommendation"""
        if score >= 8:
            return "🟢 EXCELLENT INVESTMENT: Strong yields and cash flow make this an attractive opportunity."
        elif score >= 6:
            return "🟡 GOOD INVESTMENT: Solid returns with manageable risk."
        elif score >= 4:
            return "🟠 MODERATE INVESTMENT: Consider negotiating price or improving rental potential."
        else:
            return "🔴 POOR INVESTMENT: Low returns suggest looking for better opportunities."
