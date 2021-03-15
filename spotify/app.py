import logging
import pathlib
import urllib.parse
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from spotify import data, api, service, user, config

logger = logging.getLogger('spotify')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
  'level:%(levelname)s\ttime:%(asctime)s\tname:%(name)s(%(lineno)d)\tmessage:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

REDIRECT_URI = 'http://localhost:8000/login/callback'
SCOPES = [
  'playlist-modify-public',
  'playlist-modify-private',
  'playlist-read-private',
]

SESSION = {}

secret = config.get_api_client_secret()

app = FastAPI()

base_dir_path = pathlib.Path(__file__).parent
template_dir_path = base_dir_path / "templates"
templates = Jinja2Templates(directory=template_dir_path)

ranking_client = data.RankingClient()


def get_api_client() -> Optional[api.ApiClient]:
  data = user.get_user_data()
  token = data.token
  if not token:
    return None

  return api.ApiClient(secret.client_id, secret.client_secret, token)


def get_api_service() -> service.ApiService:
  return service.ApiService(user.get_user_data(), secret, ranking_client)


@app.get("/")
async def home(request: Request):
  return templates.TemplateResponse(
    "home.html", dict(
      request=request,
      songs=ranking_client.get_song_list(),
      artists=ranking_client.get_artists_dict()
    )
  )


@app.get('/playlists')
async def playlists(request: Request):
  api_service = get_api_service()
  profile = api_service.get_profile()
  user_data = user.get_user_data()

  playlists = api_service.get_playlists()

  return templates.TemplateResponse(
    "playlists.html", dict(
      request=request,
      profile=profile,
      playlists=playlists,
      reload_playlist_id=user_data.reload_playlist_id
    )
  )


@app.post('/replace_playlist')
async def replace_playlist(request: Request):
  get_api_service().replace_playlist()
  return RedirectResponse('/', 302)


@app.post('/playlists/{playlist_id}/set')
async def set_target_playlist(playlist_id: str):
  user_data = user.get_user_data()
  user_data.reload_playlist_id = playlist_id
  user_data.save()

  return RedirectResponse('/playlists', 302)


@app.post('/playlists/{playlist_id}/replace')
async def replace(playlist_id: str):
  get_api_service().replace_playlist(playlist_id)
  return RedirectResponse('/playlists', 302)


@app.get("/login")
async def login():
  params = dict(
    response_type='code',
    client_id=secret.client_id,
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
    token = api.fetch_token(
      code, secret.client_id, secret.client_secret, REDIRECT_URI)
    user_data.token = token
  except Exception as e:
    logger.error(str(e))
    return RedirectResponse('/', 302)

  client = get_api_client()
  profile = client.get_current_user_profile()
  user_data.profile = profile
  user_data.save()

  return RedirectResponse(SESSION.pop('redirect', '/'), 302)
