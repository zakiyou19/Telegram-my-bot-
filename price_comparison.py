import logging
import re
from difflib import SequenceMatcher
import unicodedata

logger = logging.getLogger(__name__)

class PriceComparison:
    """Class for comparing product prices across different platforms."""
    
    def __init__(self):
        """Initialize the price comparison module."""
        pass
    
    @staticmethod
    def normalize_text(text):
        """
        Normalize text for comparison by removing special characters and converting to lowercase.
        
        Args:
            text (str): The text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_numeric_price(price_str):
        """
        Extract numeric price from a price string.
        
        Args:
            price_str (str): The price string (e.g., "$99.99", "99,99 €")
            
        Returns:
            float or None: The numeric price if found, None otherwise
        """
        if not price_str or price_str == "Price not available":
            return None
        
        # Remove currency symbols and non-numeric characters except for decimal points
        # Replace comma with dot for decimal separator
        price_str = price_str.replace(',', '.')
        
        # Extract all numbers with decimal points
        matches = re.findall(r'\d+\.\d+|\d+', price_str)
        
        if matches:
            # Return the first match as a float
            return float(matches[0])
        
        return None
    
    @staticmethod
    def calculate_similarity(text1, text2):
        """
        Calculate similarity between two text strings.
        
        Args:
            text1 (str): First text string
            text2 (str): Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0
        
        # Normalize texts
        norm_text1 = PriceComparison.normalize_text(text1)
        norm_text2 = PriceComparison.normalize_text(text2)
        
        # Calculate similarity using SequenceMatcher
        return SequenceMatcher(None, norm_text1, norm_text2).ratio()
    
    @staticmethod
    def is_same_product(product1, product2, threshold=0.7):
        """
        Determine if two products are the same based on name similarity.
        
        Args:
            product1 (dict): First product details
            product2 (dict): Second product details
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            bool: True if products are likely the same, False otherwise
        """
        if not product1 or not product2:
            return False
        
        # Get product names
        name1 = product1.get('name', '')
        name2 = product2.get('name', '')
        
        # Calculate similarity
        similarity = PriceComparison.calculate_similarity(name1, name2)
        
        return similarity >= threshold
    
    def find_similar_products(self, source_product, candidate_products, threshold=0.7):
        """
        Find products similar to the source product from a list of candidates.
        
        Args:
            source_product (dict): Source product details
            candidate_products (list): List of candidate product details
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            list: List of similar products
        """
        similar_products = []
        
        for product in candidate_products:
            if self.is_same_product(source_product, product, threshold):
                similar_products.append(product)
        
        return similar_products
    
    def compare_prices(self, products):
        """
        Compare prices of products and sort by price.
        
        Args:
            products (list): List of product details
            
        Returns:
            list: List of products sorted by price (cheapest first)
        """
        # Filter out products without price
        products_with_price = []
        
        for product in products:
            price_str = product.get('price', 'Price not available')
            numeric_price = self.extract_numeric_price(price_str)
            
            if numeric_price is not None:
                # Add numeric price to product for sorting
                product['numeric_price'] = numeric_price
                products_with_price.append(product)
        
        # Sort products by price
        sorted_products = sorted(products_with_price, key=lambda x: x['numeric_price'])
        
        return sorted_products
    
    def search_across_platforms(self, source_product, scrapers):
        """
        Search for a product across different platforms.
        
        Args:
            source_product (dict): Source product details
            scrapers (dict): Dictionary of platform scrapers
            
        Returns:
            list: List of similar products from different platforms
        """
        similar_products = []
        
        # Add source product to the list
        similar_products.append(source_product)
        
        # Get product name for search
        product_name = source_product.get('name', '')
        if not product_name:
            return similar_products
        
        # Create search query from product name
        # Remove brand names and common words to improve search results
        search_query = product_name
        
        # Search on each platform except the source platform
        source_platform = source_product.get('platform', '')
        
        for platform, scraper in scrapers.items():
            if platform == source_platform:
                continue
            
            try:
                # Search for products
                search_results = scraper.search_product(search_query)
                
                # Find similar products
                platform_similar_products = self.find_similar_products(source_product, search_results)
                
                # Add to the list
                similar_products.extend(platform_similar_products)
                
            except Exception as e:
                logger.error(f"Error searching on {platform}: {str(e)}")
        
        return similar_products
    
    def format_comparison_results(self, products, language='en'):
        """
        Format comparison results for display.
        
        Args:
            products (list): List of products sorted by price
            language (str): Language code ('en' or 'ar')
            
        Returns:
            dict: Formatted results for display
        """
        # Translations for platform names
        platform_translations = {
            'en': {
                'amazon': 'Amazon',
                'aliexpress': 'AliExpress',
                'noon': 'Noon',
                'temu': 'Temu'
            },
            'ar': {
                'amazon': 'أمازون',
                'aliexpress': 'علي إكسبريس',
                'noon': 'نون',
                'temu': 'تيمو'
            }
        }
        
        formatted_results = []
        
        for product in products:
            platform = product.get('platform', '')
            platform_name = platform_translations.get(language, {}).get(platform, platform)
            
            formatted_product = {
                'platform': platform_name,
                'name': product.get('name', ''),
                'price': product.get('price', ''),
                'rating': product.get('rating', ''),
                'url': product.get('url', ''),
                'image_url': product.get('image_url', ''),
                'affiliate_url': product.get('affiliate_url', product.get('url', ''))
            }
            
            formatted_results.append(formatted_product)
        
        return formatted_results
