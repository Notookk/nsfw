from config import ALERT_CHANNEL_ID, DB_URI
import motor
from database.database import (
    is_approved, update_violations, add_approved_user, remove_approved_user, get_user_violations, Database, get_all_users)