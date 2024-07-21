from aiogram.enums import ChatMemberStatus
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from config_reader import config
import re
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from handlers.user_commands import *
import logging
from aiogram.client.default import DefaultBotProperties
from db import *
import asyncio

bot = Bot(config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="MarkDown"))
router = Router()


async def is_admin(chat_id, user_id):
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

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

class SettingsCallback(CallbackData, prefix="settings"):
    action: str


def create_settings_keyboard(settings):
    builder = InlineKeyboardBuilder()
    buttons = [
        ("Удаление ссылок", "ban_links", settings[2]),
        ("Удаление пересылаемых сообщений", "ban_forwards", settings[3]),
        ("Удаление нецензурной лексики", "ban_bad_words", settings[4])
    ]
    for text, action, enabled in buttons:
        status = "✅" if enabled else "❌"
        builder.button(text=f"{text} {status}", callback_data=SettingsCallback(action=action).pack())
    builder.adjust(1)
    return builder.as_markup()


async def delete_after_delay(message: Message):
    await asyncio.sleep(300)
    await bot.delete_message(message.chat.id, message.message_id)


@router.message(Command("menu"))
async def show_menu(msg: Message):
    if await is_admin(msg.chat.id, msg.from_user.id):
        settings = get_group_settings(msg.chat.id)
        
        if settings is None:
            add_group(msg.chat.id, msg.from_user.id)
            settings = get_group_settings(msg.chat.id)
        
        await msg.answer("Настройки:", reply_markup=create_settings_keyboard(settings))
    else:
        await msg.answer("Только администраторы могут использовать эту команду.")
        asyncio.create_task(delete_after_delay(msg))

@router.callback_query(SettingsCallback.filter())
async def update_setting(callback: CallbackQuery, callback_data: SettingsCallback):
    if await is_admin(callback.message.chat.id, callback.from_user.id):
        group_id = callback.message.chat.id
        setting = callback_data.action
        settings = get_group_settings(group_id)
        current_status = settings[2] if setting == "ban_links" else (settings[3] if setting == "ban_forwards" else settings[4])
        new_status = not current_status
        update_group_setting(group_id, setting, new_status)
        status_text = "включена" if new_status else "выключена"
        await callback.answer(f"Настройка {setting.replace('_', ' ')} {status_text}.")
        await callback.message.edit_reply_markup(reply_markup=create_settings_keyboard(get_group_settings(group_id)))
    else:
        await callback.answer("Вы не админ", show_alert=True)
    asyncio.create_task(delete_after_delay(callback.message))


def contains_bad_word(message):
    message_lower = message.lower()
    for word in bad_words:
        if word in message_lower:
            return True
    return False

links = F.text.regexp(r"http[s]?://")


@router.message(F.text.regexp(r"http[s]?://"))
async def delete_link(msg: Message):
    settings = get_group_settings(msg.chat.id)
    if settings and settings[2]:
        if not await is_admin(msg.chat.id, msg.from_user.id):
            await msg.delete()
            bot_message = await msg.answer(f"Сообщение пользователя \"{msg.from_user.full_name}\" было *удалено*.\nПричина: *отправка ссылок запрещена.*")
            asyncio.create_task(delete_after_delay(bot_message))

@router.message(F.forward_from | F.forward_from_chat)
async def handle_forward(msg: Message):
    settings = get_group_settings(msg.chat.id)
    if settings and settings[3]:
        if not await is_admin(msg.chat.id, msg.from_user.id) and msg.from_user.full_name != 'Telegram':
            await msg.delete()
            reason = "сообщение переслано от пользователя" if msg.forward_from else "сообщение переслано из чата"
            bot_message = await msg.answer(f"Сообщение пользователя \"{msg.from_user.full_name}\" было *удалено*.\nПричина: *{reason}*.")
            asyncio.create_task(delete_after_delay(bot_message))

@router.message()
async def delete_bran(msg: Message):
    settings = get_group_settings(msg.chat.id)
    if settings and settings[4]:
        if contains_bad_word(msg.text) and not await is_admin(msg.chat.id, msg.from_user.id):
            await msg.delete()
            bot_message = await msg.answer(f"Сообщение пользователя *{msg.from_user.full_name}* было *удалено*.\nПричина: *использование нецензурной лексики*")
            asyncio.create_task(delete_after_delay(bot_message))

    if len(msg.text) <=3 and not await is_admin(msg.chat.id, msg.from_user.id):
        await msg.delete()
        await msg.answer(f"Сообщение пользователя *{msg.from_user.full_name}* было *удалено*.\nПричина: сообщение не может быть короче трех символов")
        asyncio.create_task(delete_after_delay(bot_message))