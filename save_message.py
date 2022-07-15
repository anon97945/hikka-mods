__version__ = (0, 0, 20)


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
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.2.11

import logging
import re

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")


def get_ids(link):
    match = regex.match(link)
    if not match:
        return False
    chat_id = match.group(4)
    msg_id = int(match.group(5))
    if chat_id.isnumeric():
        chat_id = int(chat_id)
    return chat_id, msg_id


@loader.tds
class ApodiktumSaveMessageMod(loader.Module):
    """
    Get Message/Media from given link (also works for forward restricted content).
    """
    strings = {
        "name": "Apo SaveMessage",
        "developer": "@anon97945",
        "done": "<b>Forward to saved complete.</b>",
        "invalid_link": "<b>Invalid link.</b>",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_en = {
    }

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

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_log",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_log"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_debug",
                False,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_debug"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apodiktum_library.py",
            suspend_on_error=True,
        )
        self._id = (await client.get_me(True)).user_id

    async def smcmd(self, message: Message):
        """<messagelink> to forward message/media to SavedMessages."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        if not get_ids(args):
            return await utils.answer(message, self.apo_lib.get_str("invalid_link", self.all_strings, message))
        channel_id, msg_id = get_ids(args)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(self._id, message=msgs)
        return await utils.answer(message, self.apo_lib.get_str("done", self.all_strings, message))

    async def smhcmd(self, message: Message):
        """<messagelink> to forward message/media to current chat."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        if not get_ids(args):
            return await utils.answer(message, self.apo_lib.get_str("invalid_link", self.all_strings, message))
        channel_id, msg_id = get_ids(args)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(utils.get_chat_id(message), message=msgs)
        return await message.delete()
