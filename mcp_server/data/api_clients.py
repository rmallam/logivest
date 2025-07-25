"""
Real Estate Data Client

Handles data fetching from Domain.com.au API and provides sample data fallback.
"""

import random
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RealEstateDataClient:
    """Client for fetching real estate data from Domain.com.au API with sample data fallback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Domain.com.au API configuration
        self.domain_api_key = os.getenv('DOMAIN_API_KEY', 'key_16cb38172181580c0a2d003739cd419c')
        self.domain_base_url = os.getenv('DOMAIN_BASE_URL', 'https://api.domain.com.au')
        
        # Rate limiting
        self.last_api_call = datetime.now() - timedelta(seconds=2)
        self.min_interval = 1.0  # Minimum seconds between API calls
        
        # API session
        self.session = None
        
        # Sample property data for Australian market demonstration
        self.sample_properties = {
            'melbourne, vic': [
                {
                    'address': '15 Collins Street, Melbourne VIC 3000',
                    'type': 'apartment',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'sqm': 80,
                    'price': 750000,
                    'year_built': 2019
                },
                {
                    'address': '42 Chapel Street, South Yarra VIC 3141',
                    'type': 'townhouse',
                    'bedrooms': 3,
                    'bathrooms': 2.5,
                    'sqm': 120,
                    'price': 920000,
                    'year_built': 2020
                },
                {
                    'address': '8 Flinders Lane, Melbourne VIC 3000',
                    'type': 'house',
                    'bedrooms': 4,
                    'bathrooms': 3,
                    'sqm': 180,
                    'price': 1450000,
                    'year_built': 2018
                }
            ],
            'sydney, nsw': [
                {
                    'address': '25 George Street, Sydney NSW 2000',
                    'type': 'apartment',
                    'bedrooms': 1,
                    'bathrooms': 1,
                    'sqm': 55,
                    'price': 650000,
                    'year_built': 2021
                },
                {
                    'address': '156 Oxford Street, Bondi Junction NSW 2022',
                    'type': 'apartment',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'sqm': 85,
                    'price': 980000,
                    'year_built': 2019
                }
            ],
            'brisbane, qld': [
                {
                    'address': '33 Queen Street, Brisbane QLD 4000',
                    'type': 'apartment',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'sqm': 75,
                    'price': 520000,
                    'year_built': 2020
                },
                {
                    'address': '78 Adelaide Street, Brisbane QLD 4000',
                    'type': 'house',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'sqm': 140,
                    'price': 780000,
                    'year_built': 2017
                }
            ],
            'perth, wa': [
                {
                    'address': '12 St Georges Terrace, Perth WA 6000',
                    'type': 'apartment',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'sqm': 90,
                    'price': 480000,
                    'year_built': 2018
                },
                {
                    'address': '45 Hay Street, Subiaco WA 6008',
                    'type': 'townhouse',
                    'bedrooms': 3,
                    'bathrooms': 2.5,
                    'sqm': 110,
                    'price': 650000,
                    'year_built': 2019
                }
            ],
            'adelaide, sa': [
                {
                    'address': '88 King William Street, Adelaide SA 5000',
                    'type': 'apartment',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'sqm': 85,
                    'price': 420000,
                    'year_built': 2020
                },
                {
                    'address': '22 Rundle Street, Adelaide SA 5000',
                    'type': 'house',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'sqm': 130,
                    'price': 580000,
                    'year_built': 2016
                }
            ]
        }
    
    async def get_property_data(self, address: str) -> Dict[str, Any]:
        """
        Get property data for a specific address - tries Domain API first, falls back to sample data
        
        Args:
            address: Property address
            
        Returns:
            Property data dict or None if not found
        """
        try:
            # Try Domain API first if we have an API key
            if self.domain_api_key:
                self.logger.info(f"Fetching property data from Domain API for: {address}")
                domain_data = await self._fetch_domain_property_details(address)
                if domain_data:
                    self.logger.info(f"Successfully retrieved data from Domain API")
                    return domain_data
                else:
                    self.logger.warning(f"No data found in Domain API, falling back to sample data")
            
            # Fall back to sample data
            self.logger.info(f"Using sample data for: {address}")
            return await self._get_sample_property_data(address)
            
        except Exception as e:
            self.logger.error(f"Error fetching property data for {address}: {str(e)}")
            # Fall back to sample data on any error
            return await self._get_sample_property_data(address)

    async def _get_sample_property_data(self, address: str) -> Dict[str, Any]:
        """Get sample property data (original implementation)"""
        try:
            # For demonstration, extract city from address and find matching sample data
            address_lower = address.lower()
            
            # Try to match city in sample data
            for city, properties in self.sample_properties.items():
                if any(city_part in address_lower for city_part in city.split(', ')):
                    # Return first matching property or generate one
                    if properties:
                        prop = properties[0].copy()
                        prop['address'] = address  # Use the requested address
                        prop['source'] = 'sample_data'
                        # Convert sqft to sqm for consistency (if present)
                        if 'sqft' in prop and 'sqm' not in prop:
                            prop['sqm'] = int(prop['sqft'] * 0.092903)  # Convert sqft to sqm
                        return prop
            
            # If no match found, generate sample property data
            return self._generate_sample_property(address)
            
        except Exception as e:
            self.logger.error(f"Error fetching sample property data for {address}: {str(e)}")
            return None
    
    async def search_properties(self, location: str, max_budget: float, 
                              property_type: str = "any") -> List[Dict[str, Any]]:
        """
        Search for properties in a location within budget - tries Domain API first
        
        Args:
            location: Target location
            max_budget: Maximum budget
            property_type: Property type filter
            
        Returns:
            List of matching properties
        """
        try:
            # Try Domain API first if we have an API key
            if self.domain_api_key:
                self.logger.info(f"Searching properties via Domain API: {location}, budget: ${max_budget:,.0f}")
                domain_properties = await self._fetch_domain_property_search(location, max_budget)
                
                if domain_properties:
                    # Filter by property type if specified
                    if property_type != "any":
                        domain_properties = [p for p in domain_properties 
                                           if p.get('type', '').lower() == property_type.lower()]
                    
                    self.logger.info(f"Found {len(domain_properties)} properties from Domain API")
                    return domain_properties
                else:
                    self.logger.warning(f"No properties found in Domain API, falling back to sample data")
            
            # Fall back to sample data
            return await self._get_sample_properties_search(location, max_budget, property_type)
            
        except Exception as e:
            self.logger.error(f"Error searching properties: {str(e)}")
            # Fall back to sample data on any error
            return await self._get_sample_properties_search(location, max_budget, property_type)

    async def _get_sample_properties_search(self, location: str, max_budget: float, 
                                          property_type: str = "any") -> List[Dict[str, Any]]:
        """Get sample properties search results (original implementation)"""
        try:
            location_key = location.lower()
            
            # Get sample properties for the location
            properties = []
            
            # Check if we have sample data for this location
            for city, city_properties in self.sample_properties.items():
                if any(city_part in location_key for city_part in city.split(', ')):
                    properties.extend(city_properties)
                    break
            
            # If no sample data, generate some
            if not properties:
                properties = self._generate_sample_properties(location, 5)
            
            # Filter by budget
            affordable_properties = [p for p in properties if p['price'] <= max_budget]
            
            # Filter by property type if specified
            if property_type != "any":
                affordable_properties = [p for p in affordable_properties 
                                       if p['type'] == property_type]
            
            # Add some variation to prices and details
            for prop in affordable_properties:
                prop = self._add_market_variation(prop)
            
            return affordable_properties
            
        except Exception as e:
            self.logger.error(f"Error searching properties in {location}: {str(e)}")
            return []
    
    def _generate_sample_property(self, address: str) -> Dict[str, Any]:
        """Generate a sample property for the given address"""
        property_types = ['house', 'apartment', 'townhouse']
        
        return {
            'address': address,
            'type': random.choice(property_types),
            'bedrooms': random.randint(1, 4),
            'bathrooms': random.choice([1, 1.5, 2, 2.5, 3]),
            'sqm': random.randint(50, 200),  # Square meters for Australian market
            'price': random.randint(400000, 1200000),  # Australian price range
            'year_built': random.randint(2005, 2023)
        }
    
    def _generate_sample_properties(self, location: str, count: int) -> List[Dict[str, Any]]:
        """Generate multiple sample properties for a location"""
        properties = []
        
        street_names = ['Collins St', 'Bourke St', 'George St', 'Queen St', 'King St', 
                       'Flinders St', 'Chapel St', 'Smith St', 'High St', 'Park Ave']
        property_types = ['house', 'apartment', 'townhouse']
        
        for i in range(count):
            house_number = random.randint(1, 999)
            street = random.choice(street_names)
            
            prop = {
                'address': f'{house_number} {street}, {location}',
                'type': random.choice(property_types),
                'bedrooms': random.randint(1, 4),
                'bathrooms': random.choice([1, 1.5, 2, 2.5, 3]),
                'sqm': random.randint(50, 250),  # Square meters
                'price': random.randint(350000, 1500000),  # Australian price range
                'year_built': random.randint(2000, 2023)
            }
            
            properties.append(prop)
        
        return properties
    
    def _add_market_variation(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """Add some market variation to property data"""
        # Add ±5% variation to price to simulate market conditions
        variation = random.uniform(-0.05, 0.05)
        prop['price'] = int(prop['price'] * (1 + variation))
        
        return prop
    
    async def get_rental_estimates(self, address: str, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get rental estimates for a property
        
        Args:
            address: Property address
            property_data: Property details
            
        Returns:
            Rental estimate data
        """
        try:
            # Simple estimation based on property characteristics
            base_rent_per_sqft = self._get_base_rent_per_sqft(property_data.get('type', 'house'))
            sqft = property_data.get('sqft', 1500)
            bedrooms = property_data.get('bedrooms', 3)
            
            # Base calculation
            estimated_rent = sqft * base_rent_per_sqft
            
            # Adjust for bedrooms
            if bedrooms >= 4:
                estimated_rent *= 1.1
            elif bedrooms <= 2:
                estimated_rent *= 0.95
            
            # Add market variation
            variation = random.uniform(-0.1, 0.1)
            estimated_rent = estimated_rent * (1 + variation)
            
            return {
                'estimated_monthly_rent': round(estimated_rent),
                'rent_per_sqft': round(estimated_rent / sqft, 2),
                'confidence': 'Medium',  # Would be based on data availability in real API
                'last_updated': '2024-01-15'  # Mock date
            }
            
        except Exception as e:
            self.logger.error(f"Error getting rental estimates for {address}: {str(e)}")
            return {'estimated_monthly_rent': 0, 'confidence': 'Low'}
    
    def _get_base_rent_per_sqft(self, property_type: str) -> float:
        """Get base rent per square foot by property type"""
        rent_rates = {
            'house': 1.35,
            'townhouse': 1.45,
            'condo': 1.55,
            'apartment': 1.65
        }
        
        return rent_rates.get(property_type, 1.40)

    # Domain API Integration Methods
    
    async def _get_api_session(self):
        """Get or create aiohttp session with SSL context"""
        if self.session is None:
            import ssl
            
            # Create SSL context that handles certificate issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'X-API-Key': self.domain_api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'Real-Estate-Analyzer/1.0'
            }
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=connector
            )
        return self.session

    async def _rate_limit_wait(self):
        """Ensure we don't exceed API rate limits"""
        time_since_last = (datetime.now() - self.last_api_call).total_seconds()
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        self.last_api_call = datetime.now()

    async def _fetch_domain_property_search(self, location: str, max_budget: float) -> List[Dict[str, Any]]:
        """Fetch property listings from Domain API"""
        try:
            await self._rate_limit_wait()
            session = await self._get_api_session()
            
            # Domain API endpoint for property search
            url = f"{self.domain_base_url}/v1/listings/residential/_search"
            
            # Prepare search parameters
            search_params = {
                "listingType": "Sale",
                "propertyTypes": ["House", "Apartment", "Townhouse", "Unit"],
                "minPrice": 100000,
                "maxPrice": int(max_budget),
                "locations": [{
                    "state": self._extract_state_from_location(location),
                    "region": "",
                    "area": "",
                    "suburb": self._extract_suburb_from_location(location),
                    "postCode": "",
                    "includeSurroundingSuburbs": True
                }],
                "pageSize": 20
            }
            
            async with session.post(url, json=search_params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_domain_listings(data)
                elif response.status == 401:
                    self.logger.warning("Domain API authentication failed - check API key permissions")
                    return []
                elif response.status == 403:
                    self.logger.warning("Domain API access forbidden - insufficient permissions for search endpoint")
                    return []
                else:
                    response_text = await response.text()
                    self.logger.warning(f"Domain API returned status {response.status}: {response_text}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching from Domain API: {str(e)}")
            return []

    async def _fetch_domain_property_details(self, address: str) -> Optional[Dict[str, Any]]:
        """Fetch specific property details from Domain API"""
        try:
            await self._rate_limit_wait()
            session = await self._get_api_session()
            
            # First, search for the property to get its listing ID
            search_results = await self._search_domain_by_address(address)
            
            if not search_results:
                return None
                
            # Get the first matching property
            listing_id = search_results[0].get('id')
            if not listing_id:
                return None
                
            # Get detailed property information
            url = f"{self.domain_base_url}/v1/listings/{listing_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_domain_property_details(data)
                else:
                    self.logger.warning(f"Domain API returned status {response.status} for listing {listing_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching property details from Domain API: {str(e)}")
            return None

    async def _search_domain_by_address(self, address: str) -> List[Dict[str, Any]]:
        """Search Domain API by address"""
        try:
            session = await self._get_api_session()
            
            url = f"{self.domain_base_url}/v1/listings/residential/_search"
            
            # Extract location components from address
            suburb = self._extract_suburb_from_location(address)
            state = self._extract_state_from_location(address)
            
            search_params = {
                "listingType": "Sale",
                "locations": [{
                    "state": state,
                    "suburb": suburb,
                    "includeSurroundingSuburbs": False
                }],
                "pageSize": 10
            }
            
            async with session.post(url, json=search_params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error searching Domain by address: {str(e)}")
            return []

    def _process_domain_listings(self, api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Domain API listing data into our format"""
        properties = []
        
        for listing in api_data.get('data', []):
            try:
                prop = self._convert_domain_listing(listing)
                if prop:
                    properties.append(prop)
            except Exception as e:
                self.logger.warning(f"Error processing Domain listing: {str(e)}")
                continue
                
        return properties

    def _process_domain_property_details(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Domain API property details into our format"""
        try:
            return self._convert_domain_listing(api_data)
        except Exception as e:
            self.logger.error(f"Error processing Domain property details: {str(e)}")
            return None

    def _convert_domain_listing(self, listing: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Domain API listing format to our property format"""
        try:
            # Extract basic property information
            property_details = listing.get('propertyDetails', {})
            price_details = listing.get('priceDetails', {})
            
            # Get price
            price = 0
            if 'price' in price_details:
                price = price_details['price']
            elif 'displayPrice' in price_details:
                # Try to extract numeric price from display price
                display_price = price_details['displayPrice']
                price = self._extract_price_from_string(display_price)
            
            # Get property size
            sqm = 0
            if 'buildingDetails' in property_details:
                building = property_details['buildingDetails']
                if 'area' in building:
                    sqm = building['area']
                elif 'areaSize' in building:
                    sqm = building['areaSize']
            
            # Get bedrooms and bathrooms
            bedrooms = property_details.get('bedrooms', 0)
            bathrooms = property_details.get('bathrooms', 0)
            
            # Get property type
            property_type = property_details.get('propertyType', 'house').lower()
            
            # Get address
            address_parts = []
            if 'streetNumber' in property_details:
                address_parts.append(str(property_details['streetNumber']))
            if 'street' in property_details:
                address_parts.append(property_details['street'])
            if 'suburb' in property_details:
                address_parts.append(property_details['suburb'])
            if 'state' in property_details:
                address_parts.append(property_details['state'])
            if 'postcode' in property_details:
                address_parts.append(str(property_details['postcode']))
                
            address = ' '.join(address_parts)
            
            return {
                'address': address,
                'type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqm': sqm,
                'price': price,
                'year_built': property_details.get('yearBuilt', 2020),
                'source': 'domain_api',
                'listing_id': listing.get('id'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error converting Domain listing: {str(e)}")
            return None

    def _extract_price_from_string(self, price_str: str) -> int:
        """Extract numeric price from price display string"""
        try:
            # Remove common price prefixes and formatting
            import re
            
            # Remove currency symbols, commas, and common text
            cleaned = re.sub(r'[^\d]', '', price_str)
            
            if cleaned:
                return int(cleaned)
            else:
                return 0
                
        except Exception:
            return 0

    def _extract_suburb_from_location(self, location: str) -> str:
        """Extract suburb from location string"""
        try:
            # Simple extraction - take the first part before comma
            parts = location.split(',')
            if parts:
                return parts[0].strip()
            return location.strip()
        except Exception:
            return ""

    def _extract_state_from_location(self, location: str) -> str:
        """Extract state from location string"""
        try:
            # Look for Australian state abbreviations
            state_map = {
                'vic': 'VIC', 'victoria': 'VIC',
                'nsw': 'NSW', 'new south wales': 'NSW',
                'qld': 'QLD', 'queensland': 'QLD',
                'wa': 'WA', 'western australia': 'WA',
                'sa': 'SA', 'south australia': 'SA',
                'tas': 'TAS', 'tasmania': 'TAS',
                'act': 'ACT', 'australian capital territory': 'ACT',
                'nt': 'NT', 'northern territory': 'NT'
            }
            
            location_lower = location.lower()
            for key, value in state_map.items():
                if key in location_lower:
                    return value
                    
            # Default to VIC if not found
            return 'VIC'
            
        except Exception:
            return 'VIC'

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
