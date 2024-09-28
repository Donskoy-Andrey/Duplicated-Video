import asyncio
import logging.config

import msgpack

from consumer.config.settings import settings
from consumer.handlers.handler import handle_message

from consumer.logger import context_correlation_id, LOGGING_CONFIG, logger
from consumer.storage.rabbit import channel_pool


def setup_logger() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    if settings.LOG_LEVEL == 'DEBUG':
        logger.setLevel(logging.DEBUG)


async def start_consumer():
    setup_logger()
    logger.info('Starting consumer...')

    async with channel_pool.acquire() as channel:

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await channel.declare_queue(settings.QUEUE, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    if message.correlation_id is not None:
                        context_correlation_id.set(message.correlation_id)

                    parsed_message = msgpack.unpackb(message.body)
                    logger.info('Parsed message: %s', parsed_message)

                    _ = asyncio.create_task(handle_message(parsed_message))
