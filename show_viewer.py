__version__ = (0, 0, 19)


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

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumShowViewsMod(loader.Module):
    """
    Send a message to get the current count of viewers.
    """
    strings = {
        "name": "Apo-ShowViews",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_channel": "The Channel ID to send the message from.",
        "no_args": "No message to send.",
        "no_channel": "No channel set.",
        "no_reply": "You need to reply to a message.",
        "views": "Total <code>{}</code> views.",
    }

    strings_en = {
    }

    strings_de = {
    }

    strings_ru = {
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "channel",
                "None",
                lambda: self.strings("_cfg_cst_channel"),
                validator=loader.validators.Union(
                    loader.validators.TelegramID(),
                    loader.validators.NoneType(),
                ),
            ),
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
            "https://raw.githubusercontent.com/anon97945/hikka-mods/master/apodiktum_library.py",
            suspend_on_error=True,
        )

    async def svcmd(self, message: Message):
        """
        <message/reply to msg> Send a message to get the current count of viewers with that message.
        """
        chat_id = utils.get_chat_id(message)
        args = utils.get_args_raw(message)
        msg = None
        if not self.config["channel"]:
            await utils.answer(message, self.apo_lib.utils.get_str("no_channel", self.all_strings, message))
            return
        if message.is_reply:
            msg = await message.get_reply_message()
        elif not args:
            await utils.answer(message, self.apo_lib.utils.get_str("no_args", self.all_strings, message))
            return
        await message.delete()
        if message.is_reply and msg.sender_id == self.tg_id:
            await msg.delete()
        if msg:
            msg = await message.client.send_message(self.config["channel"], msg)
        else:
            msg = await message.client.send_message(self.config["channel"], args)
        await msg.forward_to(chat_id)
        if msg.out:
            await msg.delete()

    async def gvcmd(self, message: Message):
        """
        <reply to msg> Get current views of the message.
        """
        if message.is_reply:
            msg = await message.get_reply_message()
        else:
            await utils.answer(message, self.apo_lib.utils.get_str("no_reply", self.all_strings, message))
            return
        view_count = msg.views
        await utils.answer(message, self.apo_lib.utils.get_str("views", self.all_strings, message).format(view_count))
