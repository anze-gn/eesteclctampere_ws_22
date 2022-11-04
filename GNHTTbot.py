# https://t.me/GNHTTbot

import logging
import random

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
import itertools

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
    await update.message.reply_markdown_v2(
        "Welcome to the Great Northern Health Tracking bot 🤖👋\n"
        "\n"
        "*List of commands:*\n"
        "/help lists these commands\n"
        "/new let's you input new data value from the [HRV Camera app](https://ecg4everybody.com/)\n"
        "/plot function initiates plotting of chosen data\n"
        "/cancel cancels current action\n"
        "\n"
        "*Terms & Conditions:*\n"
        "||_By using this bot you agree to health data collection and processing\.\n"
        "You also agree to donate a kidney and your firstborn child to EESTEC, when/if the need arises\. "
        "In such case, you shall be notified by a carrier pigeon and you have to respond in 5 business days\. "
        "By failing to do so, you allow EESTEC to use any means necessary to collect your donation\.\n_||",
        disable_web_page_preview=True
    )


# when /help is issued
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_markdown_v2(
        "*List of commands:*\n"
        "/help lists these commands\n"
        "/new let's you input new data value from the [HRV Camera app](https://ecg4everybody.com/)\n"
        "/plot function initiates plotting of chosen data\n"
        "/cancel cancels current action\n"
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
    await update.message.reply_text(
        "Plotting...", reply_markup=ReplyKeyboardRemove()
    )
    data = db_handler.get_user_data(update.message.from_user.id)
    if len(next(iter(data.values()))) < 2:
        await update.message.reply_text(
            "Less than two measurements saved, cannot plot\n"
            "Please add measurements using /new\n"
        )
    else:
        plot = data_plotter.plot(data, chosen_data)
        await update.message.reply_photo(photo=plot)

    return ConversationHandler.END


async def curse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    curses = {
        "SI": "Pes te nima rad",
        "TR": "Yarrak kafa",
        "PL": "Matkojebca",
        "HR": "Jebem ti pasa jarca",
        "RU": "Mudak",
        "PT": "Caralho",
        "FI": "Kikkeli",
        "RS": "Pička mater",
        "GR": "Moonopano",
    }
    args = context.args
    if len(args) < 1:
        curse = random.choice(list(curses.values()))
    else:
        curse = curses[args[0]]
    await update.message.reply_text(curse)
    return ConversationHandler.END

party_songs = itertools.cycle([
    "https://youtu.be/CdlpJhHCFlc",  # noot noot
    "https://youtu.be/cNgyuHtBBW8",  # hentai
    "https://youtu.be/0a5BJxrarL0",  # USA
    "https://youtu.be/fysw1kQKw_w",  # ximeromata
    "https://youtu.be/bPOobWvCm_4",  # zašto baš ti satisfaction
    "https://youtu.be/cpp69ghR1IM",  # simarik
    "https://youtu.be/LCcIx6bCcr8",  # ona by tak chciala
    "https://youtu.be/ADuAzItBzto",  # german sex tourist
    "https://youtu.be/bEacVcAtiKU",  # belly dancer
    "https://youtu.be/j70MeSY8tTg",  # smack that
    "https://youtu.be/PO_d169ibZ8",  # the business
    "https://youtu.be/Y0ORYHQ-VMA",  # johnny deere
])
async def party(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # song = random.choice(songs)
    song = next(party_songs)
    await update.message.reply_text(song)
    return ConversationHandler.END


dance_songs = itertools.cycle([
    "https://youtu.be/upgFEQmIp08",  # hir aj kam
    "https://youtu.be/mDFBTdToRmw",  # skibidi
    "https://youtu.be/Vt_WLYubVlk",  # gaber
    "https://youtu.be/cHcVU5cGUNE",  # stamp on the ground
    "https://youtu.be/jqTSAtU-HRA",  # helikopter 117
    "https://youtu.be/ArwFal9zjZE",  # ti
    "https://youtu.be/5fe57bDZCJE",  # belgijka
    "https://youtu.be/t3b9qjYW1z0",  # crno na belo
    "https://youtu.be/XqZsoesa55w",  # baby shark
])
async def dance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # song = random.choice(songs)
    song = next(dance_songs)
    await update.message.reply_text(song)
    return ConversationHandler.END


async def partylights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # song = random.choice(songs)
    song = next(dance_songs)
    await update.message.reply_animation("https://media.giphy.com/media/b60d0PNX0NPdS/giphy-downsized.gif")
    return ConversationHandler.END

async def bro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_voice(open('bruh.opus','rb'))
    return ConversationHandler.END


shortcuts = {
    "eastereggs": """*List of the easter 🥚🥚🥚*
    /bro
    /hello
    /bye
    /alarm /wakeup
    /durak
    /party
    /partylights
    /dance
    /alien
    /51
    /phrases
    /curse
    """,
    "hello": "Terve",
    "bye": "Heihei",
    "alarm": "https://youtu\.be/xRiHXWEpYuI",
    "wakeup": "https://youtu\.be/xRiHXWEpYuI",
    "photos": "https://photos\.app\.goo\.gl/feMqHYoaJQUk3oZN9",
    "durak": "https://en\.wikipedia\.org/wiki/Durak",
    "alien": "https://youtu\.be/gJhlyBJHv9I",
    "51": "https://youtu\.be/WxrQ3SqSt6Q",
    "phrases": """*LIST OF FINNISH PHRASES:*
    *Saisiko olutta/viinaa/ruokaa?*  \-  _Can i have some beer/booze/food?_
    *Oispa kaljaa*  \-  _I wish I had some beer_
    *Missä olen?*  \-  _Where am I?_
    *Miksi olet alasti?*  \-  _Why are you naked?_
    *Miksi olen alasti?*  \-  _Why am I naked?_
    *Kuusi*  \-  _spruce/six_
    *Kusi*  \-  _swear word meaning piss_
    *puukko*  \-  _small traditional Finnish belt knife_
    *puukkohippa*  \-  _playing tag with puukko_
    *kalsarikännit*  \-  _drinking alone at home wearing only underwears with no intention of going out_
    *kuusi palaa*  \-  _just google it_
    """
}
async def shortcut(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    command = re.search('\/([^@]+)', update.message.text).group(1)
    response = shortcuts[command]
    await update.message.reply_markdown_v2(response)
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
    application.add_handler(CommandHandler("curse", curse))
    application.add_handler(CommandHandler("party", party))
    application.add_handler(CommandHandler("dance", dance))
    application.add_handler(CommandHandler("bro", bro))
    application.add_handler(CommandHandler("partylights", partylights))
    application.add_handler(CommandHandler(shortcuts.keys(), shortcut))
    application.add_handler(storedata_handler)
    application.add_handler(plotter_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
