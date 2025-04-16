import telebot
import sqlite3
import logging
import random
import string
import anony_number
import random_connection
import controls_anonybot
import uuid
import operations

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration and state management can be added here if needed

# Dictionary of nickname components for anonymous name generation
NICKNAME_PARTS = {
    'adjectives': [
        'Amazing', 'Brave', 'Clever', 'Daring', 'Eager', 'Fierce', 'Gentle', 'Happy', 
        'Innocent', 'Jolly', 'Kind', 'Lively', 'Mighty', 'Noble', 'Polite', 'Quick', 
        'Radiant', 'Silent', 'Tough', 'Unique', 'Vibrant', 'Wise', 'Zealous'
    ],
    'animals': [
        'Ant', 'Bear', 'Cat', 'Dog', 'Eagle', 'Fox', 'Goat', 'Hawk', 'Ibex', 
        'Jaguar', 'Koala', 'Lion', 'Mouse', 'Newt', 'Owl', 'Panda', 'Quail', 
        'Rabbit', 'Snake', 'Tiger', 'Unicorn', 'Viper', 'Wolf', 'Yak', 'Zebra'
    ]
}

# Dictionary to store private link requests
private_link_requests = {}

# Dictionary of nickname components (continued)
NICKNAME_PARTS['colors'] = [
    'Amber', 'Blue', 'Crimson', 'Diamond', 'Emerald', 'Fuchsia', 'Gold', 
    'Hazel', 'Indigo', 'Jade', 'Khaki', 'Lavender', 'Magenta', 'Navy', 
    'Orange', 'Purple', 'Quartz', 'Ruby', 'Silver', 'Teal', 'Umber', 
    'Violet', 'White', 'Yellow'
    ]


def ANONY_NAME():
    """
    Generate a random anonymous name by combining parts from three categories.
    Each part has 1-3 characters taken from the beginning to ensure uniqueness.
    
    Returns:
        A unique anonymous name string
    """
    # Select random parts from each category
    adjective = random.choice(NICKNAME_PARTS['adjectives'])
    animal = random.choice(NICKNAME_PARTS['animals'])
    color = random.choice(NICKNAME_PARTS['colors'])
    
    # Take random length (1-3) prefix from each part
    adj_len = random.randint(1, 3)
    animal_len = random.randint(1, 3)
    color_len = random.randint(1, 3)
    
    adj_part = adjective[:adj_len]
    animal_part = animal[:animal_len]
    color_part = color[:color_len]
    
    # Add a random number for additional uniqueness
    random_num = random.randint(10, 999)
    
    # Combine all parts to form the anonymous name
    anony_name = f"{adj_part}{animal_part}{color_part}{random_num}"
    
    logger.info(f"Generated anonymous name: {anony_name}")
    return anony_name

def generate_anony_name():
    """
    Generate a unique anonymous name for Anony Number feature.
    Uses a short UUID to ensure uniqueness.
    
    Returns:
        A unique anonymous name string
    """
    # Generate a short UUID (first 8 characters)
    short_uuid = str(uuid.uuid4())[:8]
    
    logger.info(f"Generated anonymous number ID: {short_uuid}")
    return short_uuid

def MEMBERSHIP_ID():
    """
    Generate a membership ID consisting of 9 digits starting with '92'.
    
    Returns:
        A string representing the membership ID
    """
    # Start with '92'
    prefix = "92"
    
    # Generate 7 more random digits
    random_digits = ''.join(random.choices(string.digits, k=7))
    
    # Combine to form the 9-digit membership ID
    membership_id = f"{prefix}{random_digits}"
    
    logger.info(f"Generated membership ID: {membership_id}")
    return membership_id

# Initialize the bot with the provided API key
bot = telebot.TeleBot("5768243722:AAGuPYWlGCH9x7I-N5bJ3u6royTuEfQ5ZFw")

# Dictionary to track user transitions (e.g., from connected to AI chat)
user_transitions = {}

# Update existing users with ANONY_NAME if they don't have one
try:
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    
    # Find users without ANONY_NAME
    cursor.execute("SELECT USER_ID FROM users WHERE ANONY_NAME IS NULL OR ANONY_NAME = ''")
    users_without_anony_name = cursor.fetchall()
    
    for user_row in users_without_anony_name:
        user_id = user_row[0]
        anony_name = generate_anony_name()
        
        # Update the user with a new ANONY_NAME
        cursor.execute("UPDATE users SET ANONY_NAME = ? WHERE USER_ID = ?", (anony_name, user_id))
        logger.info(f"Updated user {user_id} with new ANONY_NAME: {anony_name}")
    
    conn.commit()
    conn.close()
    logger.info(f"Updated {len(users_without_anony_name)} users with new ANONY_NAME values")
except sqlite3.Error as e:
    logger.error(f"Database error when updating users with ANONY_NAME: {e}")

