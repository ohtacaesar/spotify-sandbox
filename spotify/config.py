from dataclasses import dataclass
import pathlib
import json

SECRET_PATH = pathlib.Path("secret.json")


@dataclass()
class ApiSecret:
  client_id: str
  client_secret: str


def get_api_client_secret() -> ApiSecret:
  assert SECRET_PATH.is_file()
  with SECRET_PATH.open() as f:
    secret = json.load(f)

  api_secret = ApiSecret(
    secret['client_id'],
    secret['client_secret'],
  )

  return api_secret
