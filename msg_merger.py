__version__ = (0, 0, 42)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2022
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/file_dumbster/11
# meta pic: https://t.me/file_dumbster/13

# scope: hikka_only
# scope: hikka_min 1.3.0


import contextlib
import logging
from datetime import datetime, timezone


from telethon.errors import MessageIdInvalidError
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumMsgMergerMod(loader.Module):
    """
    This module will merge own messages, if there is no message in between.
    """

    strings = {
        "name": "Apo-MsgMerger",
        "developer": "@anon97945",
        "_cfg_active": "Whether the module is turned on (or not).",
        "_cfg_blacklist_chats": "The list of chats that the module will watch(or not).",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_edit_timeout": (
            "The maximum time in minuted to edit the message. 0 for no limit."
        ),
        "_cfg_ignore_prefix": "The prefix to ignore the merging fully.",
        "_cfg_link_preview": (
            "Whether to send webpage previews.\nLeave empty to use"
            " automatically decide based on the messages to merge."
        ),
        "_cfg_merge_own_reply": "Whether to merge any message from own reply.",
        "_cfg_merge_own_reply_msg": (
            "The message which will stay if the message is merged from own reply."
        ),
        "_cfg_merge_urls": "Whether to merge messages with URLs.",
        "_cfg_new_lines": "The number of new lines to add to the message.",
        "_cfg_reverse_merge": (
            "Whether to merge into the new(True) or old(False) message."
        ),
        "_cfg_skip_emoji": "Whether to skip the merging of messages with single emoji.",
        "_cfg_skip_length": "The length of the message to skip the merging.",
        "_cfg_skip_prefix": "The prefix to skip the merging.",
        "_cfg_skip_reply": "Whether to skip the merging of messages with reply.",
        "_cfg_whitelist": (
            "Whether the chatlist includes(True) or excludes(False) the chat."
        ),
        "undo_merge_fail": "<b>Failed to unmerge the messages.</b>",
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

    changes = {
        "migration1": {
            "name": {
                "old": "Apo MsgMerger",
                "new": "Apo-MsgMerger",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.merged_msgs = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "active",
                True,
                doc=lambda: self.strings("_cfg_active"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "chatlist",
                doc=lambda: self.strings("_cfg_blacklist_chats"),
                validator=loader.validators.Series(loader.validators.TelegramID()),
            ),
            loader.ConfigValue(
                "edit_timeout",
                2,
                doc=lambda: self.strings("_cfg_edit_timeout"),
                validator=loader.validators.Union(
                    loader.validators.Integer(minimum=1),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "ignore_prefix",
                ["+"],
                doc=lambda: self.strings("_cfg_ignore_prefix"),
                validator=loader.validators.Series(
                    loader.validators.Union(
                        loader.validators.String(length=1),
                        loader.validators.NoneType(),
                    ),
                ),
            ),
            loader.ConfigValue(
                "link_preview",
                doc=lambda: self.strings("_cfg_link_preview"),
                validator=loader.validators.Union(
                    loader.validators.Boolean(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "merge_own_reply",
                False,
                doc=lambda: self.strings("_cfg_merge_own_reply"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "merge_urls",
                True,
                doc=lambda: self.strings("_cfg_merge_urls"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "new_line_pref",
                ">",
                doc=lambda: self.strings("_cfg_new_line_prefix"),
                validator=loader.validators.Union(
                    loader.validators.String(length=1),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "new_lines",
                1,
                doc=lambda: self.strings("_cfg_new_lines"),
                validator=loader.validators.Integer(minimum=1, maximum=2),
            ),
            loader.ConfigValue(
                "own_reply_msg",
                "<code>☝️</code>",
                doc=lambda: self.strings("_cfg_merge_own_reply_msg"),
                validator=loader.validators.Union(
                    loader.validators.String(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "reverse_merge",
                True,
                doc=lambda: self.strings("_cfg_reverse_merge"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "skip_emoji",
                True,
                doc=lambda: self.strings("_cfg_skip_emoji"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "skip_length",
                doc=lambda: self.strings("_cfg_skip_length"),
                validator=loader.validators.Union(
                    loader.validators.Integer(minimum=0),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "skip_prefix",
                [">"],
                doc=lambda: self.strings("_cfg_skip_prefix"),
                validator=loader.validators.Series(
                    loader.validators.Union(
                        loader.validators.String(length=1),
                        loader.validators.NoneType(),
                    ),
                ),
            ),
            loader.ConfigValue(
                "skip_reply",
                False,
                doc=lambda: self.strings("_cfg_skip_reply"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                True,
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )

    async def cmsgmergercmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def unmergecmd(self, message: Message):
        """
        This will unmerge the messages.
        """
        chat_id = utils.get_chat_id(message)
        if utils.get_chat_id(message) in self.merged_msgs:
            try:
                for key, msg_value in self.merged_msgs[chat_id]["message"].items():
                    if key == "text":
                        msg_text = msg_value
                    elif key == "link_preview":
                        msg_link_preview = msg_value
                for key, msg_value in self.merged_msgs[chat_id]["last_msg"].items():
                    if key == "id":
                        last_msg_id = msg_value
                    elif key == "text":
                        last_msg_text = msg_value
                    elif key == "link_preview":
                        last_msg_link_preview = msg_value
                await self.client.edit_message(
                    chat_id,
                    last_msg_id,
                    last_msg_text,
                    link_preview=last_msg_link_preview,
                )
                await self.client.edit_message(
                    message, msg_text, link_preview=msg_link_preview
                )
            except MessageIdInvalidError:
                await utils.answer(message, self.strings("undo_merge_fail"))
        else:
            await utils.answer(message, self.strings("undo_merge_fail"))
        self.merged_msgs.clear()

    @loader.watcher("out", "only_messages", "editable", "no_commands")
    async def watcher(self, message: Message):
        if (
            not self.config["active"]
            or message.via_bot
            or (
                message.media
                and not getattr(message.media, "webpage", False)
                or (
                    not self.config["merge_urls"]
                    and self.apo_lib.utils.get_entityurls(message)
                )
            )
        ):
            return

        chat_id = utils.get_chat_id(message)

        if (self.config["whitelist"] and chat_id not in self.config["chatlist"]) or (
            not self.config["whitelist"] and chat_id in self.config["chatlist"]
        ):
            return
        last_msg = None

        if self.config["ignore_prefix"] and any(
            message.raw_text.startswith(prefix)
            for prefix in self.config["ignore_prefix"]
        ):
            return

        if self.config["skip_prefix"] and (
            found_prefix := next(
                (
                    message.raw_text.startswith(prefix)
                    for prefix in self.config["skip_prefix"]
                ),
                None,
            )
        ):
            text = message.text.replace(utils.escape_html(found_prefix), "", 1)
            if len(text) > 0:
                with contextlib.suppress(Exception):
                    if message.out:
                        await message.edit(text)

                return

        if (
            self.config["skip_length"]
            and len(utils.remove_html(message.text)) >= self.config["skip_length"]
        ):
            return
        try:
            for i in range(-4, -1):
                last_msg_iter = (await self._client.get_messages(chat_id, limit=5))[i]
                if last_msg_iter.id != message.id:
                    last_msg = last_msg_iter
                    break
        except IndexError:
            return

        if self.config["merge_own_reply"] and message.is_reply:
            last_msg_reply = await message.get_reply_message()
            last_msg = last_msg_reply
        else:
            last_msg_reply = None

        if (
            (
                self.config["skip_emoji"]
                and (
                    self.apo_lib.utils.is_emoji(message.raw_text)
                    or self.apo_lib.utils.is_emoji(last_msg.raw_text)
                )
            )
            or (
                self.config["skip_reply"]
                and not self.config["merge_own_reply"]
                and (message.is_reply or last_msg.is_reply)
            )
            or (
                last_msg.is_reply
                and message.is_reply
                and not self.config["merge_own_reply"]
            )
        ):
            return

        if (
            last_msg.sender_id != self.tg_id
            or not isinstance(last_msg, Message)
            or last_msg.via_bot
            or last_msg.fwd_from
            or (
                last_msg.media
                and not getattr(last_msg.media, "webpage", False)
                or (
                    not self.config["merge_urls"]
                    and self.apo_lib.utils.get_entityurls(last_msg)
                )
            )
            or utils.remove_html(last_msg.text)[0] == self.get_prefix()
        ):
            return

        if self.config["ignore_prefix"] and any(
            last_msg.raw_text.startswith(prefix)
            for prefix in self.config["ignore_prefix"]
        ):
            return

        if (
            self.config["edit_timeout"]
            and (
                datetime.now(timezone.utc) - (last_msg.edit_date or last_msg.date)
            ).total_seconds()
            > self.config["edit_timeout"] * 60
        ) and (
            (self.config["merge_own_reply"] and not message.is_reply)
            or not self.config["merge_own_reply"]
        ):
            return

        text = last_msg.text
        text += "\n" * self.config["new_lines"]

        if self.config["new_line_pref"]:
            text += self.config["new_line_pref"]
        text += message.text

        if (message.is_reply or self.config["reverse_merge"]) and (
            not self.config["merge_own_reply"] or not message.is_reply
        ):
            message, last_msg = last_msg, message
            message_text = last_msg.text
            last_msg_text = message.text
        else:
            message_text = message.text
            last_msg_text = last_msg.text
        if self.config["link_preview"] is None:
            link_preview = getattr(message.media, "webpage", False) or getattr(
                last_msg.media, "webpage", False
            )
        else:
            link_preview = bool(self.config["link_preview"])
        try:
            if self.config["reverse_merge"] and (
                self.config["merge_own_reply"]
                and (last_msg.is_reply or message.is_reply)
            ):
                if last_msg.is_reply:
                    reply = await last_msg.get_reply_message()
                else:
                    reply = await message.get_reply_message()
                await last_msg.delete()
                msg = await last_msg.client.send_message(
                    chat_id, text, reply_to=reply, link_preview=link_preview
                )
            else:
                msg = await last_msg.edit(text, link_preview=link_preview)

            if msg.out:
                if (
                    self.config["merge_own_reply"]
                    and self.config["own_reply_msg"]
                    and not self.config["reverse_merge"]
                    and message.is_reply
                ):
                    await message.edit(
                        self.config["own_reply_msg"], link_preview=link_preview
                    )
                else:
                    await message.delete()
            self.merged_msgs.clear()
            self.merged_msgs[chat_id] = {
                "message": {
                    "text": message_text,
                    "link_preview": link_preview,
                },
                "last_msg": {
                    "id": msg.id or last_msg.id,
                    "text": last_msg_text,
                    "link_preview": link_preview,
                },
            }
            return
        except Exception as exc:
            logger.debug(f"Edit failed on last_msg:\n{str(exc)}")
            return
