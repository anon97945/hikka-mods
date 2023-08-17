__version__ = (0, 1, 0)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2022
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
from io import BytesIO

from telethon.errors import MessageIdInvalidError
from telethon.tl.types import Message

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
        "_cfg_log_group": "Group or channel ID where to send the PMs.",
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
        "_cfg_log_group": (
            "Gruppen- oder Kanal-ID, an die die PMs gesendet werden sollen."
        ),
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
        "_cfg_log_group": "Айди группы или канала для отправки личных сообщений.",
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
        self.apo_lib.apodiktum_module()
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )
        self.apo_lib.watcher_q.register(self.__class__.__name__)

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
        pmlog_group = self.config["log_group"]
        pmlog_destr = self.config["log_self_destr"]
        chat = await self._client.get_entity(utils.get_chat_id(message))

        if chat.bot and not pmlog_bot or not pmlog_group or chat.id == self.tg_id:
            return

        chatidindb = utils.get_chat_id(message) in (self.config["logs_list"] or [])

        if (
            pmlog_whitelist
            and chatidindb
            or not pmlog_whitelist
            and not chatidindb
            or not pmlog_group
        ):
            return

        link = f"Chat: {await self.apo_lib.utils.get_tag(chat)}\n#ID_{chat.id}"
        try:
            await message.forward_to(pmlog_group)
            await self._client.send_message(pmlog_group, link)
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
                pmlog_group,
                file,
                force_document=True,
                caption=caption,
            )
