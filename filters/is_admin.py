from aiogram.enums.chat_member_status import ChatMemberStatus


async def is_group_admin(message, bo):
    member = await bo.get_chat_member(message.chat.id, message.from_user.id)
    b = await bo.get_chat_member(message.chat.id, bo.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or b.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    return True
