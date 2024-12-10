import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters
from inventory import VakoInvis  # Make sure this imports the class you've defined above

from decouple import config

# Initialize the inventory manager
inventory_manager = VakoInvis("inventory.json")

TOKEN = config('TG_TOKEN')
PASSWORD = config('PASSWORD')

PASSWORD_CHECK = 0
PASSWORD_CHECK, SELECT_ITEM, ENTER_QUANTITY, ENTER_NAME, ENTER_ALARM_LIMIT = range(5)

# starting function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome to the Vako inventory Bot! Please enter the password to continue:")
    return PASSWORD_CHECK

# checks if the password was correct
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == PASSWORD:
        await update.message.reply_text("Password correct! Use /help to see available commands.")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Incorrect password. Please try again:")
        return PASSWORD_CHECK

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add [new] - Add quantity to an item.\n"
        "/sell - Sell quantity of an item.\n"
        "/view <item> [full] - View inventory or a specific item.\n"
        "/limit - change alarm limit of the item\n"
        "/help - Show this help message"
    )

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the /add command to add an item to the inventory.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Usage:
        /add [new]
    Returns:
        int: The next state for the conversation handler.
    """
    if context.args and context.args[0].lower() == "new":
        context.user_data['new_item'] = True
        context.user_data['action'] = 'add'
        await update.message.reply_text("Please enter the name of the new item:")
        return ENTER_NAME

    context.user_data['action'] = 'add'
    items = list(inventory_manager.inventory.keys())
    if not items:
        await update.message.reply_text("No items in the inventory to add.")
        context.user_data.clear()
        return ConversationHandler.END

    keyboard = [[item] for item in items]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose an item to add:", reply_markup=reply_markup)
    return SELECT_ITEM

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
    context.user_data['action'] = 'sell'
    items = list(inventory_manager.inventory.keys())
    if not items:
        await update.message.reply_text("No items in the inventory to sell.")
        context.user_data.clear()
        return ConversationHandler.END

    keyboard = [[item] for item in items]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose an item to sell:", reply_markup=reply_markup)
    return SELECT_ITEM

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the input of the name for the new item.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    context.user_data['item'] = update.message.text

    if context.user_data['item'] in inventory_manager.inventory:
        await update.message.reply_text(f"Item '{context.user_data['item']}' already exists in the inventory. Please enter a different name:")
        return ENTER_NAME

    inventory_manager.add(context.user_data['item'], 0, new=True)
    await update.message.reply_text(f"Entered item name: {context.user_data['item']}\nPlease enter the quantity to add:")
    return ENTER_QUANTITY

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

    if 'update' in context.user_data and context.user_data['update']:
        await update.message.reply_text(f"Selected item: {context.user_data['item']}\nPlease enter the new alarm limit:")
        return ENTER_ALARM_LIMIT
    else:
        action = context.user_data['action']

        if action == 'add':
            await update.message.reply_text(f"Selected item: {context.user_data['item']}\nPlease enter the quantity to add:")
            return ENTER_QUANTITY
        elif action == 'sell':
            await update.message.reply_text(f"Selected item: {context.user_data['item']}\nPlease enter the quantity to sell:")
            return ENTER_QUANTITY

async def enter_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the input of the quantity to add or sell for the selected item.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    try:
        quantity = int(update.message.text)
        item = context.user_data['item']
        action = context.user_data['action']

        if action == 'add':
            if context.user_data.get('new_item'):
                inventory_manager.add(item, quantity)
                await update.message.reply_text(f"Entered quantity: {quantity}\nPlease enter the alarm limit:")
                return ENTER_ALARM_LIMIT
            
            if inventory_manager.add(item, quantity):
                await update.message.reply_text(f"Added {quantity} of '{item}' to the inventory.")
            else:
                await update.message.reply_text(f"Error: Item '{item}' not found.")
        
        elif action == 'sell':
            if inventory_manager.remove(item, quantity):
                alarm = inventory_manager.check_alarm_limit(item)
                await update.message.reply_text(
                    f"Sold {quantity} of '{item}' from the inventory."
                    + ("\n\nALARM -> QUANTITY OF THIS ITEM IS BELOW ALARM LIMIT, CONTACT THE CHAIR" if not alarm else "")
)
            else:
                await update.message.reply_text(f"Error: Item '{item}' not found.")

        context.user_data.clear()
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text("Invalid quantity. Please enter a valid integer:")
        return ENTER_QUANTITY

async def enter_alarm_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the input of the alarm limit for the new item.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Returns:
        int: The next state for the conversation handler.
    """
    try:
        alarm_limit = int(update.message.text)
        item = context.user_data['item']
        
        if inventory_manager.update_alarm_limit(item, alarm_limit):
            await update.message.reply_text(f"{item}'s alarm limit updated to {alarm_limit}")
        else:
            await update.message.reply_text(f"Error: Could not update '{item}''s alarm limit.")
        
        context.user_data.clear()
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text("Invalid alarm limit. Please enter a valid integer:")
        return ENTER_ALARM_LIMIT

async def view_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        full = len(context.args) > 1 and "full" in " ".join(context.args).lower()
        item = " ".join(context.args[:-1]).lower() if full else " ".join(context.args).lower()

        if item in inventory_manager.inventory:
            alarm = inventory_manager.inventory[item]['alarm_limit']    # for some reason docker gives error if this is put into f string
            await update.message.reply_text(f"{item}:\n   quantity: {inventory_manager.inventory[item]['quantity']}\n"
                                            + (f'   alarm limit : {alarm}' if full else ''))
        else:
            await update.message.reply_text(f"Item '{item}' not found in inventory.")
    else:
        inventory_list = "\n".join([f"{item} =>\n   quantity: {details['quantity']}\n" for item, details in inventory_manager.inventory.items()])
        await update.message.reply_text("\n" + (inventory_list if inventory_list else "Inventory is empty."))

async def limit_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    items = list(inventory_manager.inventory.keys())
    if not items:
        await update.message.reply_text("No items in the inventory to add.")
        context.user_data.clear()
        return ConversationHandler.END
    
    context.user_data['update'] = True

    keyboard = [[item] for item in items]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose an item to update the alarm limit:", reply_markup=reply_markup)
    return SELECT_ITEM

# Main function to start the bot
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("add", add_item), CommandHandler("sell", sell_item), CommandHandler("limit", limit_item)],
        states={
            PASSWORD_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            SELECT_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_item)],
            ENTER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_quantity)],
            ENTER_ALARM_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_alarm_limit)],
        },
        fallbacks=[],
    )

    # Register command handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("view", view_inventory))

    # Start polling for updates
    application.run_polling()

if __name__ == "__main__":
    main()