import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

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

# Language settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Translations dictionary
translations = {
    "en": {
        "welcome": "Welcome to the Price Comparison Bot! Send me a product link from AliExpress, Amazon, Noon, or Temu, and I'll find the best deals for you.",
        "help": "This bot compares prices across different e-commerce platforms.\n\nCommands:\n/start - Start the bot\n/help - Show this help message\n/language - Change language\n\nJust send me a product link from AliExpress, Amazon, Noon, or Temu to get started!",
        "language_selection": "Please select your preferred language:",
        "english": "English",
        "arabic": "Arabic",
        "language_set": "Language set to English!",
        "processing": "Processing your link... This may take a moment.",
        "invalid_link": "Invalid link. Please send a product link from AliExpress, Amazon, Noon, or Temu.",
        "unsupported_platform": "Sorry, this platform is not supported yet. Currently supported platforms: AliExpress, Amazon, Noon, and Temu.",
        "error_occurred": "An error occurred while processing your request. Please try again later.",
        "no_results": "Sorry, I couldn't find any matching products on other platforms.",
        "best_price": "Best price found on {}:",
        "price": "Price: {}",
        "rating": "Rating: {}",
        "view_product": "View Product"
    },
    "ar": {
        "welcome": "مرحبًا بك في بوت مقارنة الأسعار! أرسل لي رابط منتج من AliExpress أو Amazon أو Noon أو Temu، وسأجد أفضل العروض لك.",
        "help": "يقارن هذا البوت الأسعار عبر منصات التجارة الإلكترونية المختلفة.\n\nالأوامر:\n/start - بدء البوت\n/help - عرض رسالة المساعدة هذه\n/language - تغيير اللغة\n\nما عليك سوى إرسال رابط منتج من AliExpress أو Amazon أو Noon أو Temu للبدء!",
        "language_selection": "يرجى اختيار لغتك المفضلة:",
        "english": "الإنجليزية",
        "arabic": "العربية",
        "language_set": "تم ضبط اللغة على العربية!",
        "processing": "جاري معالجة الرابط الخاص بك... قد يستغرق هذا لحظة.",
        "invalid_link": "رابط غير صالح. يرجى إرسال رابط منتج من AliExpress أو Amazon أو Noon أو Temu.",
        "unsupported_platform": "عذرًا، هذه المنصة غير مدعومة حاليًا. المنصات المدعومة حاليًا: AliExpress و Amazon و Noon و Temu.",
        "error_occurred": "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقًا.",
        "no_results": "عذرًا، لم أتمكن من العثور على أي منتجات مطابقة على المنصات الأخرى.",
        "best_price": "أفضل سعر وجد على {}:",
        "price": "السعر: {}",
        "rating": "التقييم: {}",
        "view_product": "عرض المنتج"
    }
}

# User language preferences
user_languages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    await update.message.reply_text(translations[language]["welcome"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    await update.message.reply_text(translations[language]["help"])

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
        translations[language]["language_selection"],
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
            text=translations[language_code]["language_set"]
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages that might contain product links."""
    user_id = update.effective_user.id
    language = user_languages.get(user_id, DEFAULT_LANGUAGE)
    message_text = update.message.text
    
    # Check if the message contains a URL
    if "http" in message_text:
        await update.message.reply_text(translations[language]["processing"])
        
        # TODO: Implement URL validation and product link processing
        # This will be implemented in the next steps
        
        # For now, just respond with a placeholder message
        await update.message.reply_text("This feature will be implemented soon!")
    else:
        # If no URL is found, provide help
        await update.message.reply_text(translations[language]["help"])

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to notify the user about the error
    if update and update.effective_message:
        user_id = update.effective_user.id
        language = user_languages.get(user_id, DEFAULT_LANGUAGE)
        
        await update.effective_message.reply_text(translations[language]["error_occurred"])

def main() -> None:
    """Start the bot."""
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
