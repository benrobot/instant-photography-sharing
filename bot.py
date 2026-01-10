#!/usr/bin/env python3
"""
Instant Photo Sharing Bot - Alpha Release

A Telegram bot that receives photos from photographer and instantly
distributes them to registered guests.

Usage:
    - Guests: Send /start to register
    - Photographer: Send photos to the bot, they'll be forwarded to all guests
    - Admin: Send /guests to see registered users
"""

import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PHOTOGRAPHER_USERNAME = os.getenv('PHOTOGRAPHER_USERNAME', '')  # Optional: restrict who can upload
DB_PATH = os.getenv('DB_PATH', 'photo_sharing.db')


class PhotoSharingBot:
    """Main bot class handling photo distribution"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing guest registrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guests (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                photo_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                photographer_id INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                caption TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def register_guest(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None) -> bool:
        """Register a guest to receive photos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO guests (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
            logger.info(f"Registered guest: {user_id} (@{username})")
            return True
        except Exception as e:
            logger.error(f"Error registering guest: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_guests(self) -> list:
        """Get list of all registered guests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, first_name, last_name, registered_at, photo_count FROM guests')
        guests = cursor.fetchall()
        conn.close()
        
        return guests
    
    def increment_photo_count(self, user_id: int):
        """Increment the photo count for a guest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE guests SET photo_count = photo_count + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def log_photo(self, file_id: str, photographer_id: int, caption: str = None):
        """Log an uploaded photo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO photos (file_id, photographer_id, caption)
            VALUES (?, ?, ?)
        ''', (file_id, photographer_id, caption))
        conn.commit()
        conn.close()


# Initialize bot instance
bot_instance = PhotoSharingBot(DB_PATH)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - register guest"""
    user = update.effective_user
    
    # Register the user
    success = bot_instance.register_guest(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    if success:
        welcome_message = (
            f"Welcome {user.first_name}! 🎉\n\n"
            f"You're now registered to receive event photos instantly.\n\n"
            f"Photos will be sent to you automatically as they're taken by the photographer.\n\n"
            f"Enjoy the event! 📸"
        )
    else:
        welcome_message = "Sorry, there was an error registering you. Please try again."
    
    await update.message.reply_text(welcome_message)


async def guests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /guests command - list all registered guests (photographer only)"""
    guests = bot_instance.get_all_guests()
    
    if not guests:
        await update.message.reply_text("No guests registered yet.")
        return
    
    message = f"📋 Registered Guests ({len(guests)}):\n\n"
    
    for user_id, username, first_name, last_name, registered_at, photo_count in guests:
        name = f"{first_name or ''} {last_name or ''}".strip()
        username_str = f"@{username}" if username else "no username"
        message += f"• {name} ({username_str}) - {photo_count} photos\n"
    
    await update.message.reply_text(message)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show statistics"""
    guests = bot_instance.get_all_guests()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM photos')
    total_photos = cursor.fetchone()[0]
    conn.close()
    
    stats_message = (
        f"📊 Event Statistics:\n\n"
        f"Registered Guests: {len(guests)}\n"
        f"Photos Shared: {total_photos}\n"
        f"Average Photos/Guest: {total_photos / len(guests) if guests else 0:.1f}"
    )
    
    await update.message.reply_text(stats_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📸 Instant Photo Sharing Bot\n\n"
        "Available Commands:\n"
        "/start - Register to receive photos\n"
        "/guests - List all registered guests\n"
        "/stats - Show event statistics\n"
        "/help - Show this help message\n\n"
        "How it works:\n"
        "1. Send /start to register\n"
        "2. Wait for the photographer to take photos\n"
        "3. Receive photos instantly!\n\n"
        "Note: Photos sent to this bot will be distributed to all registered guests."
    )
    
    await update.message.reply_text(help_text)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos from photographer"""
    user = update.effective_user
    photo = update.message.photo[-1]  # Get highest resolution
    caption = update.message.caption or ""
    
    # Optional: Check if sender is authorized photographer
    if PHOTOGRAPHER_USERNAME and user.username != PHOTOGRAPHER_USERNAME:
        await update.message.reply_text(
            "Only the photographer can upload photos to this bot."
        )
        return
    
    # Log the photo
    bot_instance.log_photo(photo.file_id, user.id, caption)
    
    # Get all registered guests
    guests = bot_instance.get_all_guests()
    
    if not guests:
        await update.message.reply_text(
            "Photo received, but no guests are registered yet. "
            "Photos will be sent once guests register with /start"
        )
        return
    
    # Send photo to all guests
    success_count = 0
    fail_count = 0
    
    for user_id, username, first_name, _, _, _ in guests:
        # Don't send back to photographer
        if user_id == user.id:
            continue
        
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo.file_id,
                caption=caption
            )
            bot_instance.increment_photo_count(user_id)
            success_count += 1
            logger.info(f"Sent photo to {user_id} (@{username})")
        except Exception as e:
            fail_count += 1
            logger.error(f"Failed to send photo to {user_id}: {e}")
    
    # Confirm to photographer
    confirmation = (
        f"✅ Photo distributed!\n\n"
        f"Sent to: {success_count} guests\n"
    )
    if fail_count > 0:
        confirmation += f"Failed: {fail_count} guests\n"
    
    await update.message.reply_text(confirmation)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (fallback)"""
    await update.message.reply_text(
        "Send /start to register for photos, or /help for more information."
    )


def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("guests", guests_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
