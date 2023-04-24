from django.shortcuts import render
from django.views import View
from web.models import UserStock
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from web.models import Stock
from django.db.models import Q

@method_decorator(login_required, name='dispatch')
class AddMonitorView(View):
    template_name = 'add_monitor/index.html'

    def get(self, request):
        stocks = Stock.objects.values_list('symbol', flat=True).distinct()
        # stocks = Stock.objects.all()

        times = ['1m', '5m', '15m', "30m", "60m"]
        context = {
            "times": times,
            "stocks": stocks
        }

        return render(request, self.template_name, context)

    def post(self,request):
        request.session['message'] = 'Monitoramento adicionado com sucesso.'

        if request.method == 'POST':
            stock_symbol = request.POST.get('stocks')
            max_value = request.POST.get('max_value')
            min_value = request.POST.get('min_value')
            time = request.POST.get('time')
            
            if float(max_value) < float(min_value):
                request.session['error_message'] = 'Valor máximo deve ser maior ou igual ao valor mínimo.'
                return HttpResponseRedirect('/add-monitor')

            user_stock = UserStock(
                user=request.user, 
                symbol=stock_symbol,
                max_price=max_value,
                min_price=min_value,
                periodicity=time
            )
            user_stock.save()
            request.session['success_message'] = 'Monitoramento adicionado com sucesso.'
            return HttpResponseRedirect('/add-monitor')
        return HttpResponseRedirect('/add-monitor')
