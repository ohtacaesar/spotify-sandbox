import json
import logging
import pathlib
from typing import Optional, List

from spotify import api

logger = logging.getLogger(__name__)

USERDATA_DIR = pathlib.Path('tmp/')
if not USERDATA_DIR.is_dir():
  USERDATA_DIR.mkdir()


class UserData:
  token: Optional[api.AuthorizationCodeFlowToken] = None
  profile: Optional[api.Profile] = None
  blocking_tracks: List[str] = []
  blocking_artists: List[str] = []
  reload_playlist_id: Optional[str] = None

  def to_dict(self) -> dict:
    return dict(
      token=self.token.__dict__.copy() if self.token else None,
      profile=self.profile.__dict__.copy() if self.profile else None,
      blocking_tracks=self.blocking_tracks,
      blocking_artists=self.blocking_artists,
      reload_playlist_id=self.reload_playlist_id,
    )

  def save(self):
    path = USERDATA_DIR / self.profile.id
    with path.open('w') as f:
      f.write(json.dumps(self.to_dict()))


def create_user_data_from_dict(o: dict) -> UserData:
  user_data = UserData()
  if token := o.get('token'):
    user_data.token = api.create_token_from_dict(token)
  if profile := o.get('profile'):
    user_data.profile = api.create_profile_from_dict(profile)
  user_data.blocking_tracks = o.get('blocking_tracks', [])
  user_data.blocking_artists = o.get('blocking_artists', [])
  user_data.reload_playlist_id = o.get('reload_playlist_id')

  return user_data


def get_user_data(profile_id: str) -> UserData:
  path = USERDATA_DIR / profile_id
  if not path.is_file():
    return UserData()

  with path.open() as f:
    try:
      d = json.load(f)
      user_data = create_user_data_from_dict(d)
      logger.info("USER_DATA was loaded from file")
      return user_data
    except:
      return UserData()
