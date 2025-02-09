import random
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackQueryHandler, CallbackContext
from telegram.constants import ParseMode
from telegram import ChatPermissions, User, MessageEntity, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database import (
    is_approved, update_violations, add_approved_user, remove_approved_user, get_user_violations, Database)
from config import ALERT_CHANNEL_ID


EXEMPT_USER_IDS = [7379318591]
GROUP_CHAT_IDS = []

# Initialize the database
db = Database("users.db")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

OWNER_USER_ID = 7379318591

GROUP_CHAT_IDS = set()

# Set a maximum length for messages
MAX_MESSAGE_LENGTH = 200

# List of video file URLs to send randomly
VIDEO_LIST = [
    "https://telegra.ph/file/1722b8e21ef54ef4fbc23.mp4",
    "https://telegra.ph/file/ac7186fffc5ac5f764fc1.mp4",
    "https://telegra.ph/file/4156557a73657501918c4.mp4",
    "https://telegra.ph/file/0d896710f1f1c02ad2549.mp4",
    "https://telegra.ph/file/03ac4a6e94b5b4401fa5a.mp4",
]


# Function to create the main inline keyboard
def get_main_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("‣ʜᴇʟᴘ‣", callback_data="help"),
            InlineKeyboardButton("‣ᴀᴅᴅ ᴍᴇ‣", url="https://t.me/copyright_ro_bot?startgroup=true"),
        ],
        [
            InlineKeyboardButton("‣ʀᴇᴘᴏ‣", callback_data="repo"),
            InlineKeyboardButton("‣ᴏᴡɴᴇʀ‣", callback_data="owner"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Function to create the "Back" button to return to the main menu
def get_back_inline_keyboard():
    keyboard = [[InlineKeyboardButton("‣ʙᴀᴄᴋ‣", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

# Function to check if a user is exempt from deletion
def is_exempt_user(user_id):
    return user_id in EXEMPT_USER_IDS

# Handler for the /start command
async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command, sends an animated message, and tracks the user."""
    message = update.message
    user = update.effective_user

    # ✅ Step 1: Store user in the database and mark them as started
    if user:
        await db.add_user(user.id, user.username or "Unknown")
        await db.mark_user_started(user.id)
        print(f"✅ User started the bot: {user.id} - {user.username}")

    # ✅ Step 2: Animate the message "dιиg dιиg"
    accha = await message.reply_text(text="❤️‍🔥ᴅιиg ᴅιиg ꨄ︎ ѕтαятιиg••")
    await asyncio.sleep(0.2)
    await accha.edit_text("💛ᴅιиg ᴅιиg ꨄ︎ sтαятιиg•••")
    await asyncio.sleep(0.2)
    await accha.edit_text("🩵ᴅιиg ᴅιиg ꨄ︎ sтαятιиg•••••")
    await asyncio.sleep(0.2)
    await accha.edit_text("🤍ᴅιиg ᴅιиg ꨄ︎ sтαятιиg••••••••")
    await asyncio.sleep(0.2)
    await accha.delete()

    # ✅ Step 3: Select a random video from the VIDEO_LIST
    video_url = random.choice(VIDEO_LIST)

    user_first_name = update.effective_user.first_name
    user_username = update.effective_user.id

    # ✅ Step 4: Prepare the final message caption
    caption = "Hey [{user_first_name}](tg://user?id={user_username}), 🥀\n" \
              "𝐓ʜɪs ɪs [˹𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕 ✗ 𝜝𝒐𝒕˼](https://t.me/copyright_ro_bot) 🤍\n" \
              "➻ 𝐀 𝐅ᴀsᴛ & 𝐏ᴏᴡᴇʀғᴜʟ 𝐓ᴇʟᴇɢʀᴀᴍ 𝐒ᴇᴄᴜʀɪᴛʏ 𝐁ᴏᴛ.\n" \
              "𝐅ᴀsᴛ 𝐍sғᴡ 𝐌ᴏᴅᴇʟ ɪɴsᴛᴀʟʟᴇᴅ 𝐇ᴇʟᴩs 𝐓ᴏ 𝐏ʀᴏᴛᴇᴄᴛ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ 𝐅ʀᴏᴍ 𝐏ᴏʀɴᴏɢʀᴀᴘʜʏ 𝐀ɴᴅ 𝐂ᴏᴘʏʀɪɢʜᴛ\n" \
              "──────────────────\n" \
              "๏ 𝐂ʟɪᴄᴋ 𝐎ɴ 𝐓ʜᴇ 𝐇ᴇʟᴩ 𝐁ᴜᴛᴛᴏɴ 𝐓ᴏ 𝐆ᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ 𝐀ʙᴏᴜᴛ 𝐂ᴏᴍᴍᴀɴᴅs.".format(user_first_name=user_first_name, user_username=user_username)
    
    # ✅ Step 5: Send the video with the caption and inline keyboard
    await message.reply_video(
        video=video_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=get_main_inline_keyboard()
    )

# Handler for button presses
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        help_text = ( "💫Here are some commands:\n\n" "● ᴛʜɪs ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇs ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs, ʟᴏɴɢ ᴍᴇssᴀɢᴇs, ᴀɴᴅ sʜᴀʀᴇᴅ ʟɪɴᴋs ᴏʀ ᴘᴅғs ᴀɴᴅ ᴀʟsᴏ 18+ ᴄᴏɴᴛᴇɴᴛs 🍃\n" "● ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ʏᴏᴜʀsᴇʟᴠᴇ ᴀs sᴜᴅᴏ ᴅᴍ - @xotikop_bot💛\n" "● ᴛʏᴘᴇ /command ᴛᴏ ɢᴇᴛ ᴄᴏᴍᴍᴀɴᴅs\n\n" "#𝐒ᴀфᴇ ᴇᴄᴏ🍃 , #𝐗ᴏᴛɪᴋ❤️‍🔥" )
        await query.message.edit_caption(help_text, reply_markup=get_back_inline_keyboard())

    elif query.data == "back":
        video_url = random.choice(VIDEO_LIST)

        user_first_name = update.effective_user.first_name
        user_username = update.effective_user.id
        caption = "Hey [{user_first_name}](https://t.me/{user_username}), 🥀\n" \
              "𝐓ʜɪs ɪs [˹𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕 ✗ 𝜝𝒐𝒕˼](https://t.me/copyright_ro_bot) 🤍\n" \
              "➻ 𝐀 𝐅ᴀsᴛ & 𝐏ᴏᴡᴇʀғᴜʟ 𝐓ᴇʟᴇɢʀᴀᴍ 𝐒ᴇᴄᴜʀɪᴛʏ 𝐁ᴏᴛ.\n" \
              "𝐅ᴀsᴛ 𝐍sғᴡ 𝐌ᴏᴅᴇʟ ɪɴsᴛᴀʟʟᴇᴅ 𝐇ᴇʟᴩs 𝐓ᴏ 𝐏ʀᴏᴛᴇᴄᴛ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ 𝐅ʀᴏᴍ 𝐏ᴏʀɴᴏɢʀᴀᴘʜʏ 𝐀ɴᴅ 𝐂ᴏᴘʏʀɪɢʜᴛ\n" \
              "──────────────────\n" \
              "๏ 𝐂ʟɪᴄᴋ 𝐎ɴ 𝐓ʜᴇ 𝐇ᴇʟᴩ 𝐁ᴜᴛᴛᴏɴ 𝐓ᴏ 𝐆ᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ 𝐀ʙᴏᴜᴛ 𝐂ᴏᴍᴍᴀɴᴅs.".format(user_first_name=user_first_name, user_username=user_username)
    
        await query.message.edit_caption(caption, reply_markup=get_main_inline_keyboard(), parse_mode="Markdown")
    elif query.data == "owner":
        await query.message.edit_caption("❤️‍🔥 ​𝙢𝙮 𝙤𝙬𝙣𝙚𝙧 𝙞𝙨 𝙘𝙤𝙢𝙢𝙞𝙣𝙜 ​● ")
        await query.message.edit_caption("🍁 𝙢𝙮 𝙤𝙬𝙣𝙚𝙧 𝙞𝙨 𝙘𝙤𝙢𝙢𝙞𝙣𝙜 ​●● ")
        await query.message.edit_caption("🌙 ​𝙢𝙮 𝙤𝙬𝙣𝙚𝙧 𝙞𝙨 𝙘𝙤𝙢𝙢𝙞𝙣𝙜 ​●●● ")
        await query.message.edit_caption("💫 𝙢𝙮 𝙤𝙬𝙣𝙚𝙧 𝙞𝙨 𝙘𝙤𝙢𝙢𝙞𝙣𝙜 ​●●●● ")
        image_url = "https://files.catbox.moe/0jb630.jpg"
        await query.message.edit_media(
            InputMediaPhoto(media=image_url)
        )
        await query.message.edit_caption(
            f"𓆰‌⁪‌⁪‌⁪‌⁪‌⁪ 𝙃𝙀𝙍𝙀 𝙄𝙎 \n 𓆩𝙈𝙔 𝘾𝙐𝙏𝙀𓆪 𝙊𝙒𝙉𝙀𝙍𓂃🍃🥂꯭ ⎯᪵\n\n",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⭑ᴀʙᴏᴜᴛ⭑", url="https://t.me/love_mhe"),
                    InlineKeyboardButton("⭑ʜᴇᴀᴠᴇɴ⭑", url="https://t.me/vibes_I"),
                ],
                [
                    InlineKeyboardButton("⭑ᴘᴀʀᴀᴅɪsᴇ⭑", url="https://t.me/links_of"),
                    InlineKeyboardButton("⭑ǫᴜɪᴄᴋ⭑", url="https://t.me/addlist/Hbspf10i_LliZjI0"),
                ],
                [
                    InlineKeyboardButton("Back", callback_data="back")
                ]
            ])
        )
    elif query.data == "repo":
        video_link = "https://files.catbox.moe/jeufr1.mp4"
        caption = "BAHUT TEEZ HO RHE HO BAHUT TEZZ"
        await query.message.edit_media(
            InputMediaVideo(media=video_link, caption=caption),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
        )
        
# Function to resolve user input
async def resolve_user(context: ContextTypes.DEFAULT_TYPE, update: Update, user_input):
    """
    Resolve a user ID from various input types: numeric ID, username, or mention.
    """
    try:

        # Case 1: Input is numeric (user ID)
        if str(user_input).isdigit():
            return int(user_input)

        # Case 2: Input is a username
        async def get_user_id_from_username(bot, username):
            try:
                # Add some debug logging here
                print(f"Searching for user with username {username}")
                print(f"Username: {username}")
                search_results = await bot.search(username)
                print(f"Search results: {search_results}")
                if search_results and len(search_results) > 0:
                    user_id = search_results[0].id
                    print(f"Found user with ID {user_id}")
                    return user_id
                else:
                    print(f"User not found")
                    return None
            except Exception as e:
                print(f"Error: {e}")
                return None

        # Case 3: Input is a mention (from message entities)
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type == MessageEntity.MENTION:
                    mention_user_id = entity.user.id if entity.user else None
                    if mention_user_id:
                        return mention_user_id

        # Case 4: Replied message (fetch user ID)
        if update.message.reply_to_message:
            return update.message.reply_to_message.from_user.id

        # Final fallback
        await update.message.reply_text(
            "❌ Could not resolve the user. Provide a valid numeric ID, username, or reply to a user's message."
        )
        return None
    except Exception as e:
        print(f"Unexpected error in resolve_user: {e}")
        await update.message.reply_text("❌ An error occurred while resolving the user.")
        return None


import requests

def get_user_id_from_username(bot, username):
    try:
        response = requests.get(f"https://t.me/{username}")
        if response.status_code == 200:
            return response.url.split("/")[-1]
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None



# Command to add a user to sudo
# async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Adds a user to the sudo list. Accepts user ID, username, or mention.
#     Only the owner can add users.
#     """
#     if update.message.from_user.id != OWNER_USER_ID:
#         await update.message.reply_text("❌ You don't have permission to add sudo users!")
#         return

#     # Check if the command includes arguments or is a reply
#     user_input = None
#     if len(context.args) == 1:
#         user_input = context.args[0]  # Get the username/user_id from the arguments
#     elif update.message.reply_to_message:
#         user_input = update.message.reply_to_message.from_user.id  # Get the user ID from the replied message

#     if not user_input:
#         await update.message.reply_text(
#             "❌ Usage: /add <username>, <user_id>, or reply to a user's message with /add."
#         )
#         return

#     # Resolve the user ID
#     resolved_user_id = await resolve_user(context, update, user_input)

#     if resolved_user_id is None:
#         await update.message.reply_text("❌ Unable to resolve the user. Please ensure the input is correct.")
#         return

#     # Add the user to the sudo list if not already present
#     if resolved_user_id not in EXEMPT_USER_IDS:
#         EXEMPT_USER_IDS.append(resolved_user_id)
#         await update.message.reply_text(f"✅ User {resolved_user_id} has been added to the sudo list!")
#     else:
#         await update.message.reply_text("❌ This user is already in the sudo list.")


# async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Removes a user from the sudo list. Accepts user ID, username, or mention.
#     Only the owner can remove users.
#     """
#     if update.message.from_user.id != OWNER_USER_ID:
#         await update.message.reply_text("❌ You don't have permission to remove sudo users!")
#         return

#     # Check if the command includes arguments or is a reply
#     user_input = None
#     if len(context.args) == 1:
#         user_input = context.args[0]  # Get the username/user_id from the arguments
#     elif update.message.reply_to_message:
#         user_input = update.message.reply_to_message.from_user.id  # Get the user ID from the replied message

#     if not user_input:
#         await update.message.reply_text(
#             "❌ Usage: /remove <username>, <user_id>, or reply to a user's message with /remove."
#         )
#         return

#     # Resolve the user ID
#     resolved_user_id = await resolve_user(context, update, user_input)

#     if resolved_user_id is None:
#         await update.message.reply_text("❌ Unable to resolve the user. Please ensure the input is correct.")
#         return

#     # Remove the user from the sudo list if present
#     if resolved_user_id in EXEMPT_USER_IDS:
#         EXEMPT_USER_IDS.remove(resolved_user_id)
#         await update.message.reply_text(f"✅ User {resolved_user_id} has been removed from the sudo list!")
#     else:
#         await update.message.reply_text("❌ This user is not in the sudo list.")










# Command to mute a user
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mutes a user in the chat. Accepts user ID, username, or mention.
    Usage: /mute <user_id|username|mention> <duration_in_minutes>
    """
    if update.message.from_user.id != OWNER_USER_ID:
        await update.message.reply_text("❌ You need to be the owner or admin to use this command!")
        return

    # Check if the user provided an input or mentioned/replied to someone
    user_input = None
    if context.args:
        user_input = context.args[0]  # Get the user identifier from arguments
    elif update.message.reply_to_message:
        user_input = update.message.reply_to_message.from_user.id  # Get the user ID from a reply
    elif update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                user_input = update.message.text[entity.offset : entity.offset + entity.length]  # Extract mention text

    if not user_input:
        await update.message.reply_text(
            "❌ Usage: /mute <user_id|username|mention> <duration_in_minutes>, or reply to a user's message."
        )
        return

    # Default duration is 60 minutes (1 hour)
    try:
        duration = int(context.args[1]) if len(context.args) > 1 else 60
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")
    except ValueError:
        await update.message.reply_text("❌ Invalid duration. Please provide a positive number of minutes.")
        return

    # Resolve user ID
    resolved_user_id = await resolve_user(context, update, user_input)

    if resolved_user_id is None:
        await update.message.reply_text(
            f"❌ Unable to resolve the user '{user_input}'. Ensure the input is correct and the user has started the bot."
        )
        return

    # Mute the user
    try:
        permissions = ChatPermissions(can_send_messages=False)
        until_date = datetime.now() + timedelta(minutes=duration)
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=resolved_user_id,
            permissions=permissions,
            until_date=until_date
        )
        await update.message.reply_text(
            f"✅ User {user_input} ({resolved_user_id}) has been muted for {duration} minutes."
        )
    except Exception as e:
        print(f"Error while muting user {resolved_user_id}: {e}")
        await update.message.reply_text("❌ Failed to mute the user. Please check the bot's permissions.")




async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unmutes a user in the chat. Accepts user ID, username, or mention.
    Usage: /unmute <user_id|username|mention>, or reply to a user's message.
    """
    if update.message.from_user.id != OWNER_USER_ID:
        await update.message.reply_text("❌ You need to be the owner or admin to use this command!")
        return

    # Check if the user provided an input or mentioned/replied to someone
    user_input = None
    if context.args:
        user_input = context.args[0]  # Get the user identifier from arguments
    elif update.message.reply_to_message:
        user_input = update.message.reply_to_message.from_user.id  # Get the user ID from a reply
    elif update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                user_input = update.message.text[entity.offset : entity.offset + entity.length]  # Extract mention text

    if not user_input:
        await update.message.reply_text(
            "❌ Usage: /unmute <user_id|username|mention>, or reply to a user's message."
        )
        return

    # Resolve user ID
    resolved_user_id = await resolve_user(context, update, user_input)

    if resolved_user_id is None:
        await update.message.reply_text(
            f"❌ Unable to resolve the user '{user_input}'. Ensure the input is correct and the user has started the bot."
        )
        return

    # Unmute the user
    try:
        permissions = ChatPermissions(can_send_messages=True)  # Grant permission to send messages
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=resolved_user_id,
            permissions=permissions
        )
        await update.message.reply_text(
            f"✅ User {user_input} ({resolved_user_id}) has been unmuted."
        )
    except Exception as e:
        print(f"Error while unmuting user {resolved_user_id}: {e}")
        await update.message.reply_text("❌ Failed to unmute the user. Please check the bot's permissions.")










import psutil
from psutil import cpu_percent, virtual_memory, disk_usage
import time
# /ping Command
async def ping_u(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.perf_counter()
    image_url = "https://files.catbox.moe/tizgai.jpg"
    event = await update.message.reply_photo(image_url, caption="ᴩɪɴɢɪɴɢ ʙᴀʙʏ ●🍃")
    await event.edit_caption("ᴩɪɴɢɪɴɢ ʙᴀʙʏ ●●🍃")
    await event.edit_caption("ᴩɪɴɢɪɴɢ ʙᴀʙʏ ●●●🍃")
    await event.edit_caption("ᴩɪɴɢɪɴɢ ʙᴀʙʏ ●●●●🍃")
    await event.edit_caption("ᴩɪɴɢɪɴɢ ʙᴀʙʏ ●●●●●🍃")
    await asyncio.sleep(2)
    end = time.perf_counter()
    ms = (end - start) * 1000
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    ping_text = f"\n\n<b><u>System Stats of copyright bot :</u></b>\n\n             🍃 Uptime : {ms}\n»»————- ★ - ★ ————-««\n             ❣️ Ram : {ram}\n»»————- ★ - ★ ————-««\n             ❣️ Cpu : {cpu}\n»»————- ★ - ★ ————-««\n             ❣️ Disk : {disk}\n»»————- ★ - ★ ————-««\n             🍃 Py-TgCalls : {ms}ms\n»»————- ★ - ★ ————-««"
    ping_text += " ◈ ━━━━━━━ ⸙ - ⸙ ━━━━━━━ ◈\n🍃 \n◈ ━━━━━━━ ⸙ - ⸙ ━━━━━━━ ◈\n\n ᴍᴀᴅᴇ ᴡɪᴛʜ 🖤 ʙʏ <a href=\"https://t.me/xazoc\">||ᴀʀɪ||❣️</a>"
    await event.edit_caption(caption=ping_text, parse_mode=ParseMode.HTML)

# Handler to delete edited messages
async def delete_edited_messages(update: Update, context):
    if update.edited_message:
        user_id = update.edited_message.from_user.id

        # Check if the user is exempt from deletion
        if is_approved(user_id) and OWNER_USER_ID != user_id:
            return  # Do nothing if the user is approved

        user_mention = update.edited_message.from_user.mention_html()

        # Delete the edited message
        await context.bot.delete_message(
            chat_id=update.edited_message.chat_id,
            message_id=update.edited_message.message_id
        )

        # Notify the group about the deleted edited message
        await context.bot.send_message(
            chat_id=update.edited_message.chat_id,
            text=f"🚫 {user_mention}, edited messages are not allowed and have been deleted!",
            parse_mode=ParseMode.HTML
        )

# Handler to delete links, PDFs, long messages, and notify the user
async def delete_invalid_messages(update: Update, context):
    user_id = update.message.from_user.id

    # Check if the user is exempt from deletion
    if is_approved(user_id) and OWNER_USER_ID != user_id:
        return  # Do nothing if the user is approved

    user_mention = update.message.from_user.mention_html()

    # Check if the message contains a link or PDF
    if (update.message.entities and any(entity.type in [MessageEntity.URL, MessageEntity.TEXT_LINK] for entity in update.message.entities)) or \
            update.message.document:
        await update.message.delete()

        # Notify the group about the deleted message
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"🚫 {user_mention}, links or PDFs are not allowed and have been deleted!",
            parse_mode=ParseMode.HTML
        )

    # Check if the message exceeds the maximum length
    elif len(update.message.text) > MAX_MESSAGE_LENGTH:
        await update.message.delete()

        # Notify the group about the deleted message
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"🚫 {user_mention}, long messages are not allowed and have been deleted!",
            parse_mode=ParseMode.HTML
        )

# Error handler function
async def error_handler(update: Update, context):
    print(f"Error: {context.error}")


# # Handler to add user ID to the EXEMPT_USER_IDS list
# async def add_user_command(update: Update, context):
#     # Only allow the owner to use this command
#     if update.message.from_user.id != OWNER_USER_ID:
#         await update.message.reply_text("❌ You don't have permission to add users!")
#         return

slang_words = [
    "anal", "anus", "arse", "ass", "asses", "assfucker", "assfukka", "asshole", "arsehole", "asswhole",
    "assmunch", "auto erotic", "autoerotic", "ballsack", "bastard", "beastial", "bestial", "bhen ka lode",
    "betichod", "bhenchod", "bellend", "bdsm", "beastiality", "bestiality", "bitch", "bitches", "bitchin",
    "bitching", "bimbo", "bimbos", "blow job", "blowjob", "blowjobs", "blue waffle", "boob", "boobs",
    "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "booty call", "brown shower", "brown showers",
    "boner", "bondage", "buceta", "bukake", "bukkake", "bullshit", "bull shit", "busty", "butthole",
    "carpet muncher", "cawk", "chink", "chut", "chutiya", "cipa", "clit", "clits", "clitoris", "cnut",
    "cock", "chod dunga", "cocks", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocksuck",
    "cocksucked", "cocksucking", "cocksucks", "cocksucker", "cokmuncher", "coon", "cow girl", "cow girls",
    "cowgirl", "cowgirls", "crap", "crotch", "cum", "cummer", "cumming", "cuming", "cums", "cumshot",
    "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlicker", "cuntlicking", "cunts", "damn",
    "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "deepthroat", "deep throat", "dog style",
    "doggie style", "doggiestyle", "doggy style", "doggystyle", "donkeyribber", "doosh", "douche", "duche",
    "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation",
    "ejakulate", "erotic", "erotism", "fag", "fuddi", "fuddu", "faggot", "fagging", "faggit", "faggitt",
    "faggs", "fagot", "fagots", "fags", "fatass", "femdom", "fingering", "footjob", "foot job", "fuck",
    "fucks", "fucker", "fuckers", "fucked", "fuckhead", "fuckheads", "fuckin", "fucking", "fcuk",
    "fcuker", "fcuking", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker",
    "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers",
    "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fucka", "fuk", "fuks", "fuker",
    "fukker", "fukkin", "fukking", "futanari", "futanary", "gangbang", "gangbanged", "gang bang", "gokkun",
    "golden shower", "goldenshower", "gaysex", "gand", "gand mara", "goatse", "handjob", "hand job",
    "hentai", "hooker", "hoer", "homo", "horny", "incest", "jackoff", "jack off", "jerkoff", "jerk off",
    "jizz", "knob", "kinbaku", "labia", "lund", "lun", "lawda", "lavda", "masturbate", "masochist", "mofo",
    "mothafuck", "motherfuck", "motherfucker", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked",
    "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks",
    "mother fucker", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking",
    "motherfuckings", "motherfuckka", "motherfucks", "milf", "muff", "nigga", "nigger", "nigg", "nipple",
    "nipples", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "nude",
    "nudes", "orgy", "orgasm", "orgasms", "panty", "panties", "penis", "playboy", "porn", "porno",
    "pornography", "pron", "pussy", "pussies", "rape", "raping", "rapist", "rectum", "retard", "rimming",
    "sadist", "sadism", "schlong", "scrotum", "sex", "semen", "shemale", "she male", "shibari", "shibary",
    "shit", "shitdick", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted",
    "shitters", "shitting", "shittings", "shitty", "shota", "skank", "slut", "sluts", "smut", "smegma",
    "spunk", "strip club", "stripclub", "tit", "tits", "titties", "titty", "titfuck", "tittiefucker",
    "titties", "tittyfuck", "tittywank", "titwank", "threesome", "three some", "throating", "twat",
    "twathead", "twatty", "twunt", "viagra", "vagina", "vulva", "wank", "wanker", "wanky", "whore",
    "whoar", "xxx", "xx", "yaoi", "yury", "sexy", "Myr", "Myru", "Myre", "Andi", "Kunna", "Kunne",
    "Pelayadi", "Polayadi", "Phoonda", "Phoonde", "Kundi", "Pooru", "Poori", "Pooran", "Umb", "poothichi",
    "vedichi", "pulayaadi", "pelichi", "koothichi", "Oomb", "oombu", "Oomban", "Umban"
]

async def delete_slang_words(update: Update, context: CallbackContext):
    message = update.message
    text = message.text.lower()
    if any(word in text for word in slang_words):
        await message.delete()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🚫 <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>, Slang words are not allowed and have been deleted!🍃", parse_mode="HTML")
        keyboard = [[InlineKeyboardButton("👤 View Profile", url=f"tg://user?id={message.from_user.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"🚫{message.from_user.first_name}, Slang has been deleted! 🍃\nDeleted text: {message.text}\nReason: Slang words are not allowed"
        spoiler_offset = text.find(message.text)

        entities = [MessageEntity(type=MessageEntity.SPOILER, offset=spoiler_offset, length=len(message.text))]

        await context.bot.send_message(ALERT_CHANNEL_ID, text=text, entities=entities, reply_markup=reply_markup)

async def commands(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/ping - Check the bot's latency\n"
        "/userinfo - Get information about a user\n"
        "/myinfo - Get information about yourself\n"
        "/mute - Mute a user in the chat\n"        
        "/unmute - Unmute a user in the chat\n"
        "/broadcast - Broadcast a message to all users and groups\n"
        "/add - Add a user to the database\n"
        "/remove - Remove a user from the database\n"
        "/sudolist - Get a list of approved users\n"
    )