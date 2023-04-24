from django.shortcuts import render
from django.views import View
from web.models import Stock, StockData
from django.http import JsonResponse

class StocksView(View):
    template_name = 'stocks/index.html'

    def get(self, request):
        symbols = Stock.objects.values_list('symbol', flat=True).distinct()
        
        times = ['1m', '5m', '15m', "30m", "60m"]
        context = {"symbols": symbols, "times": times}

        return render(request, self.template_name, context)
    
class StockDataView(View):
    def get(self, request, symbol):
        interval = request.GET.get("interval", "1m")
        stock = Stock.objects.get(symbol=symbol, interval=interval)
        stock_data = stock.stockdata_set.all()

        data = []
        for sd in stock_data:
            data.append({
                "date_time": sd.date_time,
                "open_price": sd.open_price,
                "high_price": sd.high_price,
                "low_price": sd.low_price,
                "close_price": sd.close_price,
                "volume": sd.volume
            })

        return JsonResponse(data, safe=False)