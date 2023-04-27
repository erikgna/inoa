import datetime
import json
import threading    
import time
import pytz
import requests 
from schedule import Scheduler
from email_sender.tasks.tasks import send_email
from web.models import Stock, UserStock, StockData
from django.contrib.auth.models import User

def fill_stock_model():
    if len(Stock.objects.all()) < 1:
        b3_stocks = [
            'ABEV', 'ASAI', 'AZUL', 'B3SA', 'BBAS', 'BBDC', 'BBDC', 'BBSE',
            'BEEF', 'BPAC', 'BRAP', 'BRDT', 'BRFS', 'BRKM', 'BRML', 'BTOW',
            'CCRO', 'CESP', 'CIEL', 'CMIG', 'COGN', 'CPFE', 'CPLE', 'CRFB',
            'CSAN', 'CSNA', 'CVCB', 'CYRE', 'ECOR', 'EGIE', 'ELET', 'ELET',
            'EMBR', 'ENBR', 'ENGI', 'EQTL', 'EZTC', 'FLRY', 'GGBR', 'GNDI',
            'GOAU', 'GOLL', 'HAPV', 'HGTX', 'HYPE', 'IGTA', 'IRBR', 'ITSA',
            'ITUB', 'JBSS', 'JHSF', 'KLBN', 'LAME', 'LCAM', 'LIGT', 'LINX',
            'LREN', 'MGLU', 'MOVI', 'MRFG', 'MRVE', 'MULT', 'NTCO', 'PCAR',
            'PETR', 'PETR', 'POMO', 'PSSA', 'QUAL', 'RADL', 'RAIL', 'RENT',
            'SANB', 'SBSP', 'SMLS', 'SULA', 'SUZB', 'TAEE', 'TIMP', 'TOTS',
            'TRPL', 'UGPA', 'USIM', 'VALE', 'VIVT', 'VVAR', 'WEGE', 'YDUQ'
        ]

        intervals = ['1m', '5m', '15m', '30m', '60m']
        for stock in b3_stocks:
            for interval in intervals:
                stock_data = Stock(symbol=stock, interval=interval)
                stock_data.save()

def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously

def verifyPriceTunnels():
    users = User.objects.all()
    for user in users:
        user_stocks = UserStock.objects.filter(user=user)
        user_stocks = UserStock.objects.filter()
        for user_stock in user_stocks:
            stock_data = StockData.objects.filter(
                stock__symbol=user_stock.symbol,
                date_time__gte=datetime.datetime.now() - datetime.timedelta(days=5)
            ).order_by('-date_time')[:5]
            if stock_data:
                exceeded_prices = []
                for data in stock_data:
                    if data.high_price > user_stock.max_price:
                        exceeded_prices.append(f'{user_stock.symbol} atingiu o preço máximo de {data.high_price}')
                    if data.low_price < user_stock.min_price:
                        exceeded_prices.append(f'{user_stock.symbol} atingiu o preço mínimo de {data.low_price}')
                if exceeded_prices:
                    message = f"As seguintes ações excederam os preços definidos pelo usuário {user.username}:\n\n"
                    message += "\n".join(exceeded_prices)
                    send_email(
                        'Ações que atingiram o preço máximo ou mínimo',
                        message,
                        [user.email]
                    )
            else:
                pass

last_request_time = None
def save_stock_data():
    global last_request_time

    stocks = Stock.objects.all()
    for stock in stocks:
        url_yahoo = f'https://query1.finance.yahoo.com/v8/finance/chart/{stock.symbol}?interval={stock.interval}&range=1d'
        response_yahoo = requests.get(url_yahoo, headers={'User-agent': 'Mozilla/5.0'})
        data_yahoo = json.loads(response_yahoo.text)
        if data_yahoo is not None and 'chart' in data_yahoo and 'result' in data_yahoo['chart'] and data_yahoo['chart']['result'] is not None:
            yf_data(stock, data_yahoo)
        else:
            if not last_request_time or time.time() - last_request_time >= 60:
                alpha_vantage_data(stock)
            else:
                time_to_wait = 60 - (time.time() - last_request_time)
                time.sleep(time_to_wait)
                alpha_vantage_data(stock)
    verifyPriceTunnels()

def yf_data(stock, data_yahoo):
    
    brasil = pytz.timezone('America/Sao_Paulo')
    try:
        timestamps = data_yahoo['chart']['result'][0]['timestamp']
        opens = data_yahoo['chart']['result'][0]['indicators']['quote'][0]['open']
        highs = data_yahoo['chart']['result'][0]['indicators']['quote'][0]['high']
        lows = data_yahoo['chart']['result'][0]['indicators']['quote'][0]['low']
        closes = data_yahoo['chart']['result'][0]['indicators']['quote'][0]['close']
        volumes = data_yahoo['chart']['result'][0]['indicators']['quote'][0]['volume']

        for i in range(len(timestamps)):
            stock_data, created = StockData.objects.get_or_create(
                stock=stock,
                date_time=datetime.datetime.fromtimestamp(timestamps[i]).astimezone(brasil),
                defaults={
                    'open_price': opens[i] if opens[i] is not None else 0,
                    'high_price': highs[i] if highs[i] is not None else 0,
                    'low_price': lows[i] if lows[i] is not None else 0,
                    'close_price': closes[i] if closes[i] is not None else 0,
                    'volume': volumes[i] if volumes[i] is not None else 0
                }
            )
            if not created:
                stock_data.open_price = opens[i] if opens[i] is not None else 0
                stock_data.high_price = highs[i] if highs[i] is not None else 0
                stock_data.low_price = lows[i] if lows[i] is not None else 0
                stock_data.close_price = closes[i] if closes[i] is not None else 0
                stock_data.volume = volumes[i] if volumes[i] is not None else 0
                stock_data.save()
    except:
        pass

def alpha_vantage_data(stock):
    global last_request_time
    
    brasil = pytz.timezone('America/Sao_Paulo')
    url_alpha_vantage = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock.symbol}&interval={stock.interval}&apikey=I6A21HND55ZAQKPI'
    try:
        response_alpha_vantage = requests.get(url_alpha_vantage, headers={'User-agent': 'Mozilla/5.0'})
        last_request_time = time.time()
        data_alpha_vantage = json.loads(response_alpha_vantage.text)
        if data_alpha_vantage is not None and 'Time Series ({})'.format(stock.interval) in data_alpha_vantage:
            for key in data_alpha_vantage['Time Series ({})'.format(stock.interval)]:
                stock_data, created = StockData.objects.get_or_create(
                    stock=stock,
                    date_time=datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S').astimezone(brasil),
                    defaults={ 'open_price': float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['1. open']),
                'high_price': float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['2. high']),
                'low_price': float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['3. low']),
                'close_price': float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['4. close']),
                'volume': int(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['5. volume'])
                }
            )
            if not created:
                stock_data.open_price = float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['1. open'])
                stock_data.high_price = float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['2. high'])
                stock_data.low_price = float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['3. low'])
                stock_data.close_price = float(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['4. close'])
                stock_data.volume = int(data_alpha_vantage['Time Series ({})'.format(stock.interval)][key]['5. volume'])
                stock_data.save()
    except:
        pass

continuous_thread = None 
def start_scheduler():
    global continuous_thread

    if continuous_thread and continuous_thread.is_alive():
        return
    
    scheduler = Scheduler()
    scheduler.every(15).minutes.do(save_stock_data)
    cease_continuous_run = scheduler.run_continuously()
    continuous_thread = threading.Thread(target=lambda: cease_continuous_run.wait())
    continuous_thread.start()
