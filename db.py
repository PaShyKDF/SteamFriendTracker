import os
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class BotDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            port=os.getenv('POSTGRES_PORT')
        )
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        return bool(len(self.cursor.fetchall()))

    def add_user(self, user_id, tg_name):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO users (user_id, tg_name) VALUES (%s, %s)", (user_id, tg_name))
        return self.conn.commit()

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        try:
            self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
            return self.cursor.fetchone()[0]
        except TypeError:
            print('Такого пользователя нет в базе данных')

    def does_user_have_games(self, user_id):
        """Проверяем, есть ли у пользователя отслеживаемые игры"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT Count(*) FROM game_tracking WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0] != 0

    def is_game_tracking(self, user_id, game_id):
        """Проверяем, отслеживает ли пользователь игру"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT game_name FROM game_tracking WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        result = bool(len(self.cursor.fetchall()))
        return result

    def add_game_to_track(self, user_id, game_id, game_name):
        """Добавляем игру в отслеживаемые"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("INSERT INTO game_tracking (user_id, game_id, game_name) VALUES (%s, %s, %s)", (user_id, game_id, game_name))
        return self.conn.commit()

    def get_all_user_games(self, user_id):
        """Получаем все игры пользователя"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT game_id, game_name FROM game_tracking WHERE user_id = %s", (user_id,))
        # self.cursor.execute('CREATE INDEX user_id_index ON "game_tracking"("user_id");')
        # self.cursor.execute("DROP INDEX user_id_index;")
        return self.cursor.fetchall()

    def get_game_name_by_id(self, user_id, game_id):
        """Получаем название игры по ее id"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT game_name FROM game_tracking WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        return self.cursor.fetchone()[0]

    def remove_game_from_track(self, user_id, game_id):
        """Удаляем игру из отслеживаемых"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("DELETE FROM game_tracking WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        return self.conn.commit()

    def is_user_tracking(self, user_id, steam_id):
        """Проверяем, отслеживает ли пользователь игрока"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT steam_id FROM steam_accounts WHERE user_id = %s AND steam_id = %s", (user_id, steam_id))
        result = bool(len(self.cursor.fetchall()))
        return result
        # self.cursor.execute('CREATE INDEX user_id_index ON "steam_accounts"("user_id");')
        # self.cursor.execute('CREATE INDEX steam_id_index ON "steam_accounts"("steam_id");')
        # self.cursor.execute("EXPLAIN SELECT steam_id FROM steam_accounts WHERE user_id = %s AND steam_id = %s", (user_id, steam_id))
        # return self.cursor.fetchone()

    def add_user_to_track(self, user_id, steam_id, nickname):
        """Добавляем игрока в отслеживаемые"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("INSERT INTO steam_accounts (user_id, nickname, steam_id) VALUES (%s, %s, %s)", (user_id, nickname, steam_id))
        return self.conn.commit()

    def get_all_track_users(self, user_id):
        """Получаем всех игроков пользователя"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT nickname, steam_id FROM steam_accounts WHERE user_id = %s", (user_id,))
        return self.cursor.fetchall()

    def remove_user_from_track(self, user_id, steam_id):
        """Удаляем игрока из отслеживаемых"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("DELETE FROM steam_accounts WHERE user_id = %s AND steam_id = %s", (user_id, steam_id))
        return self.conn.commit()

    def get_nickname_by_steam_id(self, user_id, steam_id):
        """Получаем ник игрока по его стим id"""
        user_id = self.get_user_id(user_id)
        self.cursor.execute("SELECT nickname FROM steam_accounts WHERE user_id = %s AND steam_id = %s", (user_id, steam_id))
        return self.cursor.fetchone()[0]

    def is_game_verdict(self, game_id):
        self.cursor.execute("SELECT * FROM game_verdicts WHERE game_id = %s", (game_id,))
        return bool(len(self.cursor.fetchall()))


if __name__ == '__main__':
    time_start = time.time()
    BotDB = BotDB()
    print(BotDB.is_user_tracking(6535524676, 76561198331314442))
    time_stop = time.time()
    print(time_stop - time_start)


# import sqlite3


# class BotDB:
#     def __init__(self, db_file):
#         self.conn = sqlite3.connect(db_file)
#         self.cursor = self.conn.cursor()

#     def user_exists(self, user_id):
#         """Проверяем, есть ли юзер в базе"""
#         result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
#         return bool(len(result.fetchall()))

