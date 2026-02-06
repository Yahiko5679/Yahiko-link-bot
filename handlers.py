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
            await message.reply_text(Formatter.error_message("Access denied."))
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            # Fixed: Removed markdown formatting that caused ENTITY_BOUNDS_INVALID
            await message.reply_text(
                f"{Colors.ERROR} **Usage:**\n\n"
                f"/addchannel <channel_id>\n\n"
                f"Example: /addchannel -1001234567890"
            )
            return

        try:
            channel_id = int(parts[1])
        except ValueError:
            await message.reply_text(Formatter.error_message("Invalid channel ID. Must be a number."))
            return

        status_msg = await message.reply_text(f"{Colors.INFO} Please wait...")

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

            if not success:
                await status_msg.edit_text(
                    Formatter.error_message("Channel already exists or failed to add.")
                )
                return

            # Generate deep links
            encoded = db.encode_channel_id(channel_id)
            bot_username = Config.BOT_USERNAME or (await client.get_me()).username

            normal_link = f"https://t.me/{bot_username}?start={encoded}"
            request_link = f"https://t.me/{bot_username}?start=req_{encoded}"

            await status_msg.edit_text(
                f"{Colors.SUCCESS} **Channel Added Successfully!**\n\n"
                f"📢 **Name:** {channel_name}\n"
                f"🆔 **ID:** `{channel_id}`\n"
                f"📊 **Encoded:** `{encoded}`\n\n"
                f"{Colors.LINK} **Deep Links:**\n\n"
                f"🔗 **Normal Link:**\n`{normal_link}`\n\n"
                f"🔗 **Request Link:**\n`{request_link}`\n\n"
                f"{Colors.INFO} **How it works:**\n"
                f"• Users click the deep link\n"
                f"• Bot generates temporary invite link\n"
                f"• Link auto-revokes after {Config.TEMP_LINK_REVOKE_SECONDS} seconds\n"
                f"• Keeps your channel secure!"
            )

        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            await status_msg.edit_text(
                Formatter.error_message(
                    f"Failed to add channel.\n\n"
                    f"Make sure:\n"
                    f"• Bot is admin in the channel\n"
                    f"• Channel ID is correct\n"
                    f"• Bot has proper permissions\n\n"
                    f"Error: {str(e)}"
                )
            )

    # ==================== ADMIN: REMOVE CHANNEL ====================

    @app.on_message(filters.command("removechannel") & filters.private)
    async def remove_channel_command(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            await message.reply_text(Formatter.error_message("Access denied."))
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text(
                f"{Colors.ERROR} **Usage:**\n\n/removechannel <channel_id>"
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

    # ==================== ADMIN: BROADCAST ====================

    @app.on_message(filters.command("broadcast") & filters.private)
    async def broadcast_command(client: Client, message: Message):
        if not Config.is_admin(message.from_user.id):
            await message.reply_text(Formatter.error_message("Access denied."))
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

    # ==================== CALLBACK HANDLER ====================

    @app.on_callback_query()
    async def callback_handler(client: Client, cb: CallbackQuery):
        data = cb.data
        uid = cb.from_user.id
        await db.update_last_active(uid)

        if data == "start":
            is_admin = Config.is_admin(uid)
            welcome_text = Formatter.welcome_message(cb.from_user.first_name or "User", is_admin)
            await cb.message.edit_text(
                welcome_text,
                reply_markup=UI.start_menu(is_admin)
            )

        elif data == "help":
            await cb.message.edit_text(
                Formatter.help_message(),
                reply_markup=UI.close_button()
            )

        elif data == "stats":
            stats = await db.get_stats()
            await cb.message.edit_text(
                Formatter.stats_message(stats),
                reply_markup=UI.close_button()
            )

        elif data == "get_links":
            channels = await db.get_all_channels()
            if not channels:
                await cb.answer("No channels available!", show_alert=True)
                return

            await cb.message.edit_text(
                f"{Colors.CHANNEL} **Available Channels** ({len(channels)})\n\nSelect a channel:",
                reply_markup=UI.channel_list_keyboard(channels, 0)
            )

        elif data.startswith("page_"):
            page = int(data.split("_")[1])
            channels = await db.get_all_channels()
            await cb.message.edit_reply_markup(
                UI.channel_list_keyboard(channels, page)
            )

        elif data.startswith("channel_"):
            channel_id = int(data.split("_")[1])
            channel = await db.get_channel(channel_id)

            if not channel:
                await cb.answer("Channel not found!", show_alert=True)
                return

            await generate_invite_link(client, cb, channel_id, channel)

        elif data == "admin_panel":
            if not Config.is_admin(uid):
                await cb.answer("Access denied!", show_alert=True)
                return

            await cb.message.edit_text(
                f"{Colors.ADMIN} **Admin Panel**\n\nSelect an option:",
                reply_markup=UI.admin_panel()
            )

        elif data == "admin_stats":
            if not Config.is_admin(uid):
                await cb.answer("Access denied!", show_alert=True)
                return

            stats = await db.get_stats()
            uptime = get_uptime()

            await cb.message.edit_text(
                Formatter.admin_stats(stats, uptime),
                reply_markup=UI.close_button()
            )

        elif data == "close":
            await cb.message.delete()

        elif data == "noop":
            await cb.answer()

        else:
            await cb.answer("Feature coming soon!", show_alert=True)


# ==========================================================
# 🔹 HELPER FUNCTIONS (NO DECORATORS)
# ==========================================================

async def handle_deep_link(client: Client, message: Message, payload: str):
    """Handle deep link payload to generate invite links"""
    try:
        # Determine link type
        is_request_link = payload.startswith('req_')

        # Decode channel ID
        channel_id = db.decode_channel_id(payload)

        if not channel_id:
            await message.reply_text(
                Formatter.error_message("Invalid link. Please try again.")
            )
            return

        # Get channel from database
        channel = await db.get_channel(channel_id)

        if not channel:
            await message.reply_text(
                Formatter.error_message("Channel not found or has been removed.")
            )
            return

        # Send "Generating link..." message
        status_msg = await message.reply_text(
            f"{Colors.INFO} **Generating your invite link...**\n\n"
            f"Please wait a moment..."
        )

        # Generate temporary invite link
        try:
            if is_request_link:
                # Create request link (join with approval)
                invite = await client.create_chat_invite_link(
                    channel_id,
                    creates_join_request=True,
                    name=f"User_{message.from_user.id}"
                )
            else:
                # Create regular invite link (direct join, 1 use only)
                invite = await client.create_chat_invite_link(
                    channel_id,
                    member_limit=1,
                    name=f"User_{message.from_user.id}"
                )

            invite_link = invite.invite_link

            # Save to database
            await db.save_link(channel_id, invite_link, "request" if is_request_link else "invite")
            await db.increment_channel_joins(channel_id)

            # Send the invite link
            link_type_text = "Request Link" if is_request_link else "Invite Link"

            await status_msg.edit_text(
                f"{Colors.SUCCESS} **{link_type_text} Generated!**\n\n"
                f"📢 **Channel:** {channel.get('channel_name', 'Unknown')}\n"
                f"🔗 **Link:** `{invite_link}`\n\n"
                f"{Colors.TIME} **Important:**\n"
                f"• This link will be revoked in **{Config.TEMP_LINK_REVOKE_SECONDS} seconds**\n"
                f"• Use it immediately!\n"
                f"• After revoke, request a new link\n\n"
                f"{Colors.INFO} _Click the link above to join the channel_"
            )

            logger.info(f"Invite link generated for channel {channel_id}, will revoke in {Config.TEMP_LINK_REVOKE_SECONDS}s")

            # Auto-revoke after specified seconds
            asyncio.create_task(
                auto_revoke_link(client, channel_id, invite_link, Config.TEMP_LINK_REVOKE_SECONDS)
            )

        except Exception as e:
            logger.error(f"Error generating invite link: {e}")
            await status_msg.edit_text(
                Formatter.error_message(
                    f"Failed to generate invite link.\n\n"
                    f"**Possible reasons:**\n"
                    f"• Bot is not admin in the channel\n"
                    f"• Bot lacks 'Create Invite Links' permission\n"
                    f"• Channel settings restrict invites\n\n"
                    f"Please contact the bot owner."
                )
            )

    except Exception as e:
        logger.error(f"Error in handle_deep_link: {e}", exc_info=True)
        await message.reply_text(
            Formatter.error_message(f"An error occurred: {str(e)}")
        )


async def auto_revoke_link(client: Client, channel_id: int, invite_link: str, delay_seconds: int):
    """Automatically revoke invite link after delay"""
    try:
        # Wait for specified seconds
        await asyncio.sleep(delay_seconds)

        # Revoke the link
        await client.revoke_chat_invite_link(channel_id, invite_link)

        logger.info(f"Auto-revoked invite link for channel {channel_id} after {delay_seconds}s")

    except Exception as e:
        logger.error(f"Error auto-revoking link: {e}")


async def generate_invite_link(client: Client, callback: CallbackQuery, 
                               channel_id: int, channel: dict):
    """Generate and send invite link for a channel"""
    try:
        await callback.answer(f"{Colors.INFO} Generating link...")

        # Try to create invite link
        invite = await client.create_chat_invite_link(
            channel_id,
            member_limit=1,
            name=f"User_{callback.from_user.id}"
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
