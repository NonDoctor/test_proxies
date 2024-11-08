import os
import sqlite3
from typing import Optional

import aiosqlite
from loguru import logger

from models import Proxy


class Storage:
    def __init__(self, db_path="storage.db"):
        self.path = db_path
        self.connection = None  # Переменная для хранения соединения с БД

        """Синхронная инициализация базы данных и создание таблицы, если её нет."""
        # Проверяем наличие файла базы данных
        if not os.path.exists(self.path):
            logger.debug(f"База данных не найдена, создаем новую: {self.path}")
        else:
            logger.debug(f"База данных найдена")

        try:
            # Синхронное создание базы данных и таблицы, если её нет
            with sqlite3.connect(self.path) as conn:
                conn.cursor().execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_proxy (
                        email TEXT PRIMARY KEY,
                        proxy_ip TEXT,
                        proxy_port TEXT,
                        proxy_user TEXT,
                        proxy_pass TEXT,
                        UNIQUE(proxy_ip, proxy_port, proxy_user, proxy_pass)
                    )
                """
                )
                conn.commit()
                logger.info("Таблица успешно создана или уже существует.")

        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблицы: {e}")

    async def connect(self):
        """Асинхронное подключение к базе данных."""
        if self.connection is None:
            try:
                self.connection = await aiosqlite.connect(self.path)
                logger.info(f"Подключение к базе данных {self.path} установлено.")
            except aiosqlite.Error as e:
                logger.error(f"Ошибка при подключении к базе данных: {e}")
                raise

    async def disconnect(self):
        """Асинхронное отключение от базы данных."""
        if self.connection:
            try:
                await self.connection.close()
                logger.info(f"Отключение от базы данных {self.path} выполнено.")
                self.connection = None
            except aiosqlite.Error as e:
                logger.error(f"Ошибка при отключении от базы данных: {e}")
                raise

    # Асинхронное обновление или добавление связки email и proxy в базу данных
    async def update_user_proxy(self, email, proxy: Optional[Proxy]):
        try:

            await self.connection.execute(
                """
                INSERT OR REPLACE INTO user_proxy (email, proxy_ip, proxy_port, proxy_user, proxy_pass)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    (email, None, None, None, None)
                    if proxy is None
                    else (email, proxy.ip, proxy.port, proxy.username, proxy.password)
                ),
            )
            await self.connection.commit()
            logger.info(f"Данные для {email} успешно обновлены в базе данных.")
        except aiosqlite.Error as e:
            logger.error(f"Ошибка при обновлении данных для {email}: {e}")
            raise

    # Асинхронное получение прокси для пользователя
    async def get_user_proxy(self, email: str) -> Optional[Proxy]:
        try:
            cursor = await self.connection.execute(
                "SELECT proxy_ip, proxy_port, proxy_user, proxy_pass FROM user_proxy WHERE email = ?",
                (email,),
            )
            proxy = await cursor.fetchone()
            if proxy:
                logger.info(f"Прокси для {email} получено из базы данных.")
                return Proxy(proxy[0], proxy[1], proxy[2], proxy[3])
            else:
                logger.warning(f"Прокси для {email} не найдено.")
                return None
        except aiosqlite.Error as e:
            logger.error(f"Ошибка при получении данных для {email}: {e}")
            raise
