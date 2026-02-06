"""
Main Bot Handlers
Handles all user interactions and commands
"""

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram import Client
from database import db
from config import Config, Colors
from ui_components import UI, Formatter, get_readable_time
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

bot_start_time = datetime.utcnow()


def get_uptime() -> str:
    uptime_seconds = int((datetime.utcnow() - bot_start_time).total_seconds())
    return get_readable_time(uptime_seconds)


# ==========================================================
# 🔹 REGISTER ALL HANDLERS ON PROVIDED APP
# ==========================================================

def register_handlers(app: Client):

    # ==================== START ====================

    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        try:
            user = message.from_user
            await db.add_user(user.id, user.username, user.first_name)
            await db.update_last_active(user.id)

            payload = message.command[1] if len(message.command) > 1 else None
            if payload:
                await handle_deep_link(client, message, payload)
                return

            is_admin = Config.is_admin(user.id)
            text = Formatter.welcome_message(user.first_name or "User", is_admin)

            await message.reply_text(
                text,
                reply_markup=UI.start_menu(is_admin)
            )

        except Exception as e:
            logger.exception(e)
            await message.reply_text(
                Formatter.error_message("Something went wrong. Please try again.")
            )

    # ==================== HELP ====================

    @app.on_message(filters.command("help") & filters.private)
    async def help_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)
        await message.reply_text(
            Formatter.help_message(),
            reply_markup=UI.close_button()
        )

    # ==================== STATS ====================

    @app.on_message(filters.command("stats") & filters.private)
    async def stats_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)
        stats = await db.get_stats()
        await message.reply_text(
            Formatter.stats_message(stats),
            reply_markup=UI.close_button()
        )

    # ==================== CHANNEL LIST ====================

    @app.on_message(filters.command("channels") & filters.private)
    async def channels_command(client: Client, message: Message):
        await db.update_last_active(message.from_user.id)
        channels = await db.get_all_channels()

        if not channels:
            await message.reply_text(Formatter.error_message("No channels available."))
            return

        await message.reply_text(
            f"{Colors.CHANNEL} **Available Channels**",
            reply_markup=UI.channel_list_keyboard(channels, 0)
        )

    # ==================== ADMIN: ADD CHANNEL ====================

    @app.on_message(filters.command("addchannel") & filters.private)
    async def add_channel(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            return await message.reply_text(Formatter.error_message("Access denied."))

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("Usage: `/addchannel <channel_id>`")

        channel_id = int(parts[1])
        chat = await client.get_chat(channel_id)

        await db.add_channel(channel_id, chat.title, chat.invite_link)

        encoded = db.encode_channel_id(channel_id)
        bot_username = Config.BOT_USERNAME or (await client.get_me()).username

        await message.reply_text(
            f"{Colors.SUCCESS} Channel Added!\n\n"
            f"https://t.me/{bot_username}?start={encoded}"
        )

    # ==================== CALLBACK HANDLER ====================

    @app.on_callback_query()
    async def callback_handler(client: Client, cb: CallbackQuery):
        data = cb.data
        uid = cb.from_user.id
        await db.update_last_active(uid)

        if data == "close":
            return await cb.message.delete()

        if data.startswith("channel_"):
            channel_id = int(data.split("_")[1])
            channel = await db.get_channel(channel_id)
            await generate_invite_link(client, cb, channel_id, channel)


# ==========================================================
# 🔹 HELPER FUNCTIONS (NO DECORATORS)
# ==========================================================

async def handle_deep_link(client: Client, message: Message, payload: str):
    channel_id = db.decode_channel_id(payload.replace("req_", ""))
    channel = await db.get_channel(channel_id)

    invite = await client.create_chat_invite_link(
        channel_id,
        member_limit=1
    )

    await message.reply_text(
        f"{Colors.SUCCESS} Invite Link:\n`{invite.invite_link}`"
    )

    asyncio.create_task(
        auto_revoke_link(client, channel_id, invite.invite_link, Config.TEMP_LINK_REVOKE_SECONDS)
    )


async def auto_revoke_link(client, channel_id, link, delay):
    await asyncio.sleep(delay)
    await client.revoke_chat_invite_link(channel_id, link)


async def generate_invite_link(client, cb, channel_id, channel):
    invite = await client.create_chat_invite_link(channel_id, member_limit=1)
    await cb.message.edit_text(
        Formatter.channel_info(channel, invite.invite_link),
        reply_markup=UI.close_button()
    )