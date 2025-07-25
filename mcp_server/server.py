"""
Real Estate Investment Analyzer MCP Server

A Model Context Protocol server for comprehensive real estate investment analysis.
Provides tools for property valuation, rental yield calculation, and investment recommendations.
"""

from typing import Any, Dict, List, Optional
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool
import json

# Configure logging to stderr to avoid stdout pollution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("real-estate-analyzer")

# Import our tool modules
from mcp_server.tools.property_analysis import PropertyAnalyzer
from .tools.financial_calc import FinancialCalculator
from .tools.market_research import MarketResearcher
from .tools.gemini_analyzer import GeminiPropertyAnalyzer
from .data.api_clients import PropertyAPIClient

# Initialize components
property_analyzer = PropertyAnalyzer()
financial_calculator = FinancialCalculator()
market_researcher = MarketResearcher()
api_client = PropertyAPIClient()
gemini_analyzer = GeminiPropertyAnalyzer()


@mcp.tool()
async def get_property_analysis(
    address: str,
    budget: float = None
) -> str:
    """Get comprehensive property analysis including valuation and investment metrics.
    
    Args:
        address: Property address (e.g., "123 Main St, Austin, TX")
        budget: Maximum budget for the property (optional)
    """
    try:
        logger.info(f"Analyzing property: {address}")
        
        # Get property data
        property_data = await api_client.get_property_data(address)
        
        if not property_data:
            return f"Could not find property data for address: {address}"
        
        # Perform analysis
        analysis = await property_analyzer.analyze_property(property_data, budget)
        
        # Format results
        result = f"""
Property Analysis for {address}

📍 Property Details:
- Address: {analysis['address']}
- Property Type: {analysis['property_type']}
- Bedrooms: {analysis['bedrooms']}
- Bathrooms: {analysis['bathrooms']}
- Square Feet: {analysis['sqft']:,}

💰 Financial Analysis:
- Estimated Value: ${analysis['estimated_value']:,.2f}
- Estimated Monthly Rent: ${analysis['estimated_rent']:,.2f}
- Gross Rental Yield: {analysis['gross_yield']:.2f}%
- Net Rental Yield: {analysis['net_yield']:.2f}%
- Cap Rate: {analysis['cap_rate']:.2f}%

📊 Investment Metrics:
- Cash-on-Cash Return: {analysis['cash_return']:.2f}%
- Break-even Time: {analysis['breakeven_months']} months
- Annual Cash Flow: ${analysis['annual_cashflow']:,.2f}

🎯 Investment Score: {analysis['investment_score']}/10
{analysis['recommendation']}
"""
        
        if budget and analysis['estimated_value'] > budget:
            result += f"\n⚠️  Property price (${analysis['estimated_value']:,.2f}) exceeds budget (${budget:,.2f})"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_property_analysis: {str(e)}")
        return f"❌ Error analyzing property: {str(e)}"


