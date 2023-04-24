from django.views import View
import plotly.graph_objs as go
from web.models import Stock
from django import forms
from django.shortcuts import render

class StockDetailsForm(forms.Form):
    symbol = forms.CharField(max_length=10, required=True)
    interval = forms.ChoiceField(choices=[('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('1h', '1h')], required=True)

class StockDetailsView(View):
    template_name = 'stock_details/index.html'

    def get(self, request, **kwargs):
        # context = super().get_context(**kwargs)
        form = StockDetailsForm(request.GET)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
        else:
            symbol = "ABEV"
            interval = "1m"

        # Obter os dados do estoque
        stock = Stock.objects.get(symbol=symbol, interval=interval)
        stock_data = stock.stockdata_set.all()

        # Criar uma lista de valores x e y para o gráfico
        x_values = [sd.date_time for sd in stock_data]
        y_values = [sd.close_price for sd in stock_data]

        # Criar o gráfico com Plotly
        trace = go.Scatter(x=x_values, y=y_values, text=symbol)
        data = [trace]

        x_range = [min(x_values), max(x_values)] if x_values else None
        y_range = [min(y_values), max(y_values)] if y_values else None
        
        layout = go.Layout(
            title=f"Preço de fechamento para {symbol}",
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
                title="Preço de fechamento"
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

        config = dict(displayModeBar=False, responsive=True)
        fig = go.Figure(data=data, layout=layout)
        plot_div = fig.to_html(full_html=False, config=config)
        
        context = {
            "plot_div": plot_div,
            "form": form
        }

        return render(request, self.template_name, context)