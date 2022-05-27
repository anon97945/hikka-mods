__version__ = (0, 0, 8)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @anon97945

# scope: hikka_only

import asyncio
import logging

from telethon.tl.types import Message
from telethon import events
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class lcrMod(loader.Module):
    """Telegram Login Code Reciever"""
    strings = {
        "name": "Login Code Reciever",
        "timeouterror": "<b>TimeoutError:</b>\nNo login code for {} seconds recieved.",
        "error": "<b>No Login code in the message found.</b>",
        "waiting": "<b>Waiting for the login code...</b>",
        "not_pchat": "<b>This is no private chat. Use <code>.lcr group --force</code></b>",
        "not_group": "This command is for groups only.",
        "no_self": "<b>You can't use it on yourself.</b>",
        "_cfg_timeout": "<b>Define a time to wait for the Code.</b>",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "timeout",
                "120",
                doc=lambda: self.strings("_cfg_timeout"),
                validator=loader.validators.Integer(minimum=0, maximum=300),
            ),
        )

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me(True)

    @loader.owner
    async def lcrcmd(self, message: Message):
        """Available commands:
           .lcr
             - waiting for the login code from TG service chat, use in private.
           .lcr group --force
             - waiting for the login code from TG service chat, use in group."""

        user_msg = utils.get_args_raw(message)
        chatid = message.chat_id
        logincode = False
        tgacc = 777000
        lc_timeout = self.config["timeout"]
        if chatid == (await message.client.get_me(True)).user_id:
            return await utils.answer(message, self.strings("no_self"))
        if user_msg not in ["", "group --force"]:
            return
        if not message.is_private and user_msg != "group --force":
            return await utils.answer(message, self.strings("not_pchat"))
        if message.is_private and user_msg == "group --force":
            return await utils.answer(message, self.strings("not_group"))
        async with message.client.conversation(tgacc) as conv:
            try:
                msgs = await utils.answer(message, self.strings("waiting"))
                logincode = conv.wait_event(events.NewMessage(incoming=True, from_users=tgacc), timeout=lc_timeout)
                logincode = await logincode
                logincodemsg = " ".join((await message.client.get_messages(tgacc, 1,
                                                                           search="Login code:"))[0].message)
                if logincodemsg is not None and "Login code:" in logincodemsg.lower():
                    logincode = True
                if logincode:
                    await message.client.send_read_acknowledge(tgacc, clear_mentions=True)
                    await message.client.delete_messages(chatid, msgs)
                    return await message.client.send_message(chatid, logincodemsg)
                await message.client.delete_messages(chatid, msgs)
                return await message.client.send_message(chatid, self.strings("error"))
            except asyncio.TimeoutError:
                await message.client.delete_messages(chatid, msgs)
                return await message.client.send_message(chatid, self.strings("timeouterror").format(lc_timeout))