# Database functions
def setup_database():
    """Initialize the database connection and create tables if needed."""
    try:
        # Connect to the main user database
        conn = sqlite3.connect('user_db.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Create the user table if it doesn't exist with TYPE set to R48 and OTP_EXP field
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            USER_ID INTEGER PRIMARY KEY,
            PEER_ID TEXT,
            TYPE TEXT DEFAULT 'R48',
            STATUS TEXT DEFAULT 'OPEN',
            TIMER INTEGER DEFAULT 120,
            OTP TEXT,
            OTP_EXP DATETIME,
            ANONY_NAME TEXT,
            ANONY_PEER TEXT,
            CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        logger.info("Database setup completed successfully")
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Database setup error: {e}")
        raise

# Function to ensure user_def.db exists
def setup_user_def_database():
    """Initialize the user_def database connection and create tables if needed."""
    try:
        user_def_db_path = 'user_def.db'
        
        # Check if file exists
        import os
        if not os.path.exists(user_def_db_path):
            logger.info(f"Creating new user_def database at {user_def_db_path}")
            
            # Try to create the directory if it doesn't exist
            os.makedirs(os.path.dirname(user_def_db_path), exist_ok=True)
        
        # Connect to the user_def database with explicit file creation
        user_def_conn = sqlite3.connect(user_def_db_path)
        user_def_cursor = user_def_conn.cursor()
        
        # Create the user_def table if it doesn't exist - with only the required fields
        user_def_cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_def (
            USER_ID INTEGER PRIMARY KEY,
            MEMBERSHIP_ID TEXT UNIQUE,
            MEMBERSHIP_TYPE TEXT DEFAULT 'SILVER',
            CREDIT INTEGER DEFAULT 300
        )
        ''')
        
        # Verify the table was created
        user_def_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_def'")
        table_exists = user_def_cursor.fetchone() is not None
        
        if table_exists:
            logger.info("user_def table created/verified successfully")
        else:
            logger.error("Failed to create user_def table")
        
        user_def_conn.commit()
        
        # Check if the file was created
        if os.path.exists(user_def_db_path):
            file_size = os.path.getsize(user_def_db_path)
            logger.info(f"user_def.db created successfully, size: {file_size} bytes")
        else:
            logger.error("Failed to create user_def.db file")
        
        # Close the connection
        user_def_conn.close()
        return True
    except Exception as e:
        logger.error(f"User_def database setup error: {e}")
        return False

# Create database connections
conn, cursor = setup_database()
setup_user_def_database()

def insert_user(user_id):
    """Add a new user to the database if they don't already exist."""
    # First check if user already exists in users table
    try:
        cursor.execute("SELECT USER_ID FROM users WHERE USER_ID = ?", (user_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Check if the user has an ANONY_NAME, if not, generate one
            cursor.execute("SELECT ANONY_NAME FROM users WHERE USER_ID = ?", (user_id,))
            anony_name_data = cursor.fetchone()
            
            if not anony_name_data or not anony_name_data[0]:
                # Generate a random ANONY_NAME
                anony_name = generate_anony_name()
                
                # Update the user with the new ANONY_NAME
                cursor.execute("UPDATE users SET ANONY_NAME = ? WHERE USER_ID = ?", (anony_name, user_id))
                conn.commit()
                logger.info(f"Generated ANONY_NAME '{anony_name}' for existing user {user_id}")
            else:
                logger.info(f"User {user_id} already exists with ANONY_NAME '{anony_name_data[0]}'")
        else:
            # Generate a random ANONY_NAME for the new user
            anony_name = generate_anony_name()
            
            # Insert into users table in user_db.db with TYPE set to R48 and the generated ANONY_NAME
            cursor.execute('''
            INSERT INTO users (USER_ID, PEER_ID, TYPE, STATUS, TIMER, OTP, ANONY_NAME)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, '', 'R48', 'OPEN', 120, '', anony_name))
            conn.commit()
            logger.info(f"User {user_id} inserted into users table with ANONY_NAME '{anony_name}'")
    except sqlite3.Error as e:
        logger.error(f"Database error when checking/inserting user {user_id} into users table: {e}")
    
    # Now handle user_def.db separately with a direct approach
    try:
        # Ensure the user_def database exists and is properly set up
        setup_user_def_database()
        
        # Connect directly to user_def.db
        user_def_db_path = 'user_def.db'
        user_def_conn = sqlite3.connect(user_def_db_path)
        user_def_cursor = user_def_conn.cursor()
        
        # Check if user already exists in user_def table
        user_def_cursor.execute("SELECT USER_ID FROM user_def WHERE USER_ID = ?", (user_id,))
        existing_user = user_def_cursor.fetchone()
        
        if existing_user:
            logger.info(f"User {user_id} already exists in user_def.db, skipping insert")
        else:
            # Generate membership ID
            membership_id = MEMBERSHIP_ID()
            
            # Insert user into user_def table with only the required fields
            user_def_cursor.execute('''
            INSERT INTO user_def (USER_ID, MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT)
            VALUES (?, ?, ?, ?)
            ''', (user_id, membership_id, 'SILVER', 300))
            user_def_conn.commit()
            logger.info(f"User {user_id} inserted into user_def.db with membership ID {membership_id}")
        
        # Verify the data exists in the table
        user_def_cursor.execute("SELECT * FROM user_def WHERE USER_ID = ?", (user_id,))
        user_data = user_def_cursor.fetchone()
        if user_data:
            logger.info(f"Verified user {user_id} exists in user_def.db: {user_data}")
        else:
            logger.error(f"Failed to verify user {user_id} in user_def.db")
        
        user_def_conn.close()
    except Exception as e:
        logger.error(f"Error handling user_def.db for user {user_id}: {e}")

