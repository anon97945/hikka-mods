__version__ = (0, 1, 9)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

import logging
from datetime import datetime
from io import BytesIO

from telethon.errors import MessageIdInvalidError
from telethon.tl.types import Message, User

from telethon.tl.functions.messages import (
    ReadDiscussionRequest,
)
from telethon.tl.functions.channels import (
    GetForumTopicsRequest,
    CreateForumTopicRequest,
    ToggleForumRequest,
    EditForumTopicRequest,
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
        "_cfg_reatime_usernames": "Whether to update the topic names in realtime or not.",
        "_cfg_mark_read": "Whether to mark the messsages in the log as read or not.",
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
                "realtime_names",
                True,
                doc=lambda: self.strings("_cfg_reatime_usernames"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                True,
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "mark_read",
                True,
                doc=lambda: self.strings("_cfg_mark_read"),
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
                    self._topic_cache[user.id] = topic
                    break
        return user.id in self._topic_cache

    async def _topic_creator(self, user: User):
        await self._client(
            CreateForumTopicRequest(
                channel=self.c.id,
                title=f"{user.first_name} ({user.id})",
                icon_color=42,
            )
        )
        return await self._topic_cacher(user)

    async def _topic_handler(self, user: User, message: Message):
        if not await self._topic_cacher(user):  # create topic if not exists
            await self._topic_creator(user)
        if (
            self.config["realtime_names"]
            and self._topic_cache[user.id].title != f"{user.first_name} ({user.id})"
        ):
            await self._client(
                EditForumTopicRequest(
                    channel=self.c.id,
                    topic_id=self._topic_cache[user.id].id,
                    title=f"{user.first_name} ({user.id})",
                )
            )
            self._topic_cache[user.id].title = f"{user.first_name} ({user.id})"
            await message.client.send_message(
                self.c.id,
                f"New name:\n<code>{user.first_name} ({user.id})</code>\n\nOld name:\n<code>{self._topic_cache[user.id].title}</code>",
                reply_to=self._topic_cache[user.id].id,
            )
        return True

    async def q_watcher(self, message: Message):
        try:
            await self._queue_handler(message)
        except Exception as exc:  # skipcq: PYL-W0703
            if "topic was deleted" in str(exc):
                self._topic_cache.pop(utils.get_chat_id(message))
                await self._queue_handler(message)
                return

    async def _queue_handler(self, message: Message):
        if not isinstance(message, Message) or not message.is_private:
            return
        user = await message.get_sender()
        if user.id == self.tg_id:
            user = await message.get_chat()
        if user.bot and not self.config["log_bots"] or user.id == self.tg_id:
            return
        chatidindb = utils.get_chat_id(message) in (self.config["log_list"] or [])
        if (
            self.config["whitelist"]
            and chatidindb
            or not self.config["whitelist"]
            and not chatidindb
        ):
            return
        try:
            if await self._topic_handler(user, message):
                msg = await message.forward_to(
                    self.c.id, top_msg_id=self._topic_cache[user.id].id
                )
                if self.config["mark_read"]:
                    await self._client(
                        ReadDiscussionRequest(
                            self.c.id,
                            getattr(
                                getattr(msg, "reply_to", None),
                                "reply_to_top_id",
                                None,
                            )
                            or getattr(
                                getattr(msg, "reply_to", None),
                                "reply_to_msg_id",
                                None,
                            ),
                            2**31 - 1,
                        )
                    )
        except MessageIdInvalidError:
            if not message.file or not self.config["log_self_destr"]:
                return
            file = BytesIO()
            caption = f"{utils.escape_html(message.text)}"
            await self._client.download_file(message, file)
            file.name = (
                message.file.name or f"{message.file.media.id}{message.file.ext}"
            )
            file.seek(0)
            msg = await self._client.send_file(
                self.c.id,
                file,
                force_document=True,
                caption=caption,
                reply_to=self._topic_cache[user.id].id,
            )
            await self._client(
                ReadDiscussionRequest(
                    self.c.id,
                    getattr(
                        getattr(msg, "reply_to", None),
                        "reply_to_top_id",
                        None,
                    )
                    or getattr(
                        getattr(msg, "reply_to", None),
                        "reply_to_msg_id",
                        None,
                    ),
                    2**31 - 1,
                )
            )
