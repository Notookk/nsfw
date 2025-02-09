import os
import logging
from telegram import User
from config import MEDIA_DIR

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def mention_user(user: User):
    """Creates a clickable mention for a Telegram user."""
    return f"[{user.first_name}](tg://user?id={user.id})"

def clean_media_folder():
    """Ensures media directory is clean before storing new files."""
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
    for file in os.listdir(MEDIA_DIR):
        os.remove(os.path.join(MEDIA_DIR, file))

def log_message(update, nsfw_category=None):
    """Logs incoming messages and NSFW detections."""
    user = update.message.from_user
    chat = update.message.chat
    content_type = update.message.effective_attachment

    log_msg = (f"User: {user.id} | Chat: {chat.id} | "
               f"Media Type: {content_type} | NSFW: {nsfw_category if nsfw_category else 'Safe'}")
    logger.info(log_msg)
