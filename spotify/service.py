from dataclasses import dataclass
from typing import Optional, List
import logging

from . import user, api, data, config

logger = logging.getLogger(__name__)


@dataclass()
class ApiService:
  __user_data: user.UserData
  __api_secret: config.ApiSecret
  __ranking_client: data.RankingClient
  __api_client: Optional[api.ApiClient] = None

  def _api_client(self):
    if self.__api_client:
      return self.__api_client

    token = self.__user_data.token
    if not token:
      raise Exception("user data not contains token")

    self.__api_client = api.ApiClient(
      self.__api_secret.client_id, self.__api_secret.client_secret, token)

    return self.__api_client

  def get_playlists(self) -> List[api.Playlist]:
    try:
      return self._api_client().fetch_playlists()
    except api.AccessTokenExpiredError:
      token = self._api_client().refresh_token()
      logger.info("access token was refreshed")
      self.__user_data.token = token
      self.__user_data.save()
      return self._api_client().fetch_playlists()

  def replace_playlist(self, playlist_id: Optional[str] = None):
    if playlist_id is None:
      playlist_id = self.__user_data.reload_playlist_id
    if not playlist_id:
      raise Exception("user data not contains reload_playlist_id")

    song_list = self.__ranking_client.get_song_list()
    uris = [song.uri for song in song_list[:100]]
    self._api_client().replace_tracks(playlist_id, uris)
    logger.info("playlist items were replaced(playlist_id=%s)", playlist_id)
