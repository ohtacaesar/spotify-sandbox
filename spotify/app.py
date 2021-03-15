import logging
import pathlib
import urllib.parse

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from spotify import data, api, service, user, config

REDIRECT_URI = 'http://localhost:8000/login/callback'
SCOPES = [
  'playlist-modify-public',
  'playlist-modify-private',
  'playlist-read-private',
]

SESSION = {}

logger = logging.getLogger(__name__)

secret = config.get_api_client_secret()
ranking_client = data.RankingClient()

app = FastAPI()

base_dir_path = pathlib.Path(__file__).parent
template_dir_path = base_dir_path / "templates"
templates = Jinja2Templates(directory=template_dir_path)


def get_api_service() -> service.ApiService:
  return service.ApiService(user.get_user_data(), secret, ranking_client)


@app.get("/")
async def home(request: Request):
  user_data = user.get_user_data()
  return templates.TemplateResponse(
    "home.html", dict(
      request=request,
      songs=ranking_client.get_song_list(),
      artists=ranking_client.get_artists_dict(),
      blocking_songs=set(user_data.blocking_songs),
      blocking_artists=set(user_data.blocking_artists),
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


@app.post('/songs/{id}/block')
async def block_song(id: str):
  logger.info('id=%s', id)
  user_data = user.get_user_data()
  user_data.blocking_songs.append(id)
  user_data.save()

  return RedirectResponse('/', 302)


@app.post('/songs/{id}/unblock')
async def unblock_song(id: str):
  user_data = user.get_user_data()
  user_data.blocking_songs.remove(id)
  user_data.save()

  return RedirectResponse('/', 302)


@app.post('/replace_playlist')
async def replace_playlist():
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

  client = api.ApiClient(secret.client_id, secret.client_secret, token)
  profile = client.get_current_user_profile()
  user_data.profile = profile
  user_data.save()

  return RedirectResponse(SESSION.pop('redirect', '/'), 302)
