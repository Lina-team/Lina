from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated
from db.dao import set_group

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added(event: ChatMemberUpdated, bot: Bot):
    await set_group(group_id=event.chat.id)
    try:
        await bot.send_message(event.chat.id, "*Привет! Я Лина - ваш чат-бот.*\nЧтобы узнать мои команды пиши _Хелп_")
    except:
        pass
