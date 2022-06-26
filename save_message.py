__version__ = (0, 0, 12)


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
# scope: hikka_min 1.1.28

import logging
import re

from .. import loader, utils
from telethon.tl.types import Message

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
    }

    strings_de = {
        "done": "<b>Weiterleitung zu gespeicherten Daten abgeschlossen.</b>",
        "invalid_link": "<b>Ungültiger Link.</b>",
    }

    strings_ru = {
        "done": "<b>Перешлите для завершения сохранения.</b>",
        "invalid_link": "<b>Неверная ссылка.</b>",
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def smcmd(self, message: Message):
        """<messagelink> to forward message/media to SavedMessages."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        if not get_ids(args):
            return await utils.answer(message, self.strings("invalid_link"))
        channel_id, msg_id = get_ids(args)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(self._id, message=msgs)
        return await utils.answer(message, self.strings("done"))

    async def smhcmd(self, message: Message):
        """<messagelink> to forward message/media to current chat."""
        args = utils.get_args_raw(message).lower()
        if not args:
            return
        if not get_ids(args):
            return await utils.answer(message, self.strings("invalid_link"))
        channel_id, msg_id = get_ids(args)
        msgs = await message.client.get_messages(channel_id, ids=msg_id)
        msgs = await message.client.send_message(utils.get_chat_id(message), message=msgs)
        return await message.delete()
