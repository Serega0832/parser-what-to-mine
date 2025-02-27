WhatToMine Data Visualizer
Этот проект представляет собой веб-приложение на Flask, которое визуализирует данные о доходности майнинга различных криптовалют, полученные с сайта WhatToMine. Данные хранятся в базе данных MySQL, а на веб-странице отображается график доходности выбранной монеты за последние 7 дней.

Основные функции
Получение данных: Скрипт whattomine_parser.py ежедневно получает данные с WhatToMine и сохраняет их в базу данных.

Визуализация данных: Веб-приложение на Flask позволяет выбрать монету из списка и отображает график её доходности за последние 7 дней.

Интерактивный интерфейс: Пользователь может выбирать монету из выпадающего списка и обновлять график.

Структура проекта
Copy
whattomine-visualizer/
├── app.py                # Основной файл Flask-приложения
├── whattomine_parser.py  # Скрипт для получения данных с WhatToMine
├── templates/
│   └── index.html        # Шаблон HTML для отображения графика
├── config.py             # Конфигурация для подключения к базе данных
├── README.md             # Описание проекта (этот файл)
└── requirements.txt      # Список зависимостей
Установка и запуск
1. Клонирование репозитория
Склонируйте репозиторий на ваш компьютер:

bash
Copy
git clone https://github.com/ваш-username/whattomine-visualizer.git
cd whattomine-visualizer
2. Установка зависимостей
Убедитесь, что у вас установлен Python 3.x, и установите необходимые зависимости:

bash
Copy
pip install -r requirements.txt
3. Настройка базы данных
Убедитесь, что у вас установлен и запущен MySQL сервер.

Создайте базу данных и таблицу для хранения данных. Пример SQL-запроса для создания таблицы:

sql
Copy
CREATE TABLE what_to_mine_coins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coin_id INT,
    tag VARCHAR(10),
    algorithm VARCHAR(50),
    block_time FLOAT,
    block_reward FLOAT,
    block_reward24 FLOAT,
    last_block INT,
    difficulty FLOAT,
    difficulty24 FLOAT,
    nethash FLOAT,
    exchange_rate FLOAT,
    exchange_rate24 FLOAT,
    exchange_rate_vol FLOAT,
    exchange_rate_curr VARCHAR(10),
    market_cap FLOAT,
    estimated_rewards FLOAT,
    estimated_rewards24 FLOAT,
    btc_revenue FLOAT,
    btc_revenue24 FLOAT,
    profitability FLOAT,
    profitability24 FLOAT,
    lagging BOOLEAN,
    timestamp DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Настройте подключение к базе данных в файле config.py:

python
Copy
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ваш-пользователь',
    'password': 'ваш-пароль',
    'db': 'ваш-база-данных',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
4. Запуск скрипта для получения данных
Запустите скрипт whattomine_parser.py для получения данных с WhatToMine и сохранения их в базу данных:

bash
Copy
python whattomine_parser.py
5. Запуск Flask-приложения
Запустите Flask-приложение:

bash
Copy
python app.py
Перейдите по адресу http://127.0.0.1:5000/ в браузере, чтобы увидеть веб-интерфейс.

Используемые технологии
Python: Основной язык программирования.

Flask: Микрофреймворк для создания веб-приложения.

MySQL: База данных для хранения данных.

Plotly: Библиотека для создания интерактивных графиков.

Requests: Библиотека для выполнения HTTP-запросов.
