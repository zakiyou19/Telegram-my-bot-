import os
import time
import logging
from flask import Flask
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """Return a simple message to indicate the bot is running."""
    return "Telegram Price Comparison Bot is running!"

def run():
    """Run the Flask app."""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Start a thread to run the Flask app."""
    server = Thread(target=run)
    server.daemon = True
    server.start()
    logger.info("Keep-alive server started")
