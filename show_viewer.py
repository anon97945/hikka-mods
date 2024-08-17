__version__ = (0, 0, 28)


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
class ApodiktumShowViewsMod(loader.Module):
    """
    Send a message to get the current count of viewers.
    """

    strings = {
        "name": "Apo-ShowViews",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_channel": "The Channel ID to send the message from.",
        "no_args": "No message to send.",
        "no_channel": "No channel set.",
        "no_reply": "You need to reply to a message.",
        "views": "Total <code>{}</code> views.",
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
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "channel",
                None,
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

    async def svcmd(self, message: Message):
        """
        <message/reply to msg> Send a message to get the current count of viewers with that message.
        """
        chat_id = utils.get_chat_id(message)
        args = utils.get_args_raw(message)
        msg = None
        if not self.config["channel"]:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_channel", self.all_strings, message),
            )
            return
        if message.is_reply:
            msg = await message.get_reply_message()
        elif not args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_args", self.all_strings, message),
            )
            return

        await message.delete()

        if message.is_reply and msg.out:
            await msg.delete()

        msg = (
            await self._client.send_message(self.config["channel"], msg)
            if msg
            else await self._client.send_message(self.config["channel"], args)
        )

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
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
            return

        view_count = msg.views

        await utils.answer(
            message,
            self.apo_lib.utils.get_str("views", self.all_strings, message).format(
                view_count
            ),
        )
