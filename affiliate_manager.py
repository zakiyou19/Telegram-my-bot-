import os
import logging
import re
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AffiliateManager:
    """Class for managing affiliate links for different platforms."""
    
    def __init__(self):
        """Initialize the affiliate manager with API keys and affiliate IDs from environment variables."""
        # Amazon affiliate settings
        self.amazon_affiliate_id = os.getenv("AMAZON_AFFILIATE_ID")
        self.amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.amazon_partner_tag = os.getenv("AMAZON_PARTNER_TAG")
        
        # AliExpress affiliate settings
        self.aliexpress_affiliate_id = os.getenv("ALIEXPRESS_AFFILIATE_ID")
        self.aliexpress_api_key = os.getenv("ALIEXPRESS_API_KEY")
        self.aliexpress_tracking_id = os.getenv("ALIEXPRESS_TRACKING_ID")
        
        # Noon affiliate settings
        self.noon_affiliate_id = os.getenv("NOON_AFFILIATE_ID")
        self.noon_api_key = os.getenv("NOON_API_KEY")
        
        # Temu affiliate settings
        self.temu_affiliate_id = os.getenv("TEMU_AFFILIATE_ID")
        self.temu_api_key = os.getenv("TEMU_API_KEY")
    
    def convert_to_affiliate_link(self, url, platform):
        """
        Convert a regular product URL to an affiliate URL.
        
        Args:
            url (str): The original product URL
            platform (str): The platform name
            
        Returns:
            str: The affiliate URL
        """
        if platform.lower() == 'amazon':
            return self.create_amazon_affiliate_link(url)
        elif platform.lower() == 'aliexpress':
            return self.create_aliexpress_affiliate_link(url)
        elif platform.lower() == 'noon':
            return self.create_noon_affiliate_link(url)
        elif platform.lower() == 'temu':
            return self.create_temu_affiliate_link(url)
        else:
            return url  # Return original URL if platform not supported
    
    def create_amazon_affiliate_link(self, url):
        """
        Create an Amazon affiliate link.
        
        Args:
            url (str): The original Amazon product URL
            
        Returns:
            str: The Amazon affiliate URL
        """
        if not self.amazon_partner_tag:
            return url
        
        # Extract ASIN if present
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            asin = asin_match.group(1)
            
            # If we have PA-API credentials, we could use the API to generate the link
            if all([self.amazon_access_key, self.amazon_secret_key, self.amazon_partner_tag]):
                # TODO: Implement PA-API call for more advanced affiliate link generation
                # For now, we'll use a simple tag-based approach
                pass
            
            # Simple tag-based approach
            base_url = f"https://www.amazon.com/dp/{asin}"
            return f"{base_url}?tag={self.amazon_partner_tag}"
        
        # If no ASIN found, just append the tag to the URL
        if '?' in url:
            return f"{url}&tag={self.amazon_partner_tag}"
        else:
            return f"{url}?tag={self.amazon_partner_tag}"
    
    def create_aliexpress_affiliate_link(self, url):
        """
        Create an AliExpress affiliate link.
        
        Args:
            url (str): The original AliExpress product URL
            
        Returns:
            str: The AliExpress affiliate URL
        """
        if not self.aliexpress_tracking_id:
            return url
        
        # Extract product ID if present
        product_id_match = re.search(r'/item/(\d+)\.html', url)
        if product_id_match:
            product_id = product_id_match.group(1)
            
            # If we have API credentials, we could use the API to generate the link
            if all([self.aliexpress_api_key, self.aliexpress_tracking_id]):
                # TODO: Implement API call for more advanced affiliate link generation
                # For now, we'll use a simple parameter-based approach
                pass
            
            # Simple parameter-based approach
            base_url = f"https://www.aliexpress.com/item/{product_id}.html"
            return f"{base_url}?aff_platform=portals-tool&sk=_dYQF9xF&aff_trace_key={self.aliexpress_tracking_id}"
        
        # If no product ID found, just append the tracking ID to the URL
        if '?' in url:
            return f"{url}&aff_trace_key={self.aliexpress_tracking_id}"
        else:
            return f"{url}?aff_trace_key={self.aliexpress_tracking_id}"
    
    def create_noon_affiliate_link(self, url):
        """
        Create a Noon affiliate link.
        
        Args:
            url (str): The original Noon product URL
            
        Returns:
            str: The Noon affiliate URL
        """
        if not self.noon_affiliate_id:
            return url
        
        # Extract product ID if present
        product_id_match = re.search(r'/([A-Za-z0-9]+)(?:\?.*)?$', url)
        if product_id_match:
            product_id = product_id_match.group(1)
            
            # If we have API credentials, we could use the API to generate the link
            if self.noon_api_key:
                # TODO: Implement API call for more advanced affiliate link generation
                # For now, we'll use a simple parameter-based approach
                pass
            
            # Simple parameter-based approach
            base_url = f"https://www.noon.com/product/{product_id}"
            return f"{base_url}?utm_source=affiliate&utm_medium=cps&utm_campaign={self.noon_affiliate_id}"
        
        # If no product ID found, just append the affiliate ID to the URL
        if '?' in url:
            return f"{url}&utm_source=affiliate&utm_medium=cps&utm_campaign={self.noon_affiliate_id}"
        else:
            return f"{url}?utm_source=affiliate&utm_medium=cps&utm_campaign={self.noon_affiliate_id}"
    
    def create_temu_affiliate_link(self, url):
        """
        Create a Temu affiliate link.
        
        Args:
            url (str): The original Temu product URL
            
        Returns:
            str: The Temu affiliate URL
        """
        if not self.temu_affiliate_id:
            return url
        
        # Extract product ID if present
        product_id_match = re.search(r'product_([0-9]+)\.html', url)
        if product_id_match:
            product_id = product_id_match.group(1)
            
            # If we have API credentials, we could use the API to generate the link
            if self.temu_api_key:
                # TODO: Implement API call for more advanced affiliate link generation
                # For now, we'll use a simple parameter-based approach
                pass
            
            # Simple parameter-based approach
            base_url = f"https://www.temu.com/product_{product_id}.html"
            return f"{base_url}?refer_key={self.temu_affiliate_id}"
        
        # If no product ID found, just append the affiliate ID to the URL
        if '?' in url:
            return f"{url}&refer_key={self.temu_affiliate_id}"
        else:
            return f"{url}?refer_key={self.temu_affiliate_id}"
    
    def process_products_with_affiliate_links(self, products):
        """
        Process a list of products to add affiliate links.
        
        Args:
            products (list): List of product dictionaries
            
        Returns:
            list: List of products with affiliate links added
        """
        for product in products:
            platform = product.get('platform', '')
            url = product.get('url', '')
            
            if platform and url:
                affiliate_url = self.convert_to_affiliate_link(url, platform)
                product['affiliate_url'] = affiliate_url
        
        return products
