__version__ = (0, 1, 7)


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

from datetime import timedelta
from telethon import functions
from telethon.tl.types import User, Channel, Message
from telethon.errors import UserNotParticipantError

from .. import loader, utils

logger = logging.getLogger(__name__)


async def is_linkedchannel(e, c, u, message):
    if isinstance(e, User):
        return False
    full_chat = await message.client(functions.channels.GetFullChannelRequest(channel=u))
    return c == int(str(-100) + str(full_chat.full_chat.linked_chat_id))


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def to_bool(value):
    if str(value).lower() in ("true"):
        return True
    if str(value).lower() in ("false"):
        return False
    return None


def replaced(sequence, old, new):
    return (new if x == old else x for x in sequence)


async def is_member(c, u, message):
    if c != (await message.client.get_me(True)).user_id:
        try:
            await message.client.get_permissions(c, u)
            return True
        except UserNotParticipantError:
            return False


@loader.tds
class BlockNonDiscussionMod(loader.Module):
    """
    Block Comments For Non Discussion Members
    Will not be updated any further! Download ApodiktumAdminTools instead!
    """
    strings = {
        "name": "BlockNonDiscussion",
        "dev_channel": "@apodiktum_modules",
        "not_dc": "<b>This is no Groupchat.</b>",
        "start": "<b>[BlockNonDiscussion]</b> Activated in this chat.</b>",
        "stopped": "<b>[BlockNonDiscussion]</b> Deactivated in this chat.</b>",
        "turned_off": "<b>[BlockNonDiscussion]</b> The module is now turned off in all chats.</b>",
        "no_int": "<b>Your input was no int.</b>",
        "error": "<b>Your command was wrong.</b>",
        "permerror": "<b>You have no delete permissions in this chat.</b>",
        "settings": ("<b>[BlockNonDiscussion - Settings]</b> Current settings in this "
                     "chat are:\n{}."),
        "db_string": ("<b>[BlockNonDiscussion - Settings]</b> Current Database:\n\nWatcher:\n{}"
                      "\n\nChatsettings:\n{}"),
        "triggered": ("{}, the comments are limited to discussiongroup members, "
                      "please join our discussiongroup first."
                      "\n\n👉🏻 {}\n\nRespectfully, the admins."),
    }

    strings_de = {
        "name": "BlockNonDiscussion",
        "not_dc": "<b>Dies ist kein Gruppenchat.</b>",
        "start": "<b>[BlockNonDiscussion]</b> In diesem Chat aktiviert.</b>",
        "stopped": "<b>[BlockNonDiscussion]</b> Der Chat wurde aus der Liste entfernt.</b>",
        "turned_off": "<b>[BlockNonDiscussion]</b> In allen Chats ausgeschaltet.</b>",
        "no_int": "<b>Ihre Eingabe war keine Zahl.</b>",
        "error": "<b>Dein Befehl war falsch.</b>",
        "permerror": "<b>Sie haben in diesem Chat keine Löschberechtigung.</b>",
        "settings": ("<b>[BlockNonDiscussion - Settings]</b> Aktuelle Einstellungen in diesem "
                     "Chat:\n{}."),
        "db_string": ("<b>[BlockNonDiscussion - Settings]</b> Aktuelle Datenbank:\n\nWatcher:\n{}"
                      "\n\nChateinstellungen:\n{}"),
        "triggered": ("{}, die Kommentarfunktion wurde auf die Chatmitglieder begrenzt, "
                      "tritt bitte zuerst unserem Chat bei."
                      "\n\n👉🏻 {}\n\nHochachtungsvoll, die Obrigkeit."),
    }

    strings_ru = {
        "not_dc": "<b>Это не групповой чат</b>",
        "start": "<b>[BlockNonDiscussion]</b> Активировано в этом чате</b>",
        "stopped": "<b>[BlockNonDiscussion]</b> Деактивировано в этом чате</b>",
        "turned_off": "<b>[BlockNonDiscussion]</b> Теперь этот модуль выключен во всех чатах</b>",
        "no_int": "<b>Ваш ввод не является целочисленным типом (int)</b>",
        "error": "<b>Неверная команда</b>",
        "permerror": "<b>Вы не имеете права на удаление сообщений в этом чате</b>",
        "settings": ("<b>[BlockNonDiscussion - Settings]</b> Текущие настройки "
                     "в этом чате:\n{}."),
        "db_string": ("<b>[BlockNonDiscussion - Settings]</b> Текущая база данных:\n\nНаблюдающий:\n{}"
                      "\n\nChatsettings:\n{}"),
        "triggered": ("{}, комментарии ограничены для участников группы обсуждения, "
                      "Пожалуйста, для начала присоединитесь к нашей группе обсуждения."
                      "\n\n👉🏻 {}\n\nС уважением, администраторы."),
        "translated_by": "@MUTANTP7AY3R5",
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

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
        sets = self._db.get(__name__, "sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await message.get_chat()
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)

        if args and args[0] == "clearall":
            self._db.set(__name__, "bnd", [])
            self._db.set(__name__, "sets", {})
            return await utils.answer(message, self.strings("turned_off"))

        if args and args[0] == "db":
            return await utils.answer(message, self.strings("db_string").format(str(bnd), str(sets)))

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
                self._db.set(__name__, "sets", sets)
                return await utils.answer(message, self.strings("start"))
            bnd.remove(chatid_str)
            sets.pop(chatid_str)
            self._db.set(__name__, "bnd", bnd)
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("stopped"))

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
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("settings").format(str(sets[chatid_str])))

    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return
        bnd = self._db.get(__name__, "bnd", [])
        sets = self._db.get(__name__, "sets", {})
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if message.is_private or chatid_str not in bnd:
            return
        chat = await message.get_chat()
        user = await message.get_sender()
        userid = message.sender_id
        entity = await self._client.get_entity(message.sender_id)

        if (await is_linkedchannel(entity, chatid, userid, message)) or isinstance(entity, Channel):
            return
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return
        usertag = (
            (
                f"<a href=tg://user?id={str(userid)}>{user.first_name}"
                + "</a> (<code>"
            )
            + str(userid)
            + "</code>)"
        )

        if (await self._client.get_entity(chatid)).username:
            link = f"https://t.me/{str((await self._client.get_entity(chatid)).username)}"

        elif chat.admin_rights.invite_users:
            link = await message.client(functions.channels.GetFullChannelRequest(channel=chatid))
            link = link.full_chat.exported_invite.link
        else:
            link = ""
        if not await is_member(chatid, userid, message):
            await message.delete()
            if (
                chat.admin_rights.ban_users
                and sets[chatid_str].get("mute") is not None
                and sets[chatid_str].get("mute") != "0"
            ):
                MUTETIMER = sets[chatid_str].get("mute")
                await message.client.edit_permissions(chatid, userid,
                                                      timedelta(minutes=MUTETIMER), send_messages=False)
            if sets[chatid_str].get("notify") is True:
                msgs = await utils.answer(message, self.strings("triggered").format(usertag, link))
                if sets[chatid_str].get("deltimer") != "0":
                    DELTIMER = int(sets[chatid_str].get("deltimer"))
                    await asyncio.sleep(DELTIMER)
                    await message.client.delete_messages(chatid, msgs)
