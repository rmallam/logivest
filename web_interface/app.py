"""
Real Estate Investment Analyzer Web Interface

Flask-based web application for user-friendly real estate analysis.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import sys
import os

# Add the parent directory to the path so we can import our MCP server modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools.property_analysis import PropertyAnalyzer
from mcp_server.tools.financial_calc import FinancialCalculator
from mcp_server.tools.market_research import MarketResearcher
from mcp_server.tools.gemini_analyzer import GeminiPropertyAnalyzer
from mcp_server.data.api_clients import RealEstateDataClient

app = Flask(__name__)
app.secret_key = 'real-estate-analyzer-secret-key'

# Initialize components
property_analyzer = PropertyAnalyzer()
financial_calculator = FinancialCalculator()
market_researcher = MarketResearcher()
gemini_analyzer = GeminiPropertyAnalyzer()
data_client = RealEstateDataClient()


@app.route('/')
def index():
    """Main page with search form"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_property():
    """Analyze a specific property using Gemini AI"""
    try:
        address = request.form.get('address', '').strip()
        budget = request.form.get('budget', type=float)
        
        if not address:
            return render_template('index.html', error="Please enter a property address")
        
        # Use only Gemini AI analysis for comprehensive insights
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get comprehensive Gemini AI insights with all property details
            gemini_insights = loop.run_until_complete(gemini_analyzer.analyze_property(address, budget))
            
            if not gemini_insights:
                return render_template('index.html', error=f"Could not analyze property: {address}")
            
            # Use Gemini insights as the primary analysis
            return render_template('analysis.html', 
                                 address=address,
                                 budget=budget,
                                 analysis=None,  # No longer using old analyzer
                                 gemini_insights=gemini_insights)
        finally:
            loop.close()
            
    except Exception as e:
        return render_template('index.html', error=f"Error analyzing property: {str(e)}")


@app.route('/search', methods=['POST'])
def search_properties():
    """Search for investment opportunities"""
    try:
        location = request.form.get('location', '').strip()
        max_budget = request.form.get('max_budget', type=float)
        min_yield = request.form.get('min_yield', 4.0, type=float)
        property_type = request.form.get('property_type', 'any')
        
        if not location or not max_budget:
            return render_template('index.html', error="Please enter both location and budget")
        
        # Search for properties
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            properties = loop.run_until_complete(
                data_client.search_properties(location, max_budget, property_type)
            )
            
            # Analyze each property
            opportunities = []
            for prop in properties:
                analysis = loop.run_until_complete(
                    property_analyzer.analyze_property(prop, max_budget)
                )
                if analysis['gross_yield'] >= min_yield:
                    opportunities.append(analysis)
            
            # Sort by investment score
            opportunities.sort(key=lambda x: x['investment_score'], reverse=True)
            
            return render_template('search_results.html',
                                 location=location,
                                 max_budget=max_budget,
                                 min_yield=min_yield,
                                 property_type=property_type,
                                 opportunities=opportunities)
        finally:
            loop.close()
            
    except Exception as e:
        return render_template('index.html', error=f"Error searching properties: {str(e)}")


