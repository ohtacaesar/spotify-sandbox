import logging
import time
import urllib.parse

import jwt
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from spotify import data, api, service, user, config

logger = logging.getLogger(__name__)


class PutTrack(BaseModel):
  mute: bool


JWT_SECRET = config.get_jwt_secret()
JWT_ALG = "HS256"

REDIRECT_PATH = '/app/login/callback'
SCOPES = [
  'playlist-modify-public',
  'playlist-modify-private',
  'playlist-read-private',
]

client_credentials = config.get_client_credentials()
ranking_client = data.RankingClient()
api_client = api.ApiClient(client_credentials)
ranking_service = service.RankingService(api_client, ranking_client)

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_credentials=True,
  allow_origins=["*"],
  allow_headers=["*"],
  allow_methods=["*"],
)


def intersect(a, b):
  return set(a).intersection(b)


def get_user_resource_api_client(profile_id: str) -> api.UserResourceApiClient:
  user_data = user.get_user_data(profile_id)
  if not user_data.token:
    raise Exception('tokenがありません')

  return api.UserResourceApiClient(client_credentials, user_data.token)


def get_api_service(profile_id: str) -> service.UserService:
  return service.UserService(
    user.get_user_data(profile_id),
    get_user_resource_api_client(profile_id),
    ranking_service)


def get_profile_id_from(request: Request) -> str:
  token: str = request.headers.get("Authorization")
  if not token:
    logger.warning("No required header given")
    raise HTTPException(status_code=400, detail="No required header given")
  if not token.startswith("Bearer "):
    logger.warning("Header format was wrong")
    raise HTTPException(status_code=400, detail="Header format was wrong")
  token = token.split(" ")[-1]
  try:
    session = jwt.decode(token, JWT_SECRET, [JWT_ALG])
  except Exception as e:
    logger.error(e)
    raise HTTPException(status_code=403, detail=str(e))
  profile_id = session.get("sub")

  return profile_id


@app.get("/")
async def home():
  return RedirectResponse("/app")


@app.get("/tracks_and_artists")
async def tracks_and_artists(request: Request):
  profile_id = get_profile_id_from(request)
  user_data = user.get_user_data(profile_id)
  tracks = ranking_service.get_tracks()

  blocking_tracks = set(user_data.blocking_tracks)
  blocking_artists = set(user_data.blocking_artists)
  user_tracks = []
  user_artists = {}
  for track in tracks:
    artist_ids = []
    for artist in track.artists:
      artist_ids.append(artist.id)
      if artist.id in user_artists:
        continue

      user_artists[artist.id] = data.UserArtist(
        artist.id, artist.name, artist.id in blocking_artists)

    user_tracks.append(data.UserTrack(
      track.id, track.name, artist_ids, track.id in blocking_tracks))

  return dict(tracks=user_tracks, artists=list(user_artists.values()))


@app.get('/playlists')
async def playlists(request: Request):
  profile_id = get_profile_id_from(request)
  api_service = get_api_service(profile_id)
  playlists = api_service.get_playlists()

  return playlists


@app.put('/tracks/{id}')
async def put_track(request: Request, id: str, body: PutTrack):
  profile_id = get_profile_id_from(request)
  user_data = user.get_user_data(profile_id)
  if body.mute and id not in user_data.blocking_tracks:
    user_data.blocking_tracks.append(id)
  if not body.mute and id in user_data.blocking_tracks:
    user_data.blocking_tracks.remove(id)
  user_data.save()


@app.put('/artists/{id}')
async def put_artist(request: Request, id: str, body: PutTrack):
  profile_id = get_profile_id_from(request)
  user_data = user.get_user_data(profile_id)
  if body.mute and id not in user_data.blocking_artists:
    user_data.blocking_tracks.append(id)
  if not body.mute and id in user_data.blocking_artists:
    user_data.blocking_artists.append(id)
  user_data.save()


@app.post('/replace_playlist')
async def replace_playlist(request: Request):
  profile_id = get_profile_id_from(request)
  get_api_service(profile_id).replace_playlist()


@app.post('/playlists/{playlist_id}/set')
async def set_target_playlist(request: Request, playlist_id: str):
  profile_id = get_profile_id_from(request)
  user_data = user.get_user_data(profile_id)
  user_data.reload_playlist_id = playlist_id
  user_data.save()


@app.get("/login")
async def login(request: Request, origin: str):
  base_url = origin
  if not base_url:
    base_url = str(request.base_url)
  redirect_uri = f"{base_url.strip('/')}{REDIRECT_PATH}"
  logger.info("redirec_url: %s", redirect_uri)

  params = dict(
    response_type='code',
    client_id=client_credentials.id,
    redirect_uri=redirect_uri,
  )
  if SCOPES:
    params['scope'] = ' '.join(SCOPES)

  url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  return RedirectResponse(url)


@app.get("/login/callback")
async def login_callback(request: Request, code: str, origin: str):
  base_url = origin
  if not base_url:
    base_url = str(request.base_url)
  redirect_uri = f"{base_url.strip('/')}{REDIRECT_PATH}"
  logger.info("redirec_url: %s", redirect_uri)
  try:
    token = api.fetch_token(code, client_credentials, redirect_uri)
  except Exception as e:
    logger.error(str(e))
    return RedirectResponse('/', 302)

  client = api.UserResourceApiClient(client_credentials, token)
  profile = client.get_current_user_profile()

  user_data = user.get_user_data(profile.id)
  user_data.profile = profile
  user_data.token = token
  user_data.save()

  return jwt.encode(
    dict(sub=profile.id, iss=int(time.time())),
    JWT_SECRET,
    JWT_ALG
  )