# Menu creation functions
def create_main_menu():
    """Create the main menu markup with all primary options."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🔐 Private Connection", callback_data="private_connection"))
    markup.row(telebot.types.InlineKeyboardButton("🔀 Random Connection", callback_data="random_connection"))
    markup.row(
        telebot.types.InlineKeyboardButton("⏏️", callback_data="eject"),
        telebot.types.InlineKeyboardButton("⏹️", callback_data="stop"),
        telebot.types.InlineKeyboardButton("⏩️", callback_data="forward")
    )
    markup.row(telebot.types.InlineKeyboardButton("📲 Anony Number", callback_data="anony_number"))
    markup.row(telebot.types.InlineKeyboardButton("🔊 Broadcasting", callback_data="broadcasting"))
    markup.row(telebot.types.InlineKeyboardButton("✨Chat with Bella", callback_data="ai_chat_bot"))
    # About button (Privacy button is disabled)
    markup.row(
        telebot.types.InlineKeyboardButton("🚹 About", callback_data="about")
    )
    markup.row(telebot.types.InlineKeyboardButton("More >>", callback_data="more"))
    return markup

def create_more_menu():
    """Create the secondary 'More' menu markup."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🪙 Membership", callback_data="membership"))
    markup.row(
        telebot.types.InlineKeyboardButton("Help", callback_data="help"),
        telebot.types.InlineKeyboardButton("Contact Us", callback_data="contact_us")
    )
    markup.row(telebot.types.InlineKeyboardButton("<< Back", callback_data="back"))
    return markup

# Settings menu functionality has been removed

# Command handlers
# Import the database manager functions
try:
    from telegram_db_manager import register_new_user
except ImportError:
    # Define a fallback function if import fails
    def register_new_user(user_id):
        logger.error(f"Failed to import register_new_user function, using fallback for user {user_id}")
        return {
            "status": "error",
            "message": "Database module not available"
        }

# Import private connection handler
try:
    from private_connection import handle_private_connection_request, check_user_status
except ImportError:
    # Define a fallback function if import fails
    def handle_private_connection_request(user_id):
        logger.error(f"Failed to import handle_private_connection_request function, using fallback for user {user_id}")
        return "Private connection feature is currently unavailable. Please try again later."
    
    def check_user_status(user_id):
        logger.error(f"Failed to import check_user_status function, using fallback for user {user_id}")
        return {
            "status": "error",
            "message": "Private connection feature is currently unavailable. Please try again later."
        }

# Import message sender
try:
    from message_sender import handle_message
except ImportError:
    # Define a fallback function if import fails
    def handle_message(bot, message, user_id=None):
        logger.error(f"Failed to import handle_message function, using fallback for user {message.from_user.id}")
        return False

# Import private link verifier
try:
    from private_link_verifier import verify_private_link
except ImportError:
    # Define a fallback function if import fails
    def verify_private_link(link_text, user_id):
        logger.error(f"Failed to import verify_private_link function, using fallback for user {user_id}")
        return {
            "status": "error",
            "message": "Private link verification is currently unavailable. Please try again later."
        }

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle the /start command by registering the user and showing the main menu."""
    user_id = message.from_user.id
    
    # Register user in both database tables
    user_data = register_new_user(user_id)
    
    # Create welcome message based on registration status
    if user_data["status"] == "success":
        welcome_text = (
            f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\n"
            #f"Your anonymous name: {user_data['anony_name']}\n"
            #f"Your membership ID: {user_data['membership_id']}\n"
            #f"Membership type: {user_data['membership_type']}\n"
            #f"Available credits: {user_data['credit']}"
        )
    else:
        # Fallback to original message and use the old insert_user function
        insert_user(user_id)
        
        # Try to get user information from both databases after insertion
        try:
            # Get data from users table in user_db.db
            cursor.execute("SELECT ANONY_NAME FROM users WHERE USER_ID = ?", (user_id,))
            user_data = cursor.fetchone()
            anony_name = user_data[0] if user_data and user_data[0] else "Anonymous"
            
            # Get membership info from user_def.db
            user_def_db_path = 'user_def.db'
            
            # Make sure user_def.db exists and is set up
            setup_user_def_database()
            
            # Connect to user_def.db
            user_def_conn = sqlite3.connect(user_def_db_path)
            user_def_cursor = user_def_conn.cursor()
            
            # Get user data from user_def table
            user_def_cursor.execute("SELECT MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT FROM user_def WHERE USER_ID = ?", (user_id,))
            membership_data = user_def_cursor.fetchone()
            
            if membership_data:
                membership_id, membership_type, credit = membership_data
                welcome_text = (
                    f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\n"
                    #f"Your anonymous name: {anony_name}\n"
                    #f"Your membership ID: {membership_id}\n"
                    #f"Membership type: {membership_type}\n"
                    #f"Available credits: {credit}"
                )
                logger.info(f"Retrieved user data from both databases for user {user_id}")
            else:
                welcome_text = f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\nYour anonymous name: {anony_name}"
                logger.warning(f"Could not retrieve membership data for user {user_id} from user_def.db")
            user_def_conn.close()
        except Exception as e:
            logger.error(f"Error retrieving user data after fallback insertion: {e}")
            welcome_text = "||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼."
    
    # Send welcome message with main menu
    markup = create_main_menu()
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    logger.info(f"Welcome message sent to user {user_id}")

# Message handlers
# Disabled About text handler
# @bot.message_handler(func=lambda message: message.text == "🚹\nAbout")
# def handle_about_text(message):
#     """Handle text message for About."""
#     bot.reply_to(message, "Hey")
#     logger.info(f"About info sent to user {message.from_user.id} via text message")

# Callback handlers
@bot.callback_query_handler(func=lambda call: call.data == "more")
def handle_more_callback(call):
    """Handle the 'More' button callback."""
    bot.answer_callback_query(call.id)
    markup = create_more_menu()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    logger.info(f"More menu shown to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_back_callback(call):
    """Handle the 'Back' button callback to return to main menu."""
    bot.answer_callback_query(call.id)
    markup = create_main_menu()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    logger.info(f"User {call.from_user.id} returned to main menu")

@bot.callback_query_handler(func=lambda call: call.data == "private_connection")
def handle_private_connection_callback(call):
    """Handle the 'Private Connection' button callback."""
    user_id = call.from_user.id
    
    # Process the private connection request
    result = handle_private_connection_request(user_id)
    
    if result["status"] == "otp_exists":
        # Show popup message that current link is still valid
        bot.answer_callback_query(call.id, text=result["message"], show_alert=True)
        
        # Also send the connection string as a message
        connection_string = result["connection_string"]
        bot.send_message(call.message.chat.id, f"Your current private connection link:\n\n{connection_string}")
    else:
        # For other statuses, just answer the callback and send the message
        bot.answer_callback_query(call.id)
        response = result["message"]
        bot.send_message(call.message.chat.id, response)
    
    logger.info(f"Private connection request processed for user {user_id} with status {result['status']}")

# About callback handler
@bot.callback_query_handler(func=lambda call: call.data == "about")
def handle_about_callback(call):
    """Handle the 'About' button callback."""
    bot.answer_callback_query(
        call.id,
        text="Anonymous Chat 2.5.6v\n\nStatus : 🟢 Normal",
        show_alert=True
    )
    logger.info(f"About info sent to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def handle_help_callback(call):
    """Handle the 'Help' button callback."""
    help_text = """
