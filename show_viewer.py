__version__ = (0, 0, 1)

# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28

from .. import loader, utils
from telethon.tl.types import Message

import logging

logger = logging.getLogger(__name__)


@loader.tds
class ShowViewsMod(loader.Module):
    """
    Send a message to get the current count of viewers.
    """
    strings = {
        "name": "ShowViews",
        "developer": "@anon97945",
        "no_args": "No message to send.",
        "no_channel": "No channel set.",
        "_cfg_cst_channel": "The Channel ID to send the message from.",
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
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def svcmd(self, message: Message):
        """
        Send a message to get the current count of viewers.
        """
        chat = message.chat
        args = utils.get_args_raw(message)

        if not self.config["channel"]:
            await utils.answer(message, self.strings("no_channel"))
            return
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        await message.delete()
        msg = await message.client.send_message(self.config["channel"], args)
        await msg.forward_to(chat.id)
        if msg.out:
            await msg.delete()
