from aiogram.enums import ChatMemberStatus
from aiogram import Router, F, Bot
from aiogram.types import Message
from config_reader import config


bot = Bot(config.bot_token.get_secret_value(), parse_mode='MarkDown')
router = Router()


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
        await msg.answer("Ссылки запрещены!")
        
@router.message(F.forward_from | F.forward_from_chat)
async def handle_forward(msg: Message):
    if not await is_admin(msg):
        if msg.forward_from or msg.forward_from_chat:
            await msg.delete()
            await msg.answer("Пересылка сообщений запрещена")
        