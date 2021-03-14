from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import Optional, List
import logging

from spotify import user, api, data, config

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9), "JST")


@dataclass()
class ApiService:
  __user_data: user.UserData
  __api_secret: config.ApiSecret
  __ranking_client: data.RankingClient
  __api_client: Optional[api.ApiClient] = None

  def __get_api_client(self):
    if self.__api_client:
      return self.__api_client

    token = self.__user_data.token
    if not token:
      raise Exception("user data not contains token")

    self.__api_client = api.ApiClient(
      self.__api_secret.client_id, self.__api_secret.client_secret, token)

    return self.__api_client

  def __refresh_token(self):
    try:
      token = self.__get_api_client().refresh_token()
    except api.AuthorizationError:
      # refreshに失敗する場合は、user_dataからtokenを削除する
      self.__user_data.token = None
      self.__user_data.save()
      raise Exception("Failed to refresh token")
    else:
      self.__user_data.token = token
      self.__user_data.save()

  def get_playlists(self) -> List[api.Playlist]:
    try:
      return self.__get_api_client().get_current_user_playlists()
    except api.AccessTokenExpiredError:
      self.__refresh_token()
      return self.__get_api_client().get_current_user_playlists()

  def replace_playlist(self, playlist_id: Optional[str] = None):
    if playlist_id is None:
      if not (playlist_id := self.__user_data.reload_playlist_id):
        raise Exception("user data not contains reload_playlist_id")

    now = datetime.now(JST)
    song_list = self.__ranking_client.get_song_list()
    uris = [song.uri for song in song_list[:100]]
    try:
      self.__get_api_client().replace_playlist_items(playlist_id, uris)
    except api.AccessTokenExpiredError:
      self.__refresh_token()
      self.__get_api_client().replace_playlist_items(playlist_id, uris)

    description = f"Updated at {now.strftime('%Y-%m-%d %H:%M:%S')}"
    self.__get_api_client().change_playlist_details(
      playlist_id, description=description)

    logger.info("playlist items were replaced(playlist_id=%s)", playlist_id)
