__version__ = (0, 1, 0)

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

from .. import loader, utils
from telethon.tl.types import Message

import logging

from telethon.errors import ReactionInvalidError


logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumAutoReactMod(loader.Module):
    """
    AutoReact to messages.
    """
    strings = {
        "name": "Apodiktum AutoReact",
        "developer": "@anon97945",
        "no_command": "<b>This is no command. Everything is configured within</b>\n<code>.config apodiktum autoreact</code>\n\n<b><i><u>This module was created by {}.</u></i></b>",
        "_cfg_doc_raise_error": "Raise an error if the emoji is not valid.",
        "_cfg_doc_reactions": ("Setup AutoReact.\nYou can define alternative emojis to react with, when the Chat doesn't allow the first, second etc.\n"
                               "You can also define an all OR global state, which will either apply reactions to all chat members (all) or to one user in all groups(global).\n"
                               "You can't use both at the same time!\n\n"
                               "Pattern:\n<userid/all>|<chatid/global>|<emoji1>|<emoji2>|<emoji3>..."),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reaction_active",
                False,
                doc=lambda: self.strings("_cfg_doc_react"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "raise_error",
                False,
                doc=lambda: self.strings("_cfg_doc_raise_error"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "reactions",
                doc=lambda: self.strings("_cfg_doc_reactions"),
                validator=loader.validators.Series(
                    validator=loader.validators.RegExp("^(?:(?:\d+)[|](?:\d+|global)|(?:\d+|all)[|]\d+)(?:[|][👍👎❤️🔥🥰👏😁🤔🤯😱🤬😢🎉🤩🤮💩🙏👌🕊🤡🥱🥴😍🐳🌚🌭💯🤣❤️‍🔥])+$")
                ),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def autoreactcmd(self, message: Message):
        """
        This is no command.\nEverything is configured within .config apodiktum autoreact
        """
        return await utils.answer(message, self.strings("no_command").format(self.strings("developer")))

    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return
        if not self.config["reaction_active"]:
            return
        config = self.config["reactions"]
        for reaction in config:
            userid, chatid, *emojis = reaction.split("|")
            if userid == "all" and chatid == "global":
                return
            if (str(message.sender_id) == userid or userid == "all") and (str(utils.get_chat_id(message)) == chatid or chatid == "global"):
                for emoji in emojis:
                    if await self._react_message(message, emoji, chatid):
                        return

    async def _react_message(self, message, emoji, chatid):
        try:
            await message.react(emoji)
            return True
        except ReactionInvalidError:
            if self.config["raise_error"]:
                logger.info(f"ReactionInvalidError: {emoji} in chat {chatid}")
            return False
