import json
import logging
import pathlib
import urllib.parse
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import data, api

logger = logging.getLogger(__name__)
logger.info('test')

REDIRECT_URI = 'http://localhost:8000/login/callback'
SCOPES = [
  'playlist-modify-public',
  'playlist-modify-private',
  'playlist-read-private',
]
SESSION = {}
secret_path = pathlib.Path("secret.json")
assert secret_path.is_file()
with secret_path.open() as f:
  secret = json.load(f)
  CLIENT_ID = secret['client_id']
  CLIENT_SECRET = secret['client_secret']

app = FastAPI()

base_dir_path = pathlib.Path(__file__).parent
template_dir_path = base_dir_path / "templates"
templates = Jinja2Templates(directory=template_dir_path)

songs = data.fetch_ranking()
artists = {}
for song in songs:
  artists.setdefault(song.artist, []).append(song)


def get_api_client() -> Optional[api.ApiClient]:
  token = SESSION.get('token')
  if not token:
    return None

  return api.ApiClient(CLIENT_ID, CLIENT_SECRET, token)


@app.get("/")
async def home(request: Request):
  return templates.TemplateResponse(
    "home.html",
    dict(request=request, songs=songs, artists=artists)
  )


@app.get('/playlists')
async def playlists(request: Request):
  client = get_api_client()
  if client is None:
    SESSION['redirect'] = request.url.path
    return RedirectResponse('/login')

  playlists = client.fetch_playlists()

  return templates.TemplateResponse(
    "playlists.html",
    dict(request=request, playlists=playlists)
  )


@app.post('/playlists/{playlist_id}')
async def replace(playlist_id: str):
  client = get_api_client()
  if client is None:
    return RedirectResponse('/')

  songs = data.fetch_ranking()
  uris = [song.uri for song in songs[:100]]
  client.replace_tracks(playlist_id, uris)

  return RedirectResponse('/playlists', 302)


@app.get("/login")
async def login():
  params = dict(
    response_type='code',
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
  )
  if SCOPES:
    params['scope'] = ' '.join(SCOPES)

  url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  return RedirectResponse(url)


@app.get("/login/callback")
async def login_callback(code: str = None):
  token = api.fetch_token(code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
  SESSION['token'] = token

  client = get_api_client()
  profile = client.fetch_profile()
  SESSION['profile'] = profile

  return RedirectResponse(SESSION.pop('redirect', '/'))
