import os

import psycopg2

if __name__ == '__main__':
    try:
        connection = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            port=os.getenv('POSTGRES_PORT')
        )

        connection.autocommit = True

        cursor = connection.cursor()

        cursor.execute(
            '''CREATE TABLE "users" (
                "id" serial PRIMARY KEY,
                "user_id" BIGINT NOT NULL UNIQUE,
                "tg_name" TEXT NOT NULL DEFAULT 'Аноним');'''
        )

        cursor.execute(
            '''CREATE TABLE "steam_accounts" (
                "id" serial PRIMARY KEY,
                "user_id" BIGINT NOT NULL,
                "nickname" TEXT,
                "steam_id" BIGINT NOT NULL,
                FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
                UNIQUE("user_id","steam_id"));'''
        )

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS "game_tracking" (
                "id" serial PRIMARY KEY,
                "user_id" BIGINT NOT NULL,
                "game_id" BIGINT NOT NULL,
                "game_name"	TEXT NOT NULL,
                UNIQUE("user_id","game_id"),
                FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE);'''
        )

    except Exception as _ex:
        print('[INFO] Error while working with PostgreSQL', _ex)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print('[INFO] PostgreSQL connection closed')
