# Описание
Этот проект предназначен для обработки пользователей и их прокси-серверов, с возможностью проверки валидности прокси и хранения связки пользователей и прокси в базе данных. Процесс работы включает проверку прокси через HTTP-запросы, хранение данных в SQLite, а также многократную попытку присвоения новых прокси, если текущий оказался невалидным.

Проект использует асинхронность для повышения производительности и масштабируемости. Логирование происходит в отдельную папку с архивированием старых логов.

## Пример использования

#### Настройка и запуск через Docker Compose
Для простоты развертывания и настройки проекта можно использовать Docker Compose. В docker-compose.yml уже прописаны все необходимые параметры для запуска контейнеров. Убедитесь, что у вас установлен Docker и Docker Compose.

Склонируйте репозиторий.
Запустите команду:
```bash
Копировать код
docker-compose up --build -d
```
Это создаст контейнер для проекта и запустит его. Контейнер будет настроен для работы с асинхронными задачами и логированием.

#### Запуск без Docker Compose
Если вы не хотите использовать Docker, просто запускайте проект с помощью Python. Убедитесь, что у вас установлены все зависимости:

```bash
pip install poetry && poetry install
```
Запуск:

```bash
python main.py
```

# Структура проекта
* models.py — Описание классов для пользователей (User) и прокси-серверов (Proxy).
* storage.py — Описание взаимодействия с базой данных SQLite (создание, чтение, обновление).
* main.py — Главная логика обработки пользователей, проверки валидности прокси, а также запуск асинхронных задач.
* proxies.txt — Файл с прокси-серверами (формат: ip:port:username:password).
* users.txt — Файл с пользователями (формат: email:password).
* docker-compose.yml — Конфигурация для запуска проекта с использованием Docker.
* logs/ — Папка для хранения лог-файлов с архивированием в формат .zip.

## Преимущества асинхронности перед многопоточностью
### 1. Гибкость и масштабируемость
Асинхронность позволяет эффективно обрабатывать множество запросов или операций ввода/вывода (например, запросы к прокси-серверу или работе с базой данных) без создания новых потоков, что значительно снижает накладные расходы на их создание и управление ими.

### 2. Управление конкурентностью
Асинхронность обеспечивает легкость в управлении конкурирующими задачами без необходимости синхронизации потоков. Это позволяет избежать проблем, связанных с блокировками и гонками данных, которые могут возникать при многопоточности.

### 3. Меньше накладных расходов
В отличие от многопоточности, где каждый поток требует выделения системных ресурсов и переключений контекста, асинхронность использует один поток и позволяет эффективно управлять задачами ввода/вывода через цикл событий (event loop). Это делает программу менее ресурсоемкой и более производительной.

### 4. Не блокирующие операции
Асинхронные операции не блокируют основной поток, что позволяет одновременно выполнять несколько задач. Например, можно одновременно проверять несколько прокси, не ожидая завершения каждой операции.

### 5. Проще масштабировать
В отличие от многопоточности, где нужно учитывать различные аспекты синхронизации, асинхронность предоставляет гораздо более простой способ управления параллельными задачами, которые могут быть масштабированы без дополнительных сложностей.


### Структура базы данных
В проекте используется SQLite для хранения данных о пользователях и их прокси-серверах. Таблица в базе данных выглядит следующим образом:

```sql
CREATE TABLE IF NOT EXISTS user_proxy (
    email TEXT PRIMARY KEY,
    proxy_ip TEXT,
    proxy_port TEXT,
    proxy_user TEXT,
    proxy_pass TEXT
)
```
* email — уникальный идентификатор пользователя.
* proxy_ip, proxy_port, proxy_user, proxy_pass — данные прокси-сервера, который назначается пользователю.

Когда прокси для пользователя становится невалидным, система автоматически ищет новый доступный прокси и обновляет запись в базе данных.

### Логирование
Логи проекта будут сохраняться в папке logs и будут архивироваться в формате .zip. Архивация выполняется через каждые 1 час, а старые логи удаляются через 7 дней. Пример настройки логирования:

```python
logger.add(LOG_FILE, 
           rotation="1 hour",  # Архивируем логи каждый час
           retention="7 days",  # Храним логи 7 дней
           compression="zip",   # Архивируем логи в формате zip
           encoding="utf-8",     # Кодировка файлов
           level="DEBUG")       # Уровень логирования
```
# Заключение
Этот проект представляет собой эффективный и масштабируемый способ обработки пользователей и их прокси-серверов с использованием асинхронного подхода. Использование асинхронности вместо многопоточности позволяет улучшить производительность, снизить накладные расходы и упростить управление задачами.