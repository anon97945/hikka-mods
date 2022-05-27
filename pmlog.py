__version__ = (0, 0, 13)


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

from telethon.tl.types import Message, User, Channel
from telethon.errors import MessageIdInvalidError

from .. import loader, utils

logger = logging.getLogger(__name__)


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
class PMLogMod(loader.Module):
    """Logs PMs to a group/channel"""
    strings = {
        "name": "PM Logger",
        "_cfg_log_group": "Group or channel ID where to send the logged PMs.",
        "_cfg_whitelist": "Whether the list is a for excluded(True) or included chats(False).",
        "_cfg_bots": "Whether to log bots or not.",
        "_cfg_selfdestructive": "Whether selfdestructive media should be logged or not. This violates TG TOS!",
        "_cfg_loglist": "Add telegram id's to log them.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_group",
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
                "log_self_destr",
                "False",
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_list",
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def get_media(self, message: Message):
        file = (
            io.BytesIO((await self.fast_download(message.media)).getvalue())
        )
        file.seek(0)
        return file

    async def watcher(self, message: Message):
        if not message.is_private or not isinstance(message, Message):
            return
        pmlog_whitelist = self.config["whitelist"]
        pmlog_bot = self.config["log_bots"]
        pmlog_group = self.config["log_group"]
        pmlog_destr = self.config["log_self_destr"]
        chat = await message.get_chat()
        if chat.bot and not pmlog_bot or chat.id == self._id or pmlog_group is None:
            return
        chatidindb = utils.get_chat_id(message) in (self.config["logs_list"] or [])
        if pmlog_whitelist and chatidindb or not pmlog_whitelist and not chatidindb:
            return
        if pmlog_group:
            if chat.username:
                name = "@" + chat.username
            elif chat.last_name:
                name = f"{chat.first_name} {chat.last_name}"
            else:
                name = chat.first_name
            user_id = str(chat.id)
            user_url = get_link(chat.id)
            link = "Chat: <a href='" + user_url + "'>" + name + "</a>\nID: " + user_id
            try:
                await message.forward_to(pmlog_group)
                await message.client.send_message(pmlog_group, link)
                return
            except MessageIdInvalidError:
                if not message.file or not pmlog_destr:
                    return
                file = io.BytesIO()
                caption = message.text + "\n\n" + link
                file = await self.get_media(message)
                file.name = message.file.name or f"{message.file.media.id}{message.file.ext}"
                file.seek(0)
                await message.client.send_file(pmlog_group, await self.fast_upload(file), force_document=True, caption=caption)
