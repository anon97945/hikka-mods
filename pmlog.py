__version__ = (0, 0, 9)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @anon97945

# scope: hikka_only
# scope: hikka_min 1.1.28

import logging
import io

from telethon.tl.types import Message
from telethon.errors import MessageIdInvalidError

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class PMLogMod(loader.Module):
    """Logs unwanted PMs to a channel"""
    strings = {
        "name": "PM Logger",
        "start": "<b>Conversation added to the List</b>",
        "not_pm": "<b>You can't log a group</b>",
        "stopped": "<b>Conversation removed from the List</b>",
        "_cfg_log_group": "Group or channel ID where to send the logged PMs.",
        "_cfg_whitelist": "Whether the list is a for excluded(True) or included chats(False).",
        "_cfg_bots": "Whether to log bots or not.",
        "_cfg_selfdestructive": "Whether selfdestructive media should be logged or not.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_group",
                None,
                doc=lambda: self.strings("_cfg_log_group"),
                validator=loader.validators.TelegramID(),
            ),
            loader.ConfigValue(
                "whitelist",
                "false",
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_bots",
                "False",
                doc=lambda: self.strings("_cfg_bots"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_self_destr.",
                "False",
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_list",
                "",
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def watcher(self, message: Message):
        if not message.is_private or not isinstance(message, Message):
            return
        pmlog_whitelist = self.config["whitelist"]
        pmlog_bot = self.config["log_bots"]
        chat = await message.get_chat()
        if chat.bot and not pmlog_bot or chat.id == self._id:
            return
        chatidindb = utils.get_chat_id(message) in self.config["logs_list"]
        if pmlog_whitelist and chatidindb or not pmlog_whitelist and not chatidindb:
            return
        if self.config["LOG_GROUP"]:
            if chat.username:
                name = chat.username
            elif chat.last_name:
                name = f"{chat.first_name} {chat.last_name}"
            else:
                name = chat.first_name
            linkid = str(chat.id)
            link = "Chat: <a href='tg://user?id=" + linkid + "'>" + name + "</a>\nID: " + linkid
            try:
                await message.forward_to(self.config["LOG_GROUP"])
                await message.client.send_message(self.config["LOG_GROUP"], link)
                return
            except MessageIdInvalidError:
                if not message.file:
                    return
                file = io.BytesIO()
                file.name = message.file.name or f"{message.file.media.id}{message.file.ext}"
                await message.client.download_file(message, file)
                file.seek(0)
                await message.client.send_file(self.config["LOG_GROUP"], file, force_document=True, caption=link)
