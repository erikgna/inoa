from django.shortcuts import render
from django.views import View
from web.models import Stock
from django.http import JsonResponse

class StocksView(View):
    template_name = 'stocks/index.html'

    def get(self, request):
        # Obtém a lista de símbolos de ações distintas do banco de dados e cria uma lista de intervalos de tempo disponíveis.
        symbols = Stock.objects.values_list('symbol', flat=True).distinct()
        
        times = ['1m', '5m', '15m', "30m", "60m"]
        context = {"symbols": symbols, "times": times}

        return render(request, self.template_name, context)
    
# Define uma nova view que recebe um símbolo de ação e um intervalo de tempo e retorna os dados de preço correspondentes em formato JSON.
class StockDataView(View):
    def get(self, request, symbol, interval):
        # Obtém o objeto Stock correspondente ao símbolo de ação e ao intervalo de tempo fornecidos.
        stock = Stock.objects.get(symbol=symbol, interval=interval)
        # Obtém todos os objetos StockData relacionados ao objeto Stock encontrado na linha anterior.
        stock_data = stock.stockdata_set.all()

        data = []
        # Itera sobre todos os objetos StockData encontrados e adiciona seus valores em um dicionário, que é adicionado a uma lista de dados JSON.
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