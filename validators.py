import sys
import logging

import requests


LOGGER_FORMAT = logging.Formatter(
    '%(asctime)s %(filename)s %(funcName)s '
    '[%(levelname)s] line(%(lineno)s): %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(LOGGER_FORMAT)

file_handler = logging.FileHandler('steam_logs.log', mode='a')
file_handler.setFormatter(LOGGER_FORMAT)
file_handler.setLevel(logging.WARNING)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def validate_game_url(url: str) -> bool:
    if url.startswith('https://store.steampowered.com/app/'):
        game_id = url.split('/')[-3]
        responce = requests.get(
            'https://store.steampowered.com/api/appdetails?'
            f'appids={game_id}&cc=tw'
        ).json()
        try:
            responce = responce[game_id]['success']
            logger.info('Ссылка на игру валидна')
        except TypeError:
            msg = f'Пользователь отправил ссылку с некорректным id игры {url}'
            logger.warning(msg)
            responce = False
        except KeyError:
            msg = f'Пользоватеть отправил слишком длинный id игры {url}'
            logger.warning(msg)
            responce = False
        return bool(responce)
    logger.warning(f'Ссылка полностью не валидна {url}')
    return False


def validate_profile_url(url: str) -> bool:
    if (url.startswith('https://steamcommunity.com/id/')
            or url.startswith('https://steamcommunity.com/profiles/')):
        profile_id = url.rstrip('/').split('/')[-1]
        responce = requests.get(
            f'https://api.findsteamid.com/steam/api/summary/{profile_id}'
        ).json()
        if responce:
            logger.info('Ссылка на профиль стим валидна')
            return True
        else:
            logger.warning(f'Данный профиль не доступен по ссылке {url}')
            return False
    logger.warning(f'Пользователь вместо ссылки отправил {url}')
    return False


d = {'730': 'Counter-Strike 2', '570': 'Dota 2'}

if __name__ == '__main__':
    print(validate_game_url(
        'https://store.steampowered.com/app/0/Egg/'))
    # print(validate_profile_url('https://steamcommunity.com/id/DIDIiDIDIDI/'))

    # for i, j in d.items():
    #     print(i, j)
