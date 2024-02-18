import time

from telegram import Bot
import requests

bot = Bot(token='6939188388:AAE8OkE1d6mYFzhiacyiDHXsW8KUGyZ0UmE')
chat_id = 6535524676
# bot.send_message(chat_id, game)
# current_game = requests.get(URL).json()['response']['players'][0].get('gameextrainfo')
# player = requests.get(URL).json()['response']['players'][0]['personaname']

MY_WEB_API_STEAM_KEY = '661927C6BCF9FC2D66EBAAE5722A1147'

GAME_VERDICTS = {
    'Counter-Strike 2': 'играет в Counter-Strike 2',
}

steam_accounts = {'Вурдалак': '76561198804859278',
                  '1mpalions': '76561198307436325',
                  'D1vens': '76561198840271910',
                  'VICTORINO DE SPASITTO': '76561198440426454'
                  }


def get_api_answer(steamID):
    url = (
        f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={MY_WEB_API_STEAM_KEY}&steamids={steamID}'
    )
    api_data = requests.get(url).json()['response']['players'][0]
    return api_data


def parse_status(nickname, game):
    if GAME_VERDICTS.get(game):
        verdict = GAME_VERDICTS[game]
    else:
        verdict = None
    return f'{nickname} {verdict}'


verdict_list = {
        'error': None,
    }


while True:
    try:
        for nickname, steamID in steam_accounts.items():
            api_response = get_api_answer(steamID)
            profile_status = api_response.get('personastate')
            current_game = api_response.get('gameextrainfo')
            if profile_status == 1 and current_game is not None:
                message = parse_status(nickname, current_game)
                if verdict_list.get(nickname) != message and message.split()[1] != 'None':
                    print(message)
                    verdict_list[nickname] = message
            else:
                if verdict_list.get(nickname):
                    del verdict_list[nickname]
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        if verdict_list['error'] != message:
            print(message)
    else:
        verdict_list['error'] = None
        print("Ожидаем 60 секунд")
    time.sleep(60)


# while True:
#     try:
#         response = get_api_answer()
#         current_game = response.get('gameextrainfo')
#         if current_game:
#             message = parse_status(current_game)
#             if verdict_list.get(current_game) != message:
#                 # send_message(bot, message)
#                 print(message)
#                 verdict_list[current_game] = message
#         else:
#             verdict_list = {}
#     except Exception as error:
#         message = f'Сбой в работе программы: {error}'
#         if verdict_list['error'] != message:
#             print(message)
#     else:
#         verdict_list['error'] = None
#         print("Ожидаем 60 секунд")
#     time.sleep(60)
