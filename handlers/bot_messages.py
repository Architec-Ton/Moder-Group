from aiogram.enums import ChatMemberStatus
from aiogram import Router, F, Bot
from aiogram.types import Message
from config_reader import config
import re

bot = Bot(config.bot_token.get_secret_value(), parse_mode='MarkDown')
router = Router()

ban_words = [
    r'\b(бля[тд]блядь|ху[йяе]|пизд[аеуыи]еб[атьеуё]|сука|суки|нахуй|ебать)\b',
    r'\b(fuck|shit|bitch|asshole|damn|crup|motherfucker|cunt)\b'    
]

filter = F.text.regexp('|'.join(ban_words), flags=re.IGNORECASE)

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
        elif msg.forward_from_chat:
            reason = "сообщение переслано из чата"
        await msg.answer(f"Сообщение пользователя \"{msg.from_user.full_name}\" было *удалено*.\nПричина: *{reason}*.")
        
@router.message(filter)
async def delete_bran(msg: Message):
    if not await is_admin(msg):
        await msg.delete()
        await msg.answer(f"Сообщение пользователя *{msg.from_user.full_name}* было *удалено*.\nПричина: *использование нецензурной лексики*")