📋 *Anonymous Chats Features Guide*:

🔐 *Private Connection*: Connect privately with someone using a unique temporary link. Share the link with your friend to establish a secure, anonymous chat.

🔀 *Random Connection*: Get matched with a random user for anonymous chatting. Great for meeting new people.

⏏️⏹️⏩️ *Controls*: 
- ⏏️ Eject: End current chat and return to menu
- ⏹️ Stop: Pause the current chat
- ⏩️ Forward: To find other random match

📲 *Anony Number*: Get a unique permanent anonymous identifier that others can use to connect with you without knowing your real identity.

🔊 *Broadcasting*: Send messages to multiple connections at once.

✨ *Chat with Bella*: Talk to talkative bella for help or just casual conversation.

Need more help? Use the Contact Us button to reach our support team.
"""
    bot.send_message(
        call.message.chat.id,
        help_text,
        parse_mode="Markdown"
    )
    logger.info(f"Help information sent to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "contact_us")
def handle_contact_us_callback(call):
    """Handle the 'Contact Us' button callback."""
    bot.answer_callback_query(
        call.id,
        text="Email us at heron_driest8t@icloud.com",
        show_alert=True
    )
    logger.info(f"Contact information sent to user {call.from_user.id}")

# Disabled Privacy callback handler
# @bot.callback_query_handler(func=lambda call: call.data == "privacy")
# def handle_privacy_callback(call):
#     """Handle the 'Privacy' button callback."""
#     bot.answer_callback_query(call.id)
#     bot.send_message(call.message.chat.id, "Privacy information")
#     logger.info(f"Privacy info sent to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "anony_number")
def handle_anony_number_callback(call):
    """Handle the 'Anony Number' button callback."""
    bot.answer_callback_query(call.id)
    
    try:
        # Get user ID
        user_id = int(call.from_user.id)
        logger.info(f"Anony Number requested by user {user_id}")
        
        # Create a message object with the correct user ID
        # This ensures we're not passing the bot's ID by mistake
        class UserMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                self.chat = type('obj', (object,), {'id': chat_id})
        
        # Create a message with the user's ID
        user_message = UserMessage(user_id, call.message.chat.id)
        
        # Call the anony_number module's handler with the correct user ID
        anony_number.handle_anony_number_command(bot, user_message)
    except Exception as e:
        logger.error(f"Error handling anony_number request: {e}")
        bot.send_message(call.message.chat.id, "Sorry, there was an error processing your request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("share_"))
def handle_share_decision(call):
    """Handle the decision to share an anonymous number."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"Share decision from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_share_decision(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("save_"))
def handle_save_decision(call):
    """Handle the decision to save an anonymous number."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"Save decision from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_save_decision(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_an_") or call.data.startswith("decline_an_"))
def handle_an_connection_response(call):
    """Handle the response to an Anonymous Number connection request."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"AN connection response from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_an_connection_response(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "random_connection")
