import stat

from fastapi.staticfiles import StaticFiles
from starlette.responses import (
  PlainTextResponse,
  Response,
)
from starlette.types import Scope


class ReactStaticFiles(StaticFiles):
  """
  static/*以外へのアクセスの場合、ファイルが見つからないならとにかくindex.htmlを返す
  """

  async def get_response(self, path: str, scope: Scope) -> Response:
    """
    Returns an HTTP response, given the incoming path, method and request headers.
    """
    if scope["method"] not in ("GET", "HEAD"):
      return PlainTextResponse("Method Not Allowed", status_code=405)

    full_path, stat_result = await self.lookup_path(path)
    if stat_result and stat.S_ISREG(stat_result.st_mode):
      # We have a static file to serve.
      return self.file_response(full_path, stat_result, scope)

    if self.html and not path.startswith("static/"):
      full_path, stat_result = await self.lookup_path("index.html")
      if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
        return self.file_response(full_path, stat_result, scope)

    return PlainTextResponse("Not Found", status_code=404)
