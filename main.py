import os
import asyncio
import aiohttp
from loguru import logger
from models import User, Proxy
from storage import Storage

# Параметры
PROXY_TEST_URL = "https://httpbin.org/ip"  # Заглушка URL для тестирования прокси

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "log.txt")

# Создаем папку, если она не существует
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Настройка логирования
logger.add(
    LOG_FILE,
    rotation="1 hour",  # Архивируем логи каждый час
    retention="7 days",  # Храним логи 7 дней
    compression="zip",  # Архивируем логи в формате zip
    encoding="utf-8",  # Кодировка файлов
    level="DEBUG",
)  # Уровень логирования

storage = Storage()
proxies = [proxy for proxy in Proxy.from_txt("proxies.txt")]


# Асинхронная проверка валидности прокси
async def is_proxy_valid(proxy: Proxy):
    """Проверяет валидность прокси через запрос к PROXY_TEST_URL"""

    proxy_url = f"http://{proxy.ip}:{proxy.port}"
    proxy_auth = (
        aiohttp.BasicAuth(proxy.username, proxy.password)
        if proxy.username and proxy.password
        else None
    )

    try:
        async with aiohttp.ClientSession() as session:
            # Пытаемся сделать запрос через прокси
            async with session.get(
                PROXY_TEST_URL, proxy=proxy_url, proxy_auth=proxy_auth, timeout=10
            ) as response:
                # Если код состояния 200, значит прокси валидна
                if response.status == 200:
                    data = await response.json()
                    logger.debug(
                        f"Прокси {proxy} успешно прошла тест, IP: {data['origin']}"
                    )
                    return True
                else:
                    logger.warning(f"Прокси {proxy} вернула статус {response.status}.")
                    return False
    except Exception as e:
        logger.error(f"Ошибка при проверке прокси {proxy}: {e}")
        return False


async def process(user: User):
    """Запускает проверку прокси для пользователя каждую минуту."""
    while True:
        # Получаем текущий прокси для пользователя
        proxy = await storage.get_user_proxy(user.email)
        if proxy is not None and proxy in proxies:
            proxies.remove(proxy)

        # Если прокси недоступен, присваиваем None, останавливаем цикл
        if proxy and not await is_proxy_valid(proxy):
            logger.info(f"Прокси {proxy} для {user.email} невалиден, удаляем.")
            try:
                await storage.update_user_proxy(user.email, None)

            except:
                pass
            finally:
                proxy = None

        # Если прокси None, назначаем новый проверенный прокси
        if proxy is None:
            for p in proxies:
                if await is_proxy_valid(p):
                    try:
                        await storage.update_user_proxy(user.email, p)
                        proxy = p
                        logger.info(f"Назначен новый прокси {proxy} для {user.email}")
                        break
                    except:
                        pass
                else:
                    logger.warning(f"Не валидный прокси {p} - удаляем из списка")
                    if p in proxies:
                        proxies.remove(p)

        # Если прокси не найден, пропускаем итерацию
        if proxy is None:
            logger.warning(f"Нет доступного прокси для {user.email}, пропускаем.")
            break

        # Логируем текущую связку
        logger.info(f"{user.email} - {str(proxy)}")
        await asyncio.sleep(5)  # Ожидание в 1 минуту


async def main():
    # Подключаемся к базе данных
    await storage.connect()
    try:
        tasks = []  # Список для хранения задач
        for user in User.from_txt("users.txt"):
            task = asyncio.create_task(
                process(user)
            )  # Создаем задачу для каждого пользователя
            tasks.append(task)

        # Ожидаем завершения всех задач
        await asyncio.gather(*tasks)
    except Exception as e:
        print(e)
    finally:
        # Отключение от базы данных
        await storage.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
