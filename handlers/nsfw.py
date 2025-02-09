import os
import logging
import ffmpeg
import imageio
import numpy as np
from PIL import Image
from lottie import parsers
from telegram import constants
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN, OWNER_ID, ALERT_CHANNEL_ID, MEDIA_DIR
from database import is_approved, update_violations, add_approved_user, remove_approved_user, get_user_violations, get_all_users
from .predict import detect_nsfw
from database.database import init_db
# Ensure media directory exists
os.makedirs(MEDIA_DIR, exist_ok=True)

# Setup database
init_db()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ✅ Convert WebP static stickers to PNG
def convert_webp_to_png(file_path):
    try:
        png_path = file_path.replace(".webp", ".png")
        img = Image.open(file_path).convert("RGB")
        img.save(png_path, "PNG")
        return png_path
    except Exception as e:
        logger.error(f"Error converting WebP to PNG: {e}")
        return None


# ✅ Extract frame from animated WEBM stickers
def extract_frame_from_webm(input_path):
    """Extracts the first frame from a .webm video file and saves it as a .jpg image."""
    output_path = input_path.replace(".webm", ".jpg")  # Set output as JPG

    try:
        reader = imageio.get_reader(input_path, format="webm")
        frame = reader.get_next_data()  # Get the first frame
        reader.close()

        # Convert frame to numpy array (ensure it's writable)
        frame = np.array(frame, dtype=np.uint8)

        # Save frame as JPEG
        imageio.imwrite(output_path, frame, format="JPEG")  
        return output_path
    except Exception as e:
        print(f"Error extracting frame from WEBM: {e}")
        return None


# ✅ Convert TGS stickers (Lottie) to PNG
def convert_tgs_to_png(file_path):
    output_path = file_path.replace(".tgs", ".png")
    try:
        animation = parse_tgs(file_path)
        frame = animation.render_frame(0)
        frame.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logger.error(f"Error converting TGS to PNG: {e}")
        return None


