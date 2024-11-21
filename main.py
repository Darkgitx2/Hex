import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from keep_alive import keep_alive  # Import the keep-alive module

# Dictionary to store uploaded files per user
user_files = {}

# /start command handler
def start(update: Update, context: CallbackContext) -> None:
    user_files[update.effective_user.id] = []  # Initialize user file list
    update.message.reply_text("Please send your .bin files and I will give you their hex.")

# File upload handler for .bin files
def handle_file(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    file = update.message.document

    # Check file extension
    if not file.file_name.endswith('.bin'):
        update.message.reply_text("Only .bin files are supported.")
        return

    # Download the file
    try:
        file_path = file.get_file().download(custom_path=f"/tmp/{file.file_name}")
        user_files[user_id].append(file_path)  # Store file path for user
        update.message.reply_text(f"{file.file_name} loaded successfully.")
    except Exception as e:
        update.message.reply_text(f"Failed to download the file: {e}")

# /complete command handler
def complete(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Ensure the user has uploaded files
    if user_id not in user_files or not user_files[user_id]:
        update.message.reply_text("No files uploaded. Please upload .bin files first.")
        return

    # Define fixed output file path
    output_path = "/tmp/combined_hex.txt"

    # Convert each file to formatted hex data and store in list
    formatted_hex_data = []
    try:
        for file_path in user_files[user_id]:
            with open(file_path, 'rb') as f:
                hex_data = ''.join(f"\\x{byte:02x}" for byte in f.read())
                formatted_hex_data.append(f'"{hex_data}"')  # Format with quotes for each file's hex data

        # Write combined formatted hex data to output file
        with open(output_path, 'w') as hex_file:
            hex_file.write('\n'.join(formatted_hex_data))
    except Exception as e:
        update.message.reply_text(f"Error processing files: {e}")
        return

    # Send the .txt file to user
    try:
        with open(output_path, 'rb') as f:
            context.bot.send_document(chat_id=update.effective_chat.id, document=f)
    except Exception as e:
        update.message.reply_text(f"Failed to send the file: {e}")
    finally:
        # Clean up temporary files
        os.remove(output_path)
        for file_path in user_files[user_id]:
            os.remove(file_path)
        user_files[user_id] = []  # Clear user's file list

# Main function to initialize bot
def main() -> None:
    # Replace 'YOUR_BOT_TOKEN' with the actual bot token from BotFather
    updater = Updater("7868606816:AAFpnJDC5To61BJ6ejQ0Jit0a7ESpMRoYpc", use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("complete", complete))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

    # Start keep-alive server to prevent Replit from going idle
    keep_alive()

    # Run the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()