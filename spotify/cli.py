import click

from spotify import service, config, user, data


@click.group()
def main():
  pass


@main.command()
def replace_playlist():
  secret = config.get_api_client_secret()
  user_data = user.get_user_data()
  ranking_client = data.RankingClient()

  api_service = service.ApiService(user_data, secret, ranking_client)
  api_service.replace_playlist()


if __name__ == '__main__':
  main()
