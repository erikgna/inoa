from django.urls import path
from web.views.user_stocks import HomeView, delete_user_stock
from web.views.stock_charts import StockChartsView
from web.views.login import LoginView
from web.views.stocks import StocksView, StockDataView

app_name = "web"

urlpatterns = [
    path('', StocksView.as_view(), name='stocks'),
    path('user-stocks/', HomeView.as_view(), name='user-stocks'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('stock-chart/', StockChartsView.as_view(), name='stock_chart'),
    path('stock_data/<str:symbol>/<str:interval>', StockDataView.as_view(), name='stock_data'),
    path('user-stocks/delete/<int:user_stock_id>/', delete_user_stock, name='delete_user_stock')
]