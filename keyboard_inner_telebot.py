import os
import asyncio

import requests
from telebot import types
from telebot import asyncio_filters  # , asyncio_helper
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from dotenv import load_dotenv

from db import BotDB
from validators import validate_game_url, validate_profile_url, logger
from parsers import get_game_id_from_name, get_player_name_and_id_from_url


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MY_WEB_API_STEAM_KEY = os.getenv('MY_WEB_API_STEAM_KEY')

bot = AsyncTeleBot(TELEGRAM_TOKEN, state_storage=StateMemoryStorage())

BotDB = BotDB('tg_steam_accs.db')


support_games = {'Counter-Strike 2': '730', 'Dota 2': '570',
                 'PUBG: BATTLEGROUNDS': '578080', 'Palworld': '1623730',
                 'Apex Legends™': '1172470', 'Rust': '252490'}


class GameStates(StatesGroup):
    game_url = State()


class ProfileStates(StatesGroup):
    profile_url = State()


def get_api_answer(steamID):
    url = ('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
           f'?key={MY_WEB_API_STEAM_KEY}&steamids={steamID}')
    api_response = requests.get(url).json()
    try:
        api_data = api_response['response']['players'][0]
    except Exception as error:
        logger.error(f'Исключение {error}. API вернул: {api_response}')
        api_data = False
    return api_data


class Treaker:
    work = False

    async def start_spam(self, chat_id, user_id, markup):
        verdict_list = {
            'error': None,
        }
        await bot.send_message(chat_id, 'Отслеживание начато',
                               reply_markup=markup)
        while self.work:
            try:
                user_games_id = [str(games[0]) for games
                                 in BotDB.get_all_user_games(user_id)]
                for nickname, steamID in BotDB.get_all_track_users(user_id):

                    api_response = get_api_answer(steamID)
                    profile_status = api_response.get('personastate')
                    current_game = api_response.get('gameextrainfo')
                    current_game_id = api_response.get('gameid')

                    if (profile_status == 1 and
                       current_game_id in user_games_id):
                        message = f'{nickname} играет в {current_game}'

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
                    logger.error(f'Ошибка в цикле {error}')
            else:
                verdict_list['error'] = None
            await asyncio.sleep(10)


@bot.message_handler(func=lambda msg: msg.text == 'Добавить свою')
async def add_myself_game(message):
    markup = types.ReplyKeyboardRemove()

    msg = ('Отправте ссылку на игру в стиме')
    await bot.set_state(message.from_user.id, GameStates.game_url,
                        message.chat.id)
    await bot.send_message(message.chat.id, msg,
                           reply_markup=markup)


@bot.message_handler(state=GameStates.game_url)
async def save_game_url(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_one_more = types.KeyboardButton('Добавить еще одну')
    menu = types.KeyboardButton('В меню')
    markup.add(add_one_more, menu)

    if validate_game_url(message.text):
        steam_url = message.text
        game_name = steam_url.split('/')[-2]
        game_id = steam_url.split('/')[-3]
        if (not BotDB.is_game_tracking(user_id, game_id)):
            BotDB.add_game_to_track(user_id, game_id, game_name)
            await bot.send_message(chat_id,
                                   f'{game_name} успешно добавлена'
                                   ' в отслеживаемые',
                                   reply_markup=markup)
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
    await bot.send_message(chat_id, 'Отправьте ссылку на '
                                    'профиль игрока стим',
                           reply_markup=markup)


@bot.message_handler(state=ProfileStates.profile_url)
async def save_profile_url(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_one_more = types.KeyboardButton('Добавить еще одного')
    menu = types.KeyboardButton('В меню')
    markup.add(add_one_more, menu)

    if validate_profile_url(message.text):
        for username, steam_id in get_player_name_and_id_from_url(
                message.text):
            if (not BotDB.is_user_tracking(user_id, steam_id)):
                BotDB.add_user_to_track(user_id, steam_id, username)
                await bot.send_message(chat_id,
                                       f'Игрок {username} добавлен '
                                       'в отслеживаемые',
                                       reply_markup=markup)
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

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if (not BotDB.user_exists(user_id)):
        BotDB.add_user(user_id, first_name)

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
    user_id = message.from_user.id
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

            if (not BotDB.is_game_tracking(user_id, game_id)):
                game_id = get_game_id_from_name(message.text)
                BotDB.add_game_to_track(user_id, game_id, message.text)
                await bot.send_message(chat_id, soobshenie,
                                       reply_markup=markup)
            else:
                await bot.send_message(chat_id, 'Эта игра уже отслеживается',
                                       reply_markup=markup)

        elif message.text == 'Удалить игру':
            if BotDB.get_all_user_games(user_id):
                btns = []
                for id, game in BotDB.get_all_user_games(user_id):
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
            if BotDB.get_all_user_games(user_id):
                msg = ''.join(f'✅{game[1]}\n' for game
                              in BotDB.get_all_user_games(user_id))
                await bot.send_message(chat_id, msg)
            else:
                await bot.send_message(chat_id, 'У вас нет отслеживаемых игр')

        elif message.text == 'Начать отслеживание':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            stop_track = types.KeyboardButton('Прекратить отслеживане')
            markup.add(stop_track)
            Treaker.work = True
            asyncio.create_task(Treaker.start_spam(Treaker, chat_id,
                                                   user_id, markup))

        elif message.text == 'Прекратить отслеживане':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            menu = types.KeyboardButton('В меню')
            markup.add(menu)
            Treaker.work = False
            await bot.send_message(chat_id, 'Отслеживание остановлено',
                                   reply_markup=markup)

        elif message.text == 'Мои игроки':
            track_users = BotDB.get_all_track_users(user_id)
            if len(track_users):
                msg = ''.join(f'✅{acc[0]}\n' for acc in track_users)
                await bot.send_message(chat_id, msg)
            else:
                await bot.send_message(chat_id,
                                       'У вас нет отслеживаемых игроков')

        elif message.text == 'Удалить игрока':
            track_users = BotDB.get_all_track_users(user_id)
            if len(track_users):
                btns = []
                for name, id in track_users:
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
async def delete_game_or_user(id):
    user_id = id.from_user.id
    if BotDB.is_game_tracking(user_id, id.data):
        game_name = BotDB.get_game_name_by_id(user_id, id.data)
        BotDB.remove_game_from_track(user_id, id.data)
        await bot.send_message(
            chat_id=id.message.chat.id,
            text=f'{game_name} удалена из отслеживания')
    elif BotDB.is_user_tracking(user_id, id.data):
        user = BotDB.get_nickname_by_steam_id(user_id, id.data)
        BotDB.remove_user_from_track(user_id, id.data)
        await bot.send_message(
            chat_id=id.message.chat.id,
            text=f'{user} удален(a) из отслеживания')


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

# asyncio_helper.proxy = 'http://proxy.server:3128'

asyncio.run(bot.polling())
