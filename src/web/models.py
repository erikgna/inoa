from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    interval = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol

class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now)
    open_price = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    high_price = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    low_price = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    close_price = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    volume = models.IntegerField(default=0)

    def __str__(self):
        return str(self.date_time)
    
class UserStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=7)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    periodicity = models.CharField(max_length=20)
    