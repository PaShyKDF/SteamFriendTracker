import requests


storefront_api_url = ('http://store.steampowered.com/api/'
                      'storesearch/?term={}&l=english&cc=US')

findsteamid_api = 'https://api.findsteamid.com/steam/api/summary/{}'

friends_list_by_id = 'https://api.findsteamid.com/steam/api/friends/{}'


def get_game_id_from_name(game):
    return str(requests.get(storefront_api_url.format(game)).json()['items']
               [0]['id'])


if __name__ == '__main__':
    pass
