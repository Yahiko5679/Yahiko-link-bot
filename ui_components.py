"""
UI Components and Helper Functions
Beautiful buttons, keyboards, and formatting utilities
"""

from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from typing import List, Dict, Optional
from config import Config, Colors
from datetime import datetime


class UI:
    """UI Component Generator"""
    
    @staticmethod
    def start_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """Generate start menu keyboard"""
        buttons = [
            [
                InlineKeyboardButton(f"{Colors.CHANNEL} Get Links", callback_data="get_links"),
                InlineKeyboardButton(f"{Colors.INFO} Help", callback_data="help")
            ],
            [
                InlineKeyboardButton(f"{Colors.STATS} Statistics", callback_data="stats"),
            ]
        ]
        
        if is_admin:
            buttons.append([
                InlineKeyboardButton(f"{Colors.ADMIN} Admin Panel", callback_data="admin_panel")
            ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """Generate admin panel keyboard"""
        buttons = [
            [
                InlineKeyboardButton(f"{Colors.CHANNEL} Manage Channels", callback_data="manage_channels"),
            ],
            [
                InlineKeyboardButton(f"{Colors.STATS} Bot Stats", callback_data="admin_stats"),
                InlineKeyboardButton(f"{Colors.USER} User Stats", callback_data="user_stats"),
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                InlineKeyboardButton("🔧 Settings", callback_data="settings"),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="start")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def channel_list_keyboard(channels: List[Dict], page: int = 0) -> InlineKeyboardMarkup:
        """Generate paginated channel list keyboard"""
        buttons = []
        
        # Calculate pagination
        start_idx = page * Config.MAX_CHANNELS_PER_PAGE
        end_idx = start_idx + Config.MAX_CHANNELS_PER_PAGE
        page_channels = channels[start_idx:end_idx]
        
        # Add channel buttons (2 per row)
        for i in range(0, len(page_channels), 2):
            row = []
            for channel in page_channels[i:i+2]:
                channel_name = channel.get("channel_name", "Unknown")
                # Truncate long names
                display_name = channel_name[:20] + "..." if len(channel_name) > 20 else channel_name
                row.append(
                    InlineKeyboardButton(
                        f"{Colors.CHANNEL} {display_name}",
                        callback_data=f"channel_{channel['channel_id']}"
                    )
                )
            buttons.append(row)
        
        # Pagination buttons
        nav_buttons = []
        total_pages = (len(channels) - 1) // Config.MAX_CHANNELS_PER_PAGE + 1
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("« Previous", callback_data=f"page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next »", callback_data=f"page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Back button
        buttons.append([InlineKeyboardButton("« Back to Menu", callback_data="start")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def channel_action_menu(channel_id: int) -> InlineKeyboardMarkup:
        """Generate action menu for a specific channel"""
        buttons = [
            [
                InlineKeyboardButton(f"{Colors.LINK} Generate Link", callback_data=f"genlink_{channel_id}"),
            ],
            [
                InlineKeyboardButton(f"{Colors.LINK} Request Link", callback_data=f"reqlink_{channel_id}"),
            ],
            [
                InlineKeyboardButton("🔄 Refresh Info", callback_data=f"refresh_{channel_id}"),
                InlineKeyboardButton("❌ Delete", callback_data=f"delete_{channel_id}"),
            ],
            [
                InlineKeyboardButton("« Back to Channels", callback_data="get_links")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def confirm_delete(channel_id: int) -> InlineKeyboardMarkup:
        """Generate confirmation keyboard for deletion"""
        buttons = [
            [
                InlineKeyboardButton(f"{Colors.SUCCESS} Yes, Delete", callback_data=f"confirm_delete_{channel_id}"),
                InlineKeyboardButton(f"{Colors.ERROR} Cancel", callback_data=f"channel_{channel_id}"),
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def close_button() -> InlineKeyboardMarkup:
        """Generate close button"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]])


class Formatter:
    """Text formatting utilities"""
    
    @staticmethod
    def welcome_message(user_name: str, is_admin: bool = False) -> str:
        """Generate welcome message"""
        role = f"{Colors.ADMIN} **Admin**" if is_admin else f"{Colors.USER} **User**"
        
        text = f"""
{Colors.FIRE} **Welcome to {Config.BOT_NAME}!**

Hey **{user_name}**! {role}

{Colors.INFO} I help you get instant access to channel invite links with auto-expiring security.

**✨ Features:**
{Colors.LINK} Secure invite links
{Colors.TIME} Auto-expiring (5 mins)
{Colors.CHANNEL} Multiple channels
{Colors.SUCCESS} Easy to use

Use the buttons below to get started!
"""
        return text.strip()
    
    @staticmethod
    def help_message() -> str:
        """Generate help message"""
        text = f"""
{Colors.INFO} **Help & Commands**

**For Users:**
• Tap "Get Links" to see available channels
• Select a channel to get an invite link
• Links expire in {Config.LINK_EXPIRY_MINUTES} minutes for security

**Admin Commands:**
• `/addchannel <channel_id>` - Add a channel
• `/removechannel <channel_id>` - Remove a channel
• `/channels` - List all channels
• `/broadcast <message>` - Send message to all users
• `/stats` - View bot statistics

{Colors.SUCCESS} **Need more help?**
Contact the bot owner for assistance.
"""
        return text.strip()
    
    @staticmethod
    def stats_message(stats: Dict) -> str:
        """Generate statistics message"""
        text = f"""
{Colors.STATS} **Bot Statistics**

{Colors.USER} **Users:**
• Total: `{stats['total_users']}`
• Active (7d): `{stats['active_users']}`

{Colors.CHANNEL} **Channels:**
• Total: `{stats['total_channels']}`
• Active Links: `{stats['active_links']}`

{Colors.LINK} **Engagement:**
• Total Joins: `{stats['total_joins']}`

{Colors.TIME} **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
"""
        return text.strip()
    
    @staticmethod
    def channel_info(channel: Dict, invite_link: Optional[str] = None) -> str:
        """Generate channel information message"""
        channel_name = channel.get("channel_name", "Unknown")
        channel_id = channel.get("channel_id", "N/A")
        total_joins = channel.get("total_joins", 0)
        added_at = channel.get("added_at", datetime.utcnow())
        
        text = f"""
{Colors.CHANNEL} **Channel Information**

**Name:** `{channel_name}`
**ID:** `{channel_id}`
**Total Joins:** `{total_joins}`
**Added:** `{added_at.strftime('%Y-%m-%d')}`
"""
        
        if invite_link:
            text += f"\n{Colors.LINK} **Invite Link:**\n`{invite_link}`\n\n{Colors.TIME} _Link expires in {Config.LINK_EXPIRY_MINUTES} minutes_"
        
        return text.strip()
    
    @staticmethod
    def admin_stats(stats: Dict, uptime: str) -> str:
        """Generate detailed admin statistics"""
        text = f"""
{Colors.ADMIN} **Admin Dashboard**

{Colors.STATS} **System Status**
• Uptime: `{uptime}`
• Bot Version: `v{Config.BOT_VERSION}`

{Colors.USER} **User Analytics**
• Total Users: `{stats['total_users']}`
• Active Users (7d): `{stats['active_users']}`
• Engagement: `{(stats['active_users']/max(stats['total_users'], 1)*100):.1f}%`

{Colors.CHANNEL} **Channel Analytics**
• Active Channels: `{stats['total_channels']}`
• Active Links: `{stats['active_links']}`
• Total Joins: `{stats['total_joins']}`
• Avg Joins/Channel: `{(stats['total_joins']/max(stats['total_channels'], 1)):.0f}`

{Colors.TIME} **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        return text.strip()
    
    @staticmethod
    def error_message(error_text: str) -> str:
        """Generate error message"""
        return f"{Colors.ERROR} **Error**\n\n{error_text}"
    
    @staticmethod
    def success_message(success_text: str) -> str:
        """Generate success message"""
        return f"{Colors.SUCCESS} **Success**\n\n{success_text}"
    
    @staticmethod
    def loading_message() -> str:
        """Generate loading message"""
        return f"{Colors.INFO} Please wait..."


# Helper functions
def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X time ago'"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} year(s) ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month(s) ago"
    elif diff.days > 0:
        return f"{diff.days} day(s) ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour(s) ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute(s) ago"
    else:
        return "just now"


def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format"""
    intervals = (
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )
    
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value} {name}")
    
    return ', '.join(result[:2]) if result else '0 seconds'
