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

brasil = pytz.timezone('America/Sao_Paulo')

def fill_stock_model():
    if len(Stock.objects.all()) < 1:
        b3_stocks = ['ABEV3.SA', 'ASAI3.SA', 'AZUL4.SA', 'B3SA3.SA', 'BBAS3.SA', 'BBDC3.SA', 'BBDC4.SA', 'BBSE3.SA',
            'BEEF3.SA', 'BPAC11.SA', 'BRAP4.SA', 'BRDT3.SA', 'BRFS3.SA', 'BRKM5.SA', 'BRML3.SA', 'BTOW3.SA',
            'CCRO3.SA', 'CESP6.SA', 'CIEL3.SA', 'CMIG4.SA', 'COGN3.SA', 'CPFE3.SA', 'CPLE6.SA', 'CRFB3.SA',
            'CSAN3.SA', 'CSNA3.SA', 'CVCB3.SA', 'CYRE3.SA', 'ECOR3.SA', 'EGIE3.SA', 'ELET3.SA', 'ELET6.SA',
            'EMBR3.SA', 'ENBR3.SA', 'ENGI11.SA', 'EQTL3.SA', 'EZTC3.SA', 'FLRY3.SA', 'GGBR4.SA', 'GNDI3.SA',
            'GOAU4.SA', 'GOLL4.SA', 'HAPV3.SA', 'HGTX3.SA', 'HYPE3.SA', 'IGTA3.SA', 'IRBR3.SA', 'ITSA4.SA',
            'ITUB4.SA', 'JBSS3.SA', 'JHSF3.SA', 'KLBN11.SA', 'LAME4.SA', 'LCAM3.SA', 'LIGT3.SA', 'LINX3.SA',
            'LREN3.SA', 'MGLU3.SA', 'MOVI3.SA', 'MRFG3.SA', 'MRVE3.SA', 'MULT3.SA', 'NTCO3.SA', 'PCAR3.SA',
            'PETR3.SA', 'PETR4.SA', 'POMO4.SA', 'PSSA3.SA', 'QUAL3.SA', 'RADL3.SA', 'RAIL3.SA', 'RENT3.SA',
            'SANB11.SA', 'SBSP3.SA', 'SMLS3.SA', 'SULA11.SA', 'SUZB3.SA', 'TAEE11.SA', 'TIMP3.SA', 'TOTS3.SA',
            'TRPL4.SA', 'UGPA3.SA', 'USIM5.SA', 'VALE3.SA', 'VIVT3.SA', 'VVAR3.SA', 'WEGE3.SA', 'YDUQ3.SA']


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
        exceeded_prices = {}
        for user_stock in user_stocks:
            stock_data = StockData.objects.filter(
                stock__symbol=user_stock.symbol,
                date_time__gte=datetime.datetime.now().astimezone(brasil) - datetime.timedelta(days=5)
            ).order_by('-date_time')[:5]
            if stock_data:
                symbol_interval = user_stock.symbol + " - " + user_stock.periodicity
                for data in stock_data:
                    if data.high_price > user_stock.max_price and symbol_interval not in exceeded_prices:
                        exceeded_prices[symbol_interval] = f'atingiu o preço máximo de {data.high_price}'
                    if data.low_price < user_stock.min_price and user_stock.symbol not in exceeded_prices:
                        exceeded_prices[symbol_interval] = f'atingiu o preço mínimo de {data.low_price}'
        if exceeded_prices:
            message = f"As seguintes ações excederam os preços definidos pelo usuário {user.username}:\n\n"
            for symbol in exceeded_prices:
                message += f"{symbol} " + exceeded_prices[symbol] + "\n"

            send_email(
                'Ações que atingiram o preço máximo ou mínimo',
                message,
                [user.email]
            )

def save_stock_data():
    stocks = Stock.objects.all()
    for stock in stocks:
        url_yahoo = f'https://query1.finance.yahoo.com/v8/finance/chart/{stock.symbol}?interval={stock.interval}&range=1d'
        response_yahoo = requests.get(url_yahoo, headers={'User-agent': 'Mozilla/5.0'})
        data_yahoo = json.loads(response_yahoo.text)
        if data_yahoo is not None and 'chart' in data_yahoo and 'result' in data_yahoo['chart'] and data_yahoo['chart']['result'] is not None:
            yf_data(stock, data_yahoo)
        else:
            pass
    verifyPriceTunnels()

def yf_data(stock, data_yahoo):
    print(stock.symbol + " - " + stock.interval)
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
