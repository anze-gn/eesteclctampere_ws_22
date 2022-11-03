# https://t.me/GNHTTbot

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# using separate configuration and parser
from configparser import ConfigParser
# import initdb and handler to it
import initdatabase, db_handler
import ecg4everybody_api
import re
import data_plotter

# configparser
cfg = ConfigParser()
cfg.read('env.cfg')

# get token from config
TOKEN = cfg['TELEGRAM']['token']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# declaring constants
STOREDATA, PLOTDATA = range(2)

# calling method initdb creates
initdatabase.initdb()


# when /start is issued
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays starting message and lists commands."""
    await update.message.reply_text(
        "Welcome. Use the commands below to test available features.\n"
        "/help lists these commands.\n"
        "/new let's you input new data value.\n"
        "/plot function initiates plotting of chosen data.\n"
        "/cancel cancels current action.\n"
        # TODO: add the commands you need.
    )


# when /help is issued
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(
        "/new let's you input new data value.\n"
        "/plot function initiates plotting of chosen data.\n"
        "/cancel cancels current action.\n"
        # TODO: add commands you need here too
    )


# when /cancel is issued
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Action cancelled."
    )
    return ConversationHandler.END


# this /new command initiates this conversation and returns constant STOREDATA
async def newdata(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks new data point value from user."""
    await update.message.reply_text(
        "Paste crowdsourcing URL: "
    )
    return STOREDATA


# called when STOREDATA state is reached
async def store_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores the aquired data by calling add_data method from db_handler."""

    user = update.message.from_user
    url = update.message.text

    try:
        id = re.search('i=(\w+)', url).group(1)
    except AttributeError:
        logger.info(
            "URL %s from user %s not recognized", url, user.first_name
        )
        await update.message.reply_text(
            "URL not recognized, please try again: "
        )
        return STOREDATA

    # get data from ecg4everybody crowdsourcing web server
    data = ecg4everybody_api.get(id)

    # we are calling add_data method from database handler
    # # it takes the new_data as parameter
    db_handler.add_data(
        user.id,
        data['recorded_utc'],
        data['hr'],
        data['rmssd']
    )

    # Logging new_data and username
    logger.info(
        "Stored new values %s, %d, %d, from user %s", data['recorded_utc'], data['hr'], data['rmssd'], user.first_name
    )

    await update.message.reply_text(
        f"Stored new values:\n"
        f"recorded_utc: {data['recorded_utc']}\n"
        f"hr: {data['hr']}\n"
        f"rmssd: {data['rmssd']}"
    )

    return ConversationHandler.END


# called when /plot command is given
async def plotter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks user what data they want to plot."""
    reply_keyboard = [["HR", "RMSSD"]]

    await update.message.reply_text(
        "What data do you want to plot?\n"
        "Options: HR, RMSSD",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Data to plot:"
        ),
    )
    return PLOTDATA


# called when PLOTDATA state is reached in plotter_handler conversation
async def plot_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gets new data value from user."""
    user = update.message.from_user
    chosen_data = update.message.text.lower()
    logger.info(
        "Plotting data: %s from user: %s", chosen_data, user.first_name
    )

    data = db_handler.get_user_data(update.message.from_user.id)
    plot = data_plotter.plot(data, chosen_data)
    await update.message.reply_photo(photo=plot)

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    storedata_handler = ConversationHandler(
        entry_points=[CommandHandler("new", newdata)],
        states={
            # This is a message handler, takes user input from message
            STOREDATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    plotter_handler = ConversationHandler(
        entry_points=[CommandHandler("plot", plotter)],
        states={
            PLOTDATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(storedata_handler)
    application.add_handler(plotter_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
