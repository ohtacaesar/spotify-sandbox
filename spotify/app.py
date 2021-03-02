import pathlib

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from . import data

app = FastAPI()

base_dir_path = pathlib.Path(__file__).parent
template_dir_path = base_dir_path / "templates"
templates = Jinja2Templates(directory=template_dir_path)

songs = data.fetch_ranking()


@app.get("/")
async def home(request: Request):
  return templates.TemplateResponse("home.html", dict(request=request))
