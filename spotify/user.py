import json
import logging
import pathlib
from dataclasses import dataclass
from typing import Optional

from . import api

logger = logging.getLogger(__name__)

USER_DATA_PATH = pathlib.Path('user_data.json')


@dataclass()
class UserData:
  token: Optional[api.Token] = None
  reload_playlist_id: Optional[str] = None

  def to_dict(self) -> dict:
    return dict(
      reload_playlist_id=self.reload_playlist_id,
      token=self.token.to_dict() if self.token else None
    )

  def save(self):
    with USER_DATA_PATH.open('w') as f:
      f.write(json.dumps(self.to_dict()))



def create_user_data_from_dict(o: dict) -> UserData:
  user_data = UserData()
  token = o.get('token')
  if token:
    user_data.token = api.create_token_from_dict(token)
  user_data.reload_playlist_id = o.get('reload_playlist_id')

  return user_data


def get_user_data() -> UserData:
  if not USER_DATA_PATH.is_file():
    return UserData()

  with USER_DATA_PATH.open() as f:
    d = json.load(f)
    user_data = create_user_data_from_dict(d)
    logger.info("USER_DATA was loaded from file")

  return user_data
