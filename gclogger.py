#    Friendly Telegram (telegram userbot) module
#    module author: @anon97945


import logging

from telethon.errors import MessageIdInvalidError

from .. import loader, utils
from telethon.tl.types import Channel

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
    """Log given chats/channel to given group/channel"""
    strings = {"name": "Log Groups/Channel",
               "start": "<b>[Grouplogger]</b> Activated.</b>",
               "stopped": "<b>[Grouplogger]</b> Deactivated.</b>",
               "turned_off": "<b>[Grouplogger]</b> Is now turned off.</b>",
               "no_int": "<b>Your input was no int.</b>",
               "error": "<b>Your command was wrong.</b>",
               "settings": ("<b>[Grouplogger - Settings]</b> Current settings are:"
                            "\n{}."),
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db

    async def glcmd(self, message):
        """Available commands:
           .gl rem <chatid>
             - Removes given chat from watcher.
           .gl <chatid> <logchannelid>
             - Logs given groupchat in given channel
           .gl clearall
            - Clears the db of the module"""
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
        elif args[0] != "clearall" and args[0] != "rem":
            return await utils.answer(message, self.strings("error", message))
        elif not args:
            return await utils.answer(message, self.strings("error", message))
        elif args[0] != "clearall" and args[1] is None:
            return await utils.answer(message, self.strings("error", message))

        if args:
            if args[0] == "clearall":
                self._db.set(__name__, "gl", [])
                self._db.set(__name__, "sets", {})
                return await utils.answer(message, self.strings("turned_off", message))
            elif args[0] == "rem" and represents_tgid(args[1]) and chatid_str in gl:
                gl.remove(chatid_str)
                sets.pop(chatid_str)
                self._db.set(__name__, "gl", gl)
                self._db.set(__name__, "sets", sets)
                return await utils.answer(message, self.strings("stopped", message))
            elif args[0] == "rem":
                if represents_tgid(args[1]) or chatid_str not in gl:
                    return await utils.answer(message, self.strings("error", message))
        if not represents_tgid(chatid_str):
            return await utils.answer(message, self.strings("error", message))
        if chatid_str not in gl:
            if not represents_tgid(args[0]) or not represents_tgid(args[1]):
                return await utils.answer(message, self.strings("no_int", message))
            gl.append(chatid_str)
            sets.setdefault(chatid_str, {})
            sets[chatid_str].setdefault("logchannel", args[1])
            self._db.set(__name__, "gl", gl)
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("start", message))
        if chatid_str in gl:
            if args[0] is not None and args[1] is not None and chatid_str in gl:
                if not represents_tgid(args[0]) or not represents_tgid(args[1]):
                    return await utils.answer(message, self.strings("no_int", message))
                else:
                    sets[chatid_str].update({"logchannel": args[1]})
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("settings", message).format(str(sets[chatid_str])))

    async def watcher(self, message):
        gl = self._db.get(__name__, "gl", [])
        sets = self._db.get(__name__, "sets", {})
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if message.is_private or chatid_str not in gl:
            return
        entity = await message.client.get_entity(message.sender_id)
        logchanid = int(sets[chatid_str].get("logchannel"))
        loggingchat = chatid
        chatsender = await message.get_sender()
        if chatsender is None:
            return
        senderid = (await message.get_sender()).id
        chattitle = (await message.get_chat()).title
        if chatsender.username:
            name = chatsender.username
            name = "@" + name
        elif not isinstance(entity, Channel):
            if chatsender.last_name:
                name = chatsender.first_name + " " + chatsender.last_name
            else:
                name = chatsender.first_name
        else:
            name = chatsender.title
        user_url = get_link(senderid)
        link = "Chat: " + str(chattitle) + " | <code>" + str(loggingchat) + "</code>" + "\nUser: " + str(name) + \
               " ID: " + "<a href='" + user_url + "'>" + str(senderid) + "</a>"
                 + name + "</a>
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