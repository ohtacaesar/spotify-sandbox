import unittest

from spotify import api, config, data


class ApiTest(unittest.TestCase):

  def test_invalid_secrets(self):
    credentials = api.ClientCredentials('test_id', 'test_secret')
    token = api.AuthorizationCodeFlowToken(
      'test',
      "Bearer",
      "playlist-read-private playlist-modify-private playlist-modify-public",
      3600,
      "test"
    )

    client = api.UserResourceApiClient(credentials, token)
    client.get_current_user_playlists()

  def test_get_several_tracks(self):
    ranking = data.RankingClient()
    song = ranking.get_song_list()[0]
    credentials = config.get_client_credentials()

    client = api.ApiClient(credentials)
    tracks = client.get_several_tracks([song.id])
    self.assertTrue(tracks)
    track = tracks[0]
    print(track.id, track.name)


if __name__ == '__main__':
  unittest.main()
