"""
Financial Calculation Tools

Handles financial calculations for real estate investments.
"""

import math
from typing import Dict, Any
import logging
from .gemini_analyzer import RentToEMIAnalyzer

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """Handles financial calculations for real estate investments"""
    
    def __init__(self):
        self.current_interest_rate = 0.07  # 7% default
        self.default_loan_term = 30  # 30 years
    
    def calculate_investment_metrics(self, property_price: float, monthly_rent: float,
                                   annual_expenses: float = 0, down_payment_percent: float = 20) -> Dict[str, Any]:
        """
        Calculate comprehensive investment metrics
        
        Args:
            property_price: Property purchase price
            monthly_rent: Expected monthly rental income
            annual_expenses: Annual property expenses
            down_payment_percent: Down payment percentage
            
        Returns:
            Dict containing financial metrics
        """
        try:
            # Basic calculations
            annual_rent = monthly_rent * 12
            down_payment = property_price * (down_payment_percent / 100)
            loan_amount = property_price - down_payment
            
            # If no expenses provided, estimate them
            if annual_expenses == 0:
                annual_expenses = self._estimate_annual_expenses(property_price)
            
            # Yield calculations
            gross_yield = (annual_rent / property_price) * 100
            net_yield = ((annual_rent - annual_expenses) / property_price) * 100
            cap_rate = net_yield  # Simplified cap rate
            
            # Mortgage calculations
            monthly_payment = self._calculate_monthly_payment(
                loan_amount, self.current_interest_rate, self.default_loan_term
            )
            
            # Cash flow calculations
            monthly_expenses = annual_expenses / 12
            monthly_cashflow = monthly_rent - monthly_payment - monthly_expenses
            annual_cashflow = monthly_cashflow * 12
            
            # Investment return calculations
            closing_costs = property_price * 0.03  # Estimate 3% closing costs
            total_cash_invested = down_payment + closing_costs
            
            cash_return = (annual_cashflow / total_cash_invested) * 100 if total_cash_invested > 0 else 0
            
            # Break-even analysis (multiple scenarios)
            breakeven_analysis = self._calculate_comprehensive_breakeven(
                monthly_rent, monthly_payment, monthly_expenses, total_cash_invested,
                property_price, annual_rent, annual_expenses
            )
            
            # Rent-to-EMI ratio analysis
            weekly_rent = monthly_rent * 12 / 52  # Convert back to weekly for analysis
            rent_to_emi_analysis = RentToEMIAnalyzer.calculate_rent_to_emi_ratio(
                weekly_rent, monthly_payment
            )
            rent_to_emi_recommendations = RentToEMIAnalyzer.get_ratio_recommendations(
                rent_to_emi_analysis
            )
            
            # Calculate investment score (0-10)
            investment_score = self._calculate_investment_score(
                gross_yield, net_yield, cash_return, monthly_cashflow
            )
            
            # Generate analysis
            analysis = self._generate_analysis(gross_yield, net_yield, cash_return, monthly_cashflow)
            
            return {
                'property_price': property_price,
                'down_payment': down_payment,
                'loan_amount': loan_amount,
                'monthly_payment': monthly_payment,
                'gross_yield': gross_yield,
                'net_yield': net_yield,
                'cap_rate': cap_rate,
                'cash_return': cash_return,
                'monthly_cashflow': monthly_cashflow,
                'annual_cashflow': annual_cashflow,
                'breakeven_analysis': breakeven_analysis,
                'breakeven_months': breakeven_analysis.get('operational_breakeven_months', 999),  # For backward compatibility
                'rent_to_emi_analysis': rent_to_emi_analysis,
                'rent_to_emi_recommendations': rent_to_emi_recommendations,
                'total_cash_invested': total_cash_invested,
                'total_investment': total_cash_invested,  # Alias for template compatibility
                'investment_score': investment_score,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error calculating investment metrics: {str(e)}")
            raise
    
    def _calculate_monthly_payment(self, principal: float, annual_rate: float, years: int) -> float:
        """Calculate monthly mortgage payment using amortization formula"""
        if principal <= 0:
            return 0
            
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return principal / num_payments
        
        payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                 ((1 + monthly_rate)**num_payments - 1)
        
        return payment
    
    def _calculate_comprehensive_breakeven(self, monthly_rent: float, monthly_payment: float, 
                                         monthly_expenses: float, total_cash_invested: float,
                                         property_price: float, annual_rent: float, annual_expenses: float) -> Dict[str, Any]:
        """Calculate comprehensive break-even analysis including operational and total return scenarios"""
        
        current_monthly_cashflow = monthly_rent - monthly_payment - monthly_expenses
        rent_growth_rate = 0.025  # 2.5% annual rent inflation
        capital_growth_rate = 0.055  # 5.5% annual capital growth
        
        # 1. Operational Break-even (when monthly cash flow turns positive)
        operational_breakeven_months = None
        if current_monthly_cashflow >= 0:
            operational_breakeven_months = 0  # Already positive
        else:
            # Calculate when rent growth will make cash flow positive
            for months in range(1, 360):  # Check up to 30 years
                years = months / 12
                inflated_monthly_rent = monthly_rent * ((1 + rent_growth_rate) ** years)
                monthly_cashflow = inflated_monthly_rent - monthly_payment - monthly_expenses
                
                if monthly_cashflow >= 0:
                    operational_breakeven_months = months
                    break
        
        # 2. Total Return Break-even (when total value exceeds initial investment)
        total_return_breakeven_years = None
        for years in range(1, 31):  # Check up to 30 years
            # Calculate cumulative cash flow
            cumulative_cashflow = 0
            for year in range(1, years + 1):
                year_rent = annual_rent * ((1 + rent_growth_rate) ** (year - 1))
                year_cashflow = year_rent - annual_expenses - (monthly_payment * 12)
                cumulative_cashflow += year_cashflow
            
            # Calculate capital gains
            property_value = property_price * ((1 + capital_growth_rate) ** years)
            capital_gain = property_value - property_price
            
            # Total return
            total_return = cumulative_cashflow + capital_gain
            
            if total_return >= total_cash_invested:
                total_return_breakeven_years = years
                break
        
        # 3. Cash Flow Positive Break-even (simpler version)
        cashflow_positive_years = None
        if operational_breakeven_months:
            cashflow_positive_years = operational_breakeven_months / 12
        
        return {
            'operational_breakeven_months': operational_breakeven_months or 999,
            'operational_breakeven_years': round(operational_breakeven_months / 12, 1) if operational_breakeven_months else None,
            'total_return_breakeven_years': total_return_breakeven_years,
            'cashflow_positive_years': round(cashflow_positive_years, 1) if cashflow_positive_years else None,
            'current_monthly_shortfall': abs(current_monthly_cashflow) if current_monthly_cashflow < 0 else 0,
            'explanation': self._generate_breakeven_explanation(operational_breakeven_months, total_return_breakeven_years)
        }
    
    def _generate_breakeven_explanation(self, operational_months: int, total_return_years: int) -> str:
        """Generate user-friendly explanation of break-even scenarios"""
        
        explanations = []
        
        # Operational break-even
        if operational_months and operational_months < 999:
            if operational_months <= 12:
                explanations.append(f"🟢 Cash flow turns positive in {operational_months} months due to rent growth")
            else:
                years = round(operational_months / 12, 1)
                explanations.append(f"🟡 Cash flow turns positive in {years} years due to rent growth")
        else:
            explanations.append("🔴 Monthly cash flow remains negative (requires ongoing contributions)")
        
        # Total return break-even
        if total_return_years:
            if total_return_years <= 3:
                explanations.append(f"✅ Total investment breaks even in {total_return_years} years (including capital gains)")
            elif total_return_years <= 7:
                explanations.append(f"✅ Total investment breaks even in {total_return_years} years with capital growth")
            else:
                explanations.append(f"⚠️ Total break-even takes {total_return_years} years - long-term strategy required")
        else:
            explanations.append("❌ Total return break-even not achieved within 30 years")
        
        return " | ".join(explanations)
    
    def _estimate_annual_expenses(self, property_price: float) -> float:
        """Estimate annual property expenses as percentage of property value"""
        # Typical breakdown:
        # Property taxes: 1.2% of value
        # Insurance: 0.5% of value
        # Maintenance: 1% of value
        # Management: 0.8% of value (if using property manager)
        # Vacancy allowance: 0.5% of value
        
        expense_rate = 0.04  # 4% total
        return property_price * expense_rate
    
    def calculate_loan_comparison(self, property_price: float, scenarios: list) -> Dict[str, Any]:
        """Compare different loan scenarios"""
        comparisons = {}
        
        for down_payment_percent in scenarios:
            down_payment = property_price * (down_payment_percent / 100)
            loan_amount = property_price - down_payment
            monthly_payment = self._calculate_monthly_payment(
                loan_amount, self.current_interest_rate, self.default_loan_term
            )
            
            comparisons[f"{down_payment_percent}%"] = {
                'down_payment': down_payment,
                'loan_amount': loan_amount,
                'monthly_payment': monthly_payment,
                'total_interest': (monthly_payment * 12 * self.default_loan_term) - loan_amount
            }
        
        return comparisons
    
    def calculate_appreciation_scenarios(self, property_price: float, annual_rates: list, years: int = 10) -> Dict[str, Any]:
        """Calculate property value under different appreciation scenarios"""
        scenarios = {}
        
        for rate in annual_rates:
            future_value = property_price * ((1 + rate/100) ** years)
            total_appreciation = future_value - property_price
            
            scenarios[f"{rate}%"] = {
                'future_value': future_value,
                'total_appreciation': total_appreciation,
                'annualized_return': rate
            }
        
        return scenarios
    
    def _generate_analysis(self, gross_yield: float, net_yield: float, 
                          cash_return: float, monthly_cashflow: float) -> str:
        """Generate investment analysis text"""
        analysis_parts = []
        
        # Yield analysis
        if gross_yield >= 10:
            analysis_parts.append("🟢 Excellent gross yield indicates strong rental income potential.")
        elif gross_yield >= 7:
            analysis_parts.append("🟡 Good gross yield provides solid rental returns.")
        else:
            analysis_parts.append("🔴 Low gross yield may indicate overpriced property or weak rental market.")
        
        # Cash flow analysis
        if monthly_cashflow >= 500:
            analysis_parts.append("💚 Strong positive cash flow provides excellent monthly income.")
        elif monthly_cashflow >= 100:
            analysis_parts.append("💛 Positive cash flow provides modest monthly income.")
        elif monthly_cashflow >= 0:
            analysis_parts.append("💜 Break-even cash flow - property pays for itself.")
        else:
            analysis_parts.append("💔 Negative cash flow requires monthly contributions.")
        
        # Cash-on-cash return analysis
        if cash_return >= 12:
            analysis_parts.append("🚀 Outstanding cash-on-cash return beats most investments.")
        elif cash_return >= 8:
            analysis_parts.append("📈 Strong cash-on-cash return provides good investment returns.")
        elif cash_return >= 4:
            analysis_parts.append("📊 Moderate cash-on-cash return is acceptable for stable investment.")
        else:
            analysis_parts.append("📉 Low cash-on-cash return suggests poor investment performance.")
        
        return " ".join(analysis_parts)
    
    def _calculate_investment_score(self, gross_yield: float, net_yield: float, 
                                   cash_return: float, monthly_cashflow: float) -> float:
        """Calculate investment score from 0-10 based on key metrics"""
        score = 0.0
        
        # Gross yield component (0-3 points)
        if gross_yield >= 8:
            score += 3
        elif gross_yield >= 6:
            score += 2
        elif gross_yield >= 4:
            score += 1
        
        # Cash flow component (0-3 points)
        if monthly_cashflow >= 500:
            score += 3
        elif monthly_cashflow >= 200:
            score += 2
        elif monthly_cashflow >= 0:
            score += 1
        
        # Cash return component (0-3 points)
        if cash_return >= 12:
            score += 3
        elif cash_return >= 8:
            score += 2
        elif cash_return >= 4:
            score += 1
        
        # Net yield bonus (0-1 points)
        if net_yield >= 5:
            score += 1
        
        return min(score, 10.0)  # Cap at 10
    
    def _calculate_investment_score(self, gross_yield: float, net_yield: float, 
                                  cash_return: float, monthly_cashflow: float) -> float:
        """Calculate overall investment score from 0-10"""
        score = 0.0
        
        # Gross yield component (0-3 points)
        if gross_yield >= 8:
            score += 3.0
        elif gross_yield >= 6:
            score += 2.0
        elif gross_yield >= 4:
            score += 1.0
        
        # Cash flow component (0-3 points)
        if monthly_cashflow >= 500:
            score += 3.0
        elif monthly_cashflow >= 200:
            score += 2.0
        elif monthly_cashflow >= 0:
            score += 1.0
        
        # Cash-on-cash return component (0-3 points)
        if cash_return >= 10:
            score += 3.0
        elif cash_return >= 6:
            score += 2.0
        elif cash_return >= 3:
            score += 1.0
        
        # Net yield component (0-1 point)
        if net_yield >= 3:
            score += 1.0
        elif net_yield >= 1:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10
    
    def calculate_capital_gains_forecast(self, property_price: float, annual_growth_rate: float = 0.055, years: int = 10) -> Dict[str, Any]:
        """Calculate property value and capital gains over time"""
        yearly_breakdown = []
        
        for year in range(1, years + 1):
            # Calculate property value with compound growth
            property_value = property_price * ((1 + annual_growth_rate) ** year)
            cumulative_gain = property_value - property_price
            
            yearly_breakdown.append({
                'year': year,
                'property_value': round(property_value, 0),
                'cumulative_gain': round(cumulative_gain, 0)
            })
        
        final_value = property_price * ((1 + annual_growth_rate) ** years)
        total_gain = final_value - property_price
        
        return {
            'yearly_breakdown': yearly_breakdown,
            'final_value': round(final_value, 0),
            'total_gain': round(total_gain, 0),
            'annual_growth_rate': annual_growth_rate * 100,
            'years': years
        }
    
    def calculate_total_return_projection(self, property_price: float, annual_rent: float, 
                                        annual_expenses: float, down_payment: float,
                                        annual_growth_rate: float = 0.055, years: int = 10) -> Dict[str, Any]:
        """Calculate total investment returns including cash flow and capital gains"""
        
        # Calculate loan details
        loan_amount = property_price - down_payment
        monthly_payment = self._calculate_monthly_payment(
            loan_amount, self.current_interest_rate, self.default_loan_term
        )
        annual_loan_payment = monthly_payment * 12
        
        # Calculate net annual cash flow (INCLUDING loan payments for consistency)
        net_annual_cash_flow = annual_rent - annual_expenses - annual_loan_payment
        
        # Get capital gains forecast
        capital_forecast = self.calculate_capital_gains_forecast(property_price, annual_growth_rate, years)
        
        # Calculate cumulative cash flows and total returns
        total_cash_flow = 0
        rent_growth_rate = 0.025  # 2.5% annual rent inflation
        
        for year in range(1, years + 1):
            # Calculate rent with inflation for this year
            year_rent = annual_rent * ((1 + rent_growth_rate) ** (year - 1))
            # Calculate net cash flow for this year (rent - expenses - loan payment)
            year_net_cash_flow = year_rent - annual_expenses - annual_loan_payment
            total_cash_flow += year_net_cash_flow
        
        # Total return components
        total_capital_gains = capital_forecast['total_gain']
        total_return = total_cash_flow + total_capital_gains
        
        # Calculate annualized return
        if down_payment > 0:
            annualized_return = ((total_return / down_payment) ** (1/years)) - 1
        else:
            annualized_return = 0
        
        return {
            'total_cash_flow': round(total_cash_flow, 0),
            'total_capital_gains': round(total_capital_gains, 0),
            'total_return': round(total_return, 0),
            'annualized_return': annualized_return,
            'initial_investment': round(down_payment, 0),
            'years': years,
            'annual_growth_rate': annual_growth_rate * 100
        }
    
    def generate_investment_summary(self, metrics: Dict[str, Any], 
                                   capital_gains_forecast: Dict[str, Any] = None,
                                   total_return_projection: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate intelligent investment summary and recommendation"""
        
        # Extract key metrics
        gross_yield = metrics.get('gross_yield', 0)
        net_yield = metrics.get('net_yield', 0)
        cash_return = metrics.get('cash_return', 0)
        monthly_cashflow = metrics.get('monthly_cashflow', 0)
        investment_score = metrics.get('investment_score', 0)
        
        # Rental yield analysis
        rental_analysis = {
            'category': 'Poor',
            'description': '',
            'recommendation': '',
            'yield_rating': 0
        }
        
        if net_yield >= 6:
            rental_analysis = {
                'category': 'Excellent',
                'description': f'Outstanding rental yield of {net_yield:.1f}% - significantly above Australian average of 4-5%',
                'recommendation': 'Strong rental income makes this an excellent cash flow property',
                'yield_rating': 5
            }
        elif net_yield >= 5:
            rental_analysis = {
                'category': 'Very Good',
                'description': f'Strong rental yield of {net_yield:.1f}% - above Australian average',
                'recommendation': 'Good cash flow property with solid rental returns',
                'yield_rating': 4
            }
        elif net_yield >= 4:
            rental_analysis = {
                'category': 'Good',
                'description': f'Moderate rental yield of {net_yield:.1f}% - around Australian average',
                'recommendation': 'Reasonable rental returns, consider other factors',
                'yield_rating': 3
            }
        elif net_yield >= 2:
            rental_analysis = {
                'category': 'Fair',
                'description': f'Below-average rental yield of {net_yield:.1f}%',
                'recommendation': 'Low rental returns - capital growth potential is crucial',
                'yield_rating': 2
            }
        else:
            rental_analysis = {
                'category': 'Poor',
                'description': f'Very low rental yield of {net_yield:.1f}%',
                'recommendation': 'Poor for rental income - only consider if strong capital growth expected',
                'yield_rating': 1
            }
        
        # Cash flow analysis
        cashflow_analysis = {
            'status': 'Negative',
            'description': '',
            'impact': ''
        }
        
        if monthly_cashflow > 200:
            cashflow_analysis = {
                'status': 'Strongly Positive',
                'description': f'Excellent monthly cash flow of ${monthly_cashflow:,.0f}',
                'impact': 'Property pays for itself and generates surplus income'
            }
        elif monthly_cashflow > 0:
            cashflow_analysis = {
                'status': 'Positive',
                'description': f'Positive monthly cash flow of ${monthly_cashflow:,.0f}',
                'impact': 'Property is self-sustaining with some surplus'
            }
        elif monthly_cashflow > -200:
            cashflow_analysis = {
                'status': 'Slightly Negative',
                'description': f'Small monthly shortfall of ${abs(monthly_cashflow):,.0f}',
                'impact': 'Manageable out-of-pocket expenses'
            }
        else:
            cashflow_analysis = {
                'status': 'Negative',
                'description': f'Significant monthly shortfall of ${abs(monthly_cashflow):,.0f}',
                'impact': 'Substantial ongoing financial commitment required'
            }
        
        # Capital gains analysis (if provided)
        capital_analysis = None
        if capital_gains_forecast and total_return_projection:
            annual_growth = capital_gains_forecast.get('annual_growth_rate', 5.5)
            total_gain = capital_gains_forecast.get('total_gain', 0)
            annualized_return = total_return_projection.get('annualized_return', 0) * 100
            
            if annual_growth >= 7:
                capital_category = 'Excellent'
                capital_desc = f'Strong capital growth at {annual_growth:.1f}% annually'
            elif annual_growth >= 5:
                capital_category = 'Good'
                capital_desc = f'Solid capital growth at {annual_growth:.1f}% annually'
            elif annual_growth >= 3:
                capital_category = 'Moderate'
                capital_desc = f'Conservative capital growth at {annual_growth:.1f}% annually'
            else:
                capital_category = 'Low'
                capital_desc = f'Minimal capital growth at {annual_growth:.1f}% annually'
            
            capital_analysis = {
                'category': capital_category,
                'description': capital_desc,
                'total_gain': total_gain,
                'annualized_return': annualized_return,
                'projection_years': capital_gains_forecast.get('years', 10)
            }
        
        # Overall recommendation
        overall_recommendation = self._generate_overall_recommendation(
            rental_analysis, cashflow_analysis, capital_analysis, investment_score
        )
        
        return {
            'rental_analysis': rental_analysis,
            'cashflow_analysis': cashflow_analysis,
            'capital_analysis': capital_analysis,
            'overall_recommendation': overall_recommendation,
            'investment_score': investment_score
        }
    
    def _generate_overall_recommendation(self, rental_analysis: Dict, cashflow_analysis: Dict, 
                                       capital_analysis: Dict = None, investment_score: float = 0) -> Dict[str, str]:
        """Generate overall investment recommendation"""
        
        rental_rating = rental_analysis['yield_rating']
        is_positive_cashflow = 'Positive' in cashflow_analysis['status']
        
        # Base recommendation on rental yield only
        if rental_rating >= 4 and is_positive_cashflow:
            rental_only_verdict = "EXCELLENT for rental income strategy"
            rental_only_reason = "Strong yields with positive cash flow make this ideal for income-focused investors"
        elif rental_rating >= 3 and is_positive_cashflow:
            rental_only_verdict = "GOOD for rental income strategy"
            rental_only_reason = "Solid yields with positive cash flow provide reliable income"
        elif rental_rating >= 3:
            rental_only_verdict = "FAIR for rental income strategy"
            rental_only_reason = "Decent yields but negative cash flow requires ongoing funding"
        else:
            rental_only_verdict = "POOR for rental income strategy"
            rental_only_reason = "Low yields make this unsuitable for income-focused investing"
        
        # Combined recommendation (if capital gains data available)
        if capital_analysis:
            capital_category = capital_analysis['category']
            annualized_return = capital_analysis.get('annualized_return', 0)
            
            if annualized_return >= 12:
                combined_verdict = "EXCELLENT overall investment"
                combined_reason = "Strong combination of rental income and capital growth provides excellent total returns"
            elif annualized_return >= 8:
                combined_verdict = "VERY GOOD overall investment"
                combined_reason = "Good balance of income and growth makes this a solid investment choice"
            elif annualized_return >= 6:
                combined_verdict = "GOOD overall investment"
                combined_reason = "Reasonable total returns when combining rental income and capital appreciation"
            elif annualized_return >= 4:
                combined_verdict = "FAIR overall investment"
                combined_reason = "Modest total returns - consider if this meets your investment goals"
            else:
                combined_verdict = "POOR overall investment"
                combined_reason = "Low total returns make this unsuitable for most investment strategies"
        else:
            combined_verdict = "Capital gains analysis not available"
            combined_reason = "Unable to assess total return potential without capital growth projections"
        
        return {
            'rental_only_verdict': rental_only_verdict,
            'rental_only_reason': rental_only_reason,
            'combined_verdict': combined_verdict,
            'combined_reason': combined_reason
        }
    
    def generate_holding_period_recommendations(self, property_price: float, annual_rent: float,
                                               annual_expenses: float, down_payment: float,
                                               annual_growth_rate: float = 0.055) -> Dict[str, Any]:
        """Generate specific holding period recommendations with profit projections"""
        
        # Calculate loan details
        loan_amount = property_price - down_payment
        monthly_payment = self._calculate_monthly_payment(
            loan_amount, self.current_interest_rate, self.default_loan_term
        )
        annual_loan_payment = monthly_payment * 12
        
        # Calculate net annual cash flow (INCLUDING loan payments for consistency)
        net_annual_cash_flow = annual_rent - annual_expenses - annual_loan_payment
        rent_growth_rate = 0.025  # 2.5% annual rent inflation
        
        recommendations = []
        
        # Define holding periods to analyze
        holding_periods = [3, 5, 7, 10, 15, 20]
        
        for years in holding_periods:
            # Calculate capital gains
            future_value = property_price * ((1 + annual_growth_rate) ** years)
            capital_gain = future_value - property_price
            
            # Calculate cumulative cash flow with rent growth (including loan payments)
            total_cash_flow = 0
            for year in range(1, years + 1):
                year_rent = annual_rent * ((1 + rent_growth_rate) ** (year - 1))
                yearly_cash = year_rent - annual_expenses - annual_loan_payment
                total_cash_flow += yearly_cash
            
            # Total profit
            total_profit = capital_gain + total_cash_flow
            
            # Return on investment
            roi_percentage = (total_profit / down_payment) * 100 if down_payment > 0 else 0
            annualized_roi = ((total_profit / down_payment) ** (1/years) - 1) * 100 if down_payment > 0 else 0
            
            # Determine recommendation category
            if annualized_roi >= 15:
                category = "Excellent"
                recommendation = f"Outstanding returns - strongly consider holding for {years} years"
            elif annualized_roi >= 12:
                category = "Very Good"
                recommendation = f"Strong returns - excellent holding period of {years} years"
            elif annualized_roi >= 8:
                category = "Good"
                recommendation = f"Solid returns - good {years}-year investment strategy"
            elif annualized_roi >= 5:
                category = "Fair"
                recommendation = f"Moderate returns over {years} years - consider your alternatives"
            else:
                category = "Poor"
                recommendation = f"Low returns over {years} years - not recommended"
            
            recommendations.append({
                'years': years,
                'future_property_value': round(future_value, 0),
                'capital_gain': round(capital_gain, 0),
                'total_cash_flow': round(total_cash_flow, 0),
                'total_profit': round(total_profit, 0),
                'roi_percentage': round(roi_percentage, 1),
                'annualized_roi': round(annualized_roi, 1),
                'category': category,
                'recommendation': recommendation
            })
        
        # Find optimal holding periods
        best_short_term = next((r for r in recommendations if r['years'] == 3), None)
        best_medium_term = next((r for r in recommendations if r['years'] == 5), None) 
        best_long_term = next((r for r in recommendations if r['years'] == 10), None)
        
        # Generate strategic recommendations
        strategic_advice = []
        
        if best_short_term and best_short_term['annualized_roi'] >= 8:
            strategic_advice.append({
                'strategy': 'Short-term Strategy',
                'timeframe': f"{best_short_term['years']} years",
                'profit': best_short_term['total_profit'],
                'roi': best_short_term['annualized_roi'],
                'description': f"Quick returns for {best_short_term['annualized_roi']:.1f}% annual returns"
            })
        
        if best_medium_term:
            strategic_advice.append({
                'strategy': 'Medium-term Investment',
                'timeframe': f"{best_medium_term['years']} years",
                'profit': best_medium_term['total_profit'],
                'roi': best_medium_term['annualized_roi'],
                'description': f"Balanced approach for {best_medium_term['annualized_roi']:.1f}% annual returns"
            })
        
        if best_long_term:
            strategic_advice.append({
                'strategy': 'Long-term Wealth Building',
                'timeframe': f"{best_long_term['years']} years",
                'profit': best_long_term['total_profit'],
                'roi': best_long_term['annualized_roi'],
                'description': f"Maximum wealth accumulation with {best_long_term['annualized_roi']:.1f}% annual returns"
            })
        
        # Find break-even point (when total profit becomes positive)
        profit_breakeven_years = None
        cash_flow_breakeven_years = None
        
        for rec in recommendations:
            # Profit break-even (includes capital gains)
            if rec['total_profit'] > 0 and profit_breakeven_years is None:
                profit_breakeven_years = rec['years']
            
            # Cash flow break-even (operational only - when cumulative cash flow > 0)
            if rec['total_cash_flow'] > 0 and cash_flow_breakeven_years is None:
                cash_flow_breakeven_years = rec['years']
        
        return {
            'all_periods': recommendations,
            'strategic_advice': strategic_advice,
            'break_even_years': profit_breakeven_years,  # Total profit break-even
            'cash_flow_breakeven_years': cash_flow_breakeven_years,  # Cash flow break-even
            'best_short_term': best_short_term,
            'best_medium_term': best_medium_term,
            'best_long_term': best_long_term,
            'initial_investment': round(down_payment, 0),
            'annual_growth_rate': annual_growth_rate * 100
        }
