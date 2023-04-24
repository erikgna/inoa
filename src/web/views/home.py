from django.shortcuts import render
from django.views import View
from web.models import UserStock

class HomeView(View):
    template_name = 'home/index.html'

    def get(self, request):
        user_stocks = UserStock.objects.filter(user=request.user)
        
        context = {
            "user_stocks": user_stocks
        }

        return render(request, self.template_name, context)