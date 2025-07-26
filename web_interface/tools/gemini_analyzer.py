"""
Gemini AI Analyzer Module for Web Interface
Standalone version without MCP dependencies
"""
import logging
import os

logger = logging.getLogger(__name__)

# Try to import Gemini AI, but handle gracefully if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini AI not available - AI features disabled")

class GeminiPropertyAnalyzer:
    """
    AI-powered property analysis using Google Gemini
    """
    
    def __init__(self):
        self.model = None
        self.api_key = None
        
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            # Try to get API key from environment variable first
            self.api_key = os.getenv('GEMINI_API_KEY')
            
            # If not found, try to read from secret file
            if not self.api_key:
                try:
                    with open('gemini_api_key.txt', 'r') as f:
                        self.api_key = f.read().strip()
                except FileNotFoundError:
                    logger.warning("Gemini API key file not found")
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini AI initialized successfully")
            else:
                logger.warning("No Gemini API key found - AI features disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def analyze_property_with_ai(self, property_data):
        """
        Analyze property using AI insights
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            Dictionary with AI analysis results
        """
        if not GEMINI_AVAILABLE or not self.model:
            return self._fallback_analysis(property_data)
        
        try:
            # Create a prompt for the AI
            prompt = self._create_analysis_prompt(property_data)
            
            # Generate AI response
            response = self.model.generate_content(prompt)
            
            return {
                'ai_analysis': response.text,
                'ai_available': True,
                'property_summary': self._extract_property_summary(property_data)
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._fallback_analysis(property_data)
    
    def _create_analysis_prompt(self, property_data):
        """Create analysis prompt for AI"""
        prompt = f"""
        Please analyze this Australian real estate investment property:
        
        Property Details:
        - Price: ${property_data.get('price', 'Not specified')}
        - Location: {property_data.get('address', 'Not specified')}
        - Property Type: {property_data.get('property_type', 'Not specified')}
        - Bedrooms: {property_data.get('bedrooms', 'Not specified')}
        - Bathrooms: {property_data.get('bathrooms', 'Not specified')}
        - Square Feet: {property_data.get('square_feet', 'Not specified')}
        
        Please provide:
        1. Investment potential (1-10 rating)
        2. Key strengths and weaknesses
        3. Market position analysis
        4. Rental potential assessment
        5. 3-5 specific recommendations
        
        Focus on Australian real estate market conditions and investment considerations.
        Keep the analysis concise but comprehensive.
        """
        
        return prompt
    
    def _extract_property_summary(self, property_data):
        """Extract key property information"""
        return {
            'price': property_data.get('price'),
            'location': property_data.get('address'),
            'type': property_data.get('property_type'),
            'bedrooms': property_data.get('bedrooms'),
            'bathrooms': property_data.get('bathrooms')
        }
    
    def _fallback_analysis(self, property_data):
        """Provide fallback analysis when AI is not available"""
        return {
            'ai_analysis': self._generate_basic_analysis(property_data),
            'ai_available': False,
            'property_summary': self._extract_property_summary(property_data)
        }
    
    def _generate_basic_analysis(self, property_data):
        """Generate basic analysis without AI"""
        price = property_data.get('price', 0)
        bedrooms = property_data.get('bedrooms', 0)
        property_type = property_data.get('property_type', 'Unknown')
        
        analysis = f"""
        Property Investment Analysis (Basic Mode):
        
        Investment Rating: {self._calculate_basic_rating(property_data)}/10
        
        Property Overview:
        - This {property_type.lower()} is priced at ${price:,} with {bedrooms} bedroom(s)
        - {"Good entry-level investment" if price < 500000 else "Premium property opportunity"}
        
        Key Considerations:
        - {"Suitable for family rentals" if bedrooms >= 3 else "Suitable for singles/couples"}
        - {"Strong rental demand expected" if property_type.lower() == "house" else "Moderate rental demand"}
        - Location analysis requires local market research
        
        Recommendations:
        1. Conduct detailed market research for the area
        2. Calculate rental yields based on local rental rates
        3. Consider property condition and renovation needs
        4. Review local infrastructure and transport links
        5. Assess future development plans for the area
        
        Note: This is a basic analysis. For detailed AI-powered insights, ensure Gemini AI is properly configured.
        """
        
        return analysis
    
    def _calculate_basic_rating(self, property_data):
        """Calculate basic investment rating"""
        score = 5  # Base score
        
        price = property_data.get('price', 0)
        bedrooms = property_data.get('bedrooms', 0)
        property_type = property_data.get('property_type', '').lower()
        
        # Price adjustment
        if 300000 <= price <= 700000:
            score += 2
        elif price < 300000:
            score += 1
        
        # Bedroom adjustment
        if bedrooms >= 3:
            score += 2
        elif bedrooms == 2:
            score += 1
        
        # Property type adjustment
        if property_type == 'house':
            score += 1
        
        return min(max(score, 1), 10)