#     def add_user(self, user_id, tg_name):
#         """Добавляем юзера в базу"""
#         self.cursor.execute("INSERT INTO `users` (`user_id`, `tg_name`) VALUES (?, ?)", (user_id, tg_name))
#         return self.conn.commit()

#     def get_user_id(self, user_id):
#         """Достаем id юзера в базе по его user_id"""
#         try:
#             result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
#             return result.fetchone()[0]
#         except TypeError:
#             print('Такого пользователя нет в базе данных')

#     def does_user_have_games(self, user_id):
#         """Проверяем, есть ли у пользователя отслеживаемые игры"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT Count(*) FROM game_tracking WHERE user_id = ?", (user_id,))
#         return result.fetchone()[0] != 0

#     def is_game_tracking(self, user_id, game_id):
#         """Проверяем, отслеживает ли пользователь игру"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT game_name FROM game_tracking WHERE user_id = ? AND game_id = ?", (user_id, game_id))
#         res = bool(len(result.fetchall()))
#         return res

#     def add_game_to_track(self, user_id, game_id, game_name):
#         """Добавляем игру в отслеживаемые"""
#         user_id = self.get_user_id(user_id)
#         self.cursor.execute("INSERT INTO `game_tracking` (`user_id`, `game_id`, `game_name`) VALUES (?, ?, ?)", (user_id, game_id, game_name))
#         return self.conn.commit()

#     def get_all_user_games(self, user_id):
#         """Получаем все игры пользователя"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT game_id, game_name FROM game_tracking WHERE user_id = ?", (user_id,))
#         return result.fetchall()

#     def get_game_name_by_id(self, user_id, game_id):
#         """Получаем название игры по ее id"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT game_name FROM game_tracking WHERE user_id = ? AND game_id = ?", (user_id, game_id))
#         return result.fetchone()[0]

#     def remove_game_from_track(self, user_id, game_id):
#         """Удаляем игру из отслеживаемых"""
#         user_id = self.get_user_id(user_id)
#         self.cursor.execute("DELETE FROM game_tracking WHERE user_id = ? AND game_id = ?", (user_id, game_id))
#         return self.conn.commit()

#     def is_user_tracking(self, user_id, steam_id):
#         """Проверяем, отслеживает ли пользователь игрока"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT steam_id FROM steam_accounts WHERE user_id = ? AND steam_id = ?", (user_id, steam_id))
#         res = bool(len(result.fetchall()))
#         return res

#     def add_user_to_track(self, user_id, steam_id, nickname):
#         """Добавляем игрока в отслеживаемые"""
#         user_id = self.get_user_id(user_id)
#         self.cursor.execute("INSERT INTO steam_accounts (user_id, nickname, steam_id) VALUES (?, ?, ?)", (user_id, nickname, steam_id))
#         return self.conn.commit()

#     def get_all_track_users(self, user_id):
#         """Получаем всех игроков пользователя"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT nickname, steam_id FROM steam_accounts WHERE user_id = ?", (user_id,))
#         return result.fetchall()

#     def remove_user_from_track(self, user_id, steam_id):
#         """Удаляем игрока из отслеживаемых"""
#         user_id = self.get_user_id(user_id)
#         self.cursor.execute("DELETE FROM steam_accounts WHERE user_id = ? AND steam_id = ?", (user_id, steam_id))
#         return self.conn.commit()

#     def get_nickname_by_steam_id(self, user_id, steam_id):
#         """Получаем ник игрока по его стим id"""
#         user_id = self.get_user_id(user_id)
#         result = self.cursor.execute("SELECT nickname FROM steam_accounts WHERE user_id = ? AND steam_id = ?", (user_id, steam_id))
#         return result.fetchone()[0]

#     def is_game_verdict(self, game_id):
#         result = self.cursor.execute("SELECT * FROM game_verdicts WHERE game_id = ?", (game_id,))
#         return bool(len(result.fetchall()))


# if __name__ == '__main__':
#     BotDB = BotDB('tg_steam_accs.db')
#     # BotDB.add_game_to_track(6535524676, 730, 'Counter-Strike_2')
#     # print(BotDB.is_game_tracking(user_id=6535524676, game_id=730))
#     # print(BotDB.does_user_have_games(6535524676))
#     # print(BotDB.get_all_user_games(6535524676))
#     # print(len(BotDB.get_all_track_users(6535524676)))
#     # print(BotDB.get_nickname_by_steam_id(user_id=6535524676, steam_id=76561198331314442))
#     print(BotDB.is_game_verdict(game_id=730))
