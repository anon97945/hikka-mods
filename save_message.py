__version__ = (0, 0, 26)


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
# scope: hikka_min 1.3.0

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumSaveMessageMod(loader.Module):
    """
    Get Message/Media from given link (also works for forward restricted content).
    """

    strings = {
        "name": "Apo-SaveMessage",
        "developer": "@anon97945",
        "done": "<b>Forward to saved complete.</b>",
        "invalid_link": "<b>Invalid link.</b>",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {
        "done": "<b>Weiterleitung zu gespeicherten Daten abgeschlossen.</b>",
        "invalid_link": "<b>Ungültiger Link.</b>",
    }

    strings_ru = {
        "done": "<b>Перешлите для завершения сохранения.</b>",
        "invalid_link": "<b>Неверная ссылка.</b>",
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
                "old": "Apo SaveMessage",
                "new": "Apo-SaveMessage",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
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

    async def smcmd(self, message: Message):
        """<messagelink> to forward message/media to SavedMessages."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        if not self.apo_lib.utils.get_ids_from_tglink(args):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("invalid_link", self.all_strings, message),
            )
        channel_id, msg_id = self.apo_lib.utils.get_ids_from_tglink(args)
        msgs = await self._client.get_messages(channel_id, ids=msg_id)
        msgs = await self._client.send_message(self.tg_id, message=msgs)
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("done", self.all_strings, message),
        )

    async def smhcmd(self, message: Message):
        """<messagelink> to forward message/media to current chat."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return

        if not self.apo_lib.utils.get_ids_from_tglink(args):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("invalid_link", self.all_strings, message),
            )

        channel_id, msg_id = self.apo_lib.utils.get_ids_from_tglink(args)
        msgs = await self._client.get_messages(channel_id, ids=msg_id)
        msgs = await self._client.send_message(
            utils.get_chat_id(message),
            message=msgs,
        )

        await message.delete()
