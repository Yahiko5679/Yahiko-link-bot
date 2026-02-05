"""
Database Models and Operations
Handles MongoDB operations for channels, users, and links
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from config import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database manager for MongoDB operations"""

    def __init__(self):
        self.client = AsyncIOMotorClient(Config.DATABASE_URL)
        self.db = self.client[Config.DATABASE_NAME]

        # Collections
        self.channels = self.db.channels
        self.users = self.db.users
        self.links = self.db.links
        self.settings = self.db.settings

    async def initialize(self):
        """Initialize database indexes"""
        try:
            await self.channels.create_index("channel_id", unique=True)
            await self.users.create_index("user_id", unique=True)
            await self.links.create_index("channel_id")
            await self.links.create_index("expires_at")
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")

    # ==================== CHANNEL OPERATIONS ====================

    async def add_channel(self, channel_id: int, channel_name: str,
                          invite_link: Optional[str] = None) -> bool:
        try:
            await self.channels.insert_one({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "invite_link": invite_link,
                "added_at": datetime.utcnow(),
                "updated_at": None,
                "total_joins": 0,
                "is_active": True,
                "auto_approve": False
            })
            logger.info(f"✅ Channel added: {channel_name} ({channel_id})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add channel: {e}")
            return False

    async def remove_channel(self, channel_id: int) -> bool:
        try:
            result = await self.channels.delete_one({"channel_id": channel_id})
            if result.deleted_count:
                await self.links.delete_many({"channel_id": channel_id})
                logger.info(f"✅ Channel removed: {channel_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to remove channel: {e}")
            return False

    async def get_channel(self, channel_id: int) -> Optional[Dict]:
        return await self.channels.find_one({"channel_id": channel_id})

    async def get_all_channels(self) -> List[Dict]:
        return await self.channels.find({"is_active": True}).to_list(None)

    async def increment_channel_joins(self, channel_id: int):
        await self.channels.update_one(
            {"channel_id": channel_id},
            {"$inc": {"total_joins": 1}}
        )

    # ==================== USER OPERATIONS ====================

    async def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> bool:
        """
        Add user safely (NO joined_at conflict)
        """
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "first_name": first_name,
                        "last_active": datetime.utcnow(),
                        "is_banned": False
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "joined_at": datetime.utcnow(),
                        "total_requests": 0
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add user: {e}")
            return False

    async def update_last_active(self, user_id: int):
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"last_active": datetime.utcnow()},
                "$inc": {"total_requests": 1}
            }
        )

    async def get_user(self, user_id: int) -> Optional[Dict]:
        return await self.users.find_one({"user_id": user_id})

    async def get_total_users(self) -> int:
        return await self.users.count_documents({})

    async def get_active_users(self, days: int = 7) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return await self.users.count_documents({"last_active": {"$gte": cutoff}})

    async def ban_user(self, user_id: int, banned: bool = True) -> bool:
        try:
            result = await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": banned}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Failed to ban user: {e}")
            return False

    # ==================== LINK OPERATIONS ====================

    async def save_link(self, channel_id: int, invite_link: str,
                        link_type: str = "invite") -> bool:
        try:
            await self.links.insert_one({
                "channel_id": channel_id,
                "invite_link": invite_link,
                "link_type": link_type,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=Config.LINK_EXPIRY_MINUTES),
                "uses": 0,
                "is_active": True
            })
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save link: {e}")
            return False

    async def get_active_link(self, channel_id: int) -> Optional[Dict]:
        return await self.links.find_one({
            "channel_id": channel_id,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })

    async def cleanup_expired_links(self):
        try:
            result = await self.links.delete_many(
                {"expires_at": {"$lt": datetime.utcnow()}}
            )
            if result.deleted_count:
                logger.info(f"🗑️ Cleaned {result.deleted_count} expired links")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup links: {e}")

    # ==================== STATISTICS ====================

    async def get_stats(self) -> Dict:
        total_users = await self.get_total_users()
        active_users = await self.get_active_users()
        total_channels = await self.channels.count_documents({"is_active": True})
        active_links = await self.links.count_documents({
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })

        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total_joins"}}}]
        result = await self.channels.aggregate(pipeline).to_list(1)
        total_joins = result[0]["total"] if result else 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_channels": total_channels,
            "active_links": active_links,
            "total_joins": total_joins
        }


# Global database instance
db = Database()