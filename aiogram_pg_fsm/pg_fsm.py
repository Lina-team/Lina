from __future__ import annotations

from asyncio import run

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.state import State
from typing import Any, Dict, Optional

import pickle
import json
import logging

from sqlalchemy.orm import DeclarativeBase, declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class FSMData(Base):
    __tablename__ = "fsm_data"

    key: Mapped[str] = mapped_column(String(), primary_key=True)
    state: Mapped[str] = mapped_column(String())
    data: Mapped[str] = mapped_column(String())


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


logger = logging.getLogger(__name__)


class PGStorage(BaseStorage):
    
    def __init__(self, db_path: str = 'postgresql+asyncpg://username:password@host:port/db') -> None:
        """
        You can point a database path. It will be 'fsm_storage.db' for default.
        It's possible to choose srtializing method: 'pickle' (default) or 'json'. If you hange serializing method, you shoud delete existing database, and start a new one.
        'Pickle' is slower than 'json', but it can serialize some kind of objects, that 'json' cannot. 'Pickle' creates unreadable for human data in database, instead of 'json'.
        """
        self.db_path = db_path
        self.engine = create_async_engine(url=self.db_path)
        self.ser_m = "pickle"
        self.async_sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

        try:
            run(create_tables(self.engine))
            logger.debug(f'FSM Storage database {self.db_path} has been opened.')
        except Exception as e:
            logger.error(f'Error: \n{e}')

    @staticmethod
    def _key(key: StorageKey) -> str:
        """
        Create a key for every uniqe user, chat and bot
        """
        result_string = str(key.bot_id) + ':' + str(key.chat_id) + ':' + str(key.user_id)
        return result_string

    def _ser(self, obj: object) -> str|bytes|None:
        """
        Serialize object
        """
        try:
            if self.ser_m == 'json':
                return json.dumps(obj)
            else:
                return pickle.dumps(obj)
        except Exception as e:
            logger.error(f'Serializing error! {e}')
            return None

    def _dsr(self, obj) -> Optional[Dict[str, Any]]:
        """
        Deserialize object
        """
        try:
            if self.ser_m == 'json':
                return json.loads(obj)
            else:
                return pickle.loads(obj)
        except Exception as e:
            logger.error(f'Deserializing error! Probably, unsupported serializing method was used. {e}')
            return None

    async def set_state(self, key: StorageKey, state: State|None = None) -> None:
        """
        Set state for specified key

        :param key: storage key
        :param state: new state
        """
        s_key = self._key(key)
        s_state = state.state if isinstance(state, State) else state

        try:
            async with self.async_sessionmaker() as session:
                fsm_data = await session.scalar(select(FSMData).filter_by(key=s_key))

                if not fsm_data:
                    fsm_data = FSMData(key=s_key, state=s_state, data=s_key)
                    session.add(fsm_data)
                    await session.commit()
                else:
                    fsm_data.key=s_key
                    fsm_data.state = s_state
                    fsm_data.data = s_key
                    await session.commit()
        except Exception as e:
            logger.error(f'Error: \n{e}')

    async def get_state(self, key: StorageKey) -> Optional[str]:
        """
        Get key state

        :param key: storage key
        :return: current state
        """
        s_key = self._key(key)

        try:
            async with self.async_sessionmaker() as session:
                s_state = await session.scalar(select(FSMData).filter_by(key=s_key))

                if s_state:
                    return s_state.state
                else:
                    return None
            
        except Exception as e:
            logger.error(f'Error: \n{e}')
            return None
    
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """
        Write data (replace)

        :param key: storage key
        :param data: new data
        """
        s_key = self._key(key)
        s_data = self._ser(data)

        try:
            async with self.async_sessionmaker() as session:
                fsm_data = await session.scalar(select(FSMData).filter_by(key=s_key))
                if not fsm_data:
                    fsm_data = FSMData(key=s_key, state=s_key, data=s_data)
                    session.add(fsm_data)
                    await session.commit()
                else:
                    fsm_data.key = s_key
                    fsm_data.state = s_key
                    fsm_data.data = s_data
                    await session.commit()
        except Exception as e:
            logger.error(f'Error: \n{e}')
    
    async def get_data(self, key: StorageKey) -> Optional[Dict[str, Any]]:
        """
        Get current data for key

        :param key: storage key
        :return: current data
        """
        s_key = self._key(key)

        try:
            async with self.async_sessionmaker() as session:
                s_data = await session.scalar(select(FSMData).filter_by(key=s_key))
                if s_data:
                    return s_data.data
                else:
                    return None

        except Exception as e:
            logger.error(f'Error: \n{e}')
            return None

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update date in the storage for key (like dict.update)

        :param key: storage key
        :param data: partial data
        :return: new data
        """
        current_data = await self.get_data(key=key)
        if not current_data:
            current_data = {}
        current_data.update(data)
        await self.set_data(key=key, data=current_data)
        return current_data.copy()
    
    async def close(self) -> None:
        logger.debug(f'FSM Storage database {self.db_path} has been closed.')
