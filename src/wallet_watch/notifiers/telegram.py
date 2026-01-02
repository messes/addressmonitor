"""Telegram notification provider."""

import logging
import re
from typing import Any

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from wallet_watch.notifiers.base import NotifierBase


logger = logging.getLogger(__name__)


class TelegramNotifier(NotifierBase):
    """Telegram bot notification provider."""

    name = "telegram"

    def __init__(self, bot_token: str = "", chat_id: str = "", **kwargs):
        super().__init__(**kwargs)

        if not bot_token:
            raise ValueError("Telegram bot_token is required")

        self.bot_token = bot_token
        self.default_chat_id = chat_id
        self.bot = telebot.TeleBot(bot_token)
        self.subscribers: set[str] = set()

        if chat_id:
            self.subscribers.add(chat_id)

    def send(self, message: str, **kwargs) -> bool:
        """Send message to all subscribers."""
        if not self.subscribers:
            logger.warning("No Telegram subscribers configured")
            return False

        success = True
        for chat_id in self.subscribers:
            if not self.send_to(chat_id, message, **kwargs):
                success = False

        return success

    def send_to(self, recipient: str, message: str, **kwargs) -> bool:
        """Send message to a specific chat."""
        try:
            # Check for inline keyboard
            keyboard = kwargs.get("keyboard")
            reply_markup = None
            if keyboard:
                reply_markup = self._build_keyboard(keyboard)

            self.bot.send_message(
                chat_id=recipient,
                text=message,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
            logger.debug(f"Sent Telegram message to {recipient}")
            return True

        except telebot.apihelper.ApiTelegramException as e:
            if "blocked" in str(e).lower():
                logger.warning(f"Bot blocked by user {recipient}")
                self.subscribers.discard(recipient)
            else:
                logger.error(f"Telegram API error: {e}")
            return False

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def format_message(self, message: str) -> str:
        """Escape special characters for Telegram HTML."""
        # Only escape HTML special characters
        message = message.replace("&", "&amp;")
        message = message.replace("<", "&lt;")
        message = message.replace(">", "&gt;")
        return message

    def _build_keyboard(self, keyboard: list[list[dict]]) -> InlineKeyboardMarkup:
        """Build inline keyboard from config."""
        markup = InlineKeyboardMarkup()

        for row in keyboard:
            buttons = []
            for btn in row:
                if "url" in btn:
                    buttons.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                elif "callback" in btn:
                    buttons.append(InlineKeyboardButton(btn["text"], callback_data=btn["callback"]))
            if buttons:
                markup.row(*buttons)

        return markup

    def add_subscriber(self, chat_id: str) -> None:
        """Add a subscriber."""
        self.subscribers.add(chat_id)
        logger.info(f"Added Telegram subscriber: {chat_id}")

    def remove_subscriber(self, chat_id: str) -> None:
        """Remove a subscriber."""
        self.subscribers.discard(chat_id)
        logger.info(f"Removed Telegram subscriber: {chat_id}")

    def start_polling(self) -> None:
        """Start bot in polling mode for interactive features."""
        logger.info("Starting Telegram bot polling...")
        self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
