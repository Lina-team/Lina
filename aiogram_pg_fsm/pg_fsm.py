from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.sqlalchemy import SQLAlchemyStorage
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Модель для хранения состояний FSM
class FSMState(Base):
    __tablename__ = 'fsm_states'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    state = Column(String)

# Класс для хранения состояний FSM в базе данных
class DatabaseFSMStorage(MemoryStorage):
    def __init__(self, db_url):
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    async def get_state(self, chat: types.Chat, user: types.User = None) -> str:
        fsm_state = self.session.query(FSMState).filter_by(chat_id=chat.id).first()
        return fsm_state.state if fsm_state else None

    async def set_state(self, chat: types.Chat, user: types.User = None, state: str = None) -> None:
        fsm_state = self.session.query(FSMState).filter_by(chat_id=chat.id).first()
        if fsm_state:
            fsm_state.state = state
        else:
            fsm_state = FSMState(chat_id=chat.id, state=state)
            self.session.add(fsm_state)
        self.session.commit()

    async def reset_state(self, chat: types.Chat, user: types.User = None) -> None:
        fsm_state = self.session.query(FSMState).filter_by(chat_id=chat.id).first()
        if fsm_state:
            self.session.delete(fsm_state)
            self.session.commit()

# Использование DatabaseFSMStorage в вашем боте
db_storage = DatabaseFSMStorage('sqlite:///fsm_states.db')
dp = Dispatcher(bot, storage=db_storage)