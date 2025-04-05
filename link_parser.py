import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class LinkParser:
    """Class for parsing and validating product links from different e-commerce platforms."""
    
    # Supported platforms and their domain patterns
    SUPPORTED_PLATFORMS = {
        'amazon': r'amazon\.(com|co\.uk|de|fr|it|es|ca|com\.au|com\.br|nl|in|jp|ae)',
        'aliexpress': r'aliexpress\.(com|ru)',
        'noon': r'noon\.(com|com\.eg|com\.sa)',
        'temu': r'temu\.(com)'
    }
    
    @staticmethod
    def validate_url(url):
        """
        Validate if the URL is properly formatted.
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if the URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def detect_platform(url):
        """
        Detect which e-commerce platform the URL belongs to.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            str or None: Platform name if detected, None otherwise
        """
        if not LinkParser.validate_url(url):
            return None
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        for platform, pattern in LinkParser.SUPPORTED_PLATFORMS.items():
            if re.search(pattern, domain):
                return platform
        
        return None
    
    @staticmethod
    def extract_product_id(url, platform):
        """
        Extract product ID from the URL based on the platform.
        
        Args:
            url (str): The product URL
            platform (str): The detected platform
            
        Returns:
            str or None: Product ID if found, None otherwise
        """
        if platform == 'amazon':
            # Amazon product IDs are typically in the URL as /dp/XXXXXXXXXX or /gp/product/XXXXXXXXXX
            dp_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if dp_match:
                return dp_match.group(1)
            
            gp_match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
            if gp_match:
                return gp_match.group(1)
                
        elif platform == 'aliexpress':
            # AliExpress product IDs are typically in the URL as /item/XXXXXXXX.html
            item_match = re.search(r'/item/(\d+)\.html', url)
            if item_match:
                return item_match.group(1)
                
        elif platform == 'noon':
            # Noon product IDs are typically at the end of the URL after the last /
            noon_match = re.search(r'/([A-Za-z0-9]+)(?:\?.*)?$', url)
            if noon_match:
                return noon_match.group(1)
                
        elif platform == 'temu':
            # Temu product IDs might be in various formats
            # This is a simplified version, might need adjustment based on actual URL structure
            temu_match = re.search(r'_([0-9]+)_', url)
            if temu_match:
                return temu_match.group(1)
        
        return None
    
    @staticmethod
    def parse_product_link(url):
        """
        Parse a product link to extract platform and product ID.
        
        Args:
            url (str): The product URL to parse
            
        Returns:
            dict: A dictionary containing platform and product_id if successful,
                  or error information if parsing fails
        """
        if not LinkParser.validate_url(url):
            return {
                'success': False,
                'error': 'invalid_url',
                'message': 'The provided URL is not valid'
            }
        
        platform = LinkParser.detect_platform(url)
        if not platform:
            return {
                'success': False,
                'error': 'unsupported_platform',
                'message': 'The platform is not supported'
            }
        
        product_id = LinkParser.extract_product_id(url, platform)
        if not product_id:
            return {
                'success': False,
                'error': 'product_id_not_found',
                'message': 'Could not extract product ID from the URL'
            }
        
        return {
            'success': True,
            'platform': platform,
            'product_id': product_id,
            'original_url': url
        }
