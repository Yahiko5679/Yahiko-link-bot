"""
Main Bot Handlers
Handles all user interactions and commands
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from datetime import datetime
import logging

from database import db
from config import Config, Colors
from ui_components import UI, Formatter, get_readable_time

logger = logging.getLogger(__name__)

# Track bot start time for uptime
bot_start_time = datetime.utcnow()


def get_uptime() -> str:
    uptime_seconds = int((datetime.utcnow() - bot_start_time).total_seconds())
    return get_readable_time(uptime_seconds)


# =========================================================
# REGISTER HANDLERS
# =========================================================

def register_handlers(app: Client):

    # ==================== USER COMMANDS ====================

    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        user = message.from_user
        if not user:
            return

        await db.add_user(user.id, user.username, user.first_name)
        await db.update_last_active(user.id)

        is_admin = Config.is_admin(user.id)
        welcome_text = Formatter.welcome_message(user.first_name or "User", is_admin)

        await message.reply_text(
            welcome_text,
            reply_markup=UI.start_menu(is_admin),
            disable_web_page_preview=True
        )

    @app.on_message(filters.command("help") & filters.private)
    async def help_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)

        await message.reply_text(
            Formatter.help_message(),
            reply_markup=UI.close_button(),
            disable_web_page_preview=True
        )

    @app.on_message(filters.command("stats") & filters.private)
    async def stats_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)

        stats = await db.get_stats()
        await message.reply_text(
            Formatter.stats_message(stats),
            reply_markup=UI.close_button()
        )

    @app.on_message(filters.command("channels") & filters.private)
    async def channels_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)

        channels = await db.get_all_channels()
        if not channels:
            await message.reply_text(
                Formatter.error_message("No channels available yet!")
            )
            return

        await message.reply_text(
            f"{Colors.CHANNEL} **Available Channels** ({len(channels)})\n\nSelect a channel:",
            reply_markup=UI.channel_list_keyboard(channels, 0)
        )

    # ==================== ADMIN COMMANDS ====================

    @app.on_message(filters.command("addchannel") & filters.private)
    async def add_channel_command(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            await message.reply_text(
                Formatter.error_message("You don't have permission.")
            )
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text(
                Formatter.error_message("Usage: `/addchannel <channel_id>`")
            )
            return

        try:
            channel_id = int(parts[1])
        except ValueError:
            await message.reply_text(Formatter.error_message("Invalid channel ID"))
            return

        status = await message.reply_text(Formatter.loading_message())

        try:
            chat = await client.get_chat(channel_id)
            invite = None
            try:
                invite = await client.export_chat_invite_link(channel_id)
            except:
                pass

            success = await db.add_channel(channel_id, chat.title, invite)
            if success:
                await status.edit_text(
                    Formatter.success_message(
                        f"Channel added!\n\n**Name:** {chat.title}\n**ID:** `{channel_id}`"
                    )
                )
            else:
                await status.edit_text(
                    Formatter.error_message("Channel already exists.")
                )

        except Exception as e:
            logger.error(e)
            await status.edit_text(
                Formatter.error_message("Bot must be admin in the channel.")
            )

    @app.on_message(filters.command("removechannel") & filters.private)
    async def remove_channel_command(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            await message.reply_text(
                Formatter.error_message("No permission.")
            )
            return

        try:
            channel_id = int(message.text.split()[1])
        except:
            await message.reply_text(
                Formatter.error_message("Usage: `/removechannel <channel_id>`")
            )
            return

        if await db.remove_channel(channel_id):
            await message.reply_text(
                Formatter.success_message("Channel removed successfully!")
            )
        else:
            await message.reply_text(
                Formatter.error_message("Channel not found.")
            )

    @app.on_message(filters.command("broadcast") & filters.private)
    async def broadcast_command(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            return await message.reply_text(
                Formatter.error_message("Admin only.")
            )

        if not message.reply_to_message:
            return await message.reply_text(
                Formatter.error_message("Reply to a message to broadcast.")
            )

        status = await message.reply_text(f"{Colors.INFO} Broadcasting...")

        users = await db.users.find({}).to_list(length=None)
        sent, failed = 0, 0

        for u in users:
            try:
                await message.reply_to_message.copy(u["user_id"])
                sent += 1
            except:
                failed += 1

        await status.edit_text(
            Formatter.success_message(
                f"Broadcast Done!\n\nSent: {sent}\nFailed: {failed}"
            )
        )

    # ==================== CALLBACK HANDLER ====================

    @app.on_callback_query()
    async def callback_handler(client: Client, callback: CallbackQuery):
        data = callback.data
        user_id = callback.from_user.id

        await db.update_last_active(user_id)

        if data == "start":
            is_admin = Config.is_admin(user_id)
            await callback.message.edit_text(
                Formatter.welcome_message(callback.from_user.first_name or "User", is_admin),
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
                return await callback.answer("No channels!", show_alert=True)

            await callback.message.edit_text(
                f"{Colors.CHANNEL} Available Channels:",
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
                return await callback.answer("Channel not found", True)

            if Config.is_admin(user_id):
                await callback.message.edit_text(
                    Formatter.channel_info(channel),
                    reply_markup=UI.channel_action_menu(channel_id)
                )
            else:
                await generate_invite_link(client, callback, channel_id, channel)

        elif data == "admin_stats":
            if not Config.is_admin(user_id):
                return await callback.answer("Access denied", True)

            stats = await db.get_stats()
            await callback.message.edit_text(
                Formatter.admin_stats(stats, get_uptime()),
                reply_markup=UI.close_button()
            )

        elif data == "close":
            await callback.message.delete()

        else:
            await callback.answer("Coming soon!")


# ==================== INVITE LINK ====================

async def generate_invite_link(client: Client, callback: CallbackQuery,
                               channel_id: int, channel: dict):
    try:
        invite = await client.create_chat_invite_link(
            channel_id,
            member_limit=1,
            expire_date=int(datetime.utcnow().timestamp()) + (Config.LINK_EXPIRY_MINUTES * 60)
        )

        await db.save_link(channel_id, invite.invite_link, "invite")
        await db.increment_channel_joins(channel_id)

        await callback.message.edit_text(
            Formatter.channel_info(channel, invite.invite_link),
            reply_markup=UI.close_button()
        )

    except Exception as e:
        logger.error(e)
        await callback.message.edit_text(
            Formatter.error_message("Failed to generate invite link."),
            reply_markup=UI.close_button()
        )