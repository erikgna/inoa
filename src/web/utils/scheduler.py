import datetime
import json
import threading    
import time
import requests 
from schedule import Scheduler
from django.core.mail import send_mail
from django.conf import settings
from web.models import Stock, UserStock, StockData
from django.contrib.auth.models import User

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

def send_email(subject, message, recipients):
    send_mail(
    		subject=subject,
    		message=message,
    		from_email=settings.EMAIL_HOST_USER,
    		recipient_list=recipients)

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

def saveStockData():
    stocks = Stock.objects.all()
    for stock in stocks:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{stock.symbol}?interval={stock.interval}&range=1d'
        response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
        data = json.loads(response.text)
        
        timestamps = data['chart']['result'][0]['timestamp']
        opens = data['chart']['result'][0]['indicators']['quote'][0]['open']
        highs = data['chart']['result'][0]['indicators']['quote'][0]['high']
        lows = data['chart']['result'][0]['indicators']['quote'][0]['low']
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        volumes = data['chart']['result'][0]['indicators']['quote'][0]['volume']
        
        for i in range(len(timestamps)):
            stock_data, created = StockData.objects.get_or_create(
                stock=stock,
                date_time=datetime.datetime.fromtimestamp(timestamps[i]),
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
    verifyPriceTunnels()

def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(10).minutes.do(saveStockData)
    scheduler.run_continuously()