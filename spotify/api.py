import base64
import json
import urllib.parse
import logging
from dataclasses import dataclass
from typing import Optional, List

import requests

logger = logging.getLogger(__name__)


@dataclass()
class Token:
  access_token: str
  token_type: str
  scope: str
  expires_in: int
  refresh_token: str


@dataclass()
class Profile:
  id: str
  display_name: str
  uri: str
  country: str


@dataclass()
class Playlist:
  id: str
  name: str
  public: bool
  uri: str


def fetch_token(
  code: str,
  client_id: str,
  client_secret: str,
  redirect_uri: str,
) -> Optional[Token]:
  url = f"https://accounts.spotify.com/api/token"
  secret = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8'))

  headers = dict(Authorization="Basic " + secret.decode('utf-8'))
  payload = dict(
    grant_type="authorization_code",
    code=code,
    redirect_uri=redirect_uri,
  )
  r = requests.post(url, data=payload, headers=headers)
  if not r.ok:
    logger.error(r.text)
    return None

  body = r.json()
  return Token(
    body['access_token'],
    body['token_type'],
    body['scope'],
    body['expires_in'],
    body['refresh_token']
  )


@dataclass()
class ApiClient:
  client_id: str
  client_secret: str
  token: Token

  def _headers(self):
    headers = dict(Authorization="Bearer " + self.token.access_token)
    return headers

  def refresh_token(self) -> Token:
    params = dict(grant_type='refresh_token',
                  refresh_token=self.token.refresh_token)

    qs = urllib.parse.urlencode(params)
    r = requests.get(f"https://accounts.spotify.com/api/token?${qs}",
                     headers=self._headers())
    if not r.ok:
      logger.error(r.text)

    data = r.json()
    token = Token(
      data['access_token'],
      data['token_type'],
      data['scope'],
      data['expires_in'],
      self.token.refresh_token
    )
    self.token = token

    return token

  def fetch_profile(self) -> Optional[Profile]:
    r = requests.get("https://api.spotify.com/v1/me",
                     headers=self._headers())
    if not r.ok:
      logger.error(r.text)
      return None

    data = r.json()
    return Profile(
      data.get('id'), data.get('display_name'), data.get('uri'),
      data.get('country'))

  def fetch_playlists(self) -> Optional[List[Playlist]]:
    r = requests.get("https://api.spotify.com/v1/me/playlists",
                     headers=self._headers())

    if not r.ok:
      logger.error(r.text)
      return None

    playlists = []
    for item in r.json()['items']:
      playlists.append(
        Playlist(item['id'], item['name'], item['public'], item['uri'])
      )

    return playlists

  def replace_tracks(self, playlist_id: str, uris: List[str]):
    payload = dict(uris=uris)

    r = requests.put(
      f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={','.join(uris)}",
      json=json.dumps(payload),
      headers=self._headers()
    )
    if not r.ok:
      logger.error(r.text)
      return None

    print(r.json())
