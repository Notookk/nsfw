import asyncio
import datetime
import os
import random
import string
import time
import traceback
import aiofiles
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackContext

import config
from database import Database

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize database
broadcast_ids = {}
BROADCAST_AS_COPY = config.BROADCAST_AS_COPY
db = Database("users.db")  # Initialize database


### 🔹 Function to Send Message to a User or Group ###
async def send_msg(chat_id: int, message: Update) -> tuple[int, str | None]:
    """Send a message to a user or group and handle errors."""
    try:
        print(f"📤 Sending message to: {chat_id}")  # Debugging log
        if BROADCAST_AS_COPY:
            await message.copy(chat_id=chat_id)
        else:
            await message.forward(chat_id=chat_id)
        print(f"✅ Message sent to: {chat_id}")
        return 200, None
    except Exception as e:
        error_msg = f"❌ Error sending to {chat_id}: {str(e)}"
        print(error_msg)  # Debugging log
        if "blocked" in str(e) or "deactivated" in str(e) or "kicked" in str(e):
            await db.delete_user(chat_id)  # ✅ Remove inactive users or groups
            return 400, error_msg
        return 500, error_msg


### 🔹 Function to Perform the Broadcast ###
async def perform_broadcast(recipients, message, broadcast_id):
    """Handles the actual broadcasting process."""
    done, failed, success = 0, 0, 0
    failed_logs = []
    start_time = time.time()

    async with aiofiles.open("broadcast.txt", "w") as log_file:
        for chat_id in recipients:
            sts, msg = await send_msg(chat_id, message)

            if msg:
                await log_file.write(msg + "\n")
                failed_logs.append(msg)  # Store failed logs in memory

            if sts == 200:
                success += 1
            else:
                failed += 1

            done += 1
            broadcast_ids[broadcast_id].update({"current": done, "failed": failed, "success": success})

            await asyncio.sleep(0.05)  # Reduce sleep time for better efficiency

    elapsed = datetime.timedelta(seconds=int(time.time() - start_time))
    return success, failed, elapsed, failed_logs


### 🔹 Function to Start a Broadcast ###
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all users and groups."""
    m = update.message

    # ✅ Authorization check
    if not hasattr(config, "OWNER_IDS") or m.from_user.id not in config.OWNER_IDS:
        await m.reply_text("❌ You are not authorized to use this command.")
        return

    # ✅ Ensure a message is replied to
    if not m.reply_to_message:
        await m.reply_text("❌ Reply to a message to broadcast.")
        return

    all_users = await db.get_all_notif_user()  # ✅ Fetch active users
    all_groups = await db.get_all_groups()  # ✅ Fetch all groups

    recipients = all_users + all_groups  # ✅ Combine users & groups

    if not recipients:
        await m.reply_text("⚠️ No active users or groups found to broadcast.")
        return

    broadcast_msg = m.reply_to_message

    # ✅ Generate a broadcast ID
    broadcast_id = "".join(random.choices(string.ascii_letters, k=3))
    broadcast_ids[broadcast_id] = {"total": len(recipients), "current": 0, "failed": 0, "success": 0}

    out = await m.reply_text("📢 Broadcast started! You'll be notified when it's done.")

    total_users = await db.get_total_counts()
    success, failed, elapsed, failed_logs = await perform_broadcast(recipients, broadcast_msg, broadcast_id)

    await out.delete()  # Remove the initial message

    msg_text = (
        f"✅ **Broadcast Completed!**\n\n"
        f"📌 **Time Taken:** `{elapsed}`\n"
        f"👥 **Total Users:** `{total_users['users']}`\n"
        f"🏠 **Total Groups:** `{total_users['groups']}`\n"
        f"📨 **Delivered:** `{success}`\n"
        f"⚠️ **Failed:** `{failed}`"
    )

    if failed == 0:
        await m.reply_text(text=msg_text, quote=True)
    else:
        async with aiofiles.open("broadcast.txt", "w") as f:
            await f.writelines(failed_logs)
        await m.reply_document(document="broadcast.txt", caption=msg_text, quote=True)
        os.remove("broadcast.txt")  # ✅ Clean up the file

    # ✅ Remove broadcast tracking data
    broadcast_ids.pop(broadcast_id, None)


### 🔹 Command to List All Users & Groups ###
async def list_users_and_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch all users and groups from the database and print their IDs."""
    
    users = await db.get_all_users()
    groups = await db.get_all_groups()

    # ✅ Debugging Logs
    print(f"📊 Total Users: {len(users)}, Total Groups: {len(groups)}")

    if not users and not groups:
        await update.message.reply_text("⚠️ No users or groups found in the database.")
        return

    user_list = "\n".join([f"🆔 {user}" for user in users])
    group_list = "\n".join([f"🏠 {group}" for group in groups])

    message = "👥 **Registered Users:**\n" + (user_list if user_list else "No users found") + "\n\n" \
              "📌 **Registered Groups:**\n" + (group_list if group_list else "No groups found")

    # ✅ Split messages if they exceed Telegram’s character limit (4096 chars)
    if len(message) > 4000:
        for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(message)



#-----------------------------------------------------#

### 🔹 Track Users When They Interact ###
async def track_user(update: Update, context: CallbackContext):
    """Track a user when they send any message."""
    user = update.effective_user
    if user:
        await db.add_user(user.id, user.username or "Unknown")
        print(f"✅ User added: {user.id} - {user.username}")



# ### 🔹 Track Groups When the Bot Sends or Receives Messages ###
async def track_group(update: Update, context: CallbackContext):
    """Track a group when the bot sends or receives a message."""
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        await db.add_group(chat.id, chat.title)
        print(f"✅ Group added: {chat.id} - {chat.title}")

