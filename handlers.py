"""
Main Bot Handlers
Handles all user interactions and commands
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import db
from config import Config, Colors
from ui_components import UI, Formatter, get_readable_time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Track bot start time for uptime
bot_start_time = datetime.utcnow()


def get_uptime() -> str:
    """Calculate bot uptime"""
    uptime_seconds = int((datetime.utcnow() - bot_start_time).total_seconds())
    return get_readable_time(uptime_seconds)


# ==================== COMMAND HANDLERS ====================

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user = message.from_user
    
    # Add user to database
    await db.add_user(user.id, user.username, user.first_name)
    await db.update_last_active(user.id)
    
    is_admin = Config.is_admin(user.id)
    
    welcome_text = Formatter.welcome_message(user.first_name or "User", is_admin)
    
    await message.reply_text(
        welcome_text,
        reply_markup=UI.start_menu(is_admin)
    )


@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    await db.update_last_active(message.from_user.id)
    
    help_text = Formatter.help_message()
    
    await message.reply_text(
        help_text,
        reply_markup=UI.close_button()
    )


@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    """Handle /stats command"""
    await db.update_last_active(message.from_user.id)
    
    stats = await db.get_stats()
    stats_text = Formatter.stats_message(stats)
    
    await message.reply_text(
        stats_text,
        reply_markup=UI.close_button()
    )


@Client.on_message(filters.command("channels") & filters.private)
async def channels_command(client: Client, message: Message):
    """Handle /channels command - show all channels"""
    await db.update_last_active(message.from_user.id)
    
    channels = await db.get_all_channels()
    
    if not channels:
        await message.reply_text(
            Formatter.error_message("No channels available yet!")
        )
        return
    
    await message.reply_text(
        f"{Colors.CHANNEL} **Available Channels** ({len(channels)})\n\nSelect a channel to get the invite link:",
        reply_markup=UI.channel_list_keyboard(channels, 0)
    )


# ==================== ADMIN COMMANDS ====================

@Client.on_message(filters.command("addchannel") & filters.private)
async def add_channel_command(client: Client, message: Message):
    """Handle /addchannel command"""
    if not Config.is_admin(message.from_user.id):
        await message.reply_text(Formatter.error_message("You don't have permission to use this command."))
        return
    
    # Parse command
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text(
            Formatter.error_message(
                "**Usage:** `/addchannel <channel_id>`\n\n"
                "Example: `/addchannel -1001234567890`"
            )
        )
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await message.reply_text(Formatter.error_message("Invalid channel ID. Must be a number."))
        return
    
    # Get channel info
    status_msg = await message.reply_text(Formatter.loading_message())
    
    try:
        chat = await client.get_chat(channel_id)
        channel_name = chat.title
        
        # Try to get invite link
        try:
            invite_link = await client.export_chat_invite_link(channel_id)
        except:
            invite_link = None
        
        # Add to database
        success = await db.add_channel(channel_id, channel_name, invite_link)
        
        if success:
            await status_msg.edit_text(
                Formatter.success_message(
                    f"Channel added successfully!\n\n"
                    f"**Name:** {channel_name}\n"
                    f"**ID:** `{channel_id}`"
                )
            )
        else:
            await status_msg.edit_text(
                Formatter.error_message("Channel already exists or failed to add.")
            )
    
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await status_msg.edit_text(
            Formatter.error_message(
                f"Failed to add channel. Make sure:\n"
                f"• Bot is admin in the channel\n"
                f"• Channel ID is correct\n\n"
                f"Error: {str(e)}"
            )
        )


@Client.on_message(filters.command("removechannel") & filters.private)
async def remove_channel_command(client: Client, message: Message):
    """Handle /removechannel command"""
    if not Config.is_admin(message.from_user.id):
        await message.reply_text(Formatter.error_message("You don't have permission to use this command."))
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text(
            Formatter.error_message("**Usage:** `/removechannel <channel_id>`")
        )
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await message.reply_text(Formatter.error_message("Invalid channel ID."))
        return
    
    success = await db.remove_channel(channel_id)
    
    if success:
        await message.reply_text(
            Formatter.success_message(f"Channel `{channel_id}` removed successfully!")
        )
    else:
        await message.reply_text(
            Formatter.error_message("Channel not found or failed to remove.")
        )


@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    """Handle /broadcast command"""
    if not Config.is_admin(message.from_user.id):
        await message.reply_text(Formatter.error_message("You don't have permission to use this command."))
        return
    
    if not message.reply_to_message:
        await message.reply_text(
            Formatter.error_message("Reply to a message to broadcast it to all users.")
        )
        return
    
    status_msg = await message.reply_text(f"{Colors.INFO} Starting broadcast...")
    
    # Get all users
    all_users = await db.users.find({}).to_list(length=None)
    
    success_count = 0
    failed_count = 0
    
    for user in all_users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send to {user['user_id']}: {e}")
    
    await status_msg.edit_text(
        Formatter.success_message(
            f"Broadcast completed!\n\n"
            f"{Colors.SUCCESS} Sent: {success_count}\n"
            f"{Colors.ERROR} Failed: {failed_count}"
        )
    )


# ==================== CALLBACK HANDLERS ====================

@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    """Handle all callback queries"""
    data = callback.data
    user_id = callback.from_user.id
    
    await db.update_last_active(user_id)
    
    # Handle different callback types
    if data == "start":
        is_admin = Config.is_admin(user_id)
        welcome_text = Formatter.welcome_message(callback.from_user.first_name or "User", is_admin)
        await callback.message.edit_text(
            welcome_text,
            reply_markup=UI.start_menu(is_admin)
        )
    
    elif data == "help":
        await callback.message.edit_text(
            Formatter.help_message(),
            reply_markup=UI.close_button()
        )
    
    elif data == "stats":
        stats = await db.get_stats()
        await callback.message.edit_text(
            Formatter.stats_message(stats),
            reply_markup=UI.close_button()
        )
    
    elif data == "get_links":
        channels = await db.get_all_channels()
        if not channels:
            await callback.answer("No channels available!", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"{Colors.CHANNEL} **Available Channels** ({len(channels)})\n\nSelect a channel:",
            reply_markup=UI.channel_list_keyboard(channels, 0)
        )
    
    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        channels = await db.get_all_channels()
        await callback.message.edit_reply_markup(
            UI.channel_list_keyboard(channels, page)
        )
    
    elif data.startswith("channel_"):
        channel_id = int(data.split("_")[1])
        channel = await db.get_channel(channel_id)
        
        if not channel:
            await callback.answer("Channel not found!", show_alert=True)
            return
        
        channel_text = Formatter.channel_info(channel)
        
        if Config.is_admin(user_id):
            # Show admin options
            await callback.message.edit_text(
                channel_text,
                reply_markup=UI.channel_action_menu(channel_id)
            )
        else:
            # Generate link for regular users
            await generate_invite_link(client, callback, channel_id, channel)
    
    elif data.startswith("genlink_"):
        channel_id = int(data.split("_")[1])
        channel = await db.get_channel(channel_id)
        await generate_invite_link(client, callback, channel_id, channel)
    
    elif data == "admin_panel":
        if not Config.is_admin(user_id):
            await callback.answer("Access denied!", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"{Colors.ADMIN} **Admin Panel**\n\nSelect an option:",
            reply_markup=UI.admin_panel()
        )
    
    elif data == "admin_stats":
        if not Config.is_admin(user_id):
            await callback.answer("Access denied!", show_alert=True)
            return
        
        stats = await db.get_stats()
        uptime = get_uptime()
        
        await callback.message.edit_text(
            Formatter.admin_stats(stats, uptime),
            reply_markup=UI.close_button()
        )
    
    elif data == "close":
        await callback.message.delete()
    
    elif data == "noop":
        await callback.answer()
    
    else:
        await callback.answer("Feature coming soon!", show_alert=True)


async def generate_invite_link(client: Client, callback: CallbackQuery, 
                               channel_id: int, channel: dict):
    """Generate and send invite link for a channel"""
    try:
        await callback.answer(f"{Colors.INFO} Generating link...")
        
        # Try to create invite link
        invite = await client.create_chat_invite_link(
            channel_id,
            member_limit=1,
            expire_date=datetime.utcnow().timestamp() + (Config.LINK_EXPIRY_MINUTES * 60)
        )
        
        invite_link = invite.invite_link
        
        # Save to database
        await db.save_link(channel_id, invite_link, "invite")
        await db.increment_channel_joins(channel_id)
        
        # Send link
        link_text = Formatter.channel_info(channel, invite_link)
        
        await callback.message.edit_text(
            link_text,
            reply_markup=UI.close_button()
        )
        
        logger.info(f"Link generated for channel {channel_id} by user {callback.from_user.id}")
    
    except Exception as e:
        logger.error(f"Error generating link: {e}")
        await callback.message.edit_text(
            Formatter.error_message(
                f"Failed to generate invite link.\n\n"
                f"Make sure the bot is admin in the channel with permission to create invite links."
            ),
            reply_markup=UI.close_button()
        )
