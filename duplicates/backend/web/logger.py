import contextlib
import logging.config

import yaml
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError


with open('web/config/logging.conf.yml', 'r') as f:
    LOGGING_CONFIG = yaml.safe_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        with contextlib.suppress(ContextDoesNotExistError):
            if correlation_id := context.get('X-Correlation-ID'):
                return '[%s] %s' % (correlation_id, super().format(record))

        return super().format(record)


logger = logging.getLogger('backend')
