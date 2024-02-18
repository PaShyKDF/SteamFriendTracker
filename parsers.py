import requests

from validators import validate_profile_url


storefront_api_url = ('http://store.steampowered.com/api/'
                      'storesearch/?term={}&l=english&cc=US')

findsteamid_api = 'https://api.findsteamid.com/steam/api/summary/{}'

friends_list_by_id = 'https://api.findsteamid.com/steam/api/friends/{}'


def get_game_id_from_name(game):
    return str(requests.get(storefront_api_url.format(game)).json()['items']
               [0]['id'])


def get_player_name_and_id_from_url(url):
    if validate_profile_url(url):
        id = url.rstrip('/').split('/')[-1]
        responce = requests.get(findsteamid_api.format(id)).json()[0]
        return ((responce['personaname'], responce['steamid']),)


# def get_player_data_from_url(url):
#     if url.startswith('https://steamcommunity.com/id/'):
#         id = url.split('/')[-1]
#         if id.isdigit():
#             return id
#         else:
#             return (requests.get(findsteamid_api.format(id))
#                     .json()[0]['steamid'])


if __name__ == '__main__':
    # print(type(get_game_id_from_name('Counter-Strike')))

    print(get_player_name_and_id_from_url
          ('https://steamcommunity.com/id/usiless')
          )

    # print(requests.get('https://api.findsteamid.com/steam/api/summary/d1vens111').json())
