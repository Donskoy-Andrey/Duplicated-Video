from consumer.logger import logger


async def handle_message(message: dict) -> None:
    logger.info('Received message: %s', message)