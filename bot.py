import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters
from inventory import VakoInvis  # Make sure this imports the class you've defined above

# Initialize the inventory manager
inventory_manager = VakoInvis("inventory.json")

TOKEN = open('token.txt', "r").readline().strip()
PASSWORD = open('password.txt', "r").readline().strip()

PASSWORD_CHECK = 0

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
        "/add <item> <quantity> [new]- Add quantity to an item. Add 'new' at the end of the message if you want to add fully new item\n"
        "/remove <item> <quantity> [totally]- Remove quantity from an item. Add totally if you want totally remove the item from the database\n"
        "/view [item] [full] - View inventory or a specific item.\n"
        "/limit <item> <new limit> - change alarm limit of the item"
        "/help - Show this help message"
    )

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /add command to add an item to the inventory.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Usage:
        /add <item> <quantity> [new]
        <item> (str): The name of the item to add.
        <quantity> (int): The quantity of the item to add.
        [new] (optional, str): If provided and set to "new", the item will be added as a new item if it does not already exist in the inventory.
    Raises:
        IndexError: If the required arguments are not provided.
        ValueError: If the quantity is not a valid integer.
    Returns:
        None
    """
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
    """
    Asynchronously removes a specified quantity of an item from the inventory.
    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
    Usage:
        /remove <item> <quantity> [totally]
        <item> (str): The name of the item to remove.
        <quantity> (int): The quantity of the item to remove.
        [totally] (str, optional): If provided and set to "totally", removes the item completely from the inventory.
    Behavior:
        - If the item and quantity are valid, removes the specified quantity of the item from the inventory.
        - If the "totally" argument is provided, removes the item completely from the inventory.
        - Sends a reply message indicating the result of the operation.
        - If the quantity of the item falls below the alarm limit, includes an alarm message in the reply.
        - If the item is not found in the inventory, sends an error message.
    Exceptions:
        - IndexError: If the required arguments are not provided.
        - ValueError: If the quantity argument is not a valid integer.
    """
    try:
        item = context.args[0]
        quantity = int(context.args[1])
        totally = len(context.args) > 2 and context.args[2].lower() == "totally"
        
        if inventory_manager.remove(item, quantity, totally=totally):
            alarm = inventory_manager.check_alarm_limit(item)
            await update.message.reply_text(f"Removed {quantity} of '{item}' from the inventory."
                                            f"{'\nALARM! QUANTITY OF THIS ITEM IS LESS THEN ALARM LIMIT! CONTACT CHAIR ABOUT THIS PROBLEM' if alarm == False else ''}")
        else:
            await update.message.reply_text(f"Error: Item '{item}' not found in inventory.")
    
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remove <item> <quantity> [totally]")


async def view_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /view_inventory command to display inventory details.

    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.

    Behavior:
        - If an item name is provided in the command arguments, it checks if the item exists in the inventory.
            - If the item exists, it replies with the item's quantity and optionally the alarm limit if "full" is specified.
            - If the item does not exist, it replies with a message indicating the item was not found.
        - If no item name is provided, it lists all items in the inventory with their quantities.
            - If the inventory is empty, it replies with a message indicating the inventory is empty.
    """
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
    """
    Handles the /limit command to update the limit of a specified item.

    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.

    Usage:
        /limit <item> <new limit>

    Behavior:
        - Extracts the item and new limit from the command arguments.
        - Calls the inventory_manager.update_alarm_limit method to update the limit.
        - Sends a confirmation message if the limit is successfully updated.
        - Sends an error message if the item is not found or if the arguments are invalid.

    Exceptions:
        - IndexError: If the command arguments are missing.
        - ValueError: If the command arguments are invalid.
    """
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
    """
    Main function to set up and run the bot application.

    This function performs the following tasks:
    1. Initializes the bot application with the provided token.
    2. Sets up a conversation handler to manage the password check state.
    3. Registers various command handlers for the bot commands:
       - /start: Initiates the bot.
       - /help: Provides help information.
       - /add: Adds an item to the inventory.
       - /remove: Removes an item from the inventory.
       - /view: Views the current inventory.
    4. Starts polling for updates to handle incoming messages and commands.
    """
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PASSWORD_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
        },
        fallbacks=[],
    )

    # Register command handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_item))
    application.add_handler(CommandHandler("remove", remove_item))
    application.add_handler(CommandHandler("view", view_inventory))

    # Start polling for updates
    application.run_polling()

if __name__ == "__main__":
    main()
