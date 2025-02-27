import logging
import requests
import pymysql
from pymysql.cursors import DictCursor
from config import DB_CONFIG
from logging.handlers import RotatingFileHandler  # Импортируем RotatingFileHandler

# Настройка логирования (вывод в файл и в консоль)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        # Логи в файл с ограничением в 200 строк
        RotatingFileHandler(
            "whattomine.log",  # Имя файла
            maxBytes=200 * 1024,  # Максимальный размер файла (200 строк * ~1 КБ на строку)
            backupCount=1,  # Хранить только один архивный файл
            mode="w",  # Перезаписывать файл при достижении лимита
        ),
        logging.StreamHandler()  # Логи в консоль
    ],
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Функция для получения данных с WhatToMine
def fetch_data():
    url = "https://www.whattomine.com/asic.json"  # URL для ASIC-майнинга
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()
        logging.info("Данные успешно получены с WhatToMine")
        return data["coins"]  # Возвращаем только данные по монетам
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении данных: {e}")
        return None

# Функция для проверки существования данных в базе за сегодня
def is_coin_data_exists(coin_id):
    connection = None
    cursor = None
    try:
        # Подключение к базе данных
        logging.info("Подключение к базе данных для проверки существования данных...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # SQL-запрос для проверки существования данных за сегодня
        query = """
        SELECT COUNT(*) FROM what_to_mine_coins 
        WHERE coin_id = %s AND DATE(created_at) = CURDATE()
        """
        cursor.execute(query, (coin_id,))
        result = cursor.fetchone()

        # Если результат больше 0, значит данные уже существуют
        return result[0] > 0

    except pymysql.Error as e:
        logging.error(f"Ошибка при работе с MySQL: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.open:
            connection.close()

# Функция для записи данных в базу
def insert_coin_data(coin_data):
    connection = None
    cursor = None
    try:
        # Проверка, существуют ли данные для этой монеты за сегодня
        if is_coin_data_exists(coin_data["id"]):
            logging.info(f"Данные для монеты {coin_data['tag']} уже существуют в базе данных за сегодня")
            return

        # Подключение к базе данных
        logging.info("Подключение к базе данных...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # SQL-запрос для вставки данных (без created_at, так как он добавляется автоматически)
        query = """
        INSERT INTO what_to_mine_coins (
            coin_id, tag, algorithm, block_time, block_reward, block_reward24,
            last_block, difficulty, difficulty24, nethash, exchange_rate,
            exchange_rate24, exchange_rate_vol, exchange_rate_curr, market_cap,
            estimated_rewards, estimated_rewards24, btc_revenue, btc_revenue24,
            profitability, profitability24, lagging, timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Подготовка данных для вставки
        values = (
            coin_data["id"], coin_data["tag"], coin_data["algorithm"], coin_data["block_time"],
            coin_data["block_reward"], coin_data["block_reward24"], coin_data["last_block"],
            coin_data["difficulty"], coin_data["difficulty24"], coin_data["nethash"],
            coin_data["exchange_rate"], coin_data["exchange_rate24"], coin_data["exchange_rate_vol"],
            coin_data["exchange_rate_curr"], coin_data["market_cap"], coin_data["estimated_rewards"],
            coin_data["estimated_rewards24"], coin_data["btc_revenue"], coin_data["btc_revenue24"],
            coin_data["profitability"], coin_data["profitability24"], coin_data["lagging"], coin_data["timestamp"]
        )

        # Выполнение запроса
        cursor.execute(query, values)
        connection.commit()
        logging.info(f"Данные для монеты {coin_data['tag']} успешно добавлены в таблицу coins")

    except pymysql.Error as e:
        logging.error(f"Ошибка при работе с MySQL: {e}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.open:
            connection.close()

# Основной код
if __name__ == "__main__":
    # Получение данных
    data = fetch_data()
    if data:
        # Запись данных по каждой монете в базу
        for coin_name, coin_data in data.items():
            # Пропускаем монету, если tag равен 'NICEHASH'
            if coin_data["tag"] == "NICEHASH":
                logging.info(f"Пропуск монеты {coin_data['tag']} (NICEHASH)")
                continue  # Пропускаем итерацию цикла

            # Добавляем данные в базу
            insert_coin_data(coin_data)
            logging.info(f"Данные для монеты {coin_data['tag']} успешно добавлены в базу данных")
        logging.info("Все данные успешно добавлены в базу данных")
    else:
        logging.error("Не удалось получить данные с WhatToMine")
