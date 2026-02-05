"""
LinkVault Bot - Configuration
A modern Telegram bot for secure channel link sharing
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration settings"""
    
    # Telegram API Credentials
    API_ID: int = int(os.environ.get("API_ID", ""))
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # Bot Administration
    OWNER_ID: int = int(os.environ.get("OWNER_ID", ""))
    ADMIN_IDS: List[int] = [
        int(x) for x in os.environ.get("ADMIN_IDS", "").split() if x.strip()
    ]
    
    # Database Configuration
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    DATABASE_NAME: str = os.environ.get("DATABASE_NAME", "")
    
    # Storage Channel
    STORAGE_CHANNEL_ID: int = int(os.environ.get("STORAGE_CHANNEL_ID", ""))
    
    # Bot Settings
    LINK_EXPIRY_MINUTES: int = int(os.environ.get("LINK_EXPIRY_MINUTES", "5"))
    MAX_CHANNELS_PER_PAGE: int = 8
    AUTO_APPROVE_ENABLED: bool = os.environ.get("AUTO_APPROVE", "False").lower() == "true"
    
    # Messages & UI
    BOT_NAME: str = "Subaru Link"
    BOT_VERSION: str = "2.0"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = {
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "BOT_TOKEN": cls.BOT_TOKEN,
            "OWNER_ID": cls.OWNER_ID,
            "DATABASE_URL": cls.DATABASE_URL,
            "STORAGE_CHANNEL_ID": cls.STORAGE_CHANNEL_ID,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            print(f"❌ Missing required config: {', '.join(missing)}")
            return False
        
        return True
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin or owner"""
        return user_id == cls.OWNER_ID or user_id in cls.ADMIN_IDS


# Color schemes for UI
class Colors:
    PRIMARY = "🔵"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LINK = "🔗"
    CHANNEL = "📢"
    STATS = "📊"
    ADMIN = "👑"
    USER = "👤"
    TIME = "⏱️"
    FIRE = "🔥"
