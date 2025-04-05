import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

# Import custom modules
from link_parser import LinkParser
from scrapers import get_scraper
from price_comparison import PriceComparison
from affiliate_manager import AffiliateManager
from translation_manager import TranslationManager
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Default language
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# User language preferences
user_languages = {}

# Initialize modules
link_parser = LinkParser()
price_comparison = PriceComparison()
affiliate_manager = AffiliateManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    await update.message.reply_text(TranslationManager.get_translation("welcome", language))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    await update.message.reply_text(TranslationManager.get_translation("help", language))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /language command to change language."""
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("العربية", callback_data="lang_ar"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    await update.message.reply_text(
        TranslationManager.get_translation("language_selection", language),
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("lang_"):
        language_code = query.data.split("_")[1]
        user_id = update.effective_user.id
        user_languages[user_id] = language_code
        
        await query.edit_message_text(
            text=TranslationManager.get_translation("language_set", language_code)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages that might contain product links."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    message_text = update.message.text
    
    # Check if the message contains a URL
    if "http" in message_text:
        await update.message.reply_text(TranslationManager.get_translation("processing", language))
        
        # Extract URLs from the message
        urls = re.findall(r'https?://[^\s]+', message_text)
        
        if not urls:
            await update.message.reply_text(TranslationManager.get_translation("invalid_link", language))
            return
        
        # Process the first URL found
        url = urls[0]
        
        # Parse the product link
        parse_result = link_parser.parse_product_link(url)
        
        if not parse_result.get('success', False):
            error_type = parse_result.get('error', 'unknown_error')
            
            if error_type == 'invalid_url':
                await update.message.reply_text(TranslationManager.get_translation("invalid_link", language))
            elif error_type == 'unsupported_platform':
                await update.message.reply_text(TranslationManager.get_translation("unsupported_platform", language))
            else:
                await update.message.reply_text(TranslationManager.get_translation("error_occurred", language))
            
            return
        
        # Get platform and product ID
        platform = parse_result.get('platform')
        product_id = parse_result.get('product_id')
        
        # Get the appropriate scraper
        scraper = get_scraper(platform)
        
        if not scraper:
            await update.message.reply_text(TranslationManager.get_translation("unsupported_platform", language))
            return
        
        # Get product details
        product_details = scraper.get_product_details(product_id)
        
        if not product_details.get('success', False):
            await update.message.reply_text(TranslationManager.get_translation("error_occurred", language))
            return
        
        # Inform user that we're searching for the product on other platforms
        await update.message.reply_text(TranslationManager.get_translation("searching", language))
        
        # Get all scrapers
        all_scrapers = {
            'amazon': get_scraper('amazon'),
            'aliexpress': get_scraper('aliexpress'),
            'noon': get_scraper('noon'),
            'temu': get_scraper('temu')
        }
        
        # Search for similar products across platforms
        similar_products = price_comparison.search_across_platforms(product_details, all_scrapers)
        
        # Inform user that we're comparing prices
        await update.message.reply_text(TranslationManager.get_translation("comparing", language))
        
        # Compare prices and sort by price
        sorted_products = price_comparison.compare_prices(similar_products)
        
        if not sorted_products:
            await update.message.reply_text(TranslationManager.get_translation("no_results", language))
            return
        
        # Inform user that we're generating affiliate links
        await update.message.reply_text(TranslationManager.get_translation("generating_links", language))
        
        # Add affiliate links to products
        products_with_affiliate = affiliate_manager.process_products_with_affiliate_links(sorted_products)
        
        # Format comparison results
        formatted_results = price_comparison.format_comparison_results(products_with_affiliate, language)
        
        # Create message with comparison results
        comparison_message = TranslationManager.format_price_comparison_message(formatted_results, language)
        
        # Create inline keyboard with affiliate links
        keyboard = []
        
        # Add button for cheapest option
        if formatted_results:
            cheapest = formatted_results[0]
            keyboard.append([
                InlineKeyboardButton(
                    TranslationManager.get_translation("view_product", language),
                    url=cheapest.get('affiliate_url', cheapest.get('url', ''))
                )
            ])
        
        # Add buttons for other options
        for product in formatted_results[1:]:
            platform_name = TranslationManager.get_platform_name(product.get('platform', ''), language)
            keyboard.append([
                InlineKeyboardButton(
                    f"{platform_name}",
                    url=product.get('affiliate_url', product.get('url', ''))
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send comparison results with inline keyboard
        await update.message.reply_text(
            comparison_message,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    else:
        # If no URL is found, provide help
        await update.message.reply_text(TranslationManager.get_translation("help", language))

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to notify the user about the error
    if update and update.effective_message:
        user_id = update.effective_user.id
        language = user_languages.get(user_id, DEFAULT_LANGUAGE)
        
        await update.effective_message.reply_text(TranslationManager.get_translation("error_occurred", language))

def main() -> None:
    """Start the bot."""
    # Start the keep-alive server
    keep_alive()
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Add callback query handler for button interactions
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