@mcp.tool()
async def get_comprehensive_property_insights(
    address: str,
    budget: float = None
) -> str:
    """Get comprehensive property insights using AI analysis including market context, location analysis, and investment recommendations.
    
    Args:
        address: Property address (e.g., "55 Grassbird Drive, Point Cook VIC")
        budget: Maximum budget for the property (optional)
    """
    try:
        logger.info(f"🤖 Getting comprehensive insights for: {address}")
        
        # Get AI-powered property insights
        insights = gemini_analyzer.analyze_property(address, budget)
        
        # Format comprehensive response
        response = f"""🏠 **COMPREHENSIVE PROPERTY INSIGHTS: {address}**

📋 **PROPERTY DETAILS**
• Type: {insights.property_type}
• Bedrooms: {insights.bedrooms}
• Bathrooms: {insights.bathrooms}
• Land Size: {insights.land_size}
• Estimated Value: ${insights.estimated_value.get('estimate', 0):,.0f}

📊 **MARKET OVERVIEW**
• Local Median: ${insights.market_overview.get('median_price', 0):,.0f}
• 12-Month Growth: {insights.market_overview.get('growth_12m', 0):.1f}%
• Days on Market: {insights.market_overview.get('days_on_market', 0)} days
• Rental Yield: {insights.market_overview.get('rental_yield', 0):.1f}%

🎯 **LOCATION ANALYSIS**
• Family Friendly: {'✅ Yes' if insights.location_analysis.get('family_friendly') else '❌ No'}
• Transport Score: {insights.location_analysis.get('transport_score', 0)}/10
• Amenities Score: {insights.location_analysis.get('amenities_score', 0)}/10
• School Zone: {insights.location_analysis.get('school_zone', 'Unknown')}

💰 **INVESTMENT RECOMMENDATION**
• Overall Verdict: {insights.investment_recommendation.get('verdict', 'Unknown')}
• Growth Potential: {insights.investment_recommendation.get('growth_potential', 'Unknown')}
• Confidence Level: {insights.investment_recommendation.get('confidence', 'Unknown')}

✅ **KEY ADVANTAGES**
{chr(10).join(f'• {pro}' for pro in insights.pros[:5]) if insights.pros else '• Detailed analysis in progress'}

⚠️ **IMPORTANT CONSIDERATIONS**
{chr(10).join(f'• {consideration}' for consideration in insights.considerations[:5]) if insights.considerations else '• Detailed analysis in progress'}

🔍 **DETAILED ANALYSIS**
{insights.raw_analysis[:800]}{'...' if len(insights.raw_analysis) > 800 else ''}

💡 **NEXT STEPS**
• Arrange building and pest inspection
• Review comparable sales data
• Consult with local real estate agents
• Assess your financial capacity for ongoing costs
• Visit property at different times of day

For complete financial analysis including loan scenarios and cash flow projections, use the calculate_rental_yield tool.
"""
        
        logger.info(f"✅ Generated comprehensive insights for: {address}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting comprehensive insights: {str(e)}")
        return f"❌ Error getting insights: {str(e)}. Note: Comprehensive insights require Gemini API configuration."


@mcp.tool()
async def calculate_rental_yield(
    property_price: float,
    monthly_rent: float,
    annual_expenses: float = 0,
    down_payment_percent: float = 20
) -> str:
    """Calculate rental yield and investment returns for a property.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Expected monthly rental income
        annual_expenses: Annual property expenses (taxes, insurance, maintenance)
        down_payment_percent: Down payment percentage (default 20%)
    """
    try:
        # Calculate financial metrics
        metrics = financial_calculator.calculate_investment_metrics(
            property_price, monthly_rent, annual_expenses, down_payment_percent
        )
        
        return f"""
Rental Yield Analysis

💵 Investment Summary:
- Property Price: ${property_price:,.2f}
- Monthly Rent: ${monthly_rent:,.2f}
- Annual Rental Income: ${monthly_rent * 12:,.2f}
- Annual Expenses: ${annual_expenses:,.2f}

📈 Yield Calculations:
- Gross Rental Yield: {metrics['gross_yield']:.2f}%
- Net Rental Yield: {metrics['net_yield']:.2f}%
- Cap Rate: {metrics['cap_rate']:.2f}%

💰 Financing Details:
- Down Payment ({down_payment_percent}%): ${metrics['down_payment']:,.2f}
- Loan Amount: ${metrics['loan_amount']:,.2f}
- Monthly Mortgage Payment: ${metrics['monthly_payment']:,.2f}

📊 Returns Analysis:
- Cash-on-Cash Return: {metrics['cash_return']:.2f}%
- Monthly Cash Flow: ${metrics['monthly_cashflow']:,.2f}
- Annual Cash Flow: ${metrics['annual_cashflow']:,.2f}
- Break-even Period: {metrics['breakeven_months']} months

{metrics['analysis']}
"""
        
    except Exception as e:
        logger.error(f"Error calculating rental yield: {str(e)}")
        return f"Error calculating rental yield: {str(e)}"


