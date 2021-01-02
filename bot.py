import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from main import add_to_playlist, get_ytmusic
from app_secrets import TELEGRAM_TOKEN, USER_WHITELIST, PLAYLIST_ID


START_MESSAGE = "Hey! Please send the name of a song and the artist."


def main():

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    ytmusic = get_ytmusic()

    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE)

    def echo(update, context):
        result = add_to_playlist(ytmusic, update.message.text, PLAYLIST_ID)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler(
        "start", start, Filters.user(username=USER_WHITELIST)
    )
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.user(username=USER_WHITELIST), echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
