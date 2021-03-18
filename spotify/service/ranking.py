from dataclasses import dataclass
from typing import List

from spotify import data, api


@dataclass()
class RankingService:
  __api_client: api.ApiClient
  __ranking_client: data.RankingClient
  __tracks = []
  __artists = []

  def _refresh(self):
    self.__tracks = []
    song_list = self.__ranking_client.get_song_list()
    ids = [song.id for song in song_list]
    for i in range(4):
      self.__tracks.extend(
        self.__api_client.get_several_tracks(ids[i * 50:(i + 1) * 50]))
    self.__artists = []
    for track in self.__tracks:
      for artist in track.artists:
        if artist not in self.__artists:
          self.__artists.append(artist)

  def get_tracks(self) -> List[api.Track]:
    if not self.__tracks:
      self._refresh()

    return self.__tracks

  def get_artists(self) -> List[api.Artist]:
    if not self.__tracks:
      self._refresh()

    return self.__artists
