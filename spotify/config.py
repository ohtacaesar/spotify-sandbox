import json
import pathlib
from spotify import api

SECRET_PATH = pathlib.Path("secret.json")


def get_client_credentials() -> api.ClientCredentials:
  assert SECRET_PATH.is_file()
  with SECRET_PATH.open() as f:
    secret = json.load(f)

  api_secret = api.ClientCredentials(
    secret['client_id'],
    secret['client_secret'],
  )

  return api_secret
