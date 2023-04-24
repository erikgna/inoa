from django.urls import path
from web.views.home import HomeView
from web.views.add_monitor import AddMonitorView
from web.views.stock_details import StockDetailsView
from web.views.login import LoginView
from web.views.stocks import StocksView, StockDataView

app_name = "web"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('add-monitor/', AddMonitorView.as_view(), name='add_monitor'),
    path('stocks/', StocksView.as_view(), name='stocks'),
    path('stock_chart/', StockDetailsView.as_view(), name='stock_chart'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    # path('stock_data/<str:symbol>/', StockDataView.as_view(), name='stock_data'),
]