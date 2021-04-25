import logging
import urllib.parse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from spotify import data, api, service, user, config

REDIRECT_URI = 'http://localhost:8000/login/callback'
SCOPES = [
  'playlist-modify-public',
  'playlist-modify-private',
  'playlist-read-private',
]

SESSION = {}

logger = logging.getLogger(__name__)

client_credentials = config.get_client_credentials()
ranking_client = data.RankingClient()
api_client = api.ApiClient(client_credentials)
ranking_service = service.RankingService(api_client, ranking_client)

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.mount(
  '/app',
  StaticFiles(packages=['spotify'], html=True),
  name='static'
)


def intersect(a, b):
  return set(a).intersection(b)


def get_user_resource_api_client() -> api.UserResourceApiClient:
  user_data = user.get_user_data()
  if not user_data.token:
    raise Exception('tokenがありません')

  return api.UserResourceApiClient(client_credentials, user_data.token)


def get_api_service() -> service.UserService:
  return service.UserService(
    user.get_user_data(), get_user_resource_api_client(), ranking_service)


@app.get("/")
async def home():
  return RedirectResponse("/app")


@app.get("/tracks_and_artists")
async def tracks_and_artists(request: Request):
  user_data = user.get_user_data()
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
  api_service = get_api_service()
  profile = api_service.get_profile()
  user_data = user.get_user_data()

  playlists = api_service.get_playlists()


@app.post('/tracks/{id}/block')
async def block_track(id: str):
  logger.info('id=%s', id)
  user_data = user.get_user_data()
  user_data.blocking_tracks.append(id)
  user_data.save()


@app.post('/tracks/{id}/unblock')
async def unblock_track(id: str):
  user_data = user.get_user_data()
  user_data.blocking_tracks.remove(id)
  user_data.save()


@app.post('/artists/{id}/block')
async def block_artist(id: str):
  user_data = user.get_user_data()
  user_data.blocking_artists.append(id)
  user_data.save()


@app.post('/artists/{id}/unblock')
async def unblock_artist(id: str):
  user_data = user.get_user_data()
  user_data.blocking_artists.remove(id)
  user_data.save()


@app.post('/replace_playlist')
async def replace_playlist():
  get_api_service().replace_playlist()


@app.post('/playlists/{playlist_id}/set')
async def set_target_playlist(playlist_id: str):
  user_data = user.get_user_data()
  user_data.reload_playlist_id = playlist_id
  user_data.save()


@app.post('/playlists/{playlist_id}/replace')
async def replace(playlist_id: str):
  get_api_service().replace_playlist(playlist_id)


@app.get("/login")
async def login():
  params = dict(
    response_type='code',
    client_id=client_credentials.id,
    redirect_uri=REDIRECT_URI,
  )
  if SCOPES:
    params['scope'] = ' '.join(SCOPES)

  url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  return RedirectResponse(url)


@app.get("/login/callback")
async def login_callback(code: str = None):
  user_data = user.get_user_data()
  try:
    token = api.fetch_token(code, client_credentials, REDIRECT_URI)
    user_data.token = token
  except Exception as e:
    logger.error(str(e))
    return RedirectResponse('/', 302)

  client = api.UserResourceApiClient(
    client_credentials.id, client_credentials.secret, token)
  profile = client.get_current_user_profile()
  user_data.profile = profile
  user_data.save()

  return RedirectResponse(SESSION.pop('redirect', '/'), 302)
