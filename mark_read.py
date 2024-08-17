__version__ = (0, 1, 5)


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

from telethon.tl.types import Message
from telethon.tl.functions.messages import (
    ReadDiscussionRequest,
)

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumMarkReadMod(loader.Module):
    """
    This module marks chats as read.
    """

    strings = {
        "name": "Apo-MarkRead",
        "developer": "@anon97945",
        "_cfg_chat_list": "Chats to mark as read.",
        "_cfg_clear_mentions": "Whether to clear mentions or not.",
        "_cfg_clear_reactions": "Whether to clear reactions or not.",
        "_cfg_clear_pms": "Whether to clear pms or not.",
        "_cfg_whitelist": (
            "Whether the chatlist includes(True) or excludes(False) the chat."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_error_text": "The text of the error message to remove.",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {}

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "chatlist",
                doc=lambda: self.strings("_cfg_chat_list"),
                validator=loader.validators.Series(loader.validators.TelegramID()),
            ),
            loader.ConfigValue(
                "clear_mentions",
                True,
                doc=lambda: self.strings("_cfg_clear_mentions"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "clear_pms",
                True,
                doc=lambda: self.strings("_cfg_clear_pms"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "clear_reactions",
                True,
                doc=lambda: self.strings("_cfg_clear_reactions"),
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
            ),  # for MigratorClas
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

    async def cmarkreadcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @loader.watcher("in")
    async def watcher(self, message: Message):
        if (
            (
                self.config["whitelist"]
                and utils.get_chat_id(message) not in self.config["chatlist"]
            )
            or (
                not self.config["whitelist"]
                and utils.get_chat_id(message) in self.config["chatlist"]
            )
            or (message.is_private and not self.config["clear_pms"])
        ):
            return
        if (await message.get_chat()).forum:
            await self._client(
                ReadDiscussionRequest(
                    message.chat_id,
                    getattr(getattr(message, "reply_to", None), "reply_to_top_id", None)
                    or getattr(
                        getattr(message, "reply_to", None), "reply_to_msg_id", None
                    ),
                    2**31 - 1,
                )
            )
        else:
            await self._client.send_read_acknowledge(
                message.chat_id,
                message,
                clear_mentions=self.config["clear_mentions"],
                clear_reactions=self.config["clear_reactions"],
            )
        return
