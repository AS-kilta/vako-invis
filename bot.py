import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters
from inventory import VakoInvis  # Make sure this imports the class you've defined above

# Initialize the inventory manager
inventory_manager = VakoInvis("inventory.json")

TOKEN = open('token.txt', "r").readline().strip()
PASSWORD = open('password.txt', "r").readline().strip()

PASSWORD_CHECK = 0
SELECT_ITEM, ENTER_QUANTITY = range(2)

# starting function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome to the Vako inventory Bot! Please enter the password to continue:")
    return PASSWORD_CHECK

# checks if the password was correct
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == PASSWORD:
        await update.message.reply_text("Password correct! Use /help to see available commands.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Incorrect password. Please try again:")
        return PASSWORD_CHECK

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add [new] - Add quantity to an item.\n"
        "/sell - Sell quantity of an item.\n"
        "/view [item] [full] - View inventory or a specific item.\n"
        "/limit <item> <new limit> - change alarm limit of the item\n"
        "/help - Show this help message"
    )

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the /add command to add an item to the inventory.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Usage:
        /add
    Returns:
        int: The next state for the conversation handler.
    """
    items = list(inventory_manager.inventory.keys())
    if not items:
        await update.message.reply_text("No items in the inventory to add.")
        return ConversationHandler.END

    keyboard = [[item] for item in items]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose an item to add:", reply_markup=reply_markup)
    return SELECT_ITEM

async def select_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the selection of an item from the keyboard.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    context.user_data['item'] = update.message.text
    await update.message.reply_text(f"Selected item: {context.user_data['item']}\nPlease enter the quantity to add:")
    return ENTER_QUANTITY

async def enter_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the input of the quantity to add to the selected item.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    print("in quantity")
    try:
        quantity = int(update.message.text)
        item = context.user_data['item']
        
        if inventory_manager.add(item, quantity):
            await update.message.reply_text(f"Added {quantity} of '{item}' to the inventory.")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found.")
        
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text("Invalid quantity. Please enter a valid integer:")
        return ENTER_QUANTITY

async def sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the /sell command to remove an item from the inventory.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Usage:
        /sell
    Returns:
        int: The next state for the conversation handler.
    """
    items = list(inventory_manager.inventory.keys())
    if not items:
        await update.message.reply_text("No items in the inventory to sell.")
        return ConversationHandler.END

    keyboard = [[item] for item in items]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose an item to sell:", reply_markup=reply_markup)
    return SELECT_ITEM

async def select_item_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the selection of an item from the keyboard for selling.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    context.user_data['item'] = update.message.text
    await update.message.reply_text(f"Selected item: {context.user_data['item']}\nPlease enter the quantity to sell:")
    return ENTER_QUANTITY

async def enter_quantity_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the input of the quantity to sell for the selected item.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    print("in quantity sell")
    try:
        quantity = int(update.message.text)
        item = context.user_data['item']
        
        if inventory_manager.remove(item, quantity):
            await update.message.reply_text(f"Sold {quantity} of '{item}' from the inventory.")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found.")
        
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text("Invalid quantity. Please enter a valid integer:")
        return ENTER_QUANTITY

async def view_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        item = context.args[0]
        full = len(context.args) > 1 and context.args[1].lower() == "full"
        if item in inventory_manager.inventory:
            await update.message.reply_text(f"{item}:\n   quantity: {inventory_manager.inventory[item]['quantity']}\n   "
                                            f"{f'alarm limit : {inventory_manager.inventory[item]['alarm_limit']}' if full else ''}")
        else:
            await update.message.reply_text(f"Item '{item}' not found in inventory.")
    else:
        inventory_list = "\n".join([f"{item} =>\n   quantity: {details['quantity']}\n" for item, details in inventory_manager.inventory.items()])
        await update.message.reply_text("\n" + (inventory_list if inventory_list else "Inventory is empty."))

async def limit_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        item = context.args[0]
        limit = context.args[1]
        if inventory_manager.update_alarm_limit(item, limit):
            await update.message.reply_text(f"Change limit of the {item} to {limit}")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found")
    except (IndexError, ValueError):
        await update.message.reply_text(f"Usage: /limit <item> <new limit>")

# Main function to start the bot
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("add", add_item), CommandHandler("sell", sell_item)],
        states={
            PASSWORD_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            SELECT_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_item)],
            ENTER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_quantity)],
            SELECT_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_item_sell)],
            ENTER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_quantity_sell)],
        },
        fallbacks=[],
    )

    # Register command handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("view", view_inventory))
    application.add_handler(CommandHandler("limit", limit_item))

    # Start polling for updates
    application.run_polling()

if __name__ == "__main__":
    main()