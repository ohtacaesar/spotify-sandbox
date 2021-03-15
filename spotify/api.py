import base64
import logging
from dataclasses import dataclass
from typing import Optional, List

import requests

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
  pass


class UnauthorizedError(Exception):
  pass


class AccessTokenExpiredError(UnauthorizedError):
  pass


class ApiError(Exception):
  pass


@dataclass()
class Token:
  access_token: str
  token_type: str
  scope: str
  expires_in: int
  refresh_token: str


def create_token_from_dict(o: dict) -> Token:
  return Token(
    o['access_token'],
    o['token_type'],
    o['scope'],
    o['expires_in'],
    o['refresh_token']
  )


@dataclass()
class Profile:
  id: str
  display_name: str
  uri: str
  country: str


def create_profile_from_dict(o: dict) -> Profile:
  return Profile(
    o['id'],
    o['display_name'],
    o['uri'],
    o['country']
  )


@dataclass()
class Playlist:
  id: str
  name: str
  public: bool
  uri: str
  owner_id: str


def fetch_token(
  code: str,
  client_id: str,
  client_secret: str,
  redirect_uri: str,
) -> Token:
  url = f"https://accounts.spotify.com/api/token"
  secret = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8'))

  headers = dict(Authorization="Basic " + secret.decode('utf-8'))
  payload = dict(
    grant_type="authorization_code",
    code=code,
    redirect_uri=redirect_uri,
  )
  r = requests.post(url, data=payload, headers=headers)
  validate_response(r)
  body = r.json()
  return create_token_from_dict(body)


def refresh_token():
  pass


def validate_response(r: requests.Response):
  if r.ok:
    return

  if r.status_code == 401:
    body = r.json()
    message = f'{body.get("error", {}).get("message")}({r.status_code})'
    if message.startswith("The access token expired"):
      raise AccessTokenExpiredError(message)
    else:
      raise UnauthorizedError(message)
  else:
    raise ApiError(f"{r.status_code}: {r.text}")


@dataclass()
class ApiClient:
  client_id: str
  client_secret: str
  token: Token

  def _headers(self):
    headers = dict(Authorization="Bearer " + self.token.access_token)
    return headers

  def refresh_token(self) -> Token:
    payload = dict(grant_type='refresh_token',
                   refresh_token=self.token.refresh_token)

    secret = f"{self.client_id}:{self.client_secret}".encode('utf-8')
    secret = base64.b64encode(secret)
    headers = dict(Authorization="Basic " + secret.decode('utf-8'))
    r = requests.post(f"https://accounts.spotify.com/api/token", data=payload,
                      headers=headers)

    if not r.ok:
      raise AuthorizationError(r.json().get("error"))

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

  def get_current_user_profile(self) -> Optional[Profile]:
    r = requests.get("https://api.spotify.com/v1/me",
                     headers=self._headers())
    validate_response(r)

    data = r.json()
    return Profile(
      data.get('id'), data.get('display_name'), data.get('uri'),
      data.get('country'))

  def get_current_user_playlists(self) -> List[Playlist]:
    r = requests.get("https://api.spotify.com/v1/me/playlists",
                     headers=self._headers())

    validate_response(r)

    playlists = []
    for item in r.json()['items']:
      playlists.append(Playlist(
        item['id'], item['name'], item['public'], item['uri'],
        item['owner']['id']
      ))

    return playlists

  def change_playlist_details(self,
    playlist_id: str,
    name: Optional[str] = None,
    public: Optional[bool] = None,
    collaborative: Optional[bool] = None,
    description: Optional[str] = None
  ):
    payload = dict(name=name, public=public, collaborative=collaborative,
                   description=description)
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.put(
      f"https://api.spotify.com/v1/playlists/{playlist_id}",
      json=payload,
      headers=self._headers()
    )
    validate_response(r)

  def replace_playlist_items(self, playlist_id: str, uris: List[str]) -> str:
    payload = dict(uris=uris)

    r = requests.put(
      f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={','.join(uris)}",
      json=payload,
      headers=self._headers()
    )
    validate_response(r)

    return r.json().get('snapshop_it')