@app.route('/market/<location>')
def market_analysis(location):
    """Get market analysis for a location"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            market_data = loop.run_until_complete(
                market_researcher.analyze_market(location)
            )
            
            return render_template('market_analysis.html',
                                 location=location,
                                 market_data=market_data)
        finally:
            loop.close()
            
    except Exception as e:
        return render_template('index.html', error=f"Error analyzing market: {str(e)}")


@app.route('/calculator')
def calculator():
    """Rental yield calculator page"""
    return render_template('calculator.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate rental yield and returns"""
    try:
        # Basic property data
        property_price = request.form.get('property_price', type=float)
        weekly_rent = request.form.get('weekly_rent', type=float)
        
        # Loan details
        down_payment_percent = request.form.get('down_payment_percent', 20, type=float)
        interest_rate = request.form.get('interest_rate', type=float)
        loan_term = request.form.get('loan_term', 30, type=int)
        
        # Additional costs
        agent_commission = request.form.get('agent_commission', 5.0, type=float)
        other_costs = request.form.get('other_costs', 0, type=float)
        
        # Operating expenses
        property_management = request.form.get('property_management', 8.0, type=float)
        maintenance_repairs = request.form.get('maintenance_repairs', 0, type=float)
        insurance_rates = request.form.get('insurance_rates', 0, type=float)
        vacancy_allowance = request.form.get('vacancy_allowance', 2.0, type=float)
        other_expenses = request.form.get('other_expenses', 0, type=float)
        
        # Capital gains forecast
        annual_growth_rate = request.form.get('annual_growth_rate', 5.5, type=float)
        projection_years = request.form.get('projection_years', 10, type=int)
        
        if not property_price or not weekly_rent or not interest_rate:
            return render_template('calculator.html', 
                                   error="Please enter property price, weekly rent, and interest rate")
        
        # Convert weekly rent to monthly
        monthly_rent = weekly_rent * 52 / 12
        annual_rent = weekly_rent * 52
        
        # Calculate total annual expenses
        management_cost = annual_rent * (property_management / 100)
        vacancy_cost = annual_rent * (vacancy_allowance / 100)
        total_annual_expenses = (management_cost + maintenance_repairs + 
                               insurance_rates + vacancy_cost + other_expenses)
        
        # Calculate total upfront costs
        down_payment = property_price * (down_payment_percent / 100)
        commission_cost = property_price * (agent_commission / 100)
        total_upfront_costs = down_payment + commission_cost + other_costs
        
        # Update financial calculator with user's interest rate
        financial_calculator.current_interest_rate = interest_rate / 100
        financial_calculator.default_loan_term = loan_term
        
        # Calculate metrics with enhanced data
        metrics = financial_calculator.calculate_investment_metrics(
            property_price, monthly_rent, total_annual_expenses, down_payment_percent
        )
        
        # Add additional data to metrics for template
        metrics['total_annual_expenses'] = total_annual_expenses
        metrics['management_cost'] = management_cost
        metrics['vacancy_cost'] = vacancy_cost
        metrics['maintenance_repairs'] = maintenance_repairs
        metrics['insurance_rates'] = insurance_rates
        metrics['other_expenses'] = other_expenses
        metrics['annual_growth_rate'] = annual_growth_rate
        metrics['projection_years'] = projection_years
        
        # Calculate capital gains forecast
        capital_gains_forecast = financial_calculator.calculate_capital_gains_forecast(
            property_price, annual_growth_rate / 100, projection_years
        )
        
        # Calculate total return projection
        total_return_projection = financial_calculator.calculate_total_return_projection(
            property_price, monthly_rent * 12, total_annual_expenses, 
            down_payment, annual_growth_rate / 100, projection_years
        )
        
        # Generate intelligent investment summary
        investment_summary = financial_calculator.generate_investment_summary(
            metrics, capital_gains_forecast, total_return_projection
        )
        
        # Generate holding period recommendations
        holding_recommendations = financial_calculator.generate_holding_period_recommendations(
            property_price, monthly_rent * 12, total_annual_expenses, 
            down_payment, annual_growth_rate / 100
        )
        
        # Add additional details to metrics for display
        metrics['weekly_rent'] = weekly_rent
        metrics['agent_commission'] = commission_cost
        metrics['other_upfront_costs'] = other_costs
        metrics['total_upfront_costs'] = total_upfront_costs
        metrics['management_cost'] = management_cost
        metrics['vacancy_cost'] = vacancy_cost
        metrics['maintenance_repairs'] = maintenance_repairs
        metrics['insurance_rates'] = insurance_rates
        metrics['other_expenses'] = other_expenses
        metrics['interest_rate'] = interest_rate
        metrics['loan_term'] = loan_term
        metrics['annual_growth_rate'] = annual_growth_rate
        metrics['projection_years'] = projection_years
        metrics['capital_gains_forecast'] = capital_gains_forecast
        metrics['total_return_projection'] = total_return_projection
        metrics['investment_summary'] = investment_summary
        metrics['holding_recommendations'] = holding_recommendations
        
        # Debug: Print metrics to see what's available
        print("=== METRICS DEBUG ===")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        print("=== END DEBUG ===")
        
        return render_template('calculation_results.html',
                             property_price=property_price,
                             weekly_rent=weekly_rent,
                             monthly_rent=monthly_rent,
                             annual_expenses=total_annual_expenses,
                             down_payment_percent=down_payment_percent,
                             metrics=metrics,
                             # Additional data for cash flow breakdown
                             management_cost=management_cost,
                             vacancy_cost=vacancy_cost,
                             maintenance_repairs=maintenance_repairs,
                             insurance_rates=insurance_rates,
                             other_expenses=other_expenses)
        
    except Exception as e:
        import traceback
        print(f"Error in calculate route: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return render_template('calculator.html', error=f"Error calculating returns: {str(e)}")


@app.route('/api/property/<path:address>')
def api_property_data(address):
    """API endpoint for property data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            property_data = loop.run_until_complete(data_client.get_property_data(address))
            
            if property_data:
                analysis = loop.run_until_complete(
                    property_analyzer.analyze_property(property_data)
                )
                return jsonify({
                    'success': True,
                    'property_data': property_data,
                    'analysis': analysis
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Property not found'
                })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/market/<location>')
def api_market_data(location):
    """API endpoint for market data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            market_data = loop.run_until_complete(
                market_researcher.analyze_market(location)
            )
            return jsonify({
                'success': True,
                'market_data': market_data
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    # Use PORT environment variable for Render deployment, fallback to 5001 for local
    port = int(os.getenv('PORT', os.getenv('WEB_INTERFACE_PORT', 5001)))
    print("🏠 Logivest - Real Estate Investment Analyzer Web Interface")
    print(f"🌐 Starting web server at http://localhost:{port}")
    print("📊 Access the application to analyze properties and markets")
    
    app.run(debug=False, host='0.0.0.0', port=port)
