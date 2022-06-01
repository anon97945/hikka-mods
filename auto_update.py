__version__ = (0, 0, 5)


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

import logging
import asyncio

from .. import loader
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


async def buttonhandler(bmsg, chatid, caption, data_btn1, data_btn2):
    fnd_btn1 = False
    fnd_btn2 = False
    bmsg = await bmsg.client.get_messages(chatid, ids=bmsg.id)
    buttons = bmsg.buttons
    if caption in bmsg.message:
        for row in buttons:
            for button in row:
                if data_btn1 in str(button.data):
                    fnd_btn1 = True
                if data_btn2 in str(button.data):
                    fnd_btn2 = True
                if fnd_btn1 and fnd_btn2:
                    return True
    return False


@loader.tds
class AutoUpdateMod(loader.Module):
    """Automatically update your Hikka Userbot"""
    strings = {
        "name": "HikkaAutoUpdater",
        "updating": "Hikka Userbot was automatically updated."
        "_cfg_auto_update": "Whether the Hikka Userbot should automatically update or not.",
        "_cfg_auto_update_delay": "Choose a delay to wait to start the automatic update.",
        "_cfg_update_msg_read": "Whether to mark the message as read or not.",
    }

    strings_de = {
        "updating": "Hikka Userbot wurde automatisch geupdated."
        "_cfg_auto_update": "Ob der Hikka Userbot automatisch aktualisieren soll oder nicht.",
        "_cfg_auto_update_delay": "Wählen Sie eine Wartezeit bis zum Start des automatischen Updates.",
        "_cfg_update_msg_read": "Ob die Nachricht als gelesen markiert werden soll oder nicht.",
    }

    strings_ru = {
        "updating": "Hikka Юзербот был автоматически обновлен."
        "_cfg_auto_update": "Должен ли Hikka UserBot обновляться автоматически или нет.",
        "_cfg_auto_update_delay": "Выберите задержку для автоматического обновления.",
        "_cfg_update_msg_read": "Будет ли отмечать сообщение обновления как прочтённое или нет.",
    }

    strings_ru = {
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_update",
                "False",
                doc=lambda: self.strings("_cfg_auto_update"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "update_delay",
                "120",
                doc=lambda: self.strings("_cfg_auto_update_delay"),
                validator=loader.validators.Integer(minimum=60),
            ),
            loader.ConfigValue(
                "mark_read",
                "True",
                doc=lambda: self.strings("_cfg_update_msg_read"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        async for message in client.iter_messages(entity=self.inline.bot_id,
                                                        limit=20):
            if isinstance(message, Message) and message.from_id == self.inline.bot_id:
                if await buttonhandler(message, self.inline.bot_id, "🌘 Hikka Update available!", "hikka_update", "hikka_upd_ignore"):
                    if self.config["mark_read"]:
                        await self._client.send_read_acknowledge(
                            message.chat_id,
                            clear_mentions=True,
                        )
                    asyncio.sleep(self.config["update_delay"])
                    await message.delete()
                    logger.info(self.strings("updating"))
                    await self.allmodules.commands["update"](
                        await message.respond(f"{self.get_prefix()}update --force")
                    )

    async def watcher(self, message: Message):
        if (not isinstance(message, Message)
                or message.chat_id != self.inline.bot_id
                or message.from_id != self.inline.bot_id
                or not message.is_private):
            return
        if not await buttonhandler(message, self.inline.bot_id, "🌘 Hikka Update available!", "hikka_update", "hikka_upd_ignore"):
            return

        if self.config["mark_read"]:
            await self._client.send_read_acknowledge(
                message.chat_id,
                clear_mentions=True,
            )
        asyncio.sleep(self.config["update_delay"])
        await message.delete()
        logger.info(self.strings("updating"))
        await self.allmodules.commands["update"](
            await message.respond(f"{self.get_prefix()}update --force")
        )
