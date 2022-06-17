__version__ = (0, 1, 0)


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
from telethon.errors import UserNotParticipantError
from telethon.tl.types import (
    Channel,
    Chat,
    ChatAdminRights,
    Message,
    User,
    ChatBannedRights,
)
from telethon.tl.functions.channels import (
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


async def is_linkedchannel(e, c, u, message):
    if isinstance(e, User):
        return False
    full_chat = await message.client(functions.channels.GetFullChannelRequest(channel=u))
    if full_chat.full_chat.linked_chat_id:
        return c == int(full_chat.full_chat.linked_chat_id)


def represents_int(s):
    try:
        loader.validators.Integer().validate(s)
        return True
    except loader.validators.ValidationError:
        return False


def to_bool(value):
    try:
        loader.validators.Boolean().validate(value)
        if str(value).lower() in ("true"):
            return True
        return False
    except loader.validators.ValidationError:
        return None


async def is_member(c, u, message):
    if c != (await message.client.get_me(True)).user_id:
        try:
            await message.client.get_permissions(c, u)
            return True
        except UserNotParticipantError:
            return False


@loader.tds
class AnonAdminToolsMod(loader.Module):
    """Toolpack for Channel and Group Admins"""
    strings = {
        "name": "AnonAdminTools",
        "dev_channel": "@apodiktum_modules",
        "not_dc": "<b>This is no Groupchat.</b>",
        "no_int": "<b>Your input was no int.</b>",
        "error": "<b>Your command was wrong.</b>",
        "permerror": "<b>You have no delete permissions in this chat.</b>",
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
        "bcu_db_string": ("<b>[BlockChannelUser]</b> Aktuelle Datenbank:\n\nWatcher:\n{}"
                          "\n\nChateinstellungen:\n{}"),
        "bcu_triggered": "{}, you can't write as a channel here.",
    }

    strings_de = {
        "not_dc": "<b>Dies ist kein Gruppenchat.</b>",
        "no_int": "<b>Ihre Eingabe war keine Zahl.</b>",
        "error": "<b>Dein Befehl war falsch.</b>",
        "permerror": "<b>Sie haben in diesem Chat keine Löschberechtigung.</b>",
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
        "bcu_triggered": "{}, ты не можешь писать тут от имени канала.",
    }

    strings_ru = {
        "not_dc": "<b>Это не групповой чат</b>",
        "no_int": "<b>Ваш ввод не является целочисленным типом (int)</b>",
        "error": "<b>Неверная команда</b>",
        "permerror": "<b>Вы не имеете права на удаление сообщений в этом чате</b>",
        "bnd_start": "<b>[BlockNonDiscussion]</b> Активировано в этом чате</b>",
        "bnd_stopped": "<b>[BlockNonDiscussion]</b> Деактивировано в этом чате</b>",
        "bnd_turned_off": "<b>[BlockNonDiscussion]</b> Теперь этот модуль выключен во всех чатах</b>",
        "bnd_settings": ("<b>[BlockNonDiscussion]</b> Текущие настройки "
                         "в этом чате:\n{}."),
        "bnd_db_string": ("<b>[BlockNonDiscussion]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                          "\n\nChatsettings:\n{}"),
        "bnd_triggered": ("{}, комментарии ограничены для участников группы обсуждения, "
                          "Пожалуйста, для начала присоединитесь к нашей группе обсуждения."
                          "\n\n👉🏻 {}\n\nС уважением, администраторы."),
        "bcu_start": "<b>[BlockChannelUser]</b> Активировано в этом чате</b>",
        "bcu_stopped": "<b>[BlockChannelUser]</b> Деактивировано в этом чате</b>",
        "bcu_turned_off": "<b>[BlockChannelUser]</b> Теперь этот модуль выключен во всех чатах</b>",
        "bcu_settings": ("<b>[BlockChannelUser]</b> Текущие настройки "
                         "в этом чате:\n{}."),
        "bcu_db_string": ("<b>[BlockChannelUser]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                          "\n\nChatsettings:\n{}"),
        "bcu_triggered": "",
    }

    _global_queue = []

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    async def _mute(
        self,
        chat: Union[Chat, int],
        userid,
        MUTETIMER,
    ):
        try:
            await self.inline.bot.restrict_chat_member(
                int(f"-100{getattr(chat, 'id', chat)}"),
                userid,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=timedelta(minutes=MUTETIMER),
            )
        except Exception:
            pass

    async def _ban(
        self,
        chat: Union[Chat, int],
        userid,
    ):
        try:
            await self.inline.bot.kick_chat_member(
                int(f"-100{getattr(chat, 'id', chat)}"),
                userid
            )
        except Exception:
            pass

    async def _delete_message(
        self,
        chat: Union[Chat, int],
        message: Union[None, Message] = None,
    ):
        chat_id = getattr(chat, 'id', chat)
        try:
            await self.inline.bot.delete_message(
                int(f"-100{chat_id}"),
                message.id,
            )
        except MessageToDeleteNotFound:
            pass
        except (MessageCantBeDeleted, BotKicked, ChatNotFound):
            pass

    async def _promote_bot(self, chat_id: int):
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

    async def _check_inlinebot(self, chat, inline_bot_id, message):
        chat_id = getattr(chat, 'id', chat)
        if chat_id != (await message.client.get_me(True)).user_id:
            try:
                bot_perms = await message.client.get_permissions(chat_id, inline_bot_id)
                if bot_perms.is_admin and bot_perms.ban_users and bot_perms.delete_messages:
                    return True
                if await self._promote_bot(chat_id):
                    return True
                return False
            except UserNotParticipantError:
                return bool(chat.admin_rights.add_admins and await self._promote_bot(chat_id))

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

    async def bcucmd(self, message):
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

    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return
        bnd = self._db.get(__name__, "bnd", [])
        bnd_sets = self._db.get(__name__, "bnd_sets", {})
        bcu = self._db.get(__name__, "bcu", [])
        bcu_sets = self._db.get(__name__, "bcu_sets", {})
        chat_id = message.chat.id
        chatid_str = str(chat_id)
        if message.is_private or (chatid_str not in bnd and chatid_str not in bcu):
            return
        chat = await self._client.get_entity(message.chat)
        user = await self._client.get_entity(message.sender_id)
        user_id = user.id
        inline_bot_id = self.inline.bot_id
        UseBot = await self._check_inlinebot(chat, inline_bot_id, message)
        if (
            (chat.admin_rights or chat.creator)
            and (not chat.admin_rights.delete_messages
                 or not chat.admin_rights)
        ):
            return
        if isinstance(user, Channel):
            if user.username:
                usertag = (
                    (
                        f"<a href=https://t.me/{user.username}>{user.title}"
                        + "</a> (<code>"
                    )
                    + str(user_id)
                    + "</code>)"
                )
            else:
                usertag = (
                    (
                        f"{user.title}"
                        + "(<code>"
                    )
                    + str(user_id)
                    + "</code>)"
                )
        else:
            usertag = (
                (
                    f"<a href=tg://user?id={str(user_id)}>{user.first_name}"
                    + "</a> (<code>"
                )
                + str(user_id)
                + "</code>)"
            )
        if chat.username:
            link = f"https://t.me/{chat.username}"

        elif chat.admin_rights.invite_users:
            link = await message.client(functions.channels.GetFullChannelRequest(channel=chat_id))
            link = link.full_chat.exported_invite.link
        else:
            link = ""

        if chatid_str in bcu and isinstance(user, Channel):
            if await is_linkedchannel(user, chat_id, user_id, message):
                return
            if UseBot:
                await self._delete_message(chat, message)
            else:
                await message.delete()
            if bcu_sets[chatid_str].get("ban") is True:
                if UseBot:
                    await self._ban(chat, user_id)
                else:
                    await message.client(EditBannedRequest(chat_id, user_id, ChatBannedRights(view_messages=False)))
            if bcu_sets[chatid_str].get("notify") is True:
                msgs = await utils.answer(message, self.strings("bcu_triggered", message).format(usertag))
                if bcu_sets[chatid_str].get("deltimer") != "0":
                    DELTIMER = int(bcu_sets[chatid_str].get("deltimer"))
                    await asyncio.sleep(DELTIMER)
                    await message.client.delete_messages(chat_id, msgs)

            return

        if chatid_str in bnd and isinstance(user, User):
            if not await is_member(chat_id, user_id, message):
                if UseBot:
                    await self._delete_message(chat, message)
                else:
                    await message.delete()
                if (
                    chat.admin_rights.ban_users
                    and bnd_sets[chatid_str].get("mute") is not None
                    and bnd_sets[chatid_str].get("mute") != "0"
                ):
                    MUTETIMER = bnd_sets[chatid_str].get("mute")
                    if UseBot:
                        await self._mute(chat, user_id, MUTETIMER)
                    else:
                        await message.client.edit_permissions(chat_id, user_id,
                                                              timedelta(minutes=MUTETIMER), send_messages=False)
                if bnd_sets[chatid_str].get("notify") is True:
                    msgs = await utils.answer(message, self.strings("bnd_triggered").format(usertag, link))
                    if bnd_sets[chatid_str].get("deltimer") != "0":
                        DELTIMER = int(bnd_sets[chatid_str].get("deltimer"))
                        await asyncio.sleep(DELTIMER)
                        if UseBot:
                            await self._delete_message(chat, msgs)
                        else:
                            await message.client.delete_messages(chat_id, msgs)
            return
