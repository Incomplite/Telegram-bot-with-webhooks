from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from src.database.db import async_session_maker
import logging


class BaseDAO:
    model = None

    # Метод было решено скрестить с find_one_or_none, т.к. они выполняют одну и ту же функцию
    # @classmethod
    # async def find_by_id(cls, model_id: int):
    #     async with async_session_maker() as session:
    #         query = select(cls.model).filter_by(id=model_id)
    #         result = await session.execute(query)
    #         return result.mappings().one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()
    
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**data)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                return new_instance

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    @classmethod
    async def update(cls, id: int, **data):
        try:
            query = update(cls.model).where(cls.model.id == id).values(**data)
            async with async_session_maker() as session:
                await session.execute(query)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError: {e}")
            return False
        except Exception as e:
            logging.error(f"Exception: {e}")
            return False
