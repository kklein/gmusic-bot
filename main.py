import os
from collections import namedtuple
import telegram
from gmusicapi import Mobileclient, session


PLAYLIST_NAME = 'autogenerated'

def get_playlist(api):
    user_playlists = [
        playlist for playlist in api.get_all_playlists() if playlist['name'] == PLAYLIST_NAME]
    if len(user_playlists) == 0:
        print('Create new playlist')
        return api.create_playlist('autogenerated')
    return user_playlists[0]['id']


def get_oauth_info(client_id, client_secret):
    Info = namedtuple("Info", ["client_id", "client_secret"])
    return Info(client_id, client_secret)


def get_response_message(song, playlist):
    title = song['title']
    artist = song['artist']
    album = song['album']
    return f"""Added the song _{title}_ from _{artist}_'s album _{album}_ to playlist.
               https://play.google.com/music/listen?u=0#/pl/{playlist}"""


def get_api_via_refresh_auth():
    api = Mobileclient()
    # api.oauth_login(GMUSIC_LOGIN)
    gmusic_login = os.environ["GMUSIC_LOGIN"]
    refresh_token = os.environ["REFRESH_TOKEN"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"] 
    oauth_info = get_oauth_info(client_id, client_secret)
    credentials = session.credentials_from_refresh_token(refresh_token, oauth_info)
    api.oauth_login(gmusic_login, credentials)
    return api


def add_to_playlist(api, query):
    search_results = api.search(query)
    song = search_results['song_hits'][0]['track']
    playlist = get_playlist(api)
    api.add_songs_to_playlist(playlist, song['storeId'])
    return get_response_message(song, playlist)


def webhook(request):
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
    owner_id = int(os.environ["OWNER_ID"])
    whitelist = os.environ["WHITELIST"].split(" ")
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        if update.message.from_user.username not in whitelist:
            return None
        chat_id = update.message.chat.id
        api = get_api_via_refresh_auth()
        result = add_to_playlist(api, update.message.text)
        bot.sendMessage(chat_id=chat_id, text=result)
        bot.sendMessage(chat_id=owner_id, text=update.message.from_user.username + " : " + result)
    return "ok"
