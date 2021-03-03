import json
import pathlib
import urllib.parse

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import data

secret_path = pathlib.Path("secret.json")
assert secret_path.is_file()
with secret_path.open() as f:
  SECRET = json.load(f)

app = FastAPI()

base_dir_path = pathlib.Path(__file__).parent
template_dir_path = base_dir_path / "templates"
templates = Jinja2Templates(directory=template_dir_path)

songs = data.fetch_ranking()
artists = {}
for song in songs:
  artists.setdefault(song.artist, []).append(song)


@app.get("/")
async def home(request: Request):
  return templates.TemplateResponse(
    "home.html",
    dict(request=request, songs=songs, artists=artists)
  )


@app.get("/login")
async def login():
  scopes = 'user-read-private user-read-email'
  redirect_url = 'http://localhost:8000/login/callback'
  params = dict(
    response_type='code',
    client_id=SECRET['client_id'],
    scope=scopes,
    redirect_uri=redirect_url
  )

  url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  return RedirectResponse(url)


@app.get("/login/callback")
async def login_callback(request: Request):
  return RedirectResponse("/")
