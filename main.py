"""
LinkVault Bot - Main Runner
A modern Telegram bot for secure channel link sharing
"""

import asyncio
import logging
from pyrogram import Client, idle
from config import Config
from database import db
from handlers import register_handlers  # Import the register function
from aiohttp import web
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LinkVaultBot:
    """Main bot class"""
    
    def __init__(self):
        self.app = Client(
            name="LinkVaultBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=4
        )
        self.web_app = None
        
        # Register all handlers
        register_handlers(self.app)
    
    async def health_check(self, request):
        """Health check endpoint for Render"""
        return web.Response(text="Link Bot CosmicBotz!", status=200)
    
    async def start_web_server(self):
        """Start a simple web server for Render (requires web service)"""
        self.web_app = web.Application()
        self.web_app.router.add_get('/', self.health_check)
        self.web_app.router.add_get('/health', self.health_check)
        
        port = int(os.environ.get('PORT', 8080))
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"🌐 Web server started on port {port}")
    
    async def start_bot(self):
        """Start the bot"""
        logger.info("🚀 Starting LinkVault Bot...")
        
        # Validate configuration
        if not Config.validate():
            logger.error("❌ Invalid configuration. Please check your .env file.")
            return
        
        # Initialize database
        await db.initialize()
        
        # Start web server for Render
        await self.start_web_server()
        
        # Start the bot
        await self.app.start()
        
        me = await self.app.get_me()
        
        # Save bot username to config
        Config.BOT_USERNAME = me.username
        
        logger.info(f"✅ Bot started successfully as @{me.username}")
        logger.info(f"📊 Bot ID: {me.id}")
        logger.info(f"👑 Owner ID: {Config.OWNER_ID}")
        logger.info(f"🔧 Version: {Config.BOT_VERSION}")
        
        # Start cleanup task
        asyncio.create_task(self.cleanup_task())
        
        # Keep bot running
        await idle()
    
    async def cleanup_task(self):
        """Periodic cleanup of expired links"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                logger.info("🗑️ Running cleanup task...")
                await db.cleanup_expired_links()
            except Exception as e:
                logger.error(f"❌ Cleanup task error: {e}")
    
    async def stop_bot(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping bot...")
        await self.app.stop()
        logger.info("✅ Bot stopped successfully")


async def main():
    """Main entry point"""
    bot = LinkVaultBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("⚠️ Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        await bot.stop_bot()


if __name__ == "__main__":
    asyncio.run(main())
