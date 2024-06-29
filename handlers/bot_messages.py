from aiogram.enums import ChatMemberStatus
from aiogram import Router, F, Bot
from aiogram.types import Message
from config_reader import config
import re

bot = Bot(config.bot_token.get_secret_value(), parse_mode='MarkDown')
router = Router()

bad_words = [
    "блядь", "блять", "ебать", "ебаный", "ебать", "ебаться", "пизда", "пиздец",
    "хуй", "хуёво", "хуевый", "хуеплет", "хуесос", "гандон", "мудак", "дерьмо",
    "сучка", "сука", "пидор", "пидорас", "мразь", "тварь", "ублюдок", "срака",
    "залупа", "чмо", "жопа", "бля", "дрянь", "шалава", "шлюха", "мудила",
    "пиздюк", "гнида", "говно", "пошел на хуй", "иди нахуй", "черт", "еблан",
    "ебанутый", "ебло", "пидарас", "пидор", "трахать", "ебись", "курва", "сукин сын",
    "ебал", "ебать", "бля", "епта", "ёпта", "епт", "ёпт", "член", "dick", "шмара", 'сук',
    "шалава", "пидр", "пидарас", 'трах', "долбоеб", "долбоёб", "далбаеб", "далбаёб", 'хуя',
    'хуяк'
]

def contains_bad_word(message):
    message_lower = message.lower()
    for word in bad_words:
        if word in message_lower:
            return True
    return False

links = F.text.regexp(r"http[s]?://")

async def is_admin(msg: Message):
    user_status = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
    return user_status.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}


@router.message(links)
async def delete_link(msg: Message):
    status = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
    if status.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}:
        pass
    else:
        await msg.delete()
        await msg.answer(f"Сообщение пользователя \"{msg.from_user.full_name}\" было *удалено*.\nПричина: *отправка ссылок запрещена.*")
        
@router.message(F.forward_from | F.forward_from_chat)
async def handle_forward(msg: Message):
    if not await is_admin(msg) and not msg.from_user.full_name == 'Telegram':
        await msg.delete()
        if msg.forward_from:
            reason = "сообщение переслано от пользователя"
        elif msg.forward_from_chats:
            reason = "сообщение переслано из чата"
        await msg.answer(f"Сообщение пользователя \"{msg.from_user.full_name}\" было *удалено*.\nПричина: *{reason}*.")
        
@router.message()
async def delete_bran(msg: Message):
    if contains_bad_word(msg.text):
        if not await is_admin(msg):
            await msg.delete()
            await msg.answer(f"Сообщение пользователя *{msg.from_user.full_name}* было *удалено*.\nПричина: *использование нецензурной лексики*")

        
