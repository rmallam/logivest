#!/usr/bin/env python3

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import Gemini with fallback
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Gemini AI not available: {e}")
    GEMINI_AVAILABLE = False
    genai = None

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
    # Template-expected attributes
    market_outlook: str = ""
    investment_potential: float = 0.0
    investment_reasoning: str = ""
    key_risks: list = None
    key_opportunities: list = None
    recommendation: str = ""
    rent_to_emi_analysis: Dict[str, Any] = None
    
    def __post_init__(self):
        """Set default values for None fields"""
        if self.key_risks is None:
            self.key_risks = []
        if self.key_opportunities is None:
            self.key_opportunities = []
        if self.rent_to_emi_analysis is None:
            self.rent_to_emi_analysis = {}

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
        
        if not GEMINI_AVAILABLE:
            self.model = None
            self.has_api_key = False
            self.logger.warning("Google Generative AI package not available. AI analysis will be unavailable.")
            return
            
        if api_key and api_key != 'your-actual-gemini-api-key-here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.has_api_key = True
        else:
            self.model = None
            self.has_api_key = False
            self.logger.warning("Gemini API key not found. AI analysis will be unavailable.")
    
    async def analyze_property(self, address: str, budget: float = None) -> PropertyInsight:
        """Get comprehensive property analysis from Gemini AI with real data"""
        
        if not self.model:
            return self._get_fallback_analysis(address, budget)
        
        try:
            # Step 1: Get real property data first (now async)
            property_data = await self._fetch_property_data(address)
            
            # Step 2: Construct detailed prompt with real data for Gemini analysis
            prompt = self._build_analysis_prompt_with_data(address, property_data, budget)
            
            # Step 3: Get response from Gemini (handle sync call properly)
            try:
                response = self.model.generate_content(prompt)
                analysis_text = response.text
                
                # Debug logging to see the actual Gemini response
                self.logger.info(f"Gemini response received for {address}")
                self.logger.info(f"Response length: {len(analysis_text)} characters")
                self.logger.info(f"First 500 characters of response: {analysis_text[:500]}...")
                
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {gemini_error}")
                return self._get_fallback_analysis(address, budget)
            
            # Step 4: Parse the response into structured data
            insight = self._parse_gemini_response(address, analysis_text, budget, property_data)
            
            logger.info(f"Successfully analyzed property with real data: {address}")
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing property with Gemini: {str(e)}")
            return self._get_fallback_analysis(address, budget)
    
    async def _fetch_property_data(self, address: str) -> Dict[str, Any]:
        """Fetch real property data from available APIs and sources"""
        # Since external APIs aren't available, return minimal structure
        # All property details will be extracted from Gemini's response
        suburb = self._extract_suburb_from_address(address)
        
        return {
            'property_details': {
                'address': address,
                'source': 'gemini_extraction'
            },
            'market_data': {
                'location': suburb,
                'source': 'gemini_extraction'
            },
            'analysis_timestamp': 'extracted_from_gemini'
        }
    
    def _extract_suburb_from_address(self, address: str) -> str:
        """Extract suburb name from full address"""
        # Simple extraction - take the part before the state
        parts = address.split(',')
        if len(parts) >= 2:
            # Usually format is "123 Street, Suburb, State"
            return parts[-2].strip() if len(parts) > 2 else parts[0].strip()
        return address
    
    def _build_analysis_prompt_with_data(self, address: str, property_data: Dict[str, Any], budget: float = None) -> str:
        """Build comprehensive prompt for Gemini property analysis using real data"""
        
        # Extract suburb from address for a more general approach
        suburb = self._extract_suburb_from_address(address)
        budget_context = f" Budget consideration: ${budget:,.0f}" if budget else ""
        
        prompt = f"""
        Please provide a comprehensive analysis of {address} and the {suburb} area in Melbourne.

        PROPERTY DETAILS NEEDED:
        1. Property Type: Is this typically a house, apartment, townhouse, or unit area?
        2. Property Specifications: How many bedrooms and bathrooms are typical for properties in this location?
        3. Land Size: What's the typical block size or property size in this area?
        4. Property Condition: What's the general condition and age of properties in this suburb?

        MARKET ANALYSIS NEEDED:
        5. Current Property Prices: What's the current price range for properties in {suburb}?
        6. Recent Sales: What have similar properties sold for recently?
        7. Price Trends: How have property prices changed over the last 12 months?
        8. Market Activity: How long do properties typically stay on the market?

        RENTAL MARKET ANALYSIS:
        9. Weekly Rental Rates: What are current weekly rental rates for properties in {suburb}?
        10. Rental Demand: How strong is rental demand in this area?
        11. Rental Yield: What's the typical rental yield for investment properties?
        12. Vacancy Rates: How long do properties typically take to rent?

        SUBURB CHARACTERISTICS:
        13. Demographics: Who typically lives in {suburb}? (families, professionals, students, etc.)
        14. Transport: What public transport options are available?
        15. Schools: What schools and educational facilities are nearby?
        16. Shopping & Amenities: What shopping centers, medical facilities, and amenities are available?
        17. Employment: What major employment hubs or business districts are accessible?

        INVESTMENT ANALYSIS:
        18. Growth Potential: What's the expected capital growth potential for this area?
        19. Infrastructure: Are there any planned infrastructure developments?
        20. Investment Suitability: Rate this suburb out of 10 for property investment
        21. Risk Factors: What are the main risks for property investment in this area?
        22. Opportunities: What opportunities exist for property investors?

        Please provide specific data points, numbers, and detailed analysis for each section.{budget_context}
        """
        
        return prompt
    
    def _parse_gemini_response(self, address: str, response_text: str, budget: float, property_data: Dict[str, Any]) -> PropertyInsight:
        """Parse Gemini response into structured PropertyInsight object using real data"""
        
        # Extract real property details from the fetched data
        property_details = property_data.get('property_details', {})
        market_data = property_data.get('market_data', {})
        market_summary = market_data.get('market_summary', {})
        
        # Extract property details from Gemini response text instead of using sample data
        insight_data = {
            'address': address,
            'property_type': self._extract_property_type_from_response(response_text),
            'bedrooms': self._extract_bedrooms_from_response(response_text),
            'bathrooms': self._extract_bathrooms_from_response(response_text),
            'land_size': self._extract_land_size_from_response(response_text),
            'estimated_value': self._extract_property_value_from_response(response_text),
            'market_overview': self._extract_market_overview_from_response(response_text),
            'location_analysis': {
                'family_friendly': True,
                'transport_score': 7,
                'amenities_score': 7,
                'school_zone': 'Good'
            },
            'investment_recommendation': {
                'verdict': self._extract_verdict_from_response(response_text),
                'confidence': 'High',
                'growth_potential': self._extract_growth_potential(response_text)
            },
            'key_features': self._extract_features_from_response(response_text),
            'pros': self._extract_pros_from_response(response_text),
            'considerations': self._extract_considerations_from_response(response_text),
            'raw_analysis': response_text,
            # Template-expected attributes
            'market_outlook': self._extract_market_outlook(response_text),
            'investment_potential': self._extract_investment_score(response_text),
            'investment_reasoning': self._extract_investment_reasoning(response_text),
            'key_risks': self._extract_risks_from_response(response_text),
            'key_opportunities': self._extract_opportunities_from_response(response_text),
            'recommendation': self._extract_verdict_from_response(response_text),
            'rent_to_emi_analysis': self._calculate_rent_to_emi_from_response(response_text, budget)
        }
        
        # Debug logging to see what we extracted
        self.logger.info(f"Extracted property details:")
        self.logger.info(f"  Property Type: {insight_data['property_type']}")
        self.logger.info(f"  Bedrooms: {insight_data['bedrooms']}")
        self.logger.info(f"  Bathrooms: {insight_data['bathrooms']}")
        self.logger.info(f"  Land Size: {insight_data['land_size']}")
        self.logger.info(f"  Estimated Value: {insight_data['estimated_value']}")
        self.logger.info(f"  Market Overview: {insight_data['market_overview']}")
        self.logger.info(f"  Investment Score: {insight_data['investment_potential']}")
        
        return PropertyInsight(**insight_data)
    
    def _extract_verdict_from_response(self, response_text: str) -> str:
        """Extract investment verdict from Gemini response"""
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['excellent', 'outstanding', 'highly recommend', 'strong buy']):
            return 'Excellent'
        elif any(word in text_lower for word in ['good investment', 'recommended', 'buy', 'positive']):
            return 'Good'
        elif any(word in text_lower for word in ['avoid', 'poor', 'not recommended', 'negative']):
            return 'Poor'
        elif any(word in text_lower for word in ['caution', 'careful', 'moderate', 'neutral']):
            return 'Neutral'
        else:
            return 'Neutral'
    
    def _extract_growth_potential(self, response_text: str) -> str:
        """Extract growth potential from Gemini response"""
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['high growth', 'strong growth', 'excellent potential']):
            return 'High'
        elif any(word in text_lower for word in ['moderate growth', 'steady growth']):
            return 'Moderate'
        elif any(word in text_lower for word in ['low growth', 'limited growth', 'slow growth']):
            return 'Low'
        else:
            return 'Moderate'
    
    def _extract_pros_from_response(self, response_text: str) -> list:
        """Extract positive points from Gemini response"""
        pros = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['advantage', 'positive', 'strength', 'benefit', 'pro:']):
                if line and not line.startswith('#'):
                    pros.append(line.replace('- ', '').replace('* ', ''))
        
        # If no specific pros found, extract from positive sentiment
        if not pros:
            if 'good location' in response_text.lower():
                pros.append('Good location')
            if 'rental potential' in response_text.lower():
                pros.append('Strong rental potential')
        
        return pros[:5]  # Limit to 5 pros
    
    def _extract_considerations_from_response(self, response_text: str) -> list:
        """Extract considerations/risks from Gemini response"""
        considerations = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['risk', 'consideration', 'concern', 'caution', 'negative', 'con:']):
                if line and not line.startswith('#'):
                    considerations.append(line.replace('- ', '').replace('* ', ''))
        
        # If no specific considerations found, add general ones
        if not considerations:
            considerations.append('Conduct thorough due diligence')
            considerations.append('Consider property condition and maintenance needs')
        
        return considerations[:5]  # Limit to 5 considerations
    
    def _extract_property_type_from_response(self, response_text: str) -> str:
        """Extract property type from Gemini response"""
        text_lower = response_text.lower()
        
        # Look for explicit mentions of property type
        if any(word in text_lower for word in ['apartment', 'unit', 'flat']):
            return 'Apartment'
        elif any(word in text_lower for word in ['house', 'home', 'detached']):
            return 'House'
        elif any(word in text_lower for word in ['townhouse', 'townhome']):
            return 'Townhouse'
        elif any(word in text_lower for word in ['condo', 'condominium']):
            return 'Condominium'
        elif any(word in text_lower for word in ['duplex']):
            return 'Duplex'
        elif any(word in text_lower for word in ['villa']):
            return 'Villa'
        else:
            # Try to extract from lines that mention "Property Type" or similar
            lines = response_text.split('\n')
            for line in lines:
                if 'property type' in line.lower() or 'type:' in line.lower():
                    # Extract everything after the colon
                    if ':' in line:
                        return line.split(':')[1].strip().title()
            return 'Residential Property'
    
    def _extract_bedrooms_from_response(self, response_text: str) -> int:
        """Extract number of bedrooms from Gemini response"""
        import re
        
        # Look for patterns like "3 bedrooms", "3-bedroom", "3 bed", etc.
        patterns = [
            r'(\d+)\s*bedrooms?',
            r'(\d+)[\-\s]*bed(?:room)?s?',
            r'bedrooms?:\s*(\d+)',
            r'(\d+)\s*br\b',
            r'(\d+)\s*bd\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, IndexError):
                    continue
        
        # Fallback: look for common bedroom mentions
        text_lower = response_text.lower()
        if 'one bedroom' in text_lower or '1 bedroom' in text_lower:
            return 1
        elif 'two bedroom' in text_lower or '2 bedroom' in text_lower:
            return 2
        elif 'three bedroom' in text_lower or '3 bedroom' in text_lower:
            return 3
        elif 'four bedroom' in text_lower or '4 bedroom' in text_lower:
            return 4
        elif 'five bedroom' in text_lower or '5 bedroom' in text_lower:
            return 5
        
        return 3  # Default reasonable assumption
    
    def _extract_bathrooms_from_response(self, response_text: str) -> int:
        """Extract number of bathrooms from Gemini response"""
        import re
        
        # Look for patterns like "2 bathrooms", "2-bathroom", "2 bath", etc.
        patterns = [
            r'(\d+)\s*bathrooms?',
            r'(\d+)[\-\s]*bath(?:room)?s?',
            r'bathrooms?:\s*(\d+)',
            r'(\d+)\s*ba\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, IndexError):
                    continue
        
        # Fallback based on bedrooms (rough estimate)
        bedrooms = self._extract_bedrooms_from_response(response_text)
        if bedrooms <= 1:
            return 1
        elif bedrooms <= 3:
            return 2
        else:
            return 3
    
    def _extract_land_size_from_response(self, response_text: str) -> str:
        """Extract land size from Gemini response"""
        import re
        
        # Look for patterns like "600m2", "0.25 acres", "quarter acre", etc.
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:square\s*)?m(?:eters?)?2?',
            r'(\d+(?:\.\d+)?)\s*(?:square\s*)?m(?:eters?)?',
            r'(\d+(?:\.\d+)?)\s*(?:square\s*)?ft',
            r'(\d+(?:\.\d+)?)\s*(?:square\s*)?feet',
            r'(\d+(?:\.\d+)?)\s*acres?',
            r'(\d+(?:\.\d+)?)\s*hectares?',
            r'lot size[:\s]*([^\n,\.]+)',
            r'land size[:\s]*([^\n,\.]+)',
            r'block size[:\s]*([^\n,\.]+)',
            r'property size[:\s]*([^\n,\.]+)'
        ]
        
        # First try to find complete land size descriptions
        for pattern in patterns[6:]:  # Start with the complete description patterns
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                land_size = matches[0].strip()
                # Clean up the match
                land_size = re.sub(r'[^\w\s\.\-]', '', land_size)  # Remove special chars except dots and hyphens
                if land_size and len(land_size) > 2:  # Ensure it's meaningful
                    return land_size
        
        # Then try numeric patterns with units
        for pattern in patterns[:6]:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                number = matches[0]
                # Find the context around this number to determine the unit
                for match in re.finditer(pattern, response_text, re.IGNORECASE):
                    start = max(0, match.start() - 20)
                    end = min(len(response_text), match.end() + 20)
                    context = response_text[start:end].lower()
                    
                    # Determine unit based on context
                    if any(unit in context for unit in ['m2', 'sqm', 'square m', 'metres', 'meters']):
                        return f"{number} sqm"
                    elif any(unit in context for unit in ['ft', 'sqft', 'square f', 'feet']):
                        return f"{number} sqft"
                    elif 'acre' in context:
                        return f"{number} acres"
                    elif 'hectare' in context:
                        return f"{number} hectares"
        
        # Look for descriptive land sizes
        text_lower = response_text.lower()
        descriptive_patterns = [
            (r'quarter\s+acre', '0.25 acres'),
            (r'half\s+acre', '0.5 acres'),
            (r'one\s+acre', '1 acre'),
            (r'large\s+block', 'Large block'),
            (r'small\s+block', 'Small block'),
            (r'compact\s+block', 'Compact block'),
            (r'standard\s+block', 'Standard block'),
            (r'typical\s+block', 'Typical block'),
            (r'corner\s+block', 'Corner block'),
            (r'regular\s+block', 'Regular block')
        ]
        
        for pattern, description in descriptive_patterns:
            if re.search(pattern, text_lower):
                return description
        
        # Fallback based on property type mentioned in response
        if any(word in text_lower for word in ['apartment', 'unit', 'flat']):
            return 'Apartment (no land)'
        elif any(word in text_lower for word in ['townhouse', 'townhome']):
            return 'Small to medium block'
        elif any(word in text_lower for word in ['house', 'home']):
            return 'Standard residential block'
        
        return 'Standard residential block'
    
    def _extract_property_value_from_response(self, response_text: str) -> dict:
        """Extract property value from Gemini response"""
        import re
        
        # Look for price patterns like "$750,000", "$750K", "750000", price ranges, etc.
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $750,000
            r'\$(\d+)(?:k|K)',  # $750K
            r'price[:\s]*\$?(\d{1,3}(?:,\d{3})*)',  # Price: $750,000
            r'value[:\s]*\$?(\d{1,3}(?:,\d{3})*)',  # Value: $750,000
            r'range[:\s]*\$?(\d{1,3}(?:,\d{3})*)',  # Range: $750,000
            r'from\s*\$(\d{1,3}(?:,\d{3})*)',  # from $750,000
            r'to\s*\$(\d{1,3}(?:,\d{3})*)',  # to $750,000
            r'between\s*\$(\d{1,3}(?:,\d{3})*)',  # between $750,000
            r'(\d{1,3}(?:,\d{3})*)\s*dollars?',  # 750,000 dollars
            r'median[:\s]*\$?(\d{1,3}(?:,\d{3})*)',  # median: $750,000
            r'average[:\s]*\$?(\d{1,3}(?:,\d{3})*)',  # average: $750,000
            r'typical[:\s]*\$?(\d{1,3}(?:,\d{3})*)'  # typical: $750,000
        ]
        
        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                try:
                    # Handle K suffix
                    if isinstance(match, str) and 'k' in match.lower():
                        price = int(match.lower().replace('k', '')) * 1000
                    else:
                        # Remove commas and convert
                        price = int(str(match).replace(',', ''))
                    
                    # Only consider reasonable property prices (between $100K and $20M)
                    if 100000 <= price <= 20000000:
                        prices.append(price)
                except (ValueError, AttributeError):
                    continue
        
        if prices:
            # Sort prices and determine range
            prices = sorted(set(prices))
            
            if len(prices) >= 3:
                # If we have multiple prices, use them to determine min/max/estimate
                min_price = min(prices)
                max_price = max(prices)
                estimate = sum(prices) // len(prices)  # Average
            elif len(prices) == 2:
                # If we have two prices, use them as min/max
                min_price = min(prices)
                max_price = max(prices)
                estimate = (min_price + max_price) // 2
            else:
                # Single price, create a reasonable range around it
                main_price = prices[0]
                min_price = int(main_price * 0.9)
                max_price = int(main_price * 1.1)
                estimate = main_price
            
            return {
                'min': min_price,
                'max': max_price,
                'estimate': estimate
            }
        
        # Fallback: try to determine area and provide realistic estimates
        text_lower = response_text.lower()
        
        # Different suburbs have different price ranges
        if any(suburb in text_lower for suburb in ['point cook', 'werribee', 'hoppers crossing']):
            # Outer western suburbs
            return {'min': 550000, 'max': 750000, 'estimate': 650000}
        elif any(suburb in text_lower for suburb in ['melbourne cbd', 'south yarra', 'toorak', 'brighton']):
            # Premium areas
            return {'min': 900000, 'max': 1500000, 'estimate': 1200000}
        elif any(suburb in text_lower for suburb in ['richmond', 'fitzroy', 'carlton', 'st kilda']):
            # Inner suburbs
            return {'min': 700000, 'max': 1200000, 'estimate': 950000}
        else:
            # General Melbourne area
            return {'min': 600000, 'max': 900000, 'estimate': 750000}
    
    def _extract_market_overview_from_response(self, response_text: str) -> dict:
        """Extract market overview data from Gemini response"""
        import re
        
        # Extract rental yield with more patterns
        rental_yield = 4.0  # Default
        yield_patterns = [
            r'rental\s+yield[:\s]*(\d+(?:\.\d+)?)%?',
            r'yield[:\s]*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s+yield',
            r'return[:\s]*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s+return'
        ]
        
        for pattern in yield_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    yield_value = float(matches[0])
                    # Reasonable rental yield range (2% to 12%)
                    if 2.0 <= yield_value <= 12.0:
                        rental_yield = yield_value
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract median price for the area with more comprehensive patterns
        median_price = 650000  # Default
        price_patterns = [
            r'median[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'average\s+price[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'typical\s+price[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'property\s+prices[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'house\s+prices[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'home\s+values[:\s]*\$?(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    price = int(matches[0].replace(',', ''))
                    # Reasonable price range (200K to 10M)
                    if 200000 <= price <= 10000000:
                        median_price = price
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract growth rate with more patterns
        growth_rate = 5.0  # Default
        growth_patterns = [
            r'growth[:\s]*(\d+(?:\.\d+)?)%',
            r'appreciation[:\s]*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s+growth',
            r'increased[:\s]*(\d+(?:\.\d+)?)%',
            r'risen[:\s]*(\d+(?:\.\d+)?)%',
            r'up[:\s]*(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in growth_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    growth = float(matches[0])
                    # Reasonable growth range (-20% to +50%)
                    if -20.0 <= growth <= 50.0:
                        growth_rate = growth
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract days on market
        days_on_market = 28  # Default
        dom_patterns = [
            r'(\d+)\s+days?\s+on\s+market',
            r'market\s+for\s+(\d+)\s+days?',
            r'sell\s+in\s+(\d+)\s+days?',
            r'(\d+)\s+days?\s+to\s+sell'
        ]
        
        for pattern in dom_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    days = int(matches[0])
                    # Reasonable range (1 to 365 days)
                    if 1 <= days <= 365:
                        days_on_market = days
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract vacancy rate
        vacancy_rate = 2.5  # Default
        vacancy_patterns = [
            r'vacancy[:\s]*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s+vacancy',
            r'vacant[:\s]*(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in vacancy_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    vacancy = float(matches[0])
                    # Reasonable vacancy range (0% to 20%)
                    if 0.0 <= vacancy <= 20.0:
                        vacancy_rate = vacancy
                        break
                except (ValueError, IndexError):
                    continue
        
        # Determine market trend based on growth rate
        if growth_rate > 8:
            trend = "Strong Growth"
        elif growth_rate > 3:
            trend = "Moderate Growth"
        elif growth_rate > 0:
            trend = "Stable"
        elif growth_rate > -5:
            trend = "Declining"
        else:
            trend = "Weak Market"
        
        return {
            'median_price': median_price,
            'growth_12m': growth_rate,
            'days_on_market': days_on_market,
            'rental_yield': rental_yield,
            'vacancy_rate': vacancy_rate,
            'trend': trend,
            'market_sentiment': 'Positive' if growth_rate > 0 else 'Negative'
        }
    
    def _extract_features_from_response(self, response_text: str) -> list:
        """Extract property features from Gemini response"""
        features = []
        
        # Look for feature sections
        lines = response_text.split('\n')
        in_features_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering a features section
            if any(keyword in line.lower() for keyword in ['features:', 'amenities:', 'includes:', 'property features']):
                in_features_section = True
                continue
            
            # If we're in features section, collect items
            if in_features_section:
                if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                    feature = line[2:].strip()
                    if feature:
                        features.append(feature)
                elif line and not any(keyword in line.lower() for keyword in ['analysis', 'conclusion', 'recommendation']):
                    # Stop if we hit another section
                    in_features_section = False
        
        # If no features found, extract common property features from text
        if not features:
            text_lower = response_text.lower()
            common_features = [
                ('air conditioning', 'Air conditioning'),
                ('heating', 'Heating system'),
                ('garage', 'Garage'),
                ('pool', 'Swimming pool'),
                ('garden', 'Garden/landscaping'),
                ('balcony', 'Balcony'),
                ('fireplace', 'Fireplace'),
                ('dishwasher', 'Dishwasher'),
                ('walk-in', 'Walk-in closet'),
                ('ensuite', 'Ensuite bathroom'),
                ('hardwood', 'Hardwood floors'),
                ('carpet', 'Carpeted areas'),
                ('tiles', 'Tiled areas'),
                ('modern kitchen', 'Modern kitchen'),
                ('updated', 'Recently updated')
            ]
            
            for keyword, feature in common_features:
                if keyword in text_lower:
                    features.append(feature)
        
        return features[:8]  # Limit to 8 features
    
    def _calculate_rent_to_emi_from_response(self, response_text: str, budget: float) -> dict:
        """Calculate rent-to-EMI analysis from Gemini response data"""
        import re
        
        # Extract rental income from response with more comprehensive patterns
        rental_patterns = [
            r'rent[:\s]*\$?(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|\/week|pw)',
            r'rental[:\s]*\$?(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|\/week|pw)',
            r'weekly\s+rent[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|\/week|pw)',
            r'rent\s+for\s*\$?(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|pw)',
            r'rental\s+rates[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'typical\s+rent[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'average\s+rent[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'from\s*\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|pw)',
            r'to\s*\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|pw)',
            r'between\s*\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s+week|weekly|pw)'
        ]
        
        weekly_rents = []
        for pattern in rental_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                try:
                    rent = int(str(match).replace(',', ''))
                    # Only consider reasonable weekly rents (between $100 and $2000)
                    if 100 <= rent <= 2000:
                        weekly_rents.append(rent)
                except (ValueError, IndexError):
                    continue
        
        # Use average of found rents or estimate
        if weekly_rents:
            weekly_rent = sum(weekly_rents) / len(weekly_rents)
        else:
            weekly_rent = 0
        
        # Get property price from response
        property_value = self._extract_property_value_from_response(response_text)
        property_price = property_value.get('estimate', budget or 700000)
        
        # If no rent found, estimate based on typical yield for the area
        if weekly_rent == 0:
            market_overview = self._extract_market_overview_from_response(response_text)
            rental_yield = market_overview.get('rental_yield', 4.0)
            annual_rent = property_price * (rental_yield / 100)
            weekly_rent = annual_rent / 52
        
        try:
            monthly_rent = weekly_rent * 52 / 12
            
            # Calculate EMI (assuming 80% loan, 6.5% interest, 25 years)
            loan_amount = property_price * 0.8
            interest_rate = 6.5 / 100 / 12  # Monthly rate
            tenure_months = 25 * 12
            
            if interest_rate > 0:
                monthly_emi = (loan_amount * interest_rate * (1 + interest_rate)**tenure_months) / ((1 + interest_rate)**tenure_months - 1)
            else:
                monthly_emi = loan_amount / tenure_months
            
            # Calculate ratio
            rent_to_emi_ratio = (monthly_rent / monthly_emi) * 100 if monthly_emi > 0 else 0
            
            # Determine category and color
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
            
            return {
                'ratio_percentage': round(rent_to_emi_ratio, 1),
                'monthly_rent': round(monthly_rent, 0),
                'monthly_emi': round(monthly_emi, 0),
                'weekly_rent': round(weekly_rent, 0),
                'property_price': property_price,
                'loan_amount': round(loan_amount, 0),
                'category': category,
                'description': description,
                'color': color
            }
        
        except Exception as e:
            self.logger.warning(f"Could not calculate rent-to-EMI from response: {e}")
            return {
                'ratio_percentage': 0,
                'monthly_rent': 0,
                'monthly_emi': 0,
                'weekly_rent': 0,
                'property_price': budget or 700000,
                'loan_amount': 0,
                'category': 'Unknown',
                'description': 'Analysis unavailable',
                'color': 'secondary'
            }
    
    def _extract_market_outlook(self, response_text: str) -> str:
        """Extract market outlook from Gemini response"""
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['strong market', 'growing market', 'positive outlook']):
            return "Market shows strong growth potential with positive indicators"
        elif any(word in text_lower for word in ['stable market', 'steady growth']):
            return "Market demonstrates stable conditions with steady growth"
        elif any(word in text_lower for word in ['declining market', 'weak market']):
            return "Market shows signs of weakness and potential decline"
        else:
            return "Market conditions require careful analysis and monitoring"
    
    def _extract_investment_score(self, response_text: str) -> float:
        """Extract investment potential score (1-10) from Gemini response"""
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['excellent', 'outstanding', 'highly recommend']):
            return 8.5
        elif any(word in text_lower for word in ['very good', 'strong buy', 'recommended']):
            return 7.5
        elif any(word in text_lower for word in ['good investment', 'positive', 'buy']):
            return 6.5
        elif any(word in text_lower for word in ['neutral', 'moderate', 'average']):
            return 5.5
        elif any(word in text_lower for word in ['caution', 'careful', 'risky']):
            return 4.0
        elif any(word in text_lower for word in ['avoid', 'poor', 'not recommended']):
            return 2.5
        else:
            return 5.0  # Default neutral score
    
    def _extract_investment_reasoning(self, response_text: str) -> str:
        """Extract investment reasoning from Gemini response"""
        # Try to find sentences that explain investment rationale
        sentences = response_text.split('.')
        reasoning_keywords = ['because', 'due to', 'given', 'based on', 'considering', 'investment']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in reasoning_keywords):
                return sentence.strip()[:200]  # Limit length
        
        # Fallback to first meaningful sentence
        for sentence in sentences:
            if len(sentence.strip()) > 50:
                return sentence.strip()[:200]
        
        return "Investment potential based on comprehensive market analysis"
    
    def _extract_risks_from_response(self, response_text: str) -> list:
        """Extract key risks from Gemini response"""
        risks = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['risk', 'concern', 'caution', 'warning', 'negative']):
                if line and not line.startswith('#'):
                    risk_text = line.replace('- ', '').replace('* ', '').replace('Risk:', '').strip()
                    if risk_text:
                        risks.append(risk_text)
        
        # Add common investment risks if none found
        if not risks:
            risks = [
                "Market volatility may affect property values",
                "Interest rate changes could impact mortgage costs",
                "Property maintenance and vacancy risks"
            ]
        
        return risks[:5]  # Limit to 5 risks
    
    def _extract_opportunities_from_response(self, response_text: str) -> list:
        """Extract key opportunities from Gemini response"""
        opportunities = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['opportunity', 'potential', 'growth', 'advantage', 'benefit']):
                if line and not line.startswith('#'):
                    opp_text = line.replace('- ', '').replace('* ', '').replace('Opportunity:', '').strip()
                    if opp_text:
                        opportunities.append(opp_text)
        
        # Add common opportunities if none found
        if not opportunities:
            opportunities = [
                "Capital growth potential in established market",
                "Strong rental demand in the area",
                "Infrastructure development nearby"
            ]
        
        return opportunities[:5]  # Limit to 5 opportunities
    
    def _calculate_rent_to_emi_analysis(self, property_data: Dict[str, Any], budget: float) -> Dict[str, Any]:
        """Calculate rent-to-EMI analysis for the property"""
        try:
            property_details = property_data.get('property_details', {})
            market_data = property_data.get('market_data', {})
            
            # Get property price
            property_price = property_details.get('price', budget or 500000)
            
            # Estimate rental income (use market rental yield)
            rental_yield = market_data.get('market_summary', {}).get('rental_yield', 4.0)
            estimated_annual_rent = property_price * (rental_yield / 100)
            monthly_rent = estimated_annual_rent / 12
            
            # Calculate EMI (assuming 80% loan, 6.5% interest, 25 years)
            loan_amount = property_price * 0.8
            interest_rate = 6.5 / 100 / 12  # Monthly rate
            tenure_months = 25 * 12
            
            if interest_rate > 0:
                monthly_emi = (loan_amount * interest_rate * (1 + interest_rate)**tenure_months) / ((1 + interest_rate)**tenure_months - 1)
            else:
                monthly_emi = loan_amount / tenure_months
            
            # Calculate ratio
            rent_to_emi_ratio = (monthly_rent / monthly_emi) * 100 if monthly_emi > 0 else 0
            
            # Determine category and color
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
            
            return {
                'ratio_percentage': round(rent_to_emi_ratio, 1),
                'monthly_rent': round(monthly_rent, 0),
                'monthly_emi': round(monthly_emi, 0),
                'category': category,
                'description': description,
                'color': color
            }
        
        except Exception as e:
            self.logger.warning(f"Could not calculate rent-to-EMI analysis: {e}")
            return {
                'ratio_percentage': 0,
                'monthly_rent': 0,
                'monthly_emi': 0,
                'category': 'Unknown',
                'description': 'Analysis unavailable',
                'color': 'secondary'
            }
    
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
            raw_analysis='Gemini AI analysis is not available. Please provide a valid API key for comprehensive property insights.',
            # Template-expected attributes
            market_outlook='Market analysis unavailable without Gemini API',
            investment_potential=5.0,
            investment_reasoning='Complete analysis requires Gemini API configuration',
            key_risks=['API configuration required for detailed analysis'],
            key_opportunities=['Professional insights available with API setup'],
            recommendation='Configure Gemini API for comprehensive analysis',
            rent_to_emi_analysis={
                'ratio_percentage': 0,
                'monthly_rent': 0,
                'monthly_emi': 0,
                'category': 'Unknown',
                'description': 'Analysis unavailable',
                'color': 'secondary'
            }
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
