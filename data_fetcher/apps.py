from django.apps import AppConfig


class DataFetcherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_fetcher'

    def ready(self):
        from .tasks.tasks import fill_stock_model, start_scheduler
        fill_stock_model()
        start_scheduler()
