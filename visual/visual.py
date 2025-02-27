from flask import Flask, render_template, request
import pymysql
from config import DB_CONFIG
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)

# Функция для получения списка всех монет из базы данных
def fetch_coins():
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # SQL-запрос для получения списка монет
        query = "SELECT DISTINCT tag FROM what_to_mine_coins"
        cursor.execute(query)
        result = cursor.fetchall()

        # Преобразуем результат в список монет
        coins = [row['tag'] for row in result]
        return coins

    except pymysql.Error as e:
        print(f"Ошибка при работе с MySQL: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.open:
            connection.close()

# Функция для получения данных по выбранной монете
def fetch_coin_data(coin):
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # SQL-запрос для получения данных по выбранной монете за последние 7 дней
        query = """
        SELECT created_at, btc_revenue24 
        FROM what_to_mine_coins 
        WHERE tag = %s 
        ORDER BY created_at DESC 
        LIMIT 7
        """
        cursor.execute(query, (coin,))
        result = cursor.fetchall()

        # Преобразуем данные в списки для графика
        dates = [row['created_at'] for row in result]
        btc_revenue = [row['btc_revenue24'] for row in result]

        return dates, btc_revenue

    except pymysql.Error as e:
        print(f"Ошибка при работе с MySQL: {e}")
        return [], []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.open:
            connection.close()

# Маршрут для главной страницы
@app.route('/')
def index():
    # Получаем выбранную монету из запроса (если есть)
    selected_coin = request.args.get('coin', 'BTC')  # По умолчанию BTC

    # Получаем список всех монет
    coins = fetch_coins()

    # Получаем данные по выбранной монете
    dates, btc_revenue = fetch_coin_data(selected_coin)

    # Создаем график
    graph = go.Scatter(
        x=dates,
        y=btc_revenue,
        mode='lines+markers',
        name=f'{selected_coin} Revenue 24h'
    )

    layout = go.Layout(
        title=f'{selected_coin} Revenue за последние 7 дней',
        xaxis=dict(title='Дата'),
        yaxis=dict(title='BTC Revenue 24h')
    )

    fig = go.Figure(data=[graph], layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Передаем график и список монет в шаблон
    return render_template('index.html', graphJSON=graphJSON, coins=coins, selected_coin=selected_coin)

if __name__ == '__main__':
    app.run(debug=True)