def handle_random_connection_callback(call):
    """Handle the Random Connection button callback."""
    try:
        user_id = call.from_user.id
        logger.info(f"Random connection requested by user {user_id}")
        
        # Check the user's current status
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT STATUS FROM users WHERE USER_ID = ?", (user_id,))
        status_data = cursor.fetchone()
        
        if not status_data:
            conn.close()
            bot.answer_callback_query(call.id, "User not found in database. Please try again later.")
            return
        
        current_status = status_data[0]
        
        # Check if user is already in a connection
        if current_status in ["PRIVATE", "RANDOM", "CONNECTED", "AI"]:
            conn.close()
            # Show popup message
            bot.answer_callback_query(
                call.id,
                "⚠️\nYou are connected\nUse ⏹️ to close\nTry again",
                show_alert=True
            )
            return
        
        # If status is OPEN, show waiting message
        if current_status == "OPEN":
            conn.close()
            #bot.answer_callback_query(
            #    call.id,
            #    "Please wait while we are searching for partner"

            #)
            #return
            bot.answer_callback_query(
                call.id,
                "⚠️\nPlease wait while we are searching for partner",
                show_alert=True
            )
          
            return
        
        # Update user status to OPEN
        cursor.execute("UPDATE users SET STATUS = 'OPEN' WHERE USER_ID = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Updated user {user_id} status to OPEN for random connection")
        
        # Create a message object with the user's ID for the random_connection module
        class UserMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                self.chat = type('obj', (object,), {'id': chat_id})
        
        # Create a message with the user's ID
        user_message = UserMessage(int(user_id), call.message.chat.id)
        
        # Call the random_connection module's handler
        random_connection.handle_random_connection(bot, user_message)
        
    except Exception as e:
        logger.error(f"Error handling random connection request: {e}")
        bot.answer_callback_query(call.id, "Sorry, there was an error processing your request. Please try again later.")