@mcp.tool()
async def find_investment_opportunities(
    location: str,
    max_budget: float,
    min_yield: float = 6.0,
    property_type: str = "any"
) -> str:
    """Find investment properties based on budget and yield requirements.
    
    Args:
        location: Target location (city, state, or zip code)
        max_budget: Maximum property budget
        min_yield: Minimum required rental yield percentage
        property_type: Property type filter (house, condo, townhouse, any)
    """
    try:
        logger.info(f"Searching for opportunities in {location} with budget ${max_budget:,.2f}")
        
        # Get available properties
        properties = await api_client.search_properties(
            location, max_budget, property_type
        )
        
        if not properties:
            return f"No properties found in {location} within budget of ${max_budget:,.2f}"
        
        # Analyze each property
        opportunities = []
        for prop in properties:
            analysis = await property_analyzer.analyze_property(prop, max_budget)
            if analysis['gross_yield'] >= min_yield:
                opportunities.append(analysis)
        
        # Sort by investment score
        opportunities.sort(key=lambda x: x['investment_score'], reverse=True)
        
        if not opportunities:
            return f"No properties found meeting {min_yield}% yield requirement in {location}"
        
        # Format results
        result = f"""
Investment Opportunities in {location}
Budget: Up to ${max_budget:,.2f} | Min Yield: {min_yield}%

Found {len(opportunities)} qualifying properties:

"""
        
        for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
            result += f"""
{i}. {opp['address']}
   💰 Price: ${opp['estimated_value']:,.2f}
   🏠 {opp['bedrooms']}BR/{opp['bathrooms']}BA, {opp['sqft']:,} sqft
   📊 Gross Yield: {opp['gross_yield']:.2f}%
   💵 Monthly Rent: ${opp['estimated_rent']:,.2f}
   ⭐ Score: {opp['investment_score']}/10
   
"""
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding opportunities: {str(e)}")
        return f"Error finding investment opportunities: {str(e)}"


@mcp.tool()
async def get_market_analysis(
    location: str,
    property_type: str = "house"
) -> str:
    """Get comprehensive market analysis for a location.
    
    Args:
        location: Target location (city, state, or zip code)
        property_type: Property type to analyze (house, condo, townhouse)
    """
    try:
        logger.info(f"Analyzing market in {location}")
        
        # Get market data
        market_data = await market_researcher.analyze_market(location, property_type)
        
        return f"""
Market Analysis for {location}

📈 Market Overview:
- Median Home Price: ${market_data['median_price']:,.2f}
- Price Change (YoY): {market_data['price_change_yoy']:+.1f}%
- Average Days on Market: {market_data['days_on_market']} days
- Inventory Level: {market_data['inventory_level']}

🏘️ Rental Market:
- Median Rent: ${market_data['median_rent']:,.2f}
- Rental Yield Range: {market_data['yield_range']}
- Vacancy Rate: {market_data['vacancy_rate']:.1f}%
- Rent Growth (YoY): {market_data['rent_growth']:+.1f}%

📊 Investment Climate:
- Market Heat Index: {market_data['market_heat']}/10
- Investment Grade: {market_data['investment_grade']}
- Risk Level: {market_data['risk_level']}

🎯 Key Insights:
{market_data['insights']}

💡 Investment Recommendation:
{market_data['recommendation']}
"""
        
    except Exception as e:
        logger.error(f"Error analyzing market: {str(e)}")
        return f"Error analyzing market: {str(e)}"


@mcp.tool()
async def compare_loan_scenarios(
    property_price: float,
    monthly_rent: float,
    scenarios: str = "20,25,30"
) -> str:
    """Compare different loan scenarios (down payment percentages).
    
    Args:
        property_price: Property purchase price
        monthly_rent: Expected monthly rental income
        scenarios: Comma-separated down payment percentages (e.g., "20,25,30")
    """
    try:
        down_payments = [float(x.strip()) for x in scenarios.split(',')]
        
        result = f"""
Loan Scenario Comparison
Property Price: ${property_price:,.2f}
Monthly Rent: ${monthly_rent:,.2f}

"""
        
        for dp in down_payments:
            metrics = financial_calculator.calculate_investment_metrics(
                property_price, monthly_rent, 0, dp
            )
            
            result += f"""
📊 {dp}% Down Payment Scenario:
   💰 Down Payment: ${metrics['down_payment']:,.2f}
   🏦 Loan Amount: ${metrics['loan_amount']:,.2f}
   💳 Monthly Payment: ${metrics['monthly_payment']:,.2f}
   📈 Cash-on-Cash Return: {metrics['cash_return']:.2f}%
   💵 Monthly Cash Flow: ${metrics['monthly_cashflow']:,.2f}
   
"""
        
        return result
        
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        return f"Error comparing loan scenarios: {str(e)}"


def main():
    """Run the MCP server."""
    logger.info("Starting Real Estate Investment Analyzer MCP Server...")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
