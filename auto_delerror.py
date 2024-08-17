__version__ = (0, 0, 4)


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

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumAutoDelErrorMod(loader.Module):
    """
    This module deletes error messages which have defined text in it.
    """

    strings = {
        "name": "Apo-AutoDelError",
        "developer": "@anon97945",
        "_cfg_additional_id": "Additional Telegram IDs to remove the error message from.",
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
                "additional_ids",
                doc=lambda: self.strings("_cfg_additional_id"),
                validator=loader.validators.Series(loader.validators.TelegramID()),
            ),
            loader.ConfigValue(
                "error_text",
                doc=lambda: self.strings("_cfg_error_text"),
                validator=loader.validators.Series(loader.validators.String()),
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

    async def cautodelerrorcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @loader.watcher("in", "only_groups", "only_messages")
    async def watcher(self, message):
        if (
            message.sender_id != self.inline.bot_id
            and message.sender_id not in self.config["additional_ids"]
        ):
            return
        if self.config["error_text"]:
            logchan_id = int(str(self.lookup("tester").logchat).replace("-100", ""))
            if message.chat.id == logchan_id:
                for error_text in self.config["error_text"]:
                    if error_text in message.raw_text:
                        await message.delete()
                        return