@bot.callback_query_handler(func=lambda call: call.data == "eject")
def handle_eject_callback(call):
    """Handle the ⏏️ (Eject) button callback."""
    try:
        logger.info(f"Eject button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_eject_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling eject button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "stop")
def handle_stop_callback(call):
    """Handle the ⏹️ (Stop) button callback."""
    try:
        logger.info(f"Stop button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_stop_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling stop button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "forward")
def handle_forward_callback(call):
    """Handle the ⏩️ (Forward) button callback."""
    try:
        logger.info(f"Forward button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_forward_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling forward button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "broadcasting")
def handle_broadcasting_callback(call):
    """Handle the 🔊 Broadcasting button callback."""
    try:
        logger.info(f"Broadcasting button clicked by user {call.from_user.id}")
        # Show message that the feature is unavailable
        bot.answer_callback_query(
            call.id,
            text="This feature is unavailable for you",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Error handling broadcasting button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

def get_user_membership_info(user_id):
    """
    Get a user's membership information from the user_def database.
    
    Args:
        user_id: The Telegram user ID
        
    Returns:
        A dictionary with membership information or None if not found
    """
    try:
        # Define user_def database path
        user_def_db_path = 'user_def.db'
        
        # Connect to the user_def database
        conn = sqlite3.connect(user_def_db_path)
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("SELECT MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT FROM user_def WHERE USER_ID = ?", (user_id,))
        membership_data = cursor.fetchone()
        
        conn.close()
        
        if not membership_data:
            logger.error(f"User {user_id} not found in user_def database")
            return None
        
        membership_id, membership_type, credit = membership_data
        
        return {
            "membership_id": membership_id,
            "membership_type": membership_type,
            "credit": credit
        }
    except Exception as e:
        logger.error(f"Error getting membership info for user {user_id}: {e}")
        return None

@bot.callback_query_handler(func=lambda call: call.data == "membership")
def handle_membership_callback(call):
    """Handle the Membership button callback."""
    try:
        user_id = call.from_user.id
        logger.info(f"Membership button clicked by user {user_id}")
        
        # Get membership information
        membership_info = get_user_membership_info(user_id)
        
        if membership_info:
            # Show membership information
            bot.answer_callback_query(
                call.id,
                text=f"Aonymous Chat 2\n"
                     f"Membership ID: {membership_info['membership_id']}\n"
                     f"Membership Type: {membership_info['membership_type']}\n"
                     f"Credit: {membership_info['credit']}",
                show_alert=True
            )
        else:
            # Show error message
            bot.answer_callback_query(
                call.id,
                text="Could not retrieve membership information. Please try again later.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Error handling membership button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_bot")
def handle_ai_chat_bot_callback(call):
    """Handle the ✨Chat with Bella button callback."""
    try:
        user_id = call.from_user.id
        logger.info(f"Chat with Bella button clicked by user {user_id}")
        
        # Get current user status and peer_id
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT STATUS, PEER_ID FROM users WHERE USER_ID = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            bot.answer_callback_query(
                call.id,
                text="User not found in database. Please try again later.",
                show_alert=True
            )
            return
        
        current_status, peer_id = user_data
        conn.close()
        
        # 1. Check if user is in PRIVATE, OPEN, RANDOM, or CONNECTED status
        if current_status in ["PRIVATE", "OPEN", "RANDOM", "CONNECTED"]:
            bot.answer_callback_query(
                call.id,
                "⚠️\nYou are connected\nUse ⏹️ to close\nTry again",
                show_alert=True
            )
            return
        # 2. Check if user is in HOLD status
        if current_status == "HOLD":
            bot.answer_callback_query(
                call.id,
                "⚠️\nYour previous request in process\nUse ⏹️ to close\nTry again",
                show_alert=True
        
            )
            return
        
        # 3. Check if user is already in AI chat
        if current_status == "AI":
            bot.answer_callback_query(
                call.id,
                "⚠️\nYou are already connected!!",
                show_alert=True
            )
            return
        
        # User is not in any of the above statuses, start AI chat directly
        # Update user status in database
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Updated user {user_id} status to AI")
        
        # Start AI chat
        from ai_integration import start_ai_chat
        if start_ai_chat(bot, call.message):
            logger.info(f"Started AI chat for user {user_id} directly")
        else:
            logger.error(f"Failed to start AI chat for user {user_id} directly")
    except Exception as e:
        logger.error(f"Error handling Chat with Bella button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_confirm_yes")
def handle_ai_chat_confirm_yes(call):
    """Handle the YES confirmation for AI Chat."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} confirmed switching to AI chat")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Get the peer ID before updating
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT PEER_ID FROM users WHERE USER_ID = ?", (user_id,))
        peer_data = cursor.fetchone()
        
        if peer_data and peer_data[0]:
            peer_id = peer_data[0]
            logger.info(f"Found peer {peer_id} for user {user_id} before switching to AI chat")
            
            # Send notification to the peer
            try:
                bot.send_message(
                    peer_id,
                    "Your peer disconnected with you. Your status is closed now."
                )
                logger.info(f"Sent disconnection notification to peer {peer_id}")
                
                # Update peer's status to CLOSED
                cursor.execute("UPDATE users SET STATUS = 'CLOSED', PEER_ID = NULL WHERE USER_ID = ?", (peer_id,))
                logger.info(f"Updated peer {peer_id} status to CLOSED")
            except Exception as peer_e:
                logger.error(f"Error notifying peer {peer_id}: {peer_e}")
        
        # Update user status in database
        cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Updated user {user_id} status to AI")
        
        # Start AI chat
        from ai_integration import start_ai_chat
        if start_ai_chat(bot, call.message):
            logger.info(f"Started AI chat for user {user_id}")
        else:
            logger.error(f"Failed to start AI chat for user {user_id}")
    except Exception as e:
        logger.error(f"Error handling AI Chat confirmation: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_confirm_no")
def handle_ai_chat_confirm_no(call):
    """Handle the NO confirmation for AI Chat."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} declined switching to AI chat")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling AI Chat decline: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "share_an_yes")
def handle_share_an_yes(call):
    """Handle the YES confirmation for sharing anonymous number."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} confirmed sharing anonymous number")
        
        # Check if user is transitioning to AI chat
        if user_id in user_transitions and user_transitions[user_id]["transitioning_to"] == "AI":
            peer_id = user_transitions[user_id]["peer_id"]
            
            # Share anonymous number with peer
            try:
                # Get user's anonymous number
                conn = sqlite3.connect('user_def.db')
                cursor = conn.cursor()
                cursor.execute("SELECT ANONY_NUMBER FROM user_def WHERE USER_ID = ?", (user_id,))
                an_data = cursor.fetchone()
                conn.close()
                
                if an_data and an_data[0]:
                    anony_number = an_data[0]
                    
                    # Send anonymous number to peer
                    bot.send_message(
                        peer_id,
                        f"Your partner has shared their anonymous number with you: /AN{anony_number}"
                    )
                    
                    # Notify user that number was shared
                    bot.send_message(
                        call.message.chat.id,
                        "Your anonymous number has been shared with your partner."
                    )
                else:
                    # User doesn't have an anonymous number
                    bot.send_message(
                        call.message.chat.id,
                        "You don't have an anonymous number to share."
                    )
            except Exception as e:
                logger.error(f"Error sharing anonymous number: {e}")
                bot.send_message(
                    call.message.chat.id,
                    "Error sharing anonymous number. Please try again later."
                )
            
            # Now transition to AI chat
            # Update user status in database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Updated user {user_id} status to AI after sharing anonymous number")
            
            # Start AI chat
            from ai_integration import start_ai_chat
            if start_ai_chat(bot, call.message):
                logger.info(f"Started AI chat for user {user_id} after sharing anonymous number")
            else:
                logger.error(f"Failed to start AI chat for user {user_id} after sharing anonymous number")
            
            # Clean up transition data
            del user_transitions[user_id]
        else:
            # Not transitioning to AI chat, just handle normal anonymous number sharing
            bot.send_message(
                call.message.chat.id,
                "Anonymous number sharing is only available when transitioning to AI chat."
            )
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling anonymous number sharing: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "share_an_no")
def handle_share_an_no(call):
    """Handle the NO confirmation for sharing anonymous number."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} declined sharing anonymous number")
        
        # Check if user is transitioning to AI chat
        if user_id in user_transitions and user_transitions[user_id]["transitioning_to"] == "AI":
            # Just transition to AI chat without sharing anonymous number
            # Update user status in database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Updated user {user_id} status to AI without sharing anonymous number")
            
            # Start AI chat
            from ai_integration import start_ai_chat
            if start_ai_chat(bot, call.message):
                logger.info(f"Started AI chat for user {user_id} without sharing anonymous number")
            else:
                logger.error(f"Failed to start AI chat for user {user_id} without sharing anonymous number")
            
            # Clean up transition data
            del user_transitions[user_id]
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling anonymous number sharing decline: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

# Handler for Anonymous Number connection (/AN...)
@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text.startswith('/AN'))
def handle_an_command(message):
    """Handle Anonymous Number connection requests."""
    user_id = message.from_user.id
    an_text = message.text
    logger.info(f"Received Anonymous Number connection request from user {user_id}: {an_text}")
    
    # Call the anony_number module's handler
    anony_number.handle_an_command(bot, message)

