#!/usr/bin/env python3

import os
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PropertyInsight:
    """Structured property insight data"""
    address: str
    property_type: str
    bedrooms: int
    bathrooms: int
    land_size: str
    estimated_value: Dict[str, Any]
    market_overview: Dict[str, Any]
    location_analysis: Dict[str, Any]
    investment_recommendation: Dict[str, Any]
    key_features: list
    pros: list
    considerations: list
    raw_analysis: str

class GeminiPropertyAnalyzer:
    """Gemini AI integration for comprehensive property analysis"""
    
    def __init__(self):
        """Initialize the Gemini Property Analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Try to get API key from multiple sources (environment variable or secret file)
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            # Try to read from secret file (for Render deployment)
            try:
                key_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gemini_api_key.txt')
                if os.path.exists(key_file_path):
                    with open(key_file_path, 'r') as f:
                        content = f.read().strip()
                        # Skip comment lines and get the actual key
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                api_key = line
                                break
            except Exception as e:
                self.logger.warning(f"Could not read API key from file: {e}")
        
        if api_key and api_key != 'your-actual-gemini-api-key-here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.has_api_key = True
        else:
            self.model = None
            self.has_api_key = False
            self.logger.warning("Gemini API key not found. AI analysis will be unavailable.")
    
    def analyze_property(self, address: str, budget: float = None) -> PropertyInsight:
        """Get comprehensive property analysis from Gemini AI"""
        
        if not self.model:
            return self._get_fallback_analysis(address, budget)
        
        try:
            # Construct detailed prompt for property analysis
            prompt = self._build_analysis_prompt(address, budget)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Parse the response into structured data
            insight = self._parse_gemini_response(address, analysis_text, budget)
            
            logger.info(f"Successfully analyzed property: {address}")
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing property with Gemini: {str(e)}")
            return self._get_fallback_analysis(address, budget)
    
    def _build_analysis_prompt(self, address: str, budget: float = None) -> str:
        """Build comprehensive prompt for Gemini property analysis"""
        
        budget_context = f" with a budget of ${budget:,.0f}" if budget else ""
        
        prompt = f"""
        Analyze the property at {address}{budget_context} and provide a comprehensive investment analysis.

        Please structure your response to include:

        1. PROPERTY DETAILS:
        - Address verification
        - Property type (house/apartment/townhouse)
        - Bedrooms, bathrooms, parking
        - Land size
        - Key features and recent sale history
        - Current estimated value range

        2. MARKET OVERVIEW:
        - Local suburb median prices
        - Recent price growth trends (12 months, 5 years)
        - Days on market averages
        - Market conditions (buyer's/seller's market)
        - Rental yields in the area

        3. LOCATION ANALYSIS:
        - Demographics and lifestyle
        - Schools and education options
        - Transport and accessibility
        - Shopping and amenities
        - Future development plans

        4. INVESTMENT ASSESSMENT:
        - Capital growth potential
        - Rental demand and yields
        - Property condition considerations
        - Comparable sales analysis

        5. RECOMMENDATION:
        - Overall investment verdict
        - Key advantages for this property
        - Important considerations or risks
        - Action items before purchasing

        Please provide specific data where possible and be honest about both positives and negatives.
        Focus on Australian property market context and regulations.
        """
        
        return prompt
    
    def _parse_gemini_response(self, address: str, response_text: str, budget: float) -> PropertyInsight:
        """Parse Gemini response into structured PropertyInsight object"""
        
        # This is a simplified parser - in production you'd want more sophisticated parsing
        # For now, we'll extract key information and structure it
        
        # Default values
        insight_data = {
            'address': address,
            'property_type': 'Unknown',
            'bedrooms': 0,
            'bathrooms': 0,
            'land_size': 'Unknown',
            'estimated_value': {'min': 0, 'max': 0, 'estimate': 0},
            'market_overview': {
                'median_price': 0,
                'growth_12m': 0,
                'days_on_market': 0,
                'rental_yield': 0
            },
            'location_analysis': {
                'family_friendly': True,
                'transport_score': 7,
                'amenities_score': 7,
                'school_zone': 'Good'
            },
            'investment_recommendation': {
                'verdict': 'Neutral',
                'confidence': 'Medium',
                'growth_potential': 'Moderate'
            },
            'key_features': [],
            'pros': [],
            'considerations': [],
            'raw_analysis': response_text
        }
        
        # Simple text parsing to extract key information
        lines = response_text.lower()
        
        # Extract bedrooms
        if 'bedroom' in lines:
            import re
            bed_match = re.search(r'(\d+)\s*bedroom', lines)
            if bed_match:
                insight_data['bedrooms'] = int(bed_match.group(1))
        
        # Extract bathrooms
        if 'bathroom' in lines:
            bath_match = re.search(r'(\d+)\s*bathroom', lines)
            if bath_match:
                insight_data['bathrooms'] = int(bath_match.group(1))
        
        # Extract property type
        if 'house' in lines:
            insight_data['property_type'] = 'House'
        elif 'apartment' in lines or 'unit' in lines:
            insight_data['property_type'] = 'Apartment'
        elif 'townhouse' in lines:
            insight_data['property_type'] = 'Townhouse'
        
        # Extract investment verdict from text
        if 'excellent' in lines or 'outstanding' in lines:
            insight_data['investment_recommendation']['verdict'] = 'Excellent'
        elif 'good' in lines and 'buy' in lines:
            insight_data['investment_recommendation']['verdict'] = 'Good'
        elif 'poor' in lines or 'avoid' in lines:
            insight_data['investment_recommendation']['verdict'] = 'Poor'
        
        return PropertyInsight(**insight_data)
    
    def _get_fallback_analysis(self, address: str, budget: float) -> PropertyInsight:
        """Provide fallback analysis when Gemini is unavailable"""
        
        return PropertyInsight(
            address=address,
            property_type='Unknown',
            bedrooms=0,
            bathrooms=0,
            land_size='Unknown',
            estimated_value={'min': 0, 'max': 0, 'estimate': budget or 0},
            market_overview={
                'median_price': 0,
                'growth_12m': 0,
                'days_on_market': 45,
                'rental_yield': 4.0
            },
            location_analysis={
                'family_friendly': True,
                'transport_score': 7,
                'amenities_score': 7,
                'school_zone': 'Unknown'
            },
            investment_recommendation={
                'verdict': 'Analysis Unavailable',
                'confidence': 'Low',
                'growth_potential': 'Unknown'
            },
            key_features=['Gemini API not available'],
            pros=['Professional analysis requires Gemini API key'],
            considerations=['Please configure Gemini API for detailed insights'],
            raw_analysis='Gemini AI analysis is not available. Please provide a valid API key for comprehensive property insights.'
        )

class RentToEMIAnalyzer:
    """Analyze rent-to-EMI ratios for investment properties"""
    
    @staticmethod
    def calculate_rent_to_emi_ratio(weekly_rent: float, monthly_emi: float) -> Dict[str, Any]:
        """Calculate comprehensive rent-to-EMI analysis"""
        
        monthly_rent = weekly_rent * 52 / 12
        rent_to_emi_ratio = (monthly_rent / monthly_emi) * 100 if monthly_emi > 0 else 0
        
        # Determine ratio category
        if rent_to_emi_ratio >= 100:
            category = "Excellent"
            description = "Rent fully covers mortgage payments"
            color = "success"
        elif rent_to_emi_ratio >= 80:
            category = "Very Good"
            description = "Rent covers most mortgage payments"
            color = "primary"
        elif rent_to_emi_ratio >= 60:
            category = "Good"
            description = "Reasonable rental coverage"
            color = "info"
        elif rent_to_emi_ratio >= 40:
            category = "Fair"
            description = "Moderate rental coverage"
            color = "warning"
        else:
            category = "Poor"
            description = "Low rental coverage"
            color = "danger"
        
        # Calculate monthly shortfall/surplus
        monthly_difference = monthly_rent - monthly_emi
        annual_difference = monthly_difference * 12
        
        return {
            'ratio_percentage': round(rent_to_emi_ratio, 1),
            'monthly_rent': round(monthly_rent, 0),
            'monthly_emi': round(monthly_emi, 0),
            'monthly_difference': round(monthly_difference, 0),
            'annual_difference': round(annual_difference, 0),
            'category': category,
            'description': description,
            'color': color,
            'is_positive_cashflow': monthly_difference >= 0,
            'coverage_analysis': {
                'rent_covers_percentage': round(rent_to_emi_ratio, 1),
                'shortfall_percentage': round(max(0, 100 - rent_to_emi_ratio), 1),
                'monthly_contribution_needed': round(max(0, -monthly_difference), 0)
            }
        }
    
    @staticmethod
    def get_ratio_recommendations(ratio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get investment recommendations based on rent-to-EMI ratio"""
        
        ratio = ratio_data['ratio_percentage']
        
        if ratio >= 100:
            recommendation = {
                'verdict': 'EXCELLENT CASH FLOW',
                'strategy': 'Perfect for income-focused investors',
                'risk_level': 'Low',
                'investor_type': 'All investor types',
                'action': 'Strong buy consideration - positive cash flow from day 1'
            }
        elif ratio >= 80:
            recommendation = {
                'verdict': 'STRONG INVESTMENT',
                'strategy': 'Good for balanced growth and income',
                'risk_level': 'Low-Medium',
                'investor_type': 'Most investors',
                'action': 'Good buy - minimal monthly contributions required'
            }
        elif ratio >= 60:
            recommendation = {
                'verdict': 'MODERATE INVESTMENT',
                'strategy': 'Better for growth-focused investors',
                'risk_level': 'Medium',
                'investor_type': 'Experienced investors',
                'action': 'Consider if you can afford monthly contributions'
            }
        elif ratio >= 40:
            recommendation = {
                'verdict': 'HIGH CONTRIBUTION REQUIRED',
                'strategy': 'Only for capital growth strategies',
                'risk_level': 'Medium-High',
                'investor_type': 'High-income investors only',
                'action': 'Carefully assess ongoing funding capacity'
            }
        else:
            recommendation = {
                'verdict': 'POOR CASH FLOW',
                'strategy': 'Avoid unless exceptional growth expected',
                'risk_level': 'High',
                'investor_type': 'Wealthy investors only',
                'action': 'Consider alternative properties with better ratios'
            }
        
        return recommendation
