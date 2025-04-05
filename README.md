# Telegram Price Comparison Bot

A Telegram bot that compares product prices across multiple e-commerce platforms and generates affiliate links.

## Features

- Receives product links from AliExpress, Amazon, Noon, and Temu
- Automatically detects product details from the provided URL
- Searches for the same or similar products on other platforms
- Compares prices and retrieves available information
- Converts each product link into personal affiliate URLs
- Shows results with the cheapest option first
- Supports both Arabic and English languages

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A Telegram bot token (get it from [@BotFather](https://t.me/BotFather))
- Affiliate IDs for the supported platforms

### Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install python-telegram-bot requests beautifulsoup4 python-dotenv flask
   ```
4. Create a `.env` file based on the `.env.example` template and fill in your credentials
5. Run the bot:
   ```
   python main.py
   ```

### Replit Deployment

1. Create a new Replit project
2. Upload all the files to your Replit project
3. Add your environment variables in the Replit Secrets tab:
   - TELEGRAM_BOT_TOKEN
   - AMAZON_AFFILIATE_ID
   - AMAZON_ACCESS_KEY
   - AMAZON_SECRET_KEY
   - AMAZON_PARTNER_TAG
   - ALIEXPRESS_AFFILIATE_ID
   - ALIEXPRESS_API_KEY
   - ALIEXPRESS_TRACKING_ID
   - NOON_AFFILIATE_ID
   - NOON_API_KEY
   - TEMU_AFFILIATE_ID
   - TEMU_API_KEY
   - DEFAULT_LANGUAGE
4. Install the required packages:
   ```
   pip install python-telegram-bot requests beautifulsoup4 python-dotenv flask
   ```
5. Set the run command to:
   ```
   python main.py
   ```
6. Click Run to start the bot

## Usage

1. Start a chat with your bot on Telegram
2. Send the command `/start` to get started
3. Use `/help` to see available commands
4. Use `/language` to switch between English and Arabic
5. Send a product link from any supported platform (AliExpress, Amazon, Noon, or Temu)
6. The bot will process the link and return price comparisons with affiliate links

## Project Structure

- `main.py`: Main bot file that integrates all components
- `link_parser.py`: Handles URL validation and product ID extraction
- `scrapers.py`: Platform-specific scrapers for product data
- `price_comparison.py`: Logic for comparing products and prices
- `affiliate_manager.py`: Handles affiliate link generation
- `translation_manager.py`: Manages multilingual support
- `keep_alive.py`: Flask server for maintaining uptime on Replit

## Adding New Platforms

To add support for a new platform:

1. Update the `SUPPORTED_PLATFORMS` dictionary in `link_parser.py`
2. Create a new scraper class in `scrapers.py` that extends `ProductScraper`
3. Add affiliate link generation logic in `affiliate_manager.py`
4. Add platform translations in `translation_manager.py`

## Troubleshooting

- If the bot doesn't respond, check if your Telegram bot token is correct
- If price comparison doesn't work, ensure your internet connection is stable
- If affiliate links don't work, verify your affiliate IDs in the .env file

## License

This project is licensed under the MIT License - see the LICENSE file for details.
