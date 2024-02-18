import os
import asyncio

import requests
from telebot import types
from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from dotenv import load_dotenv

from validators import validate_game_url, validate_profile_url
from parsers import get_game_id_from_name, get_player_name_and_id_from_url


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MY_WEB_API_STEAM_KEY = os.getenv('MY_WEB_API_STEAM_KEY')

# GAME_VERDICTS = {
#     'Counter-Strike 2': 'играет в Counter-Strike 2',
# }

GAME_VERDICTS = {}
# steam_accounts = {'Вурдалак': '76561198804859278',
#                   '1mpalions': '76561198307436325',
#                   'D1vens': '76561198840271910',
#                   'VICTORINO DE SPASITTO': '76561198440426454'
#                   }

steam_accounts = {}

bot = AsyncTeleBot(TELEGRAM_TOKEN, state_storage=StateMemoryStorage())

support_games = {'Counter-Strike 2': '730', 'Dota 2': '570',
                 'PUBG: BATTLEGROUNDS': '578080', 'Palworld': '1623730',
                 'Apex Legends™': '1172470', 'Rust': '252490'}

game_tracking = {}


class GameStates(StatesGroup):
    game_url = State()


class ProfileStates(StatesGroup):
    profile_url = State()


def get_api_answer(steamID):
    url = ('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
           f'?key={MY_WEB_API_STEAM_KEY}&steamids={steamID}')
    api_data = requests.get(url).json()['response']['players'][0]
    return api_data


def parse_status(nickname, game):
    if GAME_VERDICTS.get(game):
        verdict = GAME_VERDICTS[game]
    else:
        verdict = None
    return f'{nickname} {verdict}'


class Treaker:
    work = False

    async def start_spam(self, chat_id, markup):
        verdict_list = {
            'error': None,
        }
        await bot.send_message(chat_id, 'Отслеживание начато',
                               reply_markup=markup)
        while self.work:
            try:
                for nickname, steamID in steam_accounts.items():
                    api_response = get_api_answer(steamID)
                    profile_status = api_response.get('personastate')
                    current_game = api_response.get('gameextrainfo')
                    if profile_status == 1 and current_game is not None:
                        message = parse_status(nickname, current_game)
                        if (verdict_list.get(nickname) != message
                           and message.split()[1] != 'None'):
                            await bot.send_message(chat_id, message)
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
                print("Ожидаем 5 секунд")
            await asyncio.sleep(5)


@bot.message_handler(func=lambda msg: msg.text == 'Добавить свою')
async def add_myself_game(message):
    markup = types.ReplyKeyboardRemove()

    msg = ('Отправь ссылку на игру в стиме')
    await bot.set_state(message.from_user.id, GameStates.game_url,
                        message.chat.id)
    await bot.send_message(message.chat.id, msg,
                           reply_markup=markup)


