__version__ = (0, 0, 3)


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
# scope: hikka_min 1.1.28

import asyncio
import logging
import io
import re

from .. import loader, utils
from telethon.tl.types import Message

logger = logging.getLogger(__name__)
regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")


async def get_ids(link, message):
    match = regex.match(link)
    if not match:
        return await utils.answer(message, self.strings("invalid_link"))
    chat_id = match.group(4)
    msg_id = int(match.group(5))
    if chat_id.isnumeric():
        chat_id  = int(chat_id)
    return chat_id, msg_id


@loader.tds
class SaveMessageMod(loader.Module):
    """Saves Message from link to SavedMessages"""
    strings = {
        "name": "Save Channel Message",
        "done": "<b>Forward to saved complete.</b>",
        "invalid_link": "<b>Invalid link.</b>",
    }

    def __init__(self):
        self._ratelimit = []
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def smcmd(self, message: Message):
        """.sm <messagelink> to forward message to SavedMessages"""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        channel_id, msg_id = await get_ids(args, message)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(self._id, message=msgs)
        return await utils.answer(message, self.strings("done"))

    async def smhcmd(self, message: Message):
        """.smh <messagelink> to forward message to current chat"""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        channel_id, msg_id = await get_ids(args, message)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(message.chat_id, message=msgs)
        return await message.delete()
