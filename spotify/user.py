import json
import logging
import pathlib
from typing import Optional, List

from spotify import api

logger = logging.getLogger(__name__)

USER_DATA_PATH = pathlib.Path('user_data.json')


class UserData:
  token: Optional[api.Token] = None
  profile: Optional[api.Profile] = None
  blocking_songs: List[str] = []
  blocking_artists: List[str] = []
  reload_playlist_id: Optional[str] = None

  def to_dict(self) -> dict:
    return dict(
      token=self.token.__dict__.copy() if self.token else None,
      profile=self.profile.__dict__.copy() if self.profile else None,
      blocking_songs=self.blocking_songs,
      blocking_artists=self.blocking_artists,
      reload_playlist_id=self.reload_playlist_id,
    )

  def save(self):
    logger.info(self.blocking_songs)
    logger.info(self.blocking_artists)
    with USER_DATA_PATH.open('w') as f:
      f.write(json.dumps(self.to_dict()))


def create_user_data_from_dict(o: dict) -> UserData:
  user_data = UserData()
  if token := o.get('token'):
    user_data.token = api.create_token_from_dict(token)
  if profile := o.get('profile'):
    user_data.profile = api.create_profile_from_dict(profile)
  user_data.blocking_songs = o.get('blocking_songs', [])
  user_data.blocking_artists = o.get('blocking_artists', [])
  user_data.reload_playlist_id = o.get('reload_playlist_id')

  return user_data


def get_user_data() -> UserData:
  if not USER_DATA_PATH.is_file():
    return UserData()

  with USER_DATA_PATH.open() as f:
    try:
      d = json.load(f)
      user_data = create_user_data_from_dict(d)
      logger.info("USER_DATA was loaded from file")
      return user_data
    except:
      return UserData()
