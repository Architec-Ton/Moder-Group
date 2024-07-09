from aiogram.enums import ChatMemberStatus
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.chat_permissions import ChatPermissions
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import MagicData
from config_reader import config
from datetime import timedelta 
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
import logging

bot = Bot(config.bot_token.get_secret_value(), parse_mode='MarkDown')
router = Router()

async def is_admin(msg: Message):
    user_status = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
    return user_status.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}

class SettingsCallback(CallbackData, prefix="settings"):
    action: str

@router.message(Command('check_status'))
async def check_status(msg: Message):
    if is_admin(msg):
        await msg.answer('Вы администратор')
    else:
        await msg.answer("Вы обычный пользователь")
        
@router.message(Command('start'))
async def start(msg: Message):
    await msg.answer('Привет! Я модератор для групп. Просто добавьте меня в группу и я буду удалять сообщения с ссылками,пересылаемые сообщения, а также админы групп смогут выдавать мут и бан пользователям.\nЧтобы управлять своей группой, введи в ней /menu. Чтобы уведомить о чем-то администраторов группы, введи /alert')

    
@router.message(Command('ban'))
async def ban_user(msg: Message):
    if await is_admin(msg):
        if not msg.reply_to_message:
            await msg.answer("Команда используется как ответ на сообщение")
            return

        user_id = msg.reply_to_message.from_user.id
        reason = ' '.join(msg.text.split()[1:]) or "Не указана"

        await bot.ban_chat_member(msg.chat.id, user_id)
        await msg.answer(f"Пользователь \"{msg.reply_to_message.from_user.full_name}\" забанен. Причина: {reason}.")
    else:
        await msg.answer("Только админы могут банить пользователей")


@router.message(Command('mute'))
async def mute_user(msg: Message):
    if not await is_admin(msg):
        await msg.answer("У вас нет прав, чтобы мутить людей")
        return
    
    if not msg.reply_to_message:
        await msg.answer("Команда используется как ответ на сообщение")
        return
    
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Команда записывается как: /mute {время} {единица времени (m,h,d,w,y)} {причина}")
        return
    
    try:
        duration = int(args[1])
    except ValueError:
        await msg.answer("Некорректное время")
        return

    unit = args[2].lower()
    match unit:
        case 'm':
            delta = timedelta(minutes=duration)
        case 'h':
            delta = timedelta(hours=duration)
        case 'd':
            delta = timedelta(days=duration)
        case 'w':
            delta = timedelta(weeks=duration)
        case 'y':
            delta = timedelta(days=duration*365)
        case _:
            await msg.answer("Некорректная единица времени")
            return
    
    reason = ' '.join(args[3:]) or "Не указана"
    user_id = msg.reply_to_message.from_user.id
    
    await bot.restrict_chat_member(
        msg.chat.id,
        user_id,
        ChatPermissions(can_send_messages=False),
        until_date=msg.date + delta
    )
    await msg.answer(f"Пользователь \"{msg.reply_to_message.from_user.full_name}\" получил мут на {duration} {unit}. Причина: {reason}.")
    
@router.message(Command('unmute'))
async def unmute_user(msg: Message):
    if not await is_admin(msg):
        await msg.answer("Такие права имеет только админ группы")
        return
    if not msg.reply_to_message:
        await msg.answer("Команда администратора должна быть ответом на чьё-то сообщение")
        return
    user_id = msg.reply_to_message.from_user.id
    await bot.restrict_chat_member(
        msg.chat.id,
        user_id,
        ChatPermissions(can_send_messages=True)
    )
    await msg.answer(f"Пользователь {msg.reply_to_message.from_user.full_name} размучен")
    
    

@router.message(Command('alert'))
async def alert_admins(msg: Message):
    if msg.reply_to_message:
        chat_id = msg.chat.id
        replied_msg = msg.reply_to_message
        admins = await bot.get_chat_administrators(chat_id)
        admin_mentions = []

        for admin in admins:
            admin_mentions.append(f"@{admin.user.username}" if admin.user.username else f"[{admin.user.full_name}](tg://user?id={admin.user.id})")

        user_name = msg.from_user.full_name
        message_link = f"https://t.me/c/{str(chat_id)[4:]}/{replied_msg.message_id}"

        mention_text = ", ".join(admin_mentions)
        alert_text = f"{mention_text}, внимание! Пользователь {user_name} сообщил о проблеме: [сообщение]({message_link})"

        await msg.answer(alert_text, parse_mode='Markdown')

    else:
        await msg.answer("Команду нужно использовать в ответ на сообщение, о котором вы хотите сообщить.")