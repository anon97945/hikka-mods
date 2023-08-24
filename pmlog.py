__version__ = (0, 1, 3)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2023
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/file_dumbster/11
# meta pic: https://t.me/file_dumbster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

import logging
from datetime import datetime
from io import BytesIO

from telethon.errors import MessageIdInvalidError
from telethon.tl.types import Message, User

from telethon.tl.functions.channels import (
    GetForumTopicsRequest,
    CreateForumTopicRequest,
    ToggleForumRequest,
)

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumPMLogMod(loader.Module):
    """
    Logs PMs to a group/channel
    """

    strings = {
        "name": "Apo-PMLog",
        "developer": "@anon97945",
        "_cfg_bots": "Whether to log bots or not.",
        "_cfg_loglist": "Add telegram id's to log them.",
        "_cfg_selfdestructive": (
            "Whether selfdestructive media should be logged or not. This"
            " violates TG TOS!"
        ),
        "_cfg_whitelist": (
            "Whether the list is a for excluded(True) or included(False) chats."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_bots": "Ob Bots geloggt werden sollen oder nicht.",
        "_cfg_loglist": "Fügen Sie Telegram-IDs hinzu, um sie zu protokollieren.",
        "_cfg_selfdestructive": (
            "Ob selbstzerstörende Medien geloggt werden sollen oder nicht. Dies"
            " verstößt gegen die TG TOS!"
        ),
        "_cfg_whitelist": (
            "Ob die Liste für ausgeschlossene (Wahr) oder eingeschlossene"
            " (Falsch) Chats ist."
        ),
        "_cmd_doc_cpmlog": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cfg_bots": "Логировать ли ботов или нет",
        "_cfg_loglist": "Добавьте айди Telegram, чтобы зарегистрировать их",
        "_cfg_selfdestructive": (
            "Должны ли самоуничтожающиеся медиафайлы регистрироваться или нет."
            " Это нарушает «Условия использования Telegram» (ToS)"
        ),
        "_cfg_whitelist": "Использовать белый список (True) или черный (False).",
        "_cmd_doc_cpmlog": "Это откроет конфиг для модуля.",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo PMLogger",
                "new": "Apo-PMLog",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_bots",
                False,
                doc=lambda: self.strings("_cfg_bots"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_list",
                [777000],
                doc=lambda: self.strings("_cfg_loglist"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "log_self_destr",
                False,
                doc=lambda: self.strings("_cfg_selfdestructive"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                True,
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )
        self.apo_lib.watcher_q.register(self.__class__.__name__)
        self._topic_cache = {}
        self.c, _ = await utils.asset_channel(
            self._client,
            "[Apo] PMLog",
            "Chat for logged PMs. The ID's in the topic titles are the user ID's, don't remove them!",
            silent=True,
            invite_bot=False,
        )
        if not self.c.forum:
            await self._client(ToggleForumRequest(self.c.id, True))

    async def on_unload(self):
        self.apo_lib.watcher_q.unregister(self.__class__.__name__)

    async def cpmlogcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def _topic_cacher(self, user: User):
        if user.id not in self._topic_cache:
            forum = await self._client(
                GetForumTopicsRequest(
                    channel=self.c.id,
                    offset_date=datetime.now(),
                    offset_id=0,
                    offset_topic=0,
                    limit=0,
                )
            )
            for topic in forum.topics:
                if str(user.id) in topic.title:
                    self._topic_cache[user.id] = topic.id
                    break
        return user.id in self._topic_cache

    async def _topic_handler(self, user: User):
        if not await self._topic_cacher(user):
            new_topic = await self._client(
                CreateForumTopicRequest(
                    channel=self.c.id,
                    title=f"{user.first_name} ({user.id})",
                    icon_color=42,
                )
            )
            self._topic_cache[user.id] = new_topic.updates[0].id

    async def q_watcher(self, message: Message):
        try:
            await self._queue_handler(message)
        except Exception as exc:  # skipcq: PYL-W0703
            self.apo_lib.utils.log(
                logging.ERROR,
                __name__,
                exc,
                exc_info=True,
            )

    async def _queue_handler(self, message: Message):
        if not isinstance(message, Message) or not message.is_private:
            return
        pmlog_whitelist = self.config["whitelist"]
        pmlog_bot = self.config["log_bots"]
        pmlog_destr = self.config["log_self_destr"]
        user = await message.get_sender()
        if user.id == self.tg_id:
            user = await self._client.get_entity(utils.get_chat_id(message))
        if user.bot and not pmlog_bot or user.id == self.tg_id:
            return
        chatidindb = utils.get_chat_id(message) in (self.config["log_list"] or [])
        if pmlog_whitelist and chatidindb or not pmlog_whitelist and not chatidindb:
            return
        link = f"Chat: {await self.apo_lib.utils.get_tag(user)}\n#ID_{user.id}"
        try:
            await self._topic_handler(user)
            await message.forward_to(self.c.id, top_msg_id=self._topic_cache[user.id])
            await message.client.send_message(
                self.c.id, link, reply_to=self._topic_cache[user.id]
            )
        except MessageIdInvalidError:
            if not message.file or not pmlog_destr:
                return
            file = BytesIO()
            caption = f"{utils.escape_html(message.text)}\n\n{link}"
            await self._client.download_file(message, file)
            file.name = (
                message.file.name or f"{message.file.media.id}{message.file.ext}"
            )
            file.seek(0)
            await self._client.send_file(
                self.c.id,
                file,
                force_document=True,
                caption=caption,
                reply_to=self._topic_cache[user.id],
            )
