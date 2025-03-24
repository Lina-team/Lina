import warnings

from aiogram import Router, F, Bot
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import Message, ChatMemberUpdated, ChatMemberOwner, ChatMemberAdministrator

from bs4 import XMLParsedAsHTMLWarning, BeautifulSoup

from requests import get

from filters import TextCommandFilter

from db.dao import set_note, delete_note, get_note, get_notes, get_rules, set_rules

from middlewares import UserMiddleware

router = Router()

router.message.middleware(UserMiddleware())


@router.message(F.text, TextCommandFilter(["лина расскажи анекдот", "расскажи анекдот", "анекдот"]))
async def say_joke(message: Message):
    url = 'http://rzhunemogu.ru/Rand.aspx?CType=1'
    response = get(url)

    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

    soup = BeautifulSoup(response.content, 'html.parser')
    anecdote = soup.find('content').text.strip()

    await message.reply(anecdote + '\n\n_Анекдот взят с сайта http://rzhunemogu.ru/_', disable_web_page_preview=True)


@router.message(F.text, TextCommandFilter(["лина кинь кубики", "лина рандом", "кости", "кубики"]))
async def roll_dice(message: Message):
    await message.reply_dice()


@router.message(F.text, TextCommandFilter(["лина помощь", "лина хелп", "хелп"]))
async def help_command(message: Message):
    await message.reply("Доступные команды можно узнать [тут](https://t.me/LinaGirlChannel/6)")


@router.message(F.text, TextCommandFilter(["+записка"]))
async def create_note_(message: Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not member != ChatMemberOwner and member != ChatMemberAdministrator:
        return
    try:
        a = message.text.find("\n")
        if a == -1:
            await message.reply("Нет текста")
            return
        name = message.text[9:a]
        if len(message.md_text[a+1:]) > 1000:
            await message.reply("Текст записки не должен превышать 1000 символов")
            return
        await set_note(name=name, note=message.md_text[a+1:], group_id=message.chat.id)
        await message.reply(f"Запись '{name}' создана")
    except Exception as e:
        await message.reply(f"Ошибка при создании записки - обратитесь в чат @LinaGirlChat: \n{str(e)}")


@router.message(F.text, TextCommandFilter(["-записка"]))
async def delete_note_(message: Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not member != ChatMemberOwner and member != ChatMemberAdministrator:
        return
    try:
        name = message.text[9:]
        res = await delete_note(name=name, group_id=message.chat.id)
        if not res:
            await message.reply(f"Запись '{name}' не найдена")
            return
        await message.reply(f"Запись '{name}' удалена")
    except Exception as e:
        await message.reply(f"Ошибка при удалении записки - обратитесь в чат @LinaGirlChat: \n{str(e)}")


@router.message(F.text, TextCommandFilter(["записки"]))
async def get_notes_(message: Message):
    notes = await get_notes(group_id=message.chat.id)
    if not notes:
        await message.reply("Записок нет")
        return
    await message.reply("*Записки группы:*\n" + "\n".join([note.name for note in notes]))


@router.message(F.text, TextCommandFilter(["записка"]))
async def get_note_(message: Message):
    name = message.text[8:]
    note = await get_note(name=name, group_id=message.chat.id)
    if not note:
        await message.reply(f"Записка '{name}' не найдена")
        return
    res = note.note.replace("\\", "")
    if message.reply_to_message:
        await message.reply_to_message.reply(f"*Записка '{name}':* \n{res}")
        return
    await message.reply(f"*Записка '{name}':* \n{res}")


@router.message(F.text, TextCommandFilter(["рулс", "?правила", "лина правила"]))
async def rules(message: Message):
    rules_ = await get_rules(group_id=message.chat.id)
    if not rules_:
        await message.reply("Правил группы нет")
        return
    if message.reply_to_message:
        await message.reply_to_message.reply("*Правила группы:*\n" + rules_.replace('\\', ''))
        return
    await message.answer("*Правила группы:*\n" + rules_.replace('\\', ''))


@router.message(F.text, TextCommandFilter(["+рулс", "лина +правила"]))
async def add_rules(message: Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not member != ChatMemberOwner and member != ChatMemberAdministrator:
        return
    try:
        a = message.text.find("\n")
        if a == -1:
            await message.reply("Нет текста")
            return
        if len(message.md_text[a + 1:]) > 1000:
            await message.reply("Максимальная длина правил не должна превышать 1000 символов")
            return
        await set_rules(rules=message.md_text[a+1:], group_id=message.chat.id)
        await message.reply("Правила группы добавлены")
    except Exception as e:
        await message.reply(f"Ошибка при создании правил - обратитесь в чат @LinaGirlChat: \n{str(e)}")
