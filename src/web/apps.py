from django.apps import AppConfig

class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        from web.utils.fill_stocks import fill_stock_model
        fill_stock_model()
        
        from .utils.scheduler import start_scheduler
        # start_scheduler()
