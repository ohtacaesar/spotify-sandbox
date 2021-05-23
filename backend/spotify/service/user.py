import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from spotify import JST, user, api, service

logger = logging.getLogger(__name__)


@dataclass()
class UserService:
  __user_data: user.UserData
  __api_client: api.UserResourceApiClient
  __ranking_service: service.RankingService

  def __refresh_token(self):
    try:
      token = self.__api_client.refresh_token()
    except api.AuthorizationError:
      # refreshに失敗する場合は、user_dataからtokenを削除する
      self.__user_data.token = None
      self.__user_data.save()
      raise Exception("Failed to refresh token")
    else:
      self.__user_data.token = token
      self.__user_data.save()

  def get_profile(self) -> api.Profile:
    if profile := self.__user_data.profile:
      return profile

    try:
      profile = self.__api_client.get_current_user_profile()
    except api.AccessTokenExpiredError:
      self.__refresh_token()
      profile = self.__api_client.get_current_user_profile()

    self.__user_data.profile = profile
    self.__user_data.save()

    return profile

  def get_playlists(self) -> List[api.Playlist]:
    try:
      return self.__api_client.get_current_user_playlists()
    except api.AccessTokenExpiredError:
      self.__refresh_token()
      return self.__api_client.get_current_user_playlists()

  def replace_playlist(self, playlist_id: Optional[str] = None):
    if playlist_id is None:
      if not (playlist_id := self.__user_data.reload_playlist_id):
        raise Exception("user data not contains reload_playlist_id")

    now = datetime.now(JST)
    blocking_tracks = set(self.__user_data.blocking_tracks)
    blocking_artists = set(self.__user_data.blocking_artists)
    tracks = self.__ranking_service.get_tracks()

    uris = []
    for track in tracks:
      blocked = False

      for artist in track.artists:
        if artist.id in blocking_artists:
          blocked = True
      if track.id in blocking_tracks:
        blocked = True
      if blocked:
        continue

      uris.append(track.uri)
      if len(uris) == 100:
        break
    try:
      self.__api_client.replace_playlist_items(playlist_id, uris)
    except api.AccessTokenExpiredError:
      self.__refresh_token()
      self.__api_client.replace_playlist_items(playlist_id, uris)

    description = f"{now.strftime('%Y-%m-%d %H:%M:%S')}更新"
    self.__api_client.change_playlist_details(
      playlist_id, description=description)

    logger.info("playlist items were replaced(playlist_id=%s)", playlist_id)