# Handler for private link verification (/92...)
@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text.startswith('/92'))
def handle_private_link(message):
    """Handle private link verification messages."""
    user_id = message.from_user.id
    link_text = message.text
    
    logger.info(f"Received private link verification request from user {user_id}: {link_text}")
    
    # Send initial verification message
    bot.send_message(user_id, "Verifying Private Link...")
    
    # Verify the private link
    result = verify_private_link(link_text, user_id)
    
    if result["status"] == "success":
        # Send the success message
        bot.send_message(user_id, result["message"])
        logger.info(f"Private link verified for user {user_id}, connected to peer {result.get('peer_id')}")
    
    elif result["status"] == "confirmation_needed":
        # Store the request details in a temporary dictionary for later use
        # This will be used when the peer responds to the confirmation
        peer_id = result["peer_id"]
        private_link_requests[str(peer_id)] = {
            "requester_id": user_id,
            "link_text": link_text
        }
        
        # Create confirmation keyboard for the peer
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("Yes", callback_data=f"private_link_confirm_yes_{user_id}"),
            telebot.types.InlineKeyboardButton("No", callback_data=f"private_link_confirm_no_{user_id}")
        )
        
        # Send confirmation message to the peer
        peer_id = result["peer_id"]
        bot.send_message(
            peer_id,
            f"User is asking to connect with you using a private link. Do you want to accept?",
            reply_markup=markup
        )
        
        # Inform the requester that confirmation is pending
        bot.send_message(
            user_id,
            "Your connection request has been sent to the peer. Waiting for their confirmation..."
        )
        
        logger.info(f"Private link confirmation request sent from user {user_id} to peer {peer_id}")
    
    else:
        # Send the error message
        bot.send_message(user_id, result["message"])
        logger.warning(f"Private link verification failed for user {user_id}: {result['message']}")

# Callback handler for private link confirmation (Yes)
@bot.callback_query_handler(func=lambda call: call.data.startswith("private_link_confirm_yes_"))
def handle_private_link_confirm_yes(call):
    """Handle the YES confirmation for private link connection."""
    try:
        peer_id = call.from_user.id
        requester_id = call.data.split("_")[-1]
        
        logger.info(f"User {peer_id} accepted private link connection from user {requester_id}")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Get the original link text
        if str(peer_id) not in private_link_requests or "requester_id" not in private_link_requests[str(peer_id)]:
            bot.send_message(peer_id, "Error: Connection request data not found.")
            return
        
        link_text = private_link_requests[str(peer_id)]["link_text"]
        requester_id = private_link_requests[str(peer_id)]["requester_id"]
        
        # Connect to database
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        
        # Update peer status to PRIVATE (don't remove OTP yet)
        cursor.execute("UPDATE users SET STATUS = 'PRIVATE' WHERE USER_ID = ?", (peer_id,))
        conn.commit()
        conn.close()
        
        # Establish the private connection directly instead of using verify_private_link again
        try:
            # Connect to database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            
            # Update requester to connect to peer
            cursor.execute("""
            UPDATE users
            SET PEER_ID = ?, STATUS = 'PRIVATE', TIMER = 5760
            WHERE USER_ID = ?
            """, (peer_id, requester_id))
            
            # Update peer to connect to requester
            cursor.execute("""
            UPDATE users
            SET PEER_ID = ?, STATUS = 'PRIVATE', TIMER = 5760
            WHERE USER_ID = ?
            """, (requester_id, peer_id))
            
            # Now that the connection is established, remove OTPs from both users
            cursor.execute("UPDATE users SET OTP = '', OTP_EXP = NULL WHERE USER_ID IN (?, ?)", 
                          (requester_id, peer_id))
            
            conn.commit()
            conn.close()
            
            # Notify the requester
            bot.send_message(
                requester_id,
                "Your connection request has been accepted! You are now connected privately."
            )
            
            # Notify the peer
            bot.send_message(
                peer_id,
                "You have accepted the connection request. You are now connected privately."
            )
            
            logger.info(f"Private connection established between user {requester_id} and peer {peer_id}")
            
        except Exception as e:
            logger.error(f"Error establishing private connection: {e}")
            
            # Something went wrong
            bot.send_message(
                requester_id,
                "Error establishing connection. Please try again later."
            )
            bot.send_message(
                peer_id,
                "Error establishing connection. Please try again later."
            )
        
        # Clean up the request data
        if str(peer_id) in private_link_requests:
            del private_link_requests[str(peer_id)]
            
    except Exception as e:
        logger.error(f"Error handling private link confirmation (Yes): {e}")
        bot.answer_callback_query(call.id, "Error processing your response.")

