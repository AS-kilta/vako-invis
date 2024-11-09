import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes
from inventory import VakoInvis  # Make sure this imports the class you've defined above

# Initialize the inventory manager
inventory_manager = VakoInvis("inventory.txt")

TOKEN = open('token.txt', "r").readline().strip()


# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Vako inventory Bot! Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add <item> <quantity> [new]- Add quantity to an item. Add 'new' at the end of the message if you want to add fully new item\n"
        "/remove <item> <quantity> [totally]- Remove quantity from an item. Add totally if you want totally remove the item from the database\n"
        "/view [item] - View inventory or a specific item.\n"
        "/help - Show this help message"
    )

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        item = context.args[0]
        quantity = int(context.args[1])
        new_item = len(context.args) > 2 and context.args[2].lower() == "new"
        
        if inventory_manager.add(item, quantity, new=new_item):
            await update.message.reply_text(f"Added {quantity} of '{item}' to the inventory.")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found. Use '/add <item> <quantity> new' to add it as a new item.")
    
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /add <item> <quantity> [new]")

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        item = context.args[0]
        quantity = int(context.args[1])
        totally = len(context.args) > 2 and context.args[2].lower() == "totally"
        
        if inventory_manager.remove(item, quantity):
            await update.message.reply_text(f"Removed {quantity} of '{item}' from the inventory.")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found in inventory.")
    
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remove <item> <quantity>")

async def view_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        item = context.args[0]
        if item in inventory_manager.inventory:
            await update.message.reply_text(f"{item} => {inventory_manager.inventory[item]}")
        else:
            await update.message.reply_text(f"Item '{item}' not found in inventory.")
    else:
        inventory_list = "\n".join([f"{item} => {quantity}" for item, quantity in inventory_manager.inventory.items()])
        await update.message.reply_text("Inventory:\n" + (inventory_list if inventory_list else "Inventory is empty."))

# Main function to start the bot
def main():
    # Replace 'YOUR_TOKEN' with your actual bot token
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_item))
    application.add_handler(CommandHandler("remove", remove_item))
    application.add_handler(CommandHandler("view", view_inventory))

    # Start polling for updates
    application.run_polling()

if __name__ == "__main__":
    main()
