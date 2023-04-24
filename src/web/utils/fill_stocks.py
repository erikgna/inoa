from web.models import Stock

def fill_stock_model():
    if len(Stock.objects.all()) < 1:
        b3_stocks = [
            'ABEV', 'ASAI', 'AZUL', 'B3SA', 'BBAS', 'BBDC', 'BBDC', 'BBSE',
            'BEEF', 'BPAC', 'BRAP', 'BRDT', 'BRFS', 'BRKM', 'BRML', 'BTOW',
            'CCRO', 'CESP', 'CIEL', 'CMIG', 'COGN', 'CPFE', 'CPLE', 'CRFB',
            'CSAN', 'CSNA', 'CVCB', 'CYRE', 'ECOR', 'EGIE', 'ELET', 'ELET',
            'EMBR', 'ENBR', 'ENGI', 'EQTL', 'EZTC', 'FLRY', 'GGBR', 'GNDI',
            'GOAU', 'GOLL', 'HAPV', 'HGTX', 'HYPE', 'IGTA', 'IRBR', 'ITSA',
            'ITUB', 'JBSS', 'JHSF', 'KLBN', 'LAME', 'LCAM', 'LIGT', 'LINX',
            'LREN', 'MGLU', 'MOVI', 'MRFG', 'MRVE', 'MULT', 'NTCO', 'PCAR',
            'PETR', 'PETR', 'POMO', 'PSSA', 'QUAL', 'RADL', 'RAIL', 'RENT',
            'SANB', 'SBSP', 'SMLS', 'SULA', 'SUZB', 'TAEE', 'TIMP', 'TOTS',
            'TRPL', 'UGPA', 'USIM', 'VALE', 'VIVT', 'VVAR', 'WEGE', 'YDUQ'
        ]

        intervals = ['1m', '5m', '15m', '30m', '60m']
        for stock in b3_stocks:
            for interval in intervals:
                stock_data = Stock(symbol=stock, interval=interval)
                stock_data.save()