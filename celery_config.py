# celery_config.py
from celery import Celery

celery = Celery("je_consultancy")

def make_celery(app):
    """Properly configure Celery with Redis"""
    
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        
        # Important for Windows + Redis
        worker_pool_restarts=True,
        worker_prefetch_multiplier=1,
    )

    # Flask app context support
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery