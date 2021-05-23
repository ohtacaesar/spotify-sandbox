import base64
import logging
from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import urlencode

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
class ClientCredentials:
  id: str
  secret: str

  def get_basic_code(self):
    return base64.b64encode(f"{self.id}:{self.secret}".encode('utf-8')).decode()


@dataclass()
class ClientCredentialsFlowToken:
  access_token: str
  token_type: str
  expires_in: int


@dataclass()
class AuthorizationCodeFlowToken:
  access_token: str
  token_type: str
  scope: str
  expires_in: int
  refresh_token: str


@dataclass(frozen=True)
class Artist:
  id: str
  name: str

  @property
  def uri(self):
    return f"spotify:artist:{self.id}"


@dataclass(frozen=True)
class Track:
  id: str
  name: str
  popularity: int
  artists: List[Artist]

  @property
  def uri(self):
    return f"spotify:track:{self.id}"


def create_token_from_dict(o: dict) -> AuthorizationCodeFlowToken:
  return AuthorizationCodeFlowToken(
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
  client_credentials: ClientCredentials,
  redirect_uri: str,
) -> AuthorizationCodeFlowToken:
  url = f"https://accounts.spotify.com/api/token"

  headers = dict(Authorization=f"Basic {client_credentials.get_basic_code()}")
  payload = dict(
    grant_type="authorization_code",
    code=code,
    redirect_uri=redirect_uri,
  )
  r = requests.post(url, data=payload, headers=headers)
  validate_response(r)
  body = r.json()
  return create_token_from_dict(body)


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
  __credentials: ClientCredentials
  __token: ClientCredentialsFlowToken = None

  def _headers(self):
    if self.__token is None:
      self.refresh_token()
    headers = dict(Authorization="Bearer " + self.__token.access_token)
    return headers

  def refresh_token(self) -> ClientCredentialsFlowToken:
    payload = dict(grant_type='client_credentials')
    headers = dict(Authorization=f"Basic {self.__credentials.get_basic_code()}")

    r = requests.post('https://accounts.spotify.com/api/token', payload,
                      headers=headers)
    validate_response(r)
    data = r.json()
    self.__token = ClientCredentialsFlowToken(
      data['access_token'],
      data['token_type'],
      data['expires_in']
    )
    return self.__token

  def get_several_tracks(self,
    ids: List[str],
    market: Optional[str] = None
  ) -> List[Track]:
    params = dict(ids=','.join(ids))
    if market:
      params['market'] = market

    r = requests.get(
      f"https://api.spotify.com/v1/tracks?{urlencode(params)}",
      headers=self._headers()
    )
    validate_response(r)
    items = r.json()['tracks']
    logger.info("Fetched %d tracks", len(items))

    tracks = []
    for item in items:
      artists = [Artist(a['id'], a['name']) for a in item['artists']]
      tracks.append(
        Track(item['id'], item['name'], item['popularity'], artists=artists))

    return tracks


@dataclass()
class UserResourceApiClient:
  __credentials: ClientCredentials
  __token: AuthorizationCodeFlowToken

  def _headers(self):
    headers = dict(Authorization="Bearer " + self.__token.access_token)
    return headers

  def refresh_token(self) -> AuthorizationCodeFlowToken:
    payload = dict(grant_type='refresh_token',
                   refresh_token=self.__token.refresh_token)

    headers = dict(Authorization=f"Basic {self.__credentials.get_basic_code()}")
    r = requests.post(f"https://accounts.spotify.com/api/token", data=payload,
                      headers=headers)

    if not r.ok:
      raise AuthorizationError(r.json().get("error"))

    data = r.json()
    token = AuthorizationCodeFlowToken(
      data['access_token'],
      data['token_type'],
      data['scope'],
      data['expires_in'],
      self.__token.refresh_token
    )
    self.__token = token

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
    # urlencodeするとurl too longになる
    uris = ','.join(uris)
    payload = dict(uris=uris)

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uris}"
    r = requests.put(url, json=payload, headers=self._headers())
    validate_response(r)

    return r.json().get('snapshot_id')
