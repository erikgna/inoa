from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# Apenas usuários não autenticados podem acessar
class LoginView(View):
    template_name = 'login/index.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return render(request, self.template_name)
    
    def post(self, request):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Faz a autenticação das credenciais
            user = authenticate(username=email.split('@')[0], password=password)
            
            # Cria um usuário caso não exista no banco de dados;
            if user is None:
                username = email.split('@')[0]
                new_user = User.objects.create_user(username=username, email=email, password=password)
                new_user.save()

                # Loga o usuário
                user = authenticate(username=email.split('@')[0], password=password)
                login(request, user)                
                return HttpResponseRedirect("/")
            else:
                login(request, user)
                return HttpResponseRedirect('/')
        return HttpResponseRedirect('/login')
