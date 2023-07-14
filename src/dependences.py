import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


class ConnectionDataBase():
    def __init__(self):
        self.connection = None

    async def __aenter__(self):
        try:
            self.connection = await asyncpg.connect(
                host=os.getenv('DB_HOST', default='db'),
                port=os.getenv('DB_PORT', default='5432'),
                user=os.getenv('POSTGRES_USER', default='postgres'),
                database=os.getenv('DB_NAME', default='postgres'),
                password=os.getenv('POSTGRES_PASSWORD', default='222SuperData')
            )

        except asyncpg.ConnectionDoesNotExistError:
            raise RuntimeError(
                'Не удалось подключится к базе данных, проверьте данные')
        return self.connection

    async def __aexit__(self, exc_type, exc, tb):
        await self.connection.close()


async def get_connection():
    async with ConnectionDataBase() as connection:
        yield connection


async def create_db():
    async with ConnectionDataBase() as connection:
        await connection.execute("""CREATE TABLE IF NOT EXISTS items(
                id serial PRIMARY KEY,
                name varchar(150) NOT NULL UNIQUE,
                value JSONB,
                date_update TIMESTAMP WITH TIME ZONE
                )""")
