import logging
from django.apps import apps

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        LogEntry = apps.get_model('russianNews', 'LogEntry')
        LogEntry.objects.create(
            user=getattr(record, 'user', None),
            action=record.msg,
            ip_address=getattr(record, 'ip_address', ''),
            user_agent=getattr(record, 'user_agent', ''),
            absolute_uri=getattr(record, 'absolute_uri', ''),
            http_method=getattr(record, 'http_method', ''),
            attackType=getattr(record, 'attackType', None),
            input= getattr(record, 'input', '')
        )

