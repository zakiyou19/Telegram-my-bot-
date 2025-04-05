import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TranslationManager:
    """Class for managing translations for multilingual support."""
    
    # Default language
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
    
    # Supported languages
    SUPPORTED_LANGUAGES = ["en", "ar"]
    
    # Translations dictionary
    translations = {
        "en": {
            # General messages
            "welcome": "Welcome to the Price Comparison Bot! Send me a product link from AliExpress, Amazon, Noon, or Temu, and I'll find the best deals for you.",
            "help": "This bot compares prices across different e-commerce platforms.\n\nCommands:\n/start - Start the bot\n/help - Show this help message\n/language - Change language\n\nJust send me a product link from AliExpress, Amazon, Noon, or Temu to get started!",
            "language_selection": "Please select your preferred language:",
            "english": "English",
            "arabic": "Arabic",
            "language_set": "Language set to English!",
            
            # Processing messages
            "processing": "Processing your link... This may take a moment.",
            "searching": "Searching for the product on other platforms...",
            "comparing": "Comparing prices across platforms...",
            "generating_links": "Generating affiliate links...",
            
            # Error messages
            "invalid_link": "Invalid link. Please send a product link from AliExpress, Amazon, Noon, or Temu.",
            "unsupported_platform": "Sorry, this platform is not supported yet. Currently supported platforms: AliExpress, Amazon, Noon, and Temu.",
            "error_occurred": "An error occurred while processing your request. Please try again later.",
            "no_results": "Sorry, I couldn't find any matching products on other platforms.",
            
            # Result messages
            "results_header": "🔍 Price Comparison Results:",
            "best_price": "Best price found on {}:",
            "price": "Price: {}",
            "rating": "Rating: {}",
            "view_product": "View Product",
            "original_product": "Original Product",
            "cheapest_option": "💰 Cheapest Option:",
            "other_options": "Other Options:",
            "platform": "Platform: {}",
            
            # Platform names
            "amazon": "Amazon",
            "aliexpress": "AliExpress",
            "noon": "Noon",
            "temu": "Temu"
        },
        "ar": {
            # General messages
            "welcome": "مرحبًا بك في بوت مقارنة الأسعار! أرسل لي رابط منتج من AliExpress أو Amazon أو Noon أو Temu، وسأجد أفضل العروض لك.",
            "help": "يقارن هذا البوت الأسعار عبر منصات التجارة الإلكترونية المختلفة.\n\nالأوامر:\n/start - بدء البوت\n/help - عرض رسالة المساعدة هذه\n/language - تغيير اللغة\n\nما عليك سوى إرسال رابط منتج من AliExpress أو Amazon أو Noon أو Temu للبدء!",
            "language_selection": "يرجى اختيار لغتك المفضلة:",
            "english": "الإنجليزية",
            "arabic": "العربية",
            "language_set": "تم ضبط اللغة على العربية!",
            
            # Processing messages
            "processing": "جاري معالجة الرابط الخاص بك... قد يستغرق هذا لحظة.",
            "searching": "جاري البحث عن المنتج على المنصات الأخرى...",
            "comparing": "مقارنة الأسعار عبر المنصات...",
            "generating_links": "إنشاء روابط الإحالة...",
            
            # Error messages
            "invalid_link": "رابط غير صالح. يرجى إرسال رابط منتج من AliExpress أو Amazon أو Noon أو Temu.",
            "unsupported_platform": "عذرًا، هذه المنصة غير مدعومة حاليًا. المنصات المدعومة حاليًا: AliExpress و Amazon و Noon و Temu.",
            "error_occurred": "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقًا.",
            "no_results": "عذرًا، لم أتمكن من العثور على أي منتجات مطابقة على المنصات الأخرى.",
            
            # Result messages
            "results_header": "🔍 نتائج مقارنة الأسعار:",
            "best_price": "أفضل سعر وجد على {}:",
            "price": "السعر: {}",
            "rating": "التقييم: {}",
            "view_product": "عرض المنتج",
            "original_product": "المنتج الأصلي",
            "cheapest_option": "💰 الخيار الأرخص:",
            "other_options": "خيارات أخرى:",
            "platform": "المنصة: {}",
            
            # Platform names
            "amazon": "أمازون",
            "aliexpress": "علي إكسبريس",
            "noon": "نون",
            "temu": "تيمو"
        }
    }
    
    @classmethod
    def get_translation(cls, key, language=None):
        """
        Get translation for a key in the specified language.
        
        Args:
            key (str): The translation key
            language (str): The language code (default: DEFAULT_LANGUAGE)
            
        Returns:
            str: The translated text
        """
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        # Ensure language is supported
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        # Get translation
        return cls.translations.get(language, {}).get(key, key)
    
    @classmethod
    def get_platform_name(cls, platform, language=None):
        """
        Get translated platform name.
        
        Args:
            platform (str): The platform code
            language (str): The language code (default: DEFAULT_LANGUAGE)
            
        Returns:
            str: The translated platform name
        """
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        # Ensure language is supported
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        # Get platform name
        return cls.translations.get(language, {}).get(platform.lower(), platform)
    
    @classmethod
    def format_price_comparison_message(cls, products, language=None):
        """
        Format price comparison results as a message.
        
        Args:
            products (list): List of product dictionaries sorted by price
            language (str): The language code (default: DEFAULT_LANGUAGE)
            
        Returns:
            str: Formatted message
        """
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        if not products:
            return cls.get_translation("no_results", language)
        
        message = [cls.get_translation("results_header", language)]
        
        # Add cheapest option
        cheapest = products[0]
        message.append(f"\n{cls.get_translation('cheapest_option', language)}")
        message.append(f"🏷️ {cheapest.get('name', '')}")
        message.append(f"💲 {cls.get_translation('price', language).format(cheapest.get('price', ''))}")
        
        if cheapest.get('rating', ''):
            message.append(f"⭐ {cls.get_translation('rating', language).format(cheapest.get('rating', ''))}")
        
        platform_name = cls.get_platform_name(cheapest.get('platform', ''), language)
        message.append(f"🏪 {cls.get_translation('platform', language).format(platform_name)}")
        
        # Add other options if available
        if len(products) > 1:
            message.append(f"\n{cls.get_translation('other_options', language)}")
            
            for product in products[1:]:
                platform_name = cls.get_platform_name(product.get('platform', ''), language)
                message.append(f"\n🏪 {platform_name}")
                message.append(f"🏷️ {product.get('name', '')}")
                message.append(f"💲 {product.get('price', '')}")
                
                if product.get('rating', ''):
                    message.append(f"⭐ {product.get('rating', '')}")
        
        return "\n".join(message)
