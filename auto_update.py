__version__ = (0, 1, 1)


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

from .. import loader, utils
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


async def buttonhandler(bmsg, chatid, caption1, caption2, data_btn1, data_btn2):
    fnd_btn1 = False
    fnd_btn2 = False
    bmsg = await bmsg.client.get_messages(chatid, ids=bmsg.id)
    buttons = bmsg.buttons
    if (
        caption1 in bmsg.message or caption2 in bmsg.message
    ) and bmsg.buttons is not None:
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
        "updating": "Hikka Userbot will be automatically updated in {} seconds.",
        "_cfg_auto_update": "Whether the Hikka Userbot should automatically update or not.",
        "_cfg_auto_update_delay": "Choose a delay to wait to start the automatic update.",
        "_cfg_update_msg_read": "Whether to mark the message as read or not.",
    }

    strings_de = {
        "updating": "Hikka Userbot wird in {} Sekunden automatisch aktualisiert.",
        "_cfg_auto_update": "Ob der Hikka Userbot automatisch aktualisieren soll oder nicht.",
        "_cfg_auto_update_delay": "Wählen Sie eine Wartezeit bis zum Start des automatischen Updates.",
        "_cfg_update_msg_read": "Ob die Nachricht als gelesen markiert werden soll oder nicht.",
    }

    strings_ru = {
        "updating": "Хикка будет автоматически обновлена через {} секунд.",
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
                "True",
                doc=lambda: self.strings("_cfg_auto_update"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "update_delay",
                "300",
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

    async def _autoupdate(self, msg):
        if self.config["mark_read"]:
            await self._client.send_read_acknowledge(
                msg.chat_id,
                clear_mentions=True,
            )
        logger.info(self.strings("updating").format(self.config["update_delay"]))
        await asyncio.sleep(self.config["update_delay"])
        try:
            return await msg.click(0)
        except Exception:
            return

    async def client_ready(self, client, db):
        self._db = db
        if self.config["auto_update"]:
            async for message in client.iter_messages(entity=self.inline.bot_id,
                                                      limit=5):
                if (
                    isinstance(message, Message)
                    and message.sender_id == self.inline.bot_id
                    and await buttonhandler(
                        message,
                        self.inline.bot_id,
                        "🌘 Hikka Update available!",
                        "🌘 Доступно обновление Hikka!",
                        "hikka_update",
                        "hikka_upd_ignore",
                    )
                ):
                    return await self._autoupdate(message)

    async def watcher(self, message: Message):
        if (
            isinstance(message, Message)
            and self.config["auto_update"]
            and utils.get_chat_id(message) == self.inline.bot_id
            and message.sender_id == self.inline.bot_id
            and message.is_private
            and await buttonhandler(
                message,
                self.inline.bot_id,
                "🌘 Hikka Update available!",
                "🌘 Доступно обновление Hikka!",
                "hikka_update",
                "hikka_upd_ignore",
            )
        ):
            return await self._autoupdate(message)
