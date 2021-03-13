import unittest

from spotify import api


class ApiTest(unittest.TestCase):

  def test_invalid_secrets(self):
    token = api.Token(
      'test',
      "Bearer",
      "playlist-read-private playlist-modify-private playlist-modify-public",
      3600,
      "test"
    )

    client = api.ApiClient('test_id', 'test_secret', token)
    client.fetch_playlists()


if __name__ == '__main__':
  unittest.main()
