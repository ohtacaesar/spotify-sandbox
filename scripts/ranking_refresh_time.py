import hashlib
import logging

import requests

FORMAT = "level:%(levelname)s\ttime:%(asctime)s\tmessage:%(message)s"
logging.basicConfig(
  filename='ranking_refresh_time.log', format=FORMAT, level=logging.INFO)

URL = "https://spotifycharts.com/regional/jp/daily/latest/download"

with requests.get(URL) as r:
  hash = None
  if r.ok:
    hash = hashlib.md5(r.text.encode()).hexdigest()
  logging.info("\tstatus_code:%d\thash:%s", r.status_code, hash)
