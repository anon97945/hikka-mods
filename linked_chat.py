__version__ = (0, 0, 6)


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

import contextlib
import logging

from telethon.hints import EntityLike
from telethon.tl.types import (
    Channel,
    Message,
    User,
)


from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumLinkedChatMod(loader.Module):
    """
    Forces users to join a linked chat before they can send messages in the current chat.
    """

    strings = {
        "name": "Apo-LinkedChat",
        "developer": "@anon97945",
        "_cfg_activate_bool": "Activate the Module.",
        "_cfg_linked_chats": "Link a chat to another chat.\nFormat: <chat_id1>|<chat_id2>\nUser must be in Chat2 or will be punished in Chat1.",
        "_cfg_delete_timer": "Delete the message after x seconds.",
        "_cfg_mute_timer": "Mute the user for x minutes.",
        "_cfg_doc_raise_error": "Raise an error instead of a debug msg.",
        "triggered": (
            "{}, the comments are limited to discussiongroup members, "
            "please join our discussiongroup first."
            "\n\n👉🏻 {}\n\nRespectfully, the admins."
        ),
    }

    strings_en = {}

    strings_de = {
        "_cfg_activate_bool": "Aktiviere das Modul.",
        "_cfg_linked_chats": "Verlinke einen Chat mit einem anderen Chat.\nFormat: <chat_id1>|<chat_id2>\nUser muss in Chat2 sein oder wird in Chat1 bestraft.",
        "_cfg_delete_timer": "Lösche die Nachricht nach x Sekunden.",
        "_cfg_mute_timer": "Stummschalten des Users für x Minuten.",
        "_cfg_doc_raise_error": "Werfe einen Fehler anstatt einer Debug-Nachricht.",
        "triggered": (
            "{}, die Kommentarfunktion wurde auf die Chatmitglieder begrenzt, "
            "tritt bitte zuerst unserem Hauptchat bei."
            "\n\n👉🏻 {}\n\nHochachtungsvoll, die Obrigkeit."
        ),
    }

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {}

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Activate",
                True,
                doc=lambda: self.strings("_cfg_activate_bool"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "linked_chats",
                [],
                doc=lambda: self.strings("_cfg_linked_chats"),
                validator=loader.validators.Series(
                    validator=loader.validators.RegExp(
                        r"^(?:\d+){8,12}[|](?:\d+){8,12}$"
                    ),
                ),
            ),
            loader.ConfigValue(
                "delete_timer",
                60,
                doc=lambda: self.strings("_cfg_delete_timer"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "mute_timer",
                1,
                doc=lambda: self.strings("_cfg_mute_timer"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClas
        )

    async def client_ready(self):
        self._classname = self.__class__.__name__
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
        self.apo_lib.watcher_q.register(self.__class__.__name__, "q_watcher")

    async def on_unload(self):
        self.apo_lib.watcher_q.unregister(self.__class__.__name__, "q_watcher")
        return

    async def clinkedchatcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def q_watcher(self, message: Message):
        await self.queue_handler(message)

    async def queue_handler(self, message: Message):  # sourcery skip: low-code-quality
        if (
            not isinstance(message, Message)
            or message.out
            or not message.is_channel
            or not message.is_group
        ):
            return
        forced_links = self.config["linked_chats"]
        chat_id = utils.get_chat_id(message)
        user_id = await self.apo_lib.utils.get_user_id(message)
        for links in forced_links:
            chat1, chat2 = map(int, links.split("|"))
            if user_id not in [chat_id, self.inline.bot_id] and chat_id == chat1:
                chat = await self._client.get_entity(chat_id)
                chat1 = await self._client.get_entity(chat1)
                chat2 = await self._client.get_entity(chat2)
                user = await message.get_sender()
                if (
                    (
                        (not chat.admin_rights and not chat.creator)
                        or not chat.admin_rights.delete_messages
                    )
                    or (
                        isinstance(user, User)
                        and (perms := await self.apo_lib.utils.is_member(chat2, user))
                        and perms.is_admin
                    )
                    or (
                        isinstance(user, Channel)
                        and not (perms := None)
                        and await self.apo_lib.utils.is_linkedchannel(chat2, user)
                        or await self.apo_lib.utils.is_linkedchannel(chat1, user)
                    )
                ):
                    return
                if (isinstance(user, User) and not perms) or isinstance(user, Channel):
                    await self.punish_handler(chat1, chat2, user, message)
            with contextlib.suppress(Exception):
                return
        return

    async def punish_handler(
        self,
        chat1: EntityLike,
        chat2: EntityLike,
        user: User,
        message: Message,
    ):  # sourcery skip: low-code-quality
        await self.apo_lib.utils.delete_message(message, True)
        if chat1.admin_rights.ban_users:
            await self.apo_lib.utils.mute(chat1.id, user.id, self.config["mute_timer"])
        usertag = await self.apo_lib.utils.get_tag(user, True)
        link = await self.apo_lib.utils.get_invite_link(
            chat2
        )  # get the invite link of the linked chat
        if message.is_reply:
            reply = await self.apo_lib.utils.get_first_msg(message)
        else:
            reply = None
        if reply and not isinstance(await reply.get_sender(), Channel):
            reply = None
        if await self.apo_lib.utils.check_inlinebot(chat1.id):
            msg = await self.inline.bot.send_message(
                chat1.id
                if str(chat1.id).startswith("-100")
                else int(f"-100{chat1.id}"),
                self.apo_lib.utils.get_str(
                    "triggered", self.all_strings, message
                ).format(usertag, link),
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_to_message_id=getattr(reply, "id", None),
                allow_sending_without_reply=True,
            )
        else:
            msg = await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "triggered", self.all_strings, message
                ).format(usertag, link),
            )
        await self.apo_lib.utils.delete_message(msg, self.config["delete_timer"])
        return
