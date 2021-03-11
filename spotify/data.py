import csv
from dataclasses import dataclass
from typing import List

import requests

URL = "https://spotifycharts.com/regional/jp/daily/latest/download"


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


def fetch_ranking() -> List[Song]:
  r = requests.get(URL)
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
  return song_list


def main():
  song_list = fetch_ranking()

  artist_map = {}
  for song in song_list:
    artist_map[song.artist] = artist_map.get(song.artist, 0) + 1
  print(artist_map)


if __name__ == '__main__':
  main()
