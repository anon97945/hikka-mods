__version__ = (0, 0, 28)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#             developed by @anon97945
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28

import logging

from telethon.errors import MessageIdInvalidError

from .. import loader, utils
from telethon.tl.types import Message, User, Channel

logger = logging.getLogger(__name__)


def represents_tgid(s):
    try:
        loader.validators.TelegramID().validate(s)
    except loader.validators.ValidationError:
        return False
    else:
        return True


def get_link(user: User or Channel) -> str:
    """Get link to object (User or Channel)"""
    return (
        f"tg://user?id={user.id}"
        if isinstance(user, User)
        else (
            f"tg://resolve?domain={user.username}"
            if getattr(user, "username", None)
            else ""
        )
    )


@loader.tds
class GroupChannelLoggerMod(loader.Module):
    """
    Log given chats/channel to given group/channel
    Will not be updated any further! Download ApodiktumAdminTools instead!
    """
    strings = {
        "name": "Group/Channel Logger",
        "developer": "@anon97945",
        "db_string": "<b>[Grouplogger - Settings]</b> Current Database:\n\nWatcher:\n{}",
        "error": "<b>Your command was wrong.</b>",
        "no_id": "<b>Your input was no TG ID.</b>",
        "settings": "<b>[Grouplogger - Settings]</b> Current settings are:\n{}",
        "start": "<b>[Grouplogger]</b> activated.",
        "stopped": "<b>[Grouplogger]</b> deactivated.",
        "turned_off": "<b>[Grouplogger]</b> Is now turned off.",
    }

    strings_de = {
        "db_string": "<b>[Grouplogger - Settings]</b> Aktuelle Datenbank:\n\nWatcher:\n{}",
        "error": "<b>Ihr Befehl war falsch.</b>",
        "no_id": "<b>Ihre Eingabe war keine TG ID.</b>",
        "settings": "<b>[Grouplogger - Einstellungen]</b> Aktuelle Einstellungen sind:\n{}.",
        "start": "<b>[Grouplogger]</b> aktiviert",
        "stopped": "<b>[Grouplogger]</b> deaktiviert.",
        "turned_off": "<b>[Grouplogger]</b> ist jetzt ausgeschaltet.",
    }

    strings_ru = {
        "db_string": "<b>[Grouplogger - Settings]</b> Текущая база данных:\n\nНаблюдающий:\n{}",
        "error": "<b>Команда не верная.</b>",
        "no_id": "<b>Ты ввёл не телеграм айди.</b>",
        "settings": "<b>[Grouplogger - Settings]</b> Текущие настройки:\n{}",
        "start": "<b>[Grouplogger]</b>активирован.",
        "stopped": "<b>[Grouplogger]</b> остановлен.",
        "turned_off": "<b>[Grouplogger]</b> Сейчас выключен.",
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    async def glcmd(self, message: Message):
        """Available commands:
           .gl <chatid> <logchannelid>
             - Logs given groupchat in given channel.
           .gl rem <chatid>
             - Removes given chat from watcher.
           .gl db
             - Shows the current database.
           .gl clearall
             - Clears the db of the module."""
        gl = self._db.get(__name__, "gl", [])
        sets = self._db.get(__name__, "sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if args[0] is not None and represents_tgid(args[0]):
            chatid = args[0]
            chatid_str = str(chatid)
        elif args[0] == "rem":
            chatid = args[1]
            chatid_str = str(chatid)
        elif args[0] == "db":
            return await utils.answer(message, self.strings("db_string").format(str(sets)))
        elif args[0] != "clearall":
            return await utils.answer(message, self.strings("error"))
        elif not args:
            return await utils.answer(message, self.strings("error"))
        if args:
            if args[0] == "clearall":
                self._db.set(__name__, "gl", [])
                self._db.set(__name__, "sets", {})
                return await utils.answer(message, self.strings("turned_off"))
            if args[0] == "rem" and represents_tgid(args[1]) and chatid_str in gl:
                gl.remove(chatid_str)
                sets.pop(chatid_str)
                self._db.set(__name__, "gl", gl)
                self._db.set(__name__, "sets", sets)
                return await utils.answer(message, self.strings("stopped"))
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
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("start"))
        if args[0] is not None and args[1] is not None:
            if not represents_tgid(args[0]) or not represents_tgid(args[1]):
                return await utils.answer(message, self.strings("no_id"))
            sets[chatid_str].update({"logchannel": args[1]})
        self._db.set(__name__, "sets", sets)
        return await utils.answer(message, self.strings("settings").format(str(sets[chatid_str])))

    async def watcher(self, message: Message):
        gl = self._db.get(__name__, "gl", [])
        sets = self._db.get(__name__, "sets", {})
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if message.is_private or chatid_str not in gl:
            return
        entity = await self._client.get_entity(message.sender_id)
        logchanid = int(sets[chatid_str].get("logchannel"))
        loggingchat = chatid
        chatsender = await message.get_sender()
        if chatsender is None:
            return
        senderid = (await message.get_sender()).id
        chattitle = (await message.get_chat()).title
        if chatsender.username:
            name = f"@{chatsender.username}"
        elif not isinstance(entity, Channel):
            if chatsender.last_name:
                name = f"{chatsender.first_name} {chatsender.last_name}"
            else:
                name = chatsender.first_name
        else:
            name = chatsender.title
        user_url = get_link(senderid)
        link = (
            (
                (
                    (
                        (
                            f"Chat: {str(chattitle)} | <code>{str(loggingchat)}</code>"
                            + "\nUser: "
                            + str(name)
                            + " ID: "
                        )
                        + "<a href='"
                    )
                    + user_url
                )
                + "'>"
            )
            + str(senderid)
            + "</a>"
        )

        try:
            await message.forward_to(logchanid)
            await message.client.send_message(logchanid, link)
            return
        except Exception as e:
            if "FORWARDS_RESTRICTED" in str(e):
                msgs = await message.client.get_messages(loggingchat, ids=message.id)
                await message.client.send_message(logchanid, message=msgs)
                await message.client.send_message(logchanid, link)
        except MessageIdInvalidError:
            return
