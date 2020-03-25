from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from gmusicapi import Mobileclient
import logging
import os
from secrets import GMUSIC_LOGIN, TELEGRAM_TOKEN, USER_WHITELIST

START_MESSAGE = 'Hey! Please send the name of a song and the artist.'
PLAYLIST_NAME = 'autogenerated'

def get_playlist(api):
    user_playlists = [playlist for playlist in api.get_all_playlists() if playlist['name'] == PLAYLIST_NAME]
    if len(user_playlists) == 0:
        print('Create new playlist')
        return api.create_playlist('autogenerated')
    else:
        return user_playlists[0]['id']

def get_response_message(song, playlist):
    title = song['title']
    artist = song['artist']
    album = song['album']
    return f"""Added the song _{title}_ from _{artist}_'s album _{album}_ to playlist. https://play.google.com/music/listen?u=0#/pl/{playlist}"""

def add_to_playlist(query):
    api = Mobileclient()
    api.oauth_login(GMUSIC_LOGIN)
    search_results = api.search(query)
    song = search_results['song_hits'][0]['track']
    playlist = get_playlist(api)
    api.add_songs_to_playlist(playlist, song['storeId'])
    return get_response_message(song, playlist)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE)
    
def echo(update, context):
    result = add_to_playlist(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     # level=logging.INFO)

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start, Filters.user(username=USER_WHITELIST))
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.user(username=USER_WHITELIST), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