@bot.message_handler(state=GameStates.game_url)
async def save_game_url(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_one_more = types.KeyboardButton('Добавить еще одну')
    menu = types.KeyboardButton('В меню')
    markup.add(add_one_more, menu)

    if validate_game_url(message.text):
        steam_url = message.text
        game_name = steam_url.split('/')[-2]
        game_id = steam_url.split('/')[-3]
        if game_id not in game_tracking:
            game_tracking[game_id] = game_name
            await bot.send_message(chat_id,
                                   f'{game_name} успешно добалвена'
                                   ' в отслеживаемые',
                                   reply_markup=markup)
            print(game_tracking)
        else:
            await bot.send_message(chat_id, 'Эта игра уже отслеживается',
                                   reply_markup=markup)
    else:
        await bot.send_message(chat_id, 'Такой игры нет или ссылка'
                               ' указана не верно',
                               reply_markup=markup)
    await bot.delete_state(message.from_user.id, chat_id)


@bot.message_handler(func=lambda msg: msg.text == 'Добавить игрока'
                     or msg.text == 'Добавить еще одного')
async def add_friend_profile(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardRemove()

    await bot.set_state(message.from_user.id, ProfileStates.profile_url,
                        chat_id)
    await bot.send_message(chat_id, 'Отправь ссылку на '
                                    'профиль игрока стим',
                           reply_markup=markup)


@bot.message_handler(state=ProfileStates.profile_url)
async def save_profile_url(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_one_more = types.KeyboardButton('Добавить еще одного')
    menu = types.KeyboardButton('В меню')
    markup.add(add_one_more, menu)

    if validate_profile_url(message.text):
        for name, id in get_player_name_and_id_from_url(message.text):
            if name not in steam_accounts:
                steam_accounts[name] = id
                await bot.send_message(chat_id,
                                       f'Игрок {name} добавлен '
                                       'в отслеживаемые',
                                       reply_markup=markup)
                print(steam_accounts)
            else:
                await bot.send_message(chat_id, 'Этот игрок уже отслеживается',
                                       reply_markup=markup)
    else:
        await bot.send_message(chat_id,
                               'Такого аккаунта нет или '
                               'ссылка указана не верно',
                               reply_markup=markup)
    await bot.delete_state(message.from_user.id, chat_id)


@bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton('В меню')
    markup.add(menu)

    msg = ('Привет, этот бот создан для того, чтобы присылать тебе '
           'уведомление, когда твои друзья заходят в игры стима. '
           'Ты можешь гулять, работать или просто валяться на '
           'диване, когда тебе приходит уведомление на телефон, '
           'что твой друг собирается сходить катку в КС или ДОТУ 😉')
    await bot.send_message(message.chat.id, msg,
                           reply_markup=markup)


@bot.message_handler(content_types=['text'])
async def bot_message(message):
    chat_id = message.chat.id
    if message.chat.type == 'private':
        if message.text == 'В меню':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            add_game = types.KeyboardButton('Добавить игру')
            delete_game = types.KeyboardButton('Удалить игру')
            games_list = types.KeyboardButton('Мои игры')
            add_player = types.KeyboardButton('Добавить игрока')
            delete_account = types.KeyboardButton('Удалить игрока')
            accounts_list = types.KeyboardButton('Мои игроки')
            start_track = types.KeyboardButton('Начать отслеживание')

            markup.add(add_game, delete_game, games_list, add_player,
                       delete_account, accounts_list, start_track)
            await bot.send_message(message.chat.id,
                                   'Здесь ты можешь настроить '
                                   'отслеживаение игр',
                                   reply_markup=markup)

        elif (message.text == 'Добавить игру'
              or message.text == 'Добавить еще одну'):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cs2 = types.KeyboardButton('Counter-Strike 2')
            dota2 = types.KeyboardButton('Dota 2')
            pubg = types.KeyboardButton('PUBG: BATTLEGROUNDS')
            palworld = types.KeyboardButton('Palworld')
            apex = types.KeyboardButton('Apex Legends™')
            rust = types.KeyboardButton('Rust')
            own = types.KeyboardButton('Добавить свою')
            menu = types.KeyboardButton('В меню')
            markup.add(cs2, dota2, pubg, palworld, apex, rust, own, menu)

            msg = 'Выбери игру из списка или добавьте свою'
            if message.text == 'Добавить еще одну':
                await bot.send_message(chat_id, 'Выбери игру',
                                       reply_markup=markup)
            else:
                await bot.send_message(chat_id, msg,
                                       reply_markup=markup)

        elif message.text in support_games:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            add_one_more = types.KeyboardButton('Добавить еще одну')
            menu = types.KeyboardButton('В меню')
            markup.add(add_one_more, menu)

            soobshenie = f'{message.text} добавлен(а) в отслеживаемые игры'
            game_id = support_games[message.text]

            if game_id not in game_tracking:
                game_id = get_game_id_from_name(message.text)
                game_tracking[game_id] = message.text
                GAME_VERDICTS[message.text] = f'играет в {message.text}'
                print(game_tracking)
                print(GAME_VERDICTS)
                await bot.send_message(chat_id, soobshenie,
                                       reply_markup=markup)
            else:
                await bot.send_message(chat_id, 'Эта игра уже отслеживается',
                                       reply_markup=markup)

        elif message.text == 'Удалить игру':
            if game_tracking:
                btns = []
                for id, game in game_tracking.items():
                    btns.append(types.InlineKeyboardButton(text=f'❌{game}',
                                                           callback_data=id))
                markup = types.InlineKeyboardMarkup()
                markup.add(*btns)
                await bot.send_message(chat_id,
                                       'Выберите игру, которую '
                                       'хотите удалить:',
                                       reply_markup=markup)
            else:
                await bot.send_message(chat_id,
                                       'У вас нет отслеживаемых игр')

        elif message.text == 'Мои игры':
            if game_tracking:
                msg = ''.join(f'✅{game}\n' for game in game_tracking.values())
                await bot.send_message(chat_id, msg)
            else:
                await bot.send_message(chat_id, 'У вас нет отслеживаемых игр')

        elif message.text == 'Начать отслеживание':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            stop_track = types.KeyboardButton('Прекратить отслеживане')
            markup.add(stop_track)
            Treaker.work = True
            asyncio.create_task(Treaker.start_spam(Treaker, chat_id, markup))

        elif message.text == 'Прекратить отслеживане':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            menu = types.KeyboardButton('В меню')
            markup.add(menu)
            Treaker.work = False
            await bot.send_message(chat_id, 'Отслеживание остановлено',
                                   reply_markup=markup)

        elif message.text == 'Мои игроки':
            if steam_accounts:
                msg = ''.join(f'✅{acc}\n' for acc in steam_accounts.keys())
                await bot.send_message(chat_id, msg)
            else:
                await bot.send_message(chat_id,
                                       'У вас нет отслеживаемых игроков')

        elif message.text == 'Удалить игрока':
            if steam_accounts:
                btns = []
                for name, id in steam_accounts.items():
                    btns.append(types.InlineKeyboardButton(text=f'❌{name}',
                                                           callback_data=id))
                markup = types.InlineKeyboardMarkup()
                markup.add(*btns)
                await bot.send_message(chat_id,
                                       'Выберите игрока, которого '
                                       'хотите удалить:',
                                       reply_markup=markup)
            else:
                await bot.send_message(chat_id,
                                       'У вас нет отслеживаемых игроков')


@bot.callback_query_handler(func=lambda call: True)
async def delete_game(id):
    if id.data in game_tracking:
        del_game = game_tracking.pop(id.data)
        await bot.send_message(
            chat_id=id.message.chat.id,
            text=f'{del_game} удалена из отслеживания')
    elif id.data in steam_accounts.values():
        invert_steam_accs = {j: i for i, j in steam_accounts.items()}
        ids = invert_steam_accs[id.data]
        del steam_accounts[ids]
        await bot.send_message(
            chat_id=id.message.chat.id,
            text=f'{ids} удален(a) из отслеживания')


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())


asyncio.run(bot.polling())
