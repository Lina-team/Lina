from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class TextCommandFilter(BaseFilter):
    def __init__(self, text_command: Union[list]):
        self.text_command = text_command

    async def __call__(self, message: Message) -> bool:
        res = False
        for i in self.text_command:
            if message.text.lower().startswith(i):
                res = True
                break
        return res
