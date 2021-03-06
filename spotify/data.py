import csv
import logging
from dataclasses import dataclass
from typing import List, Dict

import requests

URL = "https://spotifycharts.com/regional/jp/daily/latest/download"

logger = logging.getLogger(__name__)


@dataclass()
class Song:
  rank: int
  title: str
  artist: str
  count: int
  url: str

  @property
  def id(self) -> str:
    return self.url[self.url.rfind("/") + 1:]

  @property
  def uri(self) -> str:
    return f"spotify:track:{self.id}"


class RankingClient:
  song_list: List[Song] = []

  def _refresh(self):
    r = requests.get(URL)
    logger.info(f"GET(url={URL}, status_code={r.status_code})")
    reader = csv.reader(r.text.split("\n"))
    next(reader)
    next(reader)
    song_list = []
    for row in reader:
      if len(row) < 5: continue
      rank = int(row[0])
      title = row[1]
      artist = row[2]
      count = int(row[3])
      url = row[4]
      song = Song(rank, title, artist, count, url)
      song_list.append(song)

    self.song_list = song_list

  def get_song_list(self, refresh=False) -> List[Song]:
    if not self.song_list or refresh:
      self._refresh()

    return self.song_list

  def get_artists_dict(self, refresh=False) -> Dict[str, int]:
    if not self.song_list or refresh:
      self._refresh()
    artists = {}
    for song in self.song_list:
      artists.setdefault(song.artist, []).append(song)

    return artists
