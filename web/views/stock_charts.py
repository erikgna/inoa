from django.views import View
import plotly.graph_objs as go
from web.models import Stock
from django import forms
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class StockChartsForm(forms.Form):
    symbol = forms.ChoiceField(choices=[], required=True)
    interval = forms.ChoiceField(choices=[('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('60m', '60m')], required=True)

    # Inicializa o select com o symbol das ações salvas no banco de dados
    def __init__(self, *args, **kwargs):
        super(StockChartsForm, self).__init__(*args, **kwargs)
        stocks = Stock.objects.values_list('symbol', flat=True).distinct()
        self.fields['symbol'].choices = [(stock, stock) for stock in stocks]
        self.fields['symbol'].widget.attrs.update({
            'class': 'form-control custom-select'
        })
        self.fields['interval'].widget.attrs.update({
            'class': 'form-control custom-select'
        })

class StockChartsView(View):
    template_name = 'stock_charts/index.html'

    @method_decorator(cache_page(60 * 5))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = StockChartsForm(request.GET)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
        else:
            symbol = "ABEV"
            interval = "1m"

        # Obtém os dados do estoque com base no símbolo e intervalo fornecidos
        stock = Stock.objects.get(symbol=symbol, interval=interval)
        stock_data = stock.stockdata_set.all()

        # Criar uma lista de valores x e y para o gráfico
        x_values = [sd.date_time for sd in stock_data]
        y_values = [sd.close_price for sd in stock_data]

        # Criar o gráfico com Plotly
        trace = go.Scatter(x=x_values, y=y_values, text=symbol)
        data = [trace]
        
        # Define os valores mínimo e máximo para o eixo x e y, com base nos dados do estoque
        x_range = [min(x_values), max(x_values)] if x_values else None
        y_range = [min(y_values), max(y_values)] if y_values else None
        
        # Define o layout do gráfico, incluindo título, opções de eixo, configurações de estilo e opções de zoom
        layout = go.Layout(
            title=f"Preços de {symbol} período de {interval}",
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis=dict(
                fixedrange=False,
                title="Preços"
            ),
            plot_bgcolor="#1f1f1f",
            paper_bgcolor="#1f1f1f",
            font=dict(
                color="#fff"
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Zoom",
                            method="update",
                            args=[
                                {'xaxis.range': x_range, 'yaxis.range': y_range},
                                {'frame': {'duration': 0}}
                            ]
                        ),
                        dict(
                            label="Resetar zoom",
                            method="relayout",
                            args=[
                                {"xaxis.range": [None, None]},
                                {"yaxis.range": [None, None]},
                            ],
                        )
                    ],
                    direction="left",
                    pad={"r": 10, "t": 10},
                    x=0.1,
                    y=1.05
                )
            ]
        )
        
        # Define as configurações do gráfico, incluindo a exibição da barra de ferramentas interativa
        config = dict(displayModeBar=False, responsive=True)
        fig = go.Figure(data=data, layout=layout)
        plot_div = fig.to_html(full_html=False, config=config)
        
        context = {
            "plot_div": plot_div,
            "form": form
        }

        return render(request, self.template_name, context)