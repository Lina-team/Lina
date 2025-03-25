from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, IS_NOT_MEMBER, IS_MEMBER
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


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_member(event: ChatMemberUpdated):
    if
    try:
        await event.answer(f"Привет, {}")
    except:
        pass
