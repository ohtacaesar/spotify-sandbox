import json
import pathlib
from spotify import api

SECRET_PATH = pathlib.Path("secret.json")


def __get_secret_content() -> dict:
  assert SECRET_PATH.is_file()
  with SECRET_PATH.open() as f:
    return json.load(f)


def get_client_credentials() -> api.ClientCredentials:
  secret = __get_secret_content()
  api_secret = api.ClientCredentials(
    secret['client_id'],
    secret['client_secret'],
  )

  return api_secret


def get_jwt_secret() -> str:
  secret = __get_secret_content()
  return secret['jwt_secret']
