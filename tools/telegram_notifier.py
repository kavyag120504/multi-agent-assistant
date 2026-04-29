import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_telegram(message: str) -> bool:
    """
    Send a message to your Telegram chat via bot.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env

    Setup (2 minutes):
    1. Open Telegram, search @BotFather
    2. Send /newbot, follow prompts → get your BOT_TOKEN
    3. Start a chat with your new bot, send any message
    4. Visit: https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
    5. Copy the "id" value from "chat" → that's your CHAT_ID
    6. Add both to .env:
       TELEGRAM_BOT_TOKEN=123456:ABCdef...
       TELEGRAM_CHAT_ID=987654321
    """
    token   = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning(
            "Telegram not configured. Add TELEGRAM_BOT_TOKEN and "
            "TELEGRAM_CHAT_ID to your .env file."
        )
        return False

    try:
        url  = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
        if resp.status_code == 200:
            logger.info("Telegram reminder sent successfully.")
            return True
        else:
            logger.error(f"Telegram API error {resp.status_code}: {resp.text}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("Telegram: no internet connection.")
        return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False