# Callback handler for private link confirmation (No)
@bot.callback_query_handler(func=lambda call: call.data.startswith("private_link_confirm_no_"))
def handle_private_link_confirm_no(call):
    """Handle the NO confirmation for private link connection."""
    try:
        peer_id = call.from_user.id
        requester_id = call.data.split("_")[-1]
        
        logger.info(f"User {peer_id} rejected private link connection from user {requester_id}")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Notify the requester
        bot.send_message(
            requester_id,
            "Your partner rejected your connection request."
        )
        
        # We don't remove the OTP here to allow the user to use the link again if needed
        
        # Clean up the request data
        if str(peer_id) in private_link_requests:
            del private_link_requests[str(peer_id)]
            
    except Exception as e:
        logger.error(f"Error handling private link confirmation (No): {e}")
        bot.answer_callback_query(call.id, "Error processing your response.")

# Message handler for regular messages (without commands)
@bot.message_handler(func=lambda message: True, content_types=['text', 'sticker', 'voice', 'photo', 'video', 'animation', 'audio', 'document'])
def handle_all_messages(message):
    """Handle all regular messages (without commands) and forward them to peers if appropriate."""
    # Skip command messages (they start with '/')
    if message.content_type == 'text' and message.text.startswith('/'):
        return
    
    user_id = message.from_user.id
    logger.info(f"Received {message.content_type} message from user {user_id}")
    
    # Check if user is in AI chat mode or HOLD mode
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT STATUS FROM users WHERE USER_ID = ?", (user_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        user_status = user_data[0]
        
        # If user is in HOLD status, show notification and return
        if user_status == 'HOLD':
            conn.close()
            logger.info(f"User {user_id} tried to send message while in HOLD status")
            bot.send_message(
                message.chat.id,
                "Please wait, your previous request is in progress..."
            )
            return
        
        # If user is in AI chat mode, handle with AI
        elif user_status == 'AI':
            if message.content_type == 'text':
                logger.info(f"Handling AI chat message from user {user_id}")
                try:
                    # Change status to HOLD while processing
                    cursor.execute("UPDATE users SET STATUS = 'HOLD' WHERE USER_ID = ?", (user_id,))
                    conn.commit()
                    logger.info(f"Changed user {user_id} status to HOLD")
                    
                    # Show typing indicator
                    bot.send_chat_action(message.chat.id, 'typing')
                    
                    # Process the message
                    from ai_integration import handle_ai_message
                    ai_response = handle_ai_message(bot, message, user_id)
                    
                    # Show typing indicator again before sending response
                    bot.send_chat_action(message.chat.id, 'typing')
                    
                    # Send the response
                    bot.send_message(message.chat.id, ai_response)
                    logger.info(f"Sent AI response to user {user_id}")
                    
                    # Change status back to AI
                    cursor.execute("UPDATE users SET STATUS = 'AI' WHERE USER_ID = ?", (user_id,))
                    conn.commit()
                    logger.info(f"Changed user {user_id} status back to AI")
                    conn.close()
                    return
                except Exception as e:
                    logger.error(f"Error handling AI chat message: {e}")
                    # Change status back to AI in case of error
                    cursor.execute("UPDATE users SET STATUS = 'AI' WHERE USER_ID = ?", (user_id,))
                    conn.commit()
                    conn.close()
                    bot.send_message(
                        message.chat.id,
                        "Sorry, I'm having trouble connecting to the AI. Please try again later."
                    )
                    return
            else:
                # AI chat only supports text messages
                conn.close()
                bot.send_message(
                    message.chat.id,
                    "Not Allowed"
                )
                return
    
    conn.close()
    
    # Not in AI chat mode, try to handle and forward the message
    result = handle_message(bot, message)
    
    if not result:
        # If message wasn't forwarded (no valid peer), inform the user
        bot.send_message(
            user_id, 
            "You are not currently connected to anyone. Please use the menu to start a connection."
        )
        logger.info(f"User {user_id} tried to send a message but is not connected")

# Main function
def main():
    """Main function to start the bot with error handling and retry mechanism."""
    logger.info("Starting bot...")
    
    # Ensure databases are set up properly
    logger.info("Setting up databases...")
    setup_database()
    setup_user_def_database()
    logger.info("Database setup complete")
    
    # Reset webhook to avoid conflicts
    bot.remove_webhook()
    
    # Register admin operation handlers
    operations.register_operation_handlers(bot)
    logger.info("Admin operation handlers registered")
    
    retry_count = 0
    max_retries = 5
    retry_delay = 5  # seconds
    
    while retry_count < max_retries:
        try:
            logger.info("Bot started successfully!")
            # Handle the 409 conflict error
            bot.polling(none_stop=True, interval=1, timeout=20)
            # If polling exits without exception, break the loop
            break
            
        except telebot.apihelper.ApiTelegramException as telegram_error:
            if "Conflict: terminated by other getUpdates request" in str(telegram_error):
                logger.warning("Conflict with another bot instance. Resetting connection...")
                bot.stop_polling()
                time.sleep(retry_delay)
                retry_count += 1
            else:
                logger.error(f"Telegram API error: {telegram_error}")
                break
                
        except Exception as e:
            logger.error(f"Bot error: {e}")
            retry_count += 1
            logger.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
            time.sleep(retry_delay)
    
    if retry_count >= max_retries:
        logger.error("Maximum retry attempts reached. Bot stopped.")

if __name__ == "__main__":
    import time  # Add time module for sleep functionality
    main()
