import os
import logging
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ProductScraper(ABC):
    """Abstract base class for platform-specific product scrapers."""
    
    @abstractmethod
    def get_product_details(self, product_id):
        """
        Get product details from the platform.
        
        Args:
            product_id (str): The product ID to look up
            
        Returns:
            dict: Product details including name, price, rating, etc.
        """
        pass
    
    @abstractmethod
    def search_product(self, query):
        """
        Search for products using a query string.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of product results
        """
        pass
    
    @abstractmethod
    def generate_affiliate_link(self, product_id):
        """
        Generate an affiliate link for the product.
        
        Args:
            product_id (str): The product ID
            
        Returns:
            str: The affiliate link
        """
        pass


class AmazonScraper(ProductScraper):
    """Scraper for Amazon products using Amazon PA-API."""
    
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.partner_tag = os.getenv("AMAZON_PARTNER_TAG")
        self.affiliate_id = os.getenv("AMAZON_AFFILIATE_ID")
        
        # Check if credentials are available
        self.api_available = all([self.access_key, self.secret_key, self.partner_tag])
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_product_details(self, product_id):
        """
        Get Amazon product details using PA-API or fallback to scraping.
        
        Args:
            product_id (str): The Amazon ASIN
            
        Returns:
            dict: Product details
        """
        if self.api_available:
            # TODO: Implement PA-API request
            # This would require the python-amazon-paapi library or custom implementation
            # For now, we'll use a placeholder
            logger.info(f"PA-API would be used for product {product_id}")
            
        # Fallback to scraping if API is not available or fails
        try:
            url = f"https://www.amazon.com/dp/{product_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': 'request_failed',
                    'message': f'Failed to fetch product data: {response.status_code}'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name
            product_name_elem = soup.select_one('#productTitle')
            product_name = product_name_elem.get_text().strip() if product_name_elem else "Unknown Product"
            
            # Extract price
            price_elem = soup.select_one('.a-price .a-offscreen')
            price = price_elem.get_text().strip() if price_elem else "Price not available"
            
            # Extract rating
            rating_elem = soup.select_one('#acrPopover')
            rating = rating_elem.get('title', 'No ratings').strip() if rating_elem else "No ratings"
            
            # Extract image URL
            image_elem = soup.select_one('#landingImage')
            image_url = image_elem.get('src') if image_elem else None
            
            return {
                'success': True,
                'platform': 'amazon',
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'rating': rating,
                'image_url': image_url,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Amazon product {product_id}: {str(e)}")
            return {
                'success': False,
                'error': 'scraping_error',
                'message': f'Error scraping product data: {str(e)}'
            }
    
    def search_product(self, query):
        """
        Search for products on Amazon.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of product results
        """
        if self.api_available:
            # TODO: Implement PA-API search
            # For now, we'll use a placeholder
            logger.info(f"PA-API would be used for search: {query}")
        
        # Fallback to scraping
        try:
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product cards
            product_cards = soup.select('.s-result-item[data-asin]:not([data-asin=""])')
            
            for card in product_cards[:5]:  # Limit to first 5 results
                asin = card.get('data-asin')
                
                # Extract product name
                name_elem = card.select_one('h2 a span')
                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                
                # Extract price
                price_elem = card.select_one('.a-price .a-offscreen')
                price = price_elem.get_text().strip() if price_elem else "Price not available"
                
                # Extract rating
                rating_elem = card.select_one('.a-icon-star-small')
                rating = rating_elem.get_text().strip() if rating_elem else "No ratings"
                
                # Extract image URL
                image_elem = card.select_one('img.s-image')
                image_url = image_elem.get('src') if image_elem else None
                
                products.append({
                    'platform': 'amazon',
                    'product_id': asin,
                    'name': name,
                    'price': price,
                    'rating': rating,
                    'image_url': image_url,
                    'url': f"https://www.amazon.com/dp/{asin}"
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching Amazon for {query}: {str(e)}")
            return []
    
    def generate_affiliate_link(self, product_id):
        """
        Generate an Amazon affiliate link.
        
        Args:
            product_id (str): The Amazon ASIN
            
        Returns:
            str: The affiliate link
        """
        if not self.partner_tag:
            return f"https://www.amazon.com/dp/{product_id}"
        
        return f"https://www.amazon.com/dp/{product_id}?tag={self.partner_tag}"


class AliExpressScraper(ProductScraper):
    """Scraper for AliExpress products."""
    
    def __init__(self):
        self.api_key = os.getenv("ALIEXPRESS_API_KEY")
        self.tracking_id = os.getenv("ALIEXPRESS_TRACKING_ID")
        self.affiliate_id = os.getenv("ALIEXPRESS_AFFILIATE_ID")
        
        # Check if credentials are available
        self.api_available = all([self.api_key, self.tracking_id])
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_product_details(self, product_id):
        """
        Get AliExpress product details.
        
        Args:
            product_id (str): The AliExpress product ID
            
        Returns:
            dict: Product details
        """
        if self.api_available:
            # TODO: Implement AliExpress API request
            # For now, we'll use a placeholder
            logger.info(f"AliExpress API would be used for product {product_id}")
        
        # Fallback to scraping
        try:
            url = f"https://www.aliexpress.com/item/{product_id}.html"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': 'request_failed',
                    'message': f'Failed to fetch product data: {response.status_code}'
                }
            
            # AliExpress uses JavaScript to load product data, so scraping is limited
            # This is a simplified version that may not work reliably
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract product name from meta tags
            product_name = "Unknown Product"
            meta_title = soup.select_one('meta[property="og:title"]')
            if meta_title:
                product_name = meta_title.get('content', 'Unknown Product')
            
            # Try to extract price from meta tags
            price = "Price not available"
            meta_price = soup.select_one('meta[property="og:price:amount"]')
            if meta_price:
                price = meta_price.get('content', 'Price not available')
                currency = soup.select_one('meta[property="og:price:currency"]')
                if currency:
                    price = f"{price} {currency.get('content', 'USD')}"
            
            # Extract image URL
            image_url = None
            meta_image = soup.select_one('meta[property="og:image"]')
            if meta_image:
                image_url = meta_image.get('content')
            
            return {
                'success': True,
                'platform': 'aliexpress',
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'rating': "Rating not available",  # Difficult to extract reliably
                'image_url': image_url,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping AliExpress product {product_id}: {str(e)}")
            return {
                'success': False,
                'error': 'scraping_error',
                'message': f'Error scraping product data: {str(e)}'
            }
    
    def search_product(self, query):
        """
        Search for products on AliExpress.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of product results
        """
        if self.api_available:
            # TODO: Implement AliExpress API search
            # For now, we'll use a placeholder
            logger.info(f"AliExpress API would be used for search: {query}")
        
        # Fallback to scraping
        # Note: AliExpress search results are heavily JavaScript-dependent
        # This simplified version may not work reliably
        try:
            search_url = f"https://www.aliexpress.com/wholesale?SearchText={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                return []
            
            # This is a simplified version that may not work reliably
            # AliExpress uses JavaScript to load search results
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try to extract product cards
            # This selector may need to be updated based on AliExpress's current HTML structure
            product_cards = soup.select('.product-card')
            
            for card in product_cards[:5]:  # Limit to first 5 results
                # Extract product ID from URL
                link_elem = card.select_one('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                href = link_elem.get('href')
                product_id_match = re.search(r'/item/(\d+)\.html', href)
                if not product_id_match:
                    continue
                
                product_id = product_id_match.group(1)
                
                # Extract product name
                name_elem = card.select_one('.product-title')
                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                
                # Extract price
                price_elem = card.select_one('.product-price')
                price = price_elem.get_text().strip() if price_elem else "Price not available"
                
                # Extract image URL
                image_elem = card.select_one('img')
                image_url = image_elem.get('src') if image_elem else None
                
                products.append({
                    'platform': 'aliexpress',
                    'product_id': product_id,
                    'name': name,
                    'price': price,
                    'rating': "Rating not available",
                    'image_url': image_url,
                    'url': f"https://www.aliexpress.com/item/{product_id}.html"
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching AliExpress for {query}: {str(e)}")
            return []
    
    def generate_affiliate_link(self, product_id):
        """
        Generate an AliExpress affiliate link.
        
        Args:
            product_id (str): The AliExpress product ID
            
        Returns:
            str: The affiliate link
        """
        base_url = f"https://www.aliexpress.com/item/{product_id}.html"
        
        if not self.tracking_id:
            return base_url
        
        # Add affiliate parameters
        return f"{base_url}?aff_platform=portals-tool&sk=_dYQF9xF&aff_trace_key={self.tracking_id}"


class NoonScraper(ProductScraper):
    """Scraper for Noon products."""
    
    def __init__(self):
        self.api_key = os.getenv("NOON_API_KEY")
        self.affiliate_id = os.getenv("NOON_AFFILIATE_ID")
        
        # Check if credentials are available
        self.api_available = bool(self.api_key)
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_product_details(self, product_id):
        """
        Get Noon product details.
        
        Args:
            product_id (str): The Noon product ID
            
        Returns:
            dict: Product details
        """
        if self.api_available:
            # TODO: Implement Noon API request if available
            # For now, we'll use a placeholder
            logger.info(f"Noon API would be used for product {product_id}")
        
        # Fallback to scraping
        try:
            url = f"https://www.noon.com/product/{product_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': 'request_failed',
                    'message': f'Failed to fetch product data: {response.status_code}'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name
            product_name = "Unknown Product"
            meta_title = soup.select_one('meta[property="og:title"]')
            if meta_title:
                product_name = meta_title.get('content', 'Unknown Product')
            
            # Extract price
            price = "Price not available"
            price_elem = soup.select_one('[data-qa="product-price"]')
            if price_elem:
                price = price_elem.get_text().strip()
            
            # Extract rating
            rating = "Rating not available"
            rating_elem = soup.select_one('[data-qa="product-rating"]')
            if rating_elem:
                rating = rating_elem.get_text().strip()
            
            # Extract image URL
            image_url = None
            meta_image = soup.select_one('meta[property="og:image"]')
            if meta_image:
                image_url = meta_image.get('content')
            
            return {
                'success': True,
                'platform': 'noon',
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'rating': rating,
                'image_url': image_url,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Noon product {product_id}: {str(e)}")
            return {
                'success': False,
                'error': 'scraping_error',
                'message': f'Error scraping product data: {str(e)}'
            }
    
    def search_product(self, query):
        """
        Search for products on Noon.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of product results
        """
        if self.api_available:
            # TODO: Implement Noon API search if available
            # For now, we'll use a placeholder
            logger.info(f"Noon API would be used for search: {query}")
        
        # Fallback to scraping
        try:
            search_url = f"https://www.noon.com/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try to extract product cards
            # This selector may need to be updated based on Noon's current HTML structure
            product_cards = soup.select('[data-qa="product-card"]')
            
            for card in product_cards[:5]:  # Limit to first 5 results
                # Extract product ID from URL
                link_elem = card.select_one('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                href = link_elem.get('href')
                product_id_match = re.search(r'/([A-Za-z0-9]+)(?:\?.*)?$', href)
                if not product_id_match:
                    continue
                
                product_id = product_id_match.group(1)
                
                # Extract product name
                name_elem = card.select_one('[data-qa="product-name"]')
                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                
                # Extract price
                price_elem = card.select_one('[data-qa="product-price"]')
                price = price_elem.get_text().strip() if price_elem else "Price not available"
                
                # Extract rating
                rating_elem = card.select_one('[data-qa="product-rating"]')
                rating = rating_elem.get_text().strip() if rating_elem else "Rating not available"
                
                # Extract image URL
                image_elem = card.select_one('img')
                image_url = image_elem.get('src') if image_elem else None
                
                products.append({
                    'platform': 'noon',
                    'product_id': product_id,
                    'name': name,
                    'price': price,
                    'rating': rating,
                    'image_url': image_url,
                    'url': f"https://www.noon.com/product/{product_id}"
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching Noon for {query}: {str(e)}")
            return []
    
    def generate_affiliate_link(self, product_id):
        """
        Generate a Noon affiliate link.
        
        Args:
            product_id (str): The Noon product ID
            
        Returns:
            str: The affiliate link
        """
        base_url = f"https://www.noon.com/product/{product_id}"
        
        if not self.affiliate_id:
            return base_url
        
        # Add affiliate parameters
        return f"{base_url}?utm_source=affiliate&utm_medium=cps&utm_campaign={self.affiliate_id}"


class TemuScraper(ProductScraper):
    """Scraper for Temu products."""
    
    def __init__(self):
        self.api_key = os.getenv("TEMU_API_KEY")
        self.affiliate_id = os.getenv("TEMU_AFFILIATE_ID")
        
        # Check if credentials are available
        self.api_available = bool(self.api_key)
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_product_details(self, product_id):
        """
        Get Temu product details.
        
        Args:
            product_id (str): The Temu product ID
            
        Returns:
            dict: Product details
        """
        if self.api_available:
            # TODO: Implement Temu API request if available
            # For now, we'll use a placeholder
            logger.info(f"Temu API would be used for product {product_id}")
        
        # Fallback to scraping
        try:
            url = f"https://www.temu.com/product_{product_id}.html"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': 'request_failed',
                    'message': f'Failed to fetch product data: {response.status_code}'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name
            product_name = "Unknown Product"
            meta_title = soup.select_one('meta[property="og:title"]')
            if meta_title:
                product_name = meta_title.get('content', 'Unknown Product')
            
            # Extract price (Temu uses JavaScript to load prices, so this might not work reliably)
            price = "Price not available"
            price_elem = soup.select_one('.price')
            if price_elem:
                price = price_elem.get_text().strip()
            
            # Extract image URL
            image_url = None
            meta_image = soup.select_one('meta[property="og:image"]')
            if meta_image:
                image_url = meta_image.get('content')
            
            return {
                'success': True,
                'platform': 'temu',
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'rating': "Rating not available",  # Difficult to extract reliably
                'image_url': image_url,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Temu product {product_id}: {str(e)}")
            return {
                'success': False,
                'error': 'scraping_error',
                'message': f'Error scraping product data: {str(e)}'
            }
    
    def search_product(self, query):
        """
        Search for products on Temu.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of product results
        """
        if self.api_available:
            # TODO: Implement Temu API search if available
            # For now, we'll use a placeholder
            logger.info(f"Temu API would be used for search: {query}")
        
        # Fallback to scraping
        # Note: Temu search results are heavily JavaScript-dependent
        # This simplified version may not work reliably
        try:
            search_url = f"https://www.temu.com/search_result.html?search_key={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                return []
            
            # This is a simplified version that may not work reliably
            # Temu uses JavaScript to load search results
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try to extract product cards
            # This selector may need to be updated based on Temu's current HTML structure
            product_cards = soup.select('.product-item')
            
            for card in product_cards[:5]:  # Limit to first 5 results
                # Extract product ID from URL
                link_elem = card.select_one('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                href = link_elem.get('href')
                product_id_match = re.search(r'product_([0-9]+)\.html', href)
                if not product_id_match:
                    continue
                
                product_id = product_id_match.group(1)
                
                # Extract product name
                name_elem = card.select_one('.product-title')
                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                
                # Extract price
                price_elem = card.select_one('.price')
                price = price_elem.get_text().strip() if price_elem else "Price not available"
                
                # Extract image URL
                image_elem = card.select_one('img')
                image_url = image_elem.get('src') if image_elem else None
                
                products.append({
                    'platform': 'temu',
                    'product_id': product_id,
                    'name': name,
                    'price': price,
                    'rating': "Rating not available",
                    'image_url': image_url,
                    'url': f"https://www.temu.com/product_{product_id}.html"
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching Temu for {query}: {str(e)}")
            return []
    
    def generate_affiliate_link(self, product_id):
        """
        Generate a Temu affiliate link.
        
        Args:
            product_id (str): The Temu product ID
            
        Returns:
            str: The affiliate link
        """
        base_url = f"https://www.temu.com/product_{product_id}.html"
        
        if not self.affiliate_id:
            return base_url
        
        # Add affiliate parameters
        return f"{base_url}?refer_key={self.affiliate_id}"


# Factory function to get the appropriate scraper
def get_scraper(platform):
    """
    Get the appropriate scraper for a platform.
    
    Args:
        platform (str): The platform name
        
    Returns:
        ProductScraper: The appropriate scraper instance
    """
    scrapers = {
        'amazon': AmazonScraper(),
        'aliexpress': AliExpressScraper(),
        'noon': NoonScraper(),
        'temu': TemuScraper()
    }
    
    return scrapers.get(platform.lower())
