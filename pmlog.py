__version__ = (0, 0, 22)


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

from telethon.tl.types import Message, User, Channel
from telethon.errors import MessageIdInvalidError
from io import BytesIO

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
class ApodiktumPMLogMod(loader.Module):
    """
    Logs PMs to a group/channel
    """
    strings = {
        "name": "Apo PMLogger",
        "developer": "@anon97945",
        "_cfg_bots": "Whether to log bots or not.",
        "_cfg_log_group": "Group or channel ID where to send the PMs.",
        "_cfg_loglist": "Add telegram id's to log them.",
        "_cfg_selfdestructive": "Whether selfdestructive media should be logged or not. This violates TG TOS!",
        "_cfg_whitelist": "Whether the list is a for excluded(True) or included(False) chats.",
    }

    strings_de = {
        "_cfg_bots": "Ob Bots geloggt werden sollen oder nicht.",
        "_cfg_log_group": "Gruppen- oder Kanal-ID, an die die PMs gesendet werden sollen.",
        "_cfg_loglist": "Fügen Sie Telegram-IDs hinzu, um sie zu protokollieren.",
        "_cfg_selfdestructive": "Ob selbstzerstörende Medien geloggt werden sollen oder nicht. Dies verstößt gegen die TG TOS!",
        "_cfg_whitelist": "Ob die Liste für ausgeschlossene (Wahr) oder eingeschlossene (Falsch) Chats ist.",
        "_cmd_doc_cpmlog": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cfg_bots": "Регистрировать ботов или нет",
        "_cfg_log_group": "Айди группы или канала для отправки личных сообщений.",
        "_cfg_loglist": "Добавьте айди Telegram, чтобы зарегистрировать их",
        "_cfg_selfdestructive": "Должны ли самоуничтожающиеся медиафайлы регистрироваться или нет. Это нарушает «Условия использования Telegram» (ToS)",
        "_cfg_whitelist": "Является ли список для исключённых (True) или включённых чатов (False).",
        "_cmd_doc_cpmlog": "Это откроет конфиг для модуля.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_bots",
                "False",
                doc=lambda: self.strings("_cfg_bots"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_group",
                doc=lambda: self.strings("_cfg_log_group"),
                validator=loader.validators.TelegramID(),
            ),
            loader.ConfigValue(
                "log_list",
                doc=lambda: self.strings("_cfg_loglist"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "log_self_destr",
                "False",
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                "false",
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def get_media(self, message: Message):
        file = (
            BytesIO((await self.fast_download(message.media)).getvalue())
        )
        file.seek(0)
        return file

    async def cpmlogcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

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
                name = f"@{chat.username}"
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
                file = BytesIO()
                caption = message.text + "\n\n" + link
                file = await self.get_media(message)
                file.name = message.file.name or f"{message.file.media.id}{message.file.ext}"
                file.seek(0)
                await message.client.send_file(pmlog_group, await self.fast_upload(file), force_document=True, caption=caption)
