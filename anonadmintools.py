__version__ = (0, 1, 5)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only

import asyncio
import logging

from typing import Union
from datetime import timedelta
from telethon import functions
from telethon.errors import UserNotParticipantError, MessageIdInvalidError
from telethon.tl.types import (
    Channel,
    Chat,
    ChatAdminRights,
    Message,
    User,
    ChatBannedRights,
)
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    EditAdminRequest,
    InviteToChannelRequest,
    EditBannedRequest,
)
from aiogram.types import ChatPermissions
from aiogram.utils.exceptions import (
    MessageCantBeDeleted,
    MessageToDeleteNotFound,
    ChatNotFound,
    BotKicked,
)

from .. import loader, utils

logger = logging.getLogger(__name__)


async def is_linkedchannel(
    chat: Union[Chat, int],
    user: Union[User, int],
    message: Union[None, Message] = None,
):
    if isinstance(user, User):
        return False
    full_chat = await message.client(GetFullChannelRequest(channel=user.id))
    if full_chat.full_chat.linked_chat_id:
        return chat == int(full_chat.full_chat.linked_chat_id)


def represents_int(s: str) -> bool:
    try:
        loader.validators.Integer().validate(s)
        return True
    except loader.validators.ValidationError:
        return False

def represents_tgid(s: str) -> bool:
    try:
        loader.validators.TelegramID().validate(s)
        return True
    except loader.validators.ValidationError:
        return False

def to_bool(value: str) -> bool:
    try:
        loader.validators.Boolean().validate(value)
        if value.lower() in "true":
            return True
        return False
    except loader.validators.ValidationError:
        return None


