from sqlalchemy.ext.asyncio import AsyncSession

from consumer.logger import logger
from consumer.storage.db import get_db
from sqlalchemy import insert, select, update
from web.storage.db import Jobs, async_session


async def handle_message(message: dict) -> None:
    ######
    # ЛОГИКА ТУТ!!!#
    ######

    # logger.info('Received message: %s', message)
    async with async_session() as session:
        row = await session.execute(select(Jobs).filter_by(uid=message["uid"]))
        job = row.scalar_one()
        session.refresh(job)
        job.is_processed = True # сюда результат работы
        job.is_duplicate = True
        job.duplicate_for = "kek"
        await session.commit()
        row_check_obj = await session.execute(select(Jobs.is_processed).where(Jobs.uid == message["uid"]))
        row_check = row_check_obj.scalar_one()
        session.refresh(row_check)
        # job.result = {"is_duplicate": True, "duplicate_for": 123}
        logger.info(row_check)

