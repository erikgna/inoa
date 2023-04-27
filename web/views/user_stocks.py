from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from web.models import Stock, UserStock
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def delete_user_stock(request, user_stock_id):
    user_stock = get_object_or_404(UserStock, pk=user_stock_id, user=request.user)

    if request.method == 'DELETE':
        user_stock.delete()
        return JsonResponse({'message': 'Monitoramento excluído com sucesso.'})

    return JsonResponse({'message': 'Ocorreu um erro ao excluir o monitoramento.'}, status=400)

@method_decorator(login_required, name='dispatch')
class HomeView(View):
    template_name = 'user_stocks/index.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Pega as ações do usuário
        user_stocks = UserStock.objects.filter(user=request.user)
        stocks = Stock.objects.values_list('symbol', flat=True).distinct()

        times = ['1m', '5m', '15m', "30m", "60m"]
        context = {
            "times": times,
            "stocks": stocks,
            "user_stocks": user_stocks
        }

        return render(request, self.template_name, context)
    
    def post(self,request):
        request.session['message'] = 'Monitoramento adicionado com sucesso.'

        if request.method == 'POST':
            stock_symbol = request.POST.get('stocks')
            max_value = request.POST.get('max_value')
            min_value = request.POST.get('min_value')
            time = request.POST.get('time')
            
            # Verifica se o valor minímo é menor que o máximo
            if float(max_value) < float(min_value):
                request.session['error_message'] = 'Valor máximo deve ser maior ou igual ao valor mínimo.'
                return HttpResponseRedirect('/')
            
            # Adicionar a nova ação do usuário
            user_stock = UserStock(
                user=request.user, 
                symbol=stock_symbol,
                max_price=max_value,
                min_price=min_value,
                periodicity=time
            )
            user_stock.save()
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/')