import os

import telegram
from ytmusicapi import YTMusic


def get_user_whitelist():
    return os.environ["WHITELIST"].split(" ")


def get_bot():
    return telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])


def is_result_successful(result):
    return (
        "song" in result
        and "artist" in result
        and result["song"] is not None
        and result["artist"] is not None
    )


def reply_to_suggester(chat_id, result):
    if is_result_successful(result):
        response_1 = f"""Added the song '{result["song"]}' by '{result["artist"]}' to playlist.
        https://music.youtube.com/playlist?list={result["playlist"]}"""
        response_2 = "Many thanks! :)"
        get_bot().sendMessage(chat_id=chat_id, text=response_1)
        get_bot().sendMessage(chat_id=chat_id, text=response_2)
    else:
        response = "Could not find a hit for your query. :("
        get_bot().sendMessage(chat_id=chat_id, text=response)


def notify_owner(owner_id, suggester_username, result):
    if is_result_successful(result):
        response = f"""{suggester_username} :  {result["song"]} - {result["artist"]}"""
    else:
        response = f"""Could not find a hit for'{suggester_username}'s query: {result["query"]}"""
    get_bot().sendMessage(chat_id=owner_id, text=response)


def get_ytmusic():
    ytmusic = YTMusic("headers_auth.json")
    return ytmusic


def add_to_playlist(ytmusic, query, playlist_id=None):
    if playlist_id is None:
        playlist_id = os.environ["PLAYLIST_ID"]
    search_results = ytmusic.search(query)
    if len(search_results) == 0 or "videoId" not in search_results[0]:
        return {"song": None, "artist": None, "playlist": playlist_id, "query": query}
    search_result = search_results[0]
    ytmusic.add_playlist_items(playlist_id, [search_result["videoId"]])
    return {
        "song": search_result["title"],
        "artist": search_result["artists"][0]["name"],
        "playlist": playlist_id,
        "query": query,
    }


def webhook(request):
    owner_id = int(os.environ["OWNER_ID"])
    user_whitelist = get_user_whitelist()

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), get_bot())
        if update.message.from_user.username not in user_whitelist:
            return None
        chat_id = update.message.chat.id
        api = get_ytmusic()
        result = add_to_playlist(api, update.message.text)
        reply_to_suggester(chat_id, result)
        notify_owner(owner_id, update.message.from_user.username, result)
    return "ok"
