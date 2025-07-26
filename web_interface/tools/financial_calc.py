"""
Financial Calculator Module for Web Interface
Standalone version without MCP dependencies
"""
import logging

logger = logging.getLogger(__name__)

class FinancialCalculator:
    """
    Financial calculation tools for real estate investment analysis
    """
    
    def calculate_rental_yield(self, property_price, annual_rent, expenses=0):
        """
        Calculate rental yield
        
        Args:
            property_price: Property purchase price
            annual_rent: Annual rental income
            expenses: Annual expenses (optional)
            
        Returns:
            Dictionary with yield calculations
        """
        try:
            if property_price <= 0:
                return {'error': 'Property price must be greater than 0'}
                
            gross_yield = (annual_rent / property_price) * 100
            net_yield = ((annual_rent - expenses) / property_price) * 100
            
            return {
                'gross_yield': round(gross_yield, 2),
                'net_yield': round(net_yield, 2),
                'annual_rent': annual_rent,
                'annual_expenses': expenses,
                'property_price': property_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating rental yield: {e}")
            return {'error': str(e)}
    
    def calculate_mortgage_payments(self, loan_amount, interest_rate, loan_term_years):
        """
        Calculate mortgage payment details
        
        Args:
            loan_amount: Principal loan amount
            interest_rate: Annual interest rate (as percentage)
            loan_term_years: Loan term in years
            
        Returns:
            Dictionary with payment calculations
        """
        try:
            if loan_amount <= 0 or interest_rate < 0 or loan_term_years <= 0:
                return {'error': 'Invalid input values'}
                
            monthly_rate = (interest_rate / 100) / 12
            num_payments = loan_term_years * 12
            
            if monthly_rate == 0:
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            total_payment = monthly_payment * num_payments
            total_interest = total_payment - loan_amount
            
            return {
                'monthly_payment': round(monthly_payment, 2),
                'total_payment': round(total_payment, 2),
                'total_interest': round(total_interest, 2),
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'loan_term_years': loan_term_years
            }
            
        except Exception as e:
            logger.error(f"Error calculating mortgage payments: {e}")
            return {'error': str(e)}
    
    def calculate_cash_flow(self, monthly_rent, monthly_mortgage, monthly_expenses=0):
        """
        Calculate monthly cash flow
        
        Args:
            monthly_rent: Monthly rental income
            monthly_mortgage: Monthly mortgage payment
            monthly_expenses: Monthly expenses (taxes, insurance, etc.)
            
        Returns:
            Dictionary with cash flow analysis
        """
        try:
            net_cash_flow = monthly_rent - monthly_mortgage - monthly_expenses
            annual_cash_flow = net_cash_flow * 12
            
            return {
                'monthly_cash_flow': round(net_cash_flow, 2),
                'annual_cash_flow': round(annual_cash_flow, 2),
                'monthly_rent': monthly_rent,
                'monthly_mortgage': monthly_mortgage,
                'monthly_expenses': monthly_expenses,
                'cash_flow_positive': net_cash_flow > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating cash flow: {e}")
            return {'error': str(e)}
    
    def calculate_roi(self, annual_cash_flow, initial_investment):
        """
        Calculate return on investment
        
        Args:
            annual_cash_flow: Annual cash flow
            initial_investment: Initial investment amount
            
        Returns:
            Dictionary with ROI calculations
        """
        try:
            if initial_investment <= 0:
                return {'error': 'Initial investment must be greater than 0'}
                
            roi_percentage = (annual_cash_flow / initial_investment) * 100
            
            return {
                'roi_percentage': round(roi_percentage, 2),
                'annual_cash_flow': annual_cash_flow,
                'initial_investment': initial_investment,
                'payback_years': round(initial_investment / max(annual_cash_flow, 1), 1) if annual_cash_flow > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
            return {'error': str(e)}