# ✅ Handle all media (images, videos, stickers, GIFs, animated stickers)
async def handle_media(update: Update, context: CallbackContext):
    """Handles all media types and scans for NSFW content."""
    user = update.message.from_user
    chat_id = update.message.chat_id
    media_files = update.message.effective_attachment

    if is_approved(user.id):
        return  # Skip NSFW scan for approved users

    if not isinstance(media_files, (list, tuple)):
        media_files = [media_files]

    for file in media_files:
        if not hasattr(file, "file_id"):
            continue

        file_obj = await context.bot.get_file(file.file_id)
        file_path = os.path.join(MEDIA_DIR, f"{user.id}_{file.file_id}")
        await file_obj.download_to_drive(file_path)

        if not os.path.exists(file_path):
            logger.error(f"Downloaded file missing: {file_path}")
            continue

        # Handle Stickers Separately
        if update.message.sticker:
            if update.message.sticker.is_animated:
                # Convert `.tgs` animated sticker to PNG
                new_path = convert_tgs_to_png(file_path)  
            elif update.message.sticker.is_video:
                # Convert `.webm` video sticker to an image frame
                new_path = extract_frame_from_webm(file_path)  
            else:
                # Convert `.webp` static sticker to PNG
                new_path = convert_webp_to_png(file_path)

            if new_path:
                file_path = new_path
            else:
                continue

        # Run NSFW detection
        result = detect_nsfw(file_path)
        if result is None:
            continue

        max_category = max(result, key=result.get)
        if max_category in ["porn", "sexy", "hentai"]:
            await update.message.delete()
            update_violations(user.id, max_category)
            alert_message = f"""
╭─────────────────
╰──●𝙽𝚂𝙵𝚆 𝙳𝙴𝚃𝙴𝙲𝚃𝙴𝙳 🔞
╭✠╼━━━━━━❖━━━━━━━✠╮ 
│☾𝚄𝚜𝚎𝚛: {user.id}
│☾𝚄𝚜𝚎𝚛𝚗𝚊𝚖𝚎: @{user.username if user.username else 'None'}
│☾𝙳𝚎𝚝𝚊𝚒𝚕𝚜:
│☾𝙳𝚛𝚊𝚠𝚒𝚗𝚐𝚜: {result['drawings']:.2f}
│☾𝙽𝚎𝚞𝚝𝚛𝚊𝚕: {result['neutral']:.2f}
│☾𝙿𝚘𝚛𝚗: {result['porn']:.2f}
│☾𝙷𝚎𝚗𝚝𝚊𝚒: {result['hentai']:.2f}
│☾𝚂𝚎𝚡𝚢: {result['sexy']:.2f}
╰✠╼━━━━━━❖━━━━━━━✠╯"""
            await context.bot.send_message(chat_id, alert_message, parse_mode="Markdown")
            
            channel_alert = f"""
NSFW DETECTED 🔞

User: {user.id}
Username: @{user.username if user.username else 'None'}

Details:

Drawings: {result['drawings']:.2f}
Neutral: {result['neutral']:.2f}
Porn: {result['porn']:.2f}
Hentai: {result['hentai']:.2f}
Sexy: {result['sexy']:.2f}

Chat: {chat_id}
"""
            keyboard = [[InlineKeyboardButton("👤 View Profile", url=f"tg://user?id={user.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(ALERT_CHANNEL_ID, channel_alert, reply_markup=reply_markup)

        # Delete the scanned file
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            logger.warning(f"File not found for deletion: {file_path}")



# ✅ Owner Commands
async def add_approved(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("» ᴀᴡᴡ, ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ ʙᴀʙʏ.")
        return
    try:
        user_id = int(context.args[0])
        add_approved_user(user_id)
        await update.message.reply_text(f"✅ User {user_id} added to approved list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /approve <user_id>")


async def remove_approved(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("» ᴀᴡᴡ, ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ ʙᴀʙʏ.")
        return 
    try:
        user_id = int(context.args[0])
        remove_approved_user(user_id)
        await update.message.reply_text(f"❌ User {user_id} removed from approved list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /remove <user_id>")


async def my_info(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    violations = get_user_violations(user_id)
    if not violations:
        await update.message.reply_text("✅ You have a clean record.")
    else:
        info = "📊 **NSFW Violation History**\n"
        for category, count in violations:
            info += f"🔸 {category}: {count} times\n"
        await update.message.reply_text(info, parse_mode="Markdown")



async def user_info(update: Update, context: CallbackContext):
    message = update.message
    args = context.args
    if len(args) == 0:
        username_or_userid = message.from_user.id
    else:
        username_or_userid = args[0]

    violation_history = get_user_violations(username_or_userid)

    if violation_history:
        reply_text = f"User {username_or_userid} has violation history:\n"
        reply_text += "\n".join(f"{violation[0]}: {violation[1]}" for violation in violation_history)
    else:
        reply_text = f"User {username_or_userid} is clear."

    # Send the reply to the user
    await message.reply_text(reply_text)


from telegram.constants import ParseMode

async def get_approved_users_list(update: Update, context: CallbackContext):
    approved_users_list = []
    for i, user_id in enumerate(get_all_users()):
        user = await context.bot.get_chat(user_id)
        if is_approved(user_id):
            user_name = user.first_name
            if user.username:
                user_url = f"https://t.me/{user.username}"
            else:
                user_url = f"https://t.me/{user_id}"
            user_link = f"{i+1}. [{user_name}]({user_url})"
            approved_users_list.append(user_link)
    if not approved_users_list:
        await update.message.reply_text("❌ No approved users found.")
    else:
        approved_users_str = "\n".join(approved_users_list)
        message = f"""``` ✨Approved Users✨ ```
╭✠╼━━━━━━❖━━━━━━━✠━━━━━━
│
{approved_users_str}
│
╰✠╼━━━━━━❖━━━━━━━✠━━━━━━
💫Total Approved Users: {len(approved_users_list)}
"""
        await update.message.reply_text(f""""{message}""", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)