import logging
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN
from database import Database
from handlers.copyright import (
    start_command,
    button_handler,
    mute_user,
    unmute_user,
    ping_u,
    get_user_id_from_username,
    delete_edited_messages,
    delete_invalid_messages,
    error_handler,
    delete_slang_words,
    commands
)
from handlers.nsfw import *
from handlers.utils import *
from handlers.broadcast import *

# ✅ Fix event loop conflict
nest_asyncio.apply()

# ✅ Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ✅ Initialize Database
db = Database()






async def main():
    """Main function to initialize the bot and start polling."""
    await db.init_db()  # ✅ Ensure database is ready before starting bot

    application = ApplicationBuilder().token(TOKEN).build()

    # ✅ Register Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("command", commands))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("ping", ping_u))
    application.add_handler(CommandHandler("info", get_user_id_from_username))
    application.add_handler(CommandHandler("userinfo", user_info))
    application.add_handler(CommandHandler("myinfo", my_info))
    application.add_handler(CommandHandler("sudolist", get_approved_users_list))
    application.add_handler(CommandHandler("add", add_approved))
    application.add_handler(CommandHandler("remove", remove_approved))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_slang_words))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_user))
    application.add_handler(MessageHandler(filters.ALL, track_group))
    application.add_handler(CommandHandler("listusers", list_users_and_groups))
    application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, delete_edited_messages))
    application.add_handler(MessageHandler(filters.ALL, handle_media))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_invalid_messages))
    application.add_error_handler(error_handler)

    logger.info("🤖 Bot is running...✅")

    await application.run_polling(timeout=30)  # Increase timeout to 30 seconds

    logger.info("🤖 Bot stopped...✅")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  # ✅ Uses existing event loop (NO conflict)