@loader.tds
class ApodiktumAdminToolsMod(loader.Module):
    """Toolpack for Channel and Group Admins"""
    strings = {
        "name": "ApodiktumAdminTools",
        "dev_channel": "@apodiktum_modules",
        "not_dc": "<b>This is no Groupchat.</b>",
        "no_int": "<b>Your input was no int.</b>",
        "error": "<b>Your command was wrong.</b>",
        "permerror": "<b>You have no delete permissions in this chat.</b>",
        "no_id": "<b>Your input was no TG ID.</b>",
        "bnd_start": "<b>[BlockNonDiscussion]</b> Activated in this chat.</b>",
        "bnd_stopped": "<b>[BlockNonDiscussion]</b> Deactivated in this chat.</b>",
        "bnd_turned_off": "<b>[BlockNonDiscussion]</b> The module is now turned off in all chats.</b>",
        "bnd_settings": ("<b>[BlockNonDiscussion]</b> Current settings in this "
                         "chat are:\n{}."),
        "bnd_db_string": ("<b>[BlockNonDiscussion]</b> Current Database:\n\nWatcher:\n{}"
                          "\n\nChatsettings:\n{}"),
        "bnd_triggered": ("{}, the comments are limited to discussiongroup members, "
                          "please join our discussiongroup first."
                          "\n\n👉🏻 {}\n\nRespectfully, the admins."),
        "bcu_start": "<b>[BlockChannelUser]</b> Activated in this chat.</b>",
        "bcu_stopped": "<b>[BlockChannelUser]</b> Deactivated in this chat.</b>",
        "bcu_turned_off": "<b>[BlockChannelUser]</b> The module is now turned off in all chats.</b>",
        "bcu_settings": ("<b>[BlockChannelUser]</b> Current settings in this "
                         "chat are:\n{}."),
        "bcu_db_string": ("<b>[BlockChannelUser]</b> Current Database:\n\nWatcher:\n{}"
                          "\n\nChatsettings:\n{}"),
        "bcu_triggered": "{}, you can't write as a channel here.",
        "gl_start": "<b>[Grouplogger]</b> Activated in this chat.</b>",
        "gl_stopped": "<b>[Grouplogger]</b> Deactivated in this chat.</b>",
        "gl_turned_off": "<b>[Grouplogger]</b> The module is now turned off in all chats.</b>",
        "gl_settings": ("<b>[Grouplogger]</b> Current settings in this "
                         "chat are:\n{}."),
        "gl_db_string": ("<b>[Grouplogger]</b> Current Database:\n\nWatcher:\n{}"
                          "\n\nChatsettings:\n{}"),
    }

    strings_de = {
        "not_dc": "<b>Dies ist kein Gruppenchat.</b>",
        "no_int": "<b>Ihre Eingabe war keine Zahl.</b>",
        "error": "<b>Dein Befehl war falsch.</b>",
        "permerror": "<b>Sie haben in diesem Chat keine Löschberechtigung.</b>",
        "no_id": "<b>Ihre Eingabe war keine TG ID.</b>",
        "bnd_start": "<b>[BlockNonDiscussion]</b> In diesem Chat aktiviert.</b>",
        "bnd_stopped": "<b>[BlockNonDiscussion]</b> Der Chat wurde aus der Liste entfernt.</b>",
        "bnd_turned_off": "<b>[BlockNonDiscussion]</b> In allen Chats ausgeschaltet.</b>",
        "bnd_settings": ("<b>[BlockNonDiscussion - Settings]</b> Aktuelle Einstellungen in diesem "
                         "Chat:\n{}."),
        "bnd_db_string": ("<b>[BlockNonDiscussion - Settings]</b> Aktuelle Datenbank:\n\nWatcher:\n{}"
                          "\n\nChateinstellungen:\n{}"),
        "bnd_triggered": ("{}, die Kommentarfunktion wurde auf die Chatmitglieder begrenzt, "
                          "tritt bitte zuerst unserem Chat bei."
                          "\n\n👉🏻 {}\n\nHochachtungsvoll, die Obrigkeit."),
        "bcu_start": "<b>[BlockChannelUser]</b> In diesem Chat aktiviert.</b>",
        "bcu_stopped": "<b>[BlockChannelUser]</b> Der Chat wurde aus der Liste entfernt.</b>",
        "bcu_turned_off": "<b>[BlockChannelUser]</b> In allen Chats ausgeschaltet.</b>",
        "bcu_settings": ("<b>[BlockChannelUser]</b> Aktuelle Einstellungen in diesem "
                         "Chat:\n{}."),
        "bcu_db_string": ("<b>[BlockChannelUser]</b> Aktuelle Datenbank:\n\nWatcher:\n{}"
                          "\n\nChateinstellungen:\n{}"),
        "bcu_triggered": "{}, du kannst hier nicht als Kanal schreiben.",
        "gl_start": "<b>[Grouplogger]</b> In diesem Chat aktiviert.</b>",
        "gl_stopped": "<b>[Grouplogger]</b> Der Chat wurde aus der Liste entfernt.</b>",
        "gl_turned_off": "<b>[Grouplogger]</b> In allen Chats ausgeschaltet.</b>",
        "gl_settings": ("<b>[Grouplogger]</b> Aktuelle Einstellungen in diesem "
                         "Chat:\n{}."),
        "gl_db_string": ("<b>[Grouplogger]</b> Aktuelle Datenbank:\n\nWatcher:\n{}"
                          "\n\nChateinstellungen:\n{}"),

    }

    strings_ru = {
        "not_dc": "<b>Это не групповой чат</b>",
        "no_int": "<b>Ваш ввод не является целочисленным типом (int)</b>",
        "error": "<b>Неверная команда</b>",
        "permerror": "<b>Вы не имеете права на удаление сообщений в этом чате</b>",
        "no_id": "<b>Ты ввёл не телеграм айди.</b>",
        "bnd_start": "<b>[BlockNonDiscussion]</b> Активировано в этом чате</b>",
        "bnd_stopped": "<b>[BlockNonDiscussion]</b> Деактивировано в этом чате</b>",
        "bnd_turned_off": "<b>[BlockNonDiscussion]</b> Теперь этот модуль выключен во всех чатах</b>",
        "bnd_settings": ("<b>[BlockNonDiscussion]</b> Текущие настройки "
                         "в этом чате:\n{}."),
        "bnd_db_string": ("<b>[BlockNonDiscussion]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                          "\n\Настройки чата:\n{}"),
        "bnd_triggered": ("{}, комментарии ограничены для участников группы обсуждения, "
                          "Пожалуйста, для начала присоединитесь к нашей группе обсуждения."
                          "\n\n👉🏻 {}\n\nС уважением, администраторы."),
        "bcu_start": "<b>[BlockChannelUser]</b> Активировано в этом чате</b>",
        "bcu_stopped": "<b>[BlockChannelUser]</b> Деактивировано в этом чате</b>",
        "bcu_turned_off": "<b>[BlockChannelUser]</b> Теперь этот модуль выключен во всех чатах</b>",
        "bcu_settings": ("<b>[BlockChannelUser]</b> Текущие настройки "
                         "в этом чате:\n{}."),
        "bcu_db_string": ("<b>[BlockChannelUser]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                          "\n\Настройки чата:\n{}"),
        "bcu_triggered": "{}, ты не можешь писать тут от имени канала.",
        "gl_start": "<b>[Grouplogger]</b> Активировано в этом чате</b>",
        "gl_stopped": "<b>[Grouplogger]</b> Деактивировано в этом чате</b>",
        "gl_turned_off": "<b>[Grouplogger]</b> Теперь этот модуль выключен во всех чатах</b>",
        "gl_settings": ("<b>[Grouplogger]</b> Текущие настройки "
                         "в этом чате:\n{}."),
        "gl_db_string": ("<b>[Grouplogger]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                          "\n\Настройки чата:\n{}"),
    }

    _global_queue = []

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._pt_task = asyncio.ensure_future(self._global_queue_handler())

    async def on_unload(self):
        self._pt_task.cancel()
        return

    async def _mute(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
        MUTETIMER: int = 0,
        UseBot: bool = False,
    ):
        if UseBot:
            try:
                await self.inline.bot.restrict_chat_member(
                    int(f"-100{getattr(chat, 'id', chat)}"),
                    user.id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=timedelta(minutes=MUTETIMER),
                )
                return
            except Exception:
                pass
        await message.client.edit_permissions(chat.id, user.id,
                                              timedelta(minutes=MUTETIMER), send_messages=False)
        return

    async def _ban(
        self,
        chat: Union[Chat, int],
    ):
        try:
            await self.inline.bot.kick_chat_member(
                int(f"-100{getattr(chat, 'id', chat)}"),
                user.id
            )
        except Exception:
            pass

    async def _delete_message(
        self,
        chat: Union[Chat, int],
        message: Union[None, Message] = None,
        UseBot: bool = False,
    ):
        chat_id = getattr(chat, 'id', chat)
        if UseBot:
            try:
                await self.inline.bot.delete_message(
                    int(f"-100{chat_id}"),
                    message.id,
                )
                return
            except MessageToDeleteNotFound:
                pass
            except (MessageCantBeDeleted, BotKicked, ChatNotFound):
                pass
        return await message.delete()

    async def _promote_bot(
        self,
        chat_id: Union[Chat, int],
    ):
        try:
            await self._client(InviteToChannelRequest(chat_id, [self.inline.bot_username]))
        except Exception:
            logger.warning("Unable to invite cleaner to chat. Maybe he's already there?")  # fmt: skip

        try:
            await self._client(
                EditAdminRequest(
                    channel=chat_id,
                    user_id=self.inline.bot_username,
                    admin_rights=ChatAdminRights(
                        ban_users=True, delete_messages=True
                    ),
                    rank="Bot",
                )
            )

            return True
        except Exception:
            logger.exception("Cleaner promotion failed!")
            return False

    async def _check_inlinebot(
        self,
        chat: Union[Chat, int],
        inline_bot_id: Union[None, int],
        self_id: Union[None, int],
        message: Union[None, Message] = None,
    ):
        chat_id = getattr(chat, 'id', chat)
        if chat_id != self_id:
            try:
                bot_perms = await message.client.get_permissions(chat_id, inline_bot_id)
                if bot_perms.is_admin and bot_perms.ban_users and bot_perms.delete_messages:
                    return True
                if await self._promote_bot(chat_id):
                    return True
                return False
            except UserNotParticipantError:
                return bool(chat.admin_rights.add_admins and await self._promote_bot(chat_id))

    async def _is_member(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        self_id: Union[None, int],
        message: Union[None, Message] = None,
    ):
        if chat != self_id:
            try:
                await message.client.get_permissions(chat, user)
                return True
            except UserNotParticipantError:
                return False

    def _get_tag(
        self,
        user: Union[User, int],
    ):
        if isinstance(user, Channel):
            return (
                f"<a href=tg://resolve?domain={user.username}>{user.title}</a> (<code>{str(user.id)}</code>)"
                if user.username
                else f"{user.title}(<code>{str(user.id)}</code>)"
            )
        return f"<a href=tg://user?id={str(user.id)}>{user.first_name}</a> (<code>{str(user.id)}</code>)"

    async def _get_invite_link(
        self,
        chat: Union[Chat, int],
        message: Union[None, Message] = None,
    ):
        if chat.username:
            link = f"https://t.me/{chat.username}"
        elif chat.admin_rights.invite_users:
            link = await message.client(GetFullChannelRequest(channel=chat.id))
            link = link.full_chat.exported_invite.link
        else:
            link = ""
        return link

    async def bndcmd(self, message: Message):
        """Available commands:
           .bnd
             - Toggles the module for the current chat.
           .bnd notify <true/false>
             - Toggles the notification message.
           .bnd mute <minutes/or 0>
             - Mutes the user for x minutes. 0 to disable.
           .bnd deltimer <seconds/or 0>
             - Deletes the notification message in seconds. 0 to disable.
           .bnd settings
             - Shows the current configuration of the chat.
           .bnd db
             - Shows the current database.
           .bnd clearall
             - Clears the db of the module"""
        bnd = self._db.get(__name__, "bnd", [])
        sets = self._db.get(__name__, "bnd_sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await self._client.get_entity(message.chat)
        chatid = chat.id
        chatid_str = str(chatid)

        if args and args[0] == "clearall":
            self._db.set(__name__, "bnd", [])
            self._db.set(__name__, "bnd_sets", {})
            return await utils.answer(message, self.strings("bnd_turned_off"))

        if args and args[0] == "db":
            return await utils.answer(message, self.strings("bnd_db_string").format(str(bnd), str(sets)))

        if message.is_private:
            await utils.answer(message, self.strings("not_dc"))
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(message, self.strings("permerror"))

        if not args:
            if chatid_str not in bnd:
                bnd.append(chatid_str)
                sets.setdefault(chatid_str, {})
                sets[chatid_str].setdefault("notify", True)
                sets[chatid_str].setdefault("mute", 1)
                sets[chatid_str].setdefault("deltimer", 60)
                self._db.set(__name__, "bnd", bnd)
                self._db.set(__name__, "bnd_sets", sets)
                return await utils.answer(message, self.strings("bnd_start"))
            bnd.remove(chatid_str)
            sets.pop(chatid_str)
            self._db.set(__name__, "bnd", bnd)
            self._db.set(__name__, "bnd_sets", sets)
            return await utils.answer(message, self.strings("bnd_stopped"))

        if chatid_str in bnd:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(to_bool(args[1]), bool):
                    return await utils.answer(message, self.strings("error"))
                sets[chatid_str].update({"notify": to_bool(args[1])})
            elif args[0] == "mute" and args[1] is not None and chatid_str in bnd:
                if not represents_int(args[1]):
                    return await utils.answer(message, self.strings("no_int"))
                sets[chatid_str].update({"mute": args[1].capitalize()})
            elif args[0] == "deltimer" and args[1] is not None and chatid_str in bnd:
                if not represents_int(args[1]):
                    return await utils.answer(message, self.strings("no_int"))
                sets[chatid_str].update({"deltimer": args[1]})
            elif args[0] != "settings" and chatid_str in bnd:
                return
            self._db.set(__name__, "bnd_sets", sets)
            return await utils.answer(message, self.strings("bnd_settings").format(str(sets[chatid_str])))

    async def bcucmd(self, message: Message):
        """Available commands:
           .bcu
             - Toggles the module for the current chat.
           .bcu notify <true/false>
             - Toggles the notification message.
           .bcu ban <minutes/or 0>
            - Bans the user for x minutes. 0 to disable.
           .bcu deltimer <seconds/or 0>
            - Deletes the notification message in seconds. 0 to disable.
           .bnd settings
             - Shows the current configuration of the chat.
           .bnd db
             - Shows the current database.
           .bcu clearall
            - Clears the db of the module"""
        bcu = self._db.get(__name__, "bcu", [])
        sets = self._db.get(__name__, "bcu_sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await self._client.get_entity(message.chat)
        chatid = chat.id
        chatid_str = str(chatid)

        if args and args[0] == "clearall":
            self._db.set(__name__, "bcu", [])
            self._db.set(__name__, "bcu_sets", {})
            return await utils.answer(message, self.strings("bcu_turned_off", message))

        if args and args[0] == "db":
            return await utils.answer(message, self.strings("bcu_db_string").format(str(bcu), str(sets)))

        if message.is_private:
            await utils.answer(message, self.strings("not_dc", message))
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(message, self.strings("permerror", message))

        if not args:
            if chatid_str not in bcu:
                bcu.append(chatid_str)
                sets.setdefault(chatid_str, {})
                sets[chatid_str].setdefault("notify", True)
                sets[chatid_str].setdefault("ban", False)
                sets[chatid_str].setdefault("deltimer", 60)
                self._db.set(__name__, "bcu", bcu)
                self._db.set(__name__, "bcu_sets", sets)
                return await utils.answer(message, self.strings("bcu_start", message))
            bcu.remove(chatid_str)
            sets.pop(chatid_str)
            self._db.set(__name__, "bcu", bcu)
            self._db.set(__name__, "bcu_sets", sets)
            return await utils.answer(message, self.strings("bcu_stopped", message))

        if chatid_str in bcu:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(to_bool(args[1]), bool):
                    return await utils.answer(message, self.strings("error", message))
                sets[chatid_str].update({"notify": to_bool(args[1])})
            elif args[0] == "ban" and args[1] is not None and chatid_str in bcu:
                if not isinstance(to_bool(args[1]), bool):
                    return await utils.answer(message, self.strings("no_int", message))
                sets[chatid_str].update({"ban": to_bool(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chatid_str in bcu:
                if not represents_int(args[1]):
                    return await utils.answer(message, self.strings("no_int", message))
                sets[chatid_str].update({"deltimer": args[1]})
            elif args[0] != "settings" and chatid_str in bcu:
                return
            self._db.set(__name__, "bcu_sets", sets)
            return await utils.answer(message, self.strings("bcu_settings").format(str(sets[chatid_str])))

    async def glcmd(self, message: Message):
        """Available commands:
           .gl <chatid> <logchannelid>
             - Logs given groupchat in given channel.
           .gl rem <chatid>
             - Removes given chat from watcher.
           .gl db
             - Shows the current database.
           .gl settings
             - Shows the current configuration of the chat.
           .gl clearall
             - Clears the db of the module."""

        gl = self._db.get(__name__, "gl", [])
        sets = self._db.get(__name__, "gl_sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await self._client.get_entity(message.chat)

        if args and args[0] == "clearall":
            self._db.set(__name__, "gl", [])
            self._db.set(__name__, "gl_sets", {})
            return await utils.answer(message, self.strings("gl_turned_off", message))

        if args and args[0] == "db":
            return await utils.answer(message, self.strings("gl_db_string").format(str(gl), str(sets)))

        if args[0] is not None and represents_tgid(args[0]):
            chatid = args[0]
            chatid_str = str(chatid)
        elif args[0] == "rem":
            chatid = args[1]
            chatid_str = str(chatid)
        elif args[0] == "db":
            return await utils.answer(message, self.strings("gl_db_string").format(str(sets)))
        elif args[0] != "clearall":
            return await utils.answer(message, self.strings("error"))
        elif not args:
            return await utils.answer(message, self.strings("error"))
        if args:
            if args[0] == "rem" and represents_tgid(args[1]) and chatid_str in gl:
                gl.remove(chatid_str)
                sets.pop(chatid_str)
                self._db.set(__name__, "gl", gl)
                self._db.set(__name__, "gl_sets", sets)
                return await utils.answer(message, self.strings("gl_stopped"))
            if args[0] == "rem" and (represents_tgid(args[1]) or chatid_str not in gl):
                return await utils.answer(message, self.strings("error"))
        if not represents_tgid(chatid_str):
            return await utils.answer(message, self.strings("error"))
        if chatid_str not in gl:
            if not represents_tgid(args[0]) or not represents_tgid(args[1]):
                return await utils.answer(message, self.strings("no_id"))
            gl.append(chatid_str)
            sets.setdefault(chatid_str, {})
            sets[chatid_str].setdefault("logchannel", args[1])
            self._db.set(__name__, "gl", gl)
            self._db.set(__name__, "gl_sets", sets)
            return await utils.answer(message, self.strings("gl_start"))
        if args[0] is not None and args[1] is not None:
            if not represents_tgid(args[0]) or not represents_tgid(args[1]):
                return await utils.answer(message, self.strings("no_id"))
            sets[chatid_str].update({"logchannel": args[1]})
        elif args[0] != "settings" and chatid_str in gl:
            return
        self._db.set(__name__, "gl_sets", sets)
        return await utils.answer(message, self.strings("gl_settings").format(str(sets[chatid_str])))

    async def p__bcu(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
        bcu: list = None,
        bcu_sets: dict = None,
    ) -> bool:
        chatid_str = str(chat.id)
        if message.is_private or chatid_str not in bcu or not isinstance(user, Channel):
            return
        UseBot = await self._check_inlinebot(chat, self.inline.bot_id, self._tg_id, message)
        if (
            (chat.admin_rights or chat.creator)
            and (not chat.admin_rights.delete_messages
                 or not chat.admin_rights)
        ):
            return
        usertag = self._get_tag(user)

        if await is_linkedchannel(user, chat.id, message):
            return
        await self._delete_message(chat, message, UseBot)
        if bcu_sets[chatid_str].get("ban") is True:
            if UseBot:
                await self._ban(chat)
            else:
                await message.client(EditBannedRequest(chat.id, user.id, ChatBannedRights(view_messages=False)))
        if bcu_sets[chatid_str].get("notify") is True:
            msgs = await utils.answer(message, self.strings("bcu_triggered", message).format(usertag))
            if bcu_sets[chatid_str].get("deltimer") != "0":
                DELTIMER = int(bcu_sets[chatid_str].get("deltimer"))
                await asyncio.sleep(DELTIMER)
                await self._delete_message(chat, msgs, UseBot)
        return

    async def p__bnd(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
        bnd: list = None,
        bnd_sets: dict = None,
    ) -> bool:
        chatid_str = str(chat.id)
        if message.is_private or chatid_str not in bnd or not isinstance(user, User):
            return
        UseBot = await self._check_inlinebot(chat, self.inline.bot_id, self._tg_id, message)
        if (
            (chat.admin_rights or chat.creator)
            and (not chat.admin_rights.delete_messages
                 or not chat.admin_rights)
        ):
            return
        usertag = self._get_tag(user)
        link = await self._get_invite_link(chat, message)

        if not await self._is_member(chat.id, user.id, self._tg_id, message):
            await self._delete_message(chat, message, UseBot)
            if (
                chat.admin_rights.ban_users
                and bnd_sets[chatid_str].get("mute") is not None
                and bnd_sets[chatid_str].get("mute") != "0"
            ):
                MUTETIMER = bnd_sets[chatid_str].get("mute")
                await self._mute(chat, user, message, MUTETIMER, UseBot)
            if bnd_sets[chatid_str].get("notify") is True:
                msgs = await utils.answer(message, self.strings("bnd_triggered").format(usertag, link))
                if bnd_sets[chatid_str].get("deltimer") != "0":
                    DELTIMER = int(bnd_sets[chatid_str].get("deltimer"))
                    await asyncio.sleep(DELTIMER)
                    await self._delete_message(chat, msgs, UseBot)
        return








    async def p__gl(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
        gl: list = None,
        gl_sets: dict = None,
    ) -> bool:
        chatid_str = str(chat.id)
        if message.is_private or chatid_str not in gl:
            return
        logchan_id = int(gl_sets[chatid_str].get("logchannel"))
        # chatsender = await message.get_sender()
        # if chatsender is None:
        #     return
        # sender_tag = self._get_tag(chatsender)
        chat_tag = self._get_tag(chat)
        user_tag = self._get_tag(user)
        link = (
            f"Chat: {chat_tag} | #{str(chat.id)}"
            + "\nUser: "
            + str(user_tag)
            + " ID: " + str(user.id)
        )

        try:
            await message.forward_to(logchan_id)
            await message.client.send_message(logchan_id, link)
            return
        except Exception as e:
            if "FORWARDS_RESTRICTED" in str(e):
                msgs = await message.client.get_messages(chat.id, ids=message.id)
                await message.client.send_message(logchan_id, message=msgs)
                await message.client.send_message(logchan_id, link)
            return
            








        chatid_str = str(chat.id)
        if message.is_private or chatid_str not in bnd or not isinstance(user, User):
            return
        UseBot = await self._check_inlinebot(chat, self.inline.bot_id, self._tg_id, message)
        if (
            (chat.admin_rights or chat.creator)
            and (not chat.admin_rights.delete_messages
                 or not chat.admin_rights)
        ):
            return
        usertag = self._get_tag(user)
        link = await self._get_invite_link(chat, message)

        if not await self._is_member(chat.id, user.id, self._tg_id, message):
            await self._delete_message(chat, message, UseBot)
            if (
                chat.admin_rights.ban_users
                and bnd_sets[chatid_str].get("mute") is not None
                and bnd_sets[chatid_str].get("mute") != "0"
            ):
                MUTETIMER = bnd_sets[chatid_str].get("mute")
                await self._mute(chat, user, message, MUTETIMER, UseBot)
            if bnd_sets[chatid_str].get("notify") is True:
                msgs = await utils.answer(message, self.strings("bnd_triggered").format(usertag, link))
                if bnd_sets[chatid_str].get("deltimer") != "0":
                    DELTIMER = int(bnd_sets[chatid_str].get("deltimer"))
                    await asyncio.sleep(DELTIMER)
                    await self._delete_message(chat, msgs, UseBot)
        return









    async def watcher(self, message: Message):
        self._global_queue += [message]

    async def _global_queue_handler(self):
        while True:
            while self._global_queue:
                await self._global_queue_handler_process(self._global_queue.pop(0))
            await asyncio.sleep(0)

    async def _global_queue_handler_process(self, message: Message):
        if not isinstance(getattr(message, "chat", 0), (Chat, Channel)) or not isinstance(message, Message):
            return
        chat_id = utils.get_chat_id(message)
        try:
            user_id = (
                getattr(message, "sender_id", False)
                or message.action_message.action.users[0]
            )
        except Exception:
            try:
                user_id = message.action_message.action.from_id.user_id
            except Exception:
                try:
                    user_id = message.from_id.user_id
                except Exception:
                    try:
                        user_id = message.action_message.from_id.user_id
                    except Exception:
                        try:
                            user_id = message.action.from_user.id
                        except Exception:
                            try:
                                user_id = (await message.get_user()).id
                            except Exception:
                                logger.debug(f"Can't extract entity from event {type(message)}")
                                return
        user_id = (
            int(str(user_id)[4:]) if str(user_id).startswith("-100") else int(user_id)
        )
        bnd = self._db.get(__name__, "bnd", [])
        bnd_sets = self._db.get(__name__, "bnd_sets", {})
        bcu = self._db.get(__name__, "bcu", [])
        bcu_sets = self._db.get(__name__, "bcu_sets", {})
        gl = self._db.get(__name__, "gl", [])
        gl_sets = self._db.get(__name__, "gl_sets", {})
        if str(chat_id) in bnd or str(chat_id) in bcu or str(user_id) in gl:
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            asyncio.get_event_loop().create_task(self.p__gl(chat, user, message, gl, gl_sets))
            asyncio.get_event_loop().create_task(self.p__bnd(chat, user, message, bnd, bnd_sets))
            asyncio.get_event_loop().create_task(self.p__bcu(chat, user, message, bcu, bcu_sets))
        return
