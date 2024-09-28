import aio_pika
from aio_pika.abc import ExchangeType
from aio_pika.pool import Pool

from consumer.config.settings import settings


async def _get_connection():
    kwargs = {}

    return await aio_pika.connect(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USERNAME,
        password=settings.RABBITMQ_PASSWORD,
        **kwargs,
    )


amqp_conn_pool: Pool = Pool(_get_connection, max_size=settings.RABBITMQ_CONNECTION_POOL_SIZE)


async def get_channel() -> aio_pika.Channel:
    async with amqp_conn_pool.acquire() as connection:
        return await connection.channel()

channel_pool: Pool = Pool(get_channel, max_size=settings.RABBITMQ_CHANNEL_POOL_SIZE)


async def setup_queue_and_exchange() -> None:
    async with channel_pool.acquire() as channel:  # type: Channel
        queue = settings.QUEUE
        exchange = settings.EXCHANGE

        exchange = await channel.declare_exchange(exchange, type=ExchangeType.TOPIC, durable=True)
        queue_from = await channel.declare_queue(queue, durable=True)

        await queue_from.bind(exchange, routing_key=queue)
