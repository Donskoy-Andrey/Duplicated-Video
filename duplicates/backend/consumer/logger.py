import logging
from contextvars import ContextVar

import yaml


with open('consumer/config/logging.conf.yml', 'r') as f:
    LOGGING_CONFIG = yaml.full_load(f)


context_correlation_id: ContextVar[str] = ContextVar('correlation_id')


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if corr_id := context_correlation_id.get(None):
            return '[%s] %s' % (corr_id, super().format(record))

        return super().format(record)


logger = logging.getLogger('timofey_consumer')
