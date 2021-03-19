import hashlib
import logging
import pathlib

import requests

DIR_PATH = pathlib.Path("ranking_refresh_time/")
DIR_PATH.mkdir(exist_ok=True)

FORMAT = "level:%(levelname)s\ttime:%(asctime)s\t%(message)s"
URL = "https://spotifycharts.com/regional/jp/daily/latest/download"
logging.basicConfig(
  filename=DIR_PATH / 'ranking_refresh_time.log',
  format=FORMAT,
  level=logging.INFO)


def main():
  with requests.get(URL) as r:
    if not r.ok:
      logging.error("status_code:%d")
      return

    hash = hashlib.md5(r.text.encode()).hexdigest()
    file_path = DIR_PATH / f"{hash}.csv"
    if file_path.is_file():
      return
    with file_path.open('w', encoding='utf-8', newline='\n') as f:
      f.write(r.text)
    logging.error("status_code:%d\thash:%s", r.status_code, hash)


if __name__ == '__main__':
  main()
