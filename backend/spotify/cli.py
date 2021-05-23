import click

from spotify import service, config, user, data, api


@click.group()
def main():
  pass


@main.command()
def replace_playlist():
  client_credentials = config.get_client_credentials()
  user_data = user.get_user_data()
  assert user_data.token
  user_resource_api_client = api.UserResourceApiClient(client_credentials,
                                                       user_data.token)
  api_client = api.ApiClient(client_credentials)
  ranking_client = data.RankingClient()
  ranking_service = service.RankingService(api_client, ranking_client)

  api_service = service.UserService(
    user_data, user_resource_api_client, ranking_service)
  api_service.replace_playlist()


if __name__ == '__main__':
  main()
