import asyncio
import logging
import sys

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from pg_fsm import SQLAlchemyStorage


class TestStates(StatesGroup):
    first_state = State()
    second_state = State()


# Create storage key
key = StorageKey(bot_id=123, chat_id=456, user_id=789)
data = {
    'pi': 3.14,
    's': 'example string',
    'l': [1,2,3,4]
}

# Initiate a storage with default location
storage = SQLAlchemyStorage(db_uri="postgresql")

# Create a state to work with
state = FSMContext(storage=storage, key=key)


async def main():
    # Set first state
    await state.set_state(TestStates.first_state)
    c_state = await state.get_state()
    print('After setting first state: ', c_state)

    # Change state
    await state.set_state(TestStates.second_state)
    c_state = await state.get_state()
    print('After setting second state: ', c_state)

    if c_state == TestStates.second_state:
        print("State was read correctly")
    else:
        print("State wasn't read correctly")

    # Set data
    await state.set_data(data=data)
    c_data = await state.get_data()
    print('After setting data: ', c_data)

    # Update data
    data.update(new_key='new value')
    await state.update_data(data=data)
    c_data = await state.get_data()
    print('After updating data: ', c_data)

    # Clearing state
    await state.clear()
    c_state = await state.get_state()
    c_data = await state.get_data()
    print('After clear state: ', c_state, 'data: ', c_data)

    # Closing storage
    await storage.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
