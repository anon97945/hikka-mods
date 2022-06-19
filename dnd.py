__version__ = (0, 0, 6)


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
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html


# meta developer: @apodiktum_modules
# scope: hikka_only
# scope: hikka_min 1.1.28

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama


import asyncio
import contextlib
import datetime
import logging
import time

from typing import Union

from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
from telethon.tl.types import Message, PeerUser, User, Chat
from telethon.utils import get_display_name, get_peer_id

from .. import loader, utils

logger = logging.getLogger(__name__)


def format_(state: Union[bool, None]) -> str:
    if state is None:
        return "❔"

    return "✅" if state else "🚫 Not"


@loader.tds
class ApodiktumDNDMod(loader.Module):
    """
     ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
    -> Prevents people sending you unsolicited private messages.
    -> Prevents disturbing when you are unavailable.
    Check the `.config apodiktum dnd`.
    """

    strings = {
        "name": "Apodiktum DND",
        "developer": "@anon97945",
        "_cfg_active_threshold": "What number of your messages is required to trust peer.",
        "_cfg_afk_no_grp": "If set to true, AFK will not reply in groups.",
        "_cfg_custom_msg": "Custom message to notify untrusted peers. Leave empty for default one.",
        "_cfg_delete_dialog": "If set to true, dialog will be deleted after banning.",
        "_cfg_ignore_active": "If set to true, ignore peers, where you participated.",
        "_cfg_ignore_contacts": "If set to true, ignore contacts.",
        "_cfg_gone": "If set to true, the AFK message will include the time you were gone.",
        "_cfg_photo": "Photo, which is sent along with banned notification.",
        "_cfg_pmbl": "If set to true, PMBL is active.",
        "_cfg_report_spam": "If set to true, user will be reported after banning.",
        "_log_msg_approved": "User approved in pm {}, filter: {}",
        "_log_msg_punished": "Intruder punished: {}",
        "_log_msg_unapproved": "User unapproved in pm {}.",
        "afk_message_gone": "{}\n\n<b><u>Gone since:</u></b>\n<code>{}h</code>",
        "afk_message_nogone": "{}",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> approved in pm.</b>',
        "args_pmban": "ℹ️ <b>Example usage: </b><code>.pmbanlast 5</code>",
        "available_statuses": "<b>🦊 Available statuses:</b>\n\n",
        "banned": ("😊 <b>Hey there •ᴗ•</b>\n<b>Unit «SIGMA»<b>, the <b>guardian</b> of this account. You are <b>not approved</b>! "
                   "You can contact my owner <b>in chat</b>, if you need help.\n<b>I need to ban you in terms of security.</b>"),
        "banned_log": ('👮 <b>I banned <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Contact</b>\n<b>{} Started by you</b>\n<b>{} '
                       'Active conversation</b>\n\n<b>✊ Actions</b>\n\n<b>{} Reported spam</b>\n<b>{} Deleted dialog</b>\n<b>{} Banned</b>\n\n<b>ℹ️ Message</b>\n<code>{}</code>'),
        "blocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> blocked.</b>',
        "hello": "🔏 <b>Unit «SIGMA»</b> protects your personal messages from intrusions. It will block everyone, who's trying to invade you.\n\nUse <code>.pmbanlast</code> if you've already been pm-raided.",
        "no_pchat": "<b>This command is only available in private chats.</b>",
        "no_reply": "ℹ️ <b>Reply to a message to block the user.</b>",
        "no_status": "<b>🚫 No status is active.</b>",
        "pm_reported": "⚠️ <b>You just got reported to spam !</b>",
        "pzd_with_args": "<b>🚫 Args are incorrect.</b>",
        "removed": "😶‍🌫️ <b>Removed {} last dialogs!</b>",
        "removing": "😶‍🌫️ <b>Removing {} last dialogs...</b>",
        "status_created": "<b>✅ Status {} created.</b>\n<code>{}</code>\nNotify: {}",
        "status_not_found": "<b>🚫 Status not found.</b>",
        "status_removed": "<b>✅ Status {} deleted.</b>",
        "status_set": "<b>✅ Status set\n</b><code>{}</code>\nNotify: {}",
        "status_unset": "<b>✅ Status removed.</b>",
        "unapproved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> unapproved in pm.</b>',
        "unblocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> unblocked.</b>',
        "user_not_specified": "🚫 <b>You haven't specified user.</b>",
    }

    _global_queue = []

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "PMBL_Active",
                True,
                doc=lambda: self.strings("_cfg_pmbl"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "active_threshold",
                5,
                doc=lambda: self.strings("_cfg_active_threshold"),
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "afk_gone_time",
                True,
                doc=lambda: self.strings("_cfg_gone"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "afk_no_group",
                True,
                doc=lambda: self.strings("_cfg_afk_no_grp"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_message",
                doc=lambda: self.strings("_cfg_custom_msg"),
            ),
            loader.ConfigValue(
                "delete_dialog",
                False,
                doc=lambda: self.strings("_cfg_delete_dialog"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_active",
                True,
                doc=lambda: self.strings("_cfg_ignore_active"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_contacts",
                True,
                doc=lambda: self.strings("_cfg_ignore_contacts"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "photo",
                "https://github.com/hikariatama/assets/raw/master/unit_sigma.png",
                doc=lambda: self.strings("_cfg_photo"),
                validator=loader.validators.Link(),
            ),
            loader.ConfigValue(
                "report_spam",
                False,
                doc=lambda: self.strings("_cfg_report_spam"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._ratelimit_afk = []
        self._ratelimit_pmbl = []
        self._ratelimit_pmbl_threshold = 10
        self._ratelimit_pmbl_timeout = 5 * 60
        self._sent_messages = []
        self._whitelist = self.get("whitelist", [])
        if not self.get("ignore_hello", False):
            await self.inline.bot.send_photo(
                self._tg_id,
                photo=r"https://github.com/hikariatama/assets/raw/master/unit_sigma.png",
                caption=self.strings("hello"),
                parse_mode="HTML",
            )

            self.set("ignore_hello", True)
        self._pt_task = asyncio.ensure_future(self._global_queue_handler())

    async def on_unload(self):
        self._pt_task.cancel()
        return

    def _approve(self, user: int, reason: str = "unknown"):
        self._whitelist += [user]
        self._whitelist = list(set(self._whitelist))
        self.set("whitelist", self._whitelist)
        logger.info(self.strings("_log_msg_approved").format(user, reason))

    def _unapprove(self, user: int):
        self._whitelist = list(set(self._whitelist))
        self._whitelist = list(filter(lambda x: x != user, self._whitelist))
        self.set("whitelist", self._whitelist)
        logger.info(self.strings("_log_msg_unapproved").format(user))

    async def _send_pmbl_message(self, message, contact, started_by_you, active_peer, self_id):
        if len(self._ratelimit_pmbl) < self._ratelimit_pmbl_threshold:
            try:
                await self._client.send_file(
                    message.peer_id,
                    self.config["photo"],
                    caption=self.config["custom_message"] or self.strings("banned"),
                )
            except Exception:
                await utils.answer(
                    message,
                    self.config["custom_message"] or self.strings("banned"),
                )

            self._ratelimit_pmbl += [round(time.time())]

            try:
                peer = await self._client.get_entity(message.peer_id)
            except ValueError:
                await asyncio.sleep(1)
                peer = await self._client.get_entity(message.peer_id)

            await self.inline.bot.send_message(
                self_id,
                self.strings("banned_log").format(
                    peer.id,
                    utils.escape_html(peer.first_name),
                    format_(contact),
                    format_(started_by_you),
                    format_(active_peer),
                    format_(self.config["report_spam"]),
                    format_(self.config["delete_dialog"]),
                    format_(True),
                    utils.escape_html(message.raw_text[:3000]),
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

    async def _active_peer(self, message, cid):
        if self.config["ignore_active"]:
            q = 0

            async for msg in self._client.iter_messages(message.peer_id, limit=200):
                if msg.sender_id == self._tg_id:
                    q += 1

                if q >= self.config["active_threshold"]:
                    self._approve(cid, "active_threshold")
                    return True
        return False

    async def _punish_handler(self, cid):
        await self._client(BlockRequest(id=cid))
        if self.config["report_spam"]:
            await self._client(ReportSpamRequest(peer=cid))

        if self.config["delete_dialog"]:
            await self._client(
                DeleteHistoryRequest(peer=cid, just_clear=True, max_id=0)
            )

    async def pmbanlastcmd(self, message: Message):
        """
        <number> - Ban and delete dialogs with n most new users.
        """
        n = utils.get_args_raw(message)
        if not n or not n.isdigit():
            await utils.answer(message, self.strings("args_pmban"))
            return

        n = int(n)

        await utils.answer(message, self.strings("removing").format(n))

        dialogs = []
        async for dialog in self._client.iter_dialogs(ignore_pinned=True):
            try:
                if not isinstance(dialog.message.peer_id, PeerUser):
                    continue
            except AttributeError:
                continue

            m = (
                await self._client.get_messages(
                    dialog.message.peer_id,
                    limit=1,
                    reverse=True,
                )
            )[0]

            dialogs += [
                (
                    get_peer_id(dialog.message.peer_id),
                    int(time.mktime(m.date.timetuple())),
                )
            ]

        dialogs.sort(key=lambda x: x[1])
        to_ban = [d for d, _ in dialogs[::-1][:n]]

        for d in to_ban:
            await self._client(BlockRequest(id=d))

            await self._client(DeleteHistoryRequest(peer=d, just_clear=True, max_id=0))

        await utils.answer(message, self.strings("removed").format(n))

    async def allowpmcmd(self, message: Message):
        """
        <reply or user> - Allow user to pm you.
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        user = None

        try:
            user = await self._client.get_entity(args)
        except Exception:
            with contextlib.suppress(Exception):
                user = await self._client.get_entity(reply.sender_id) if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(message, self.strings("user_not_specified"))
                return

            user = chat

        self._approve(user.id, "manual_approve")
        await utils.answer(
            message, self.strings("approved").format(user.id, get_display_name(user))
        )

    async def denypmcmd(self, message: Message):
        """
        <reply or user> - Deny user to pm you.
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        user = None

        try:
            user = await self._client.get_entity(args)
        except Exception:
            with contextlib.suppress(Exception):
                user = await self._client.get_entity(reply.sender_id) if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(message, self.strings("user_not_specified"))
                return

            user = chat

        self._unapprove(user.id)
        await utils.answer(
            message, self.strings("unapproved").format(user.id, get_display_name(user))
        )

    async def reportcmd(self, message: Message):
        """
        <reply> - Report the user to spam. Use only in PM.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(message, self.strings("no_reply"))
            return
        if message.is_reply and message.is_private:
            await message.client(ReportSpamRequest(peer=user.id))
        else:
            await utils.answer(self.strings("no_pchat"))
        await utils.answer(message, self.strings("pm_reported"))

    async def blockcmd(self, message: Message):
        """
        <reply> - Block this user without being warned.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(message, self.strings("no_reply"))
            return
        await message.client(BlockRequest(user.id))
        await utils.answer(message, self.strings("blocked").format(user.id, get_display_name(user)))

    async def unblockcmd(self, message: Message):
        """
        <reply> - Unblock this user.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(message, self.strings("no_reply"))
            return
        await message.client(UnblockRequest(user.id))
        await utils.answer(message, self.strings("unblocked").format(user.id, get_display_name(user)))

    async def statuscmd(self, message: Message):
        """
        <short_name> - Set status.
        """
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(message, self.strings("status_not_found"))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.set("status", args)
        self.set("gone", time.time())
        self._ratelimit_afk = []
        await utils.answer(
            message,
            self.strings("status_set").format(
                utils.escape_html(self.get("texts", {})[args]),
                str(self.get("notif")[args]),
            ),
        )

    async def newstatuscmd(self, message: Message):
        """
        <short_name> <notif|0/1> <text> - New status.
        Example: .newstatus test 1 Hello!
        """
        args = utils.get_args_raw(message)
        args = args.split(" ", 2)
        if len(args) < 3:
            await utils.answer(message, self.strings("pzd_with_args"))
            await asyncio.sleep(3)
            await message.delete()
            return

        args[1] = args[1] in ["1", "true", "yes", "+"]
        texts = self.get("texts", {})
        texts[args[0]] = args[2]
        self.set("texts", texts)

        notif = self.get("notif", {})
        notif[args[0]] = args[1]
        self.set("notif", notif)
        await utils.answer(
            message,
            self.strings("status_created").format(
                utils.escape_html(args[0]),
                utils.escape_html(args[2]),
                args[1],
            ),
        )

    async def delstatuscmd(self, message: Message):
        """
        <short_name> - Delete status.
        """
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(message, self.strings("status_not_found"))
            await asyncio.sleep(3)
            await message.delete()
            return

        texts = self.get("texts", {})
        del texts[args]
        self.set("texts", texts)

        notif = self.get("notif", {})
        del notif[args]
        self.set("notif", notif)
        await utils.answer(
            message,
            self.strings("status_removed").format(utils.escape_html(args)),
        )

    async def unstatuscmd(self, message: Message):
        """
        Remove status.
        """
        if not self.get("status", False):
            await utils.answer(message, self.strings("no_status"))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.set("status", False)
        self.set("gone", "")
        self._ratelimit_afk = []

        for m in self._sent_messages:
            try:
                await m.delete()
            except Exception:
                logger.exception("Message not deleted due to")

        self._sent_messages = []

        await utils.answer(message, self.strings("status_unset"))

    async def statusescmd(self, message: Message):
        """
        Show available statuses.
        """
        res = self.strings("available_statuses")
        for short_name, status in self.get("texts", {}).items():
            res += f"<b><u>{short_name}</u></b> | Notify: <b>{self._db.get('Statuses', 'notif', {})[short_name]}</b>\n{status}\n➖➖➖➖➖➖➖➖➖\n"

        await utils.answer(message, res)

    async def watcher(self, message: Message):
        self._global_queue += [message]

    async def _global_queue_handler(self):
        while True:
            while self._global_queue:
                await self._global_queue_handler_process(self._global_queue.pop(0))
            await asyncio.sleep(0)

    async def _global_queue_handler_process(self, message: Message):
        is_pmbl = False
        if not isinstance(message, Message):
            return
        chat_id = utils.get_chat_id(message)
        try:
            user_id = (
                getattr(message, "sender_id", False)
                or message.action_message.action.users[0]
            )
        except Exception:
            try:
                user_id = message.action_message.action.from_id.user_id
            except Exception:
                try:
                    user_id = message.from_id.user_id
                except Exception:
                    try:
                        user_id = message.action_message.from_id.user_id
                    except Exception:
                        try:
                            user_id = message.action.from_user.id
                        except Exception:
                            try:
                                user_id = (await message.get_user()).id
                            except Exception:
                                logger.debug(f"Can't extract entity from event {type(message)}")
                                return
        user_id = (
            int(str(user_id)[4:]) if str(user_id).startswith("-100") else int(user_id)
        )
        if (
            not getattr(message, "out", False)
            and isinstance(message, Message)
            and isinstance(message.peer_id, PeerUser)
            and self.config["PMBL_Active"]
            and chat_id
            not in {
                1271266957,  # @replies
                777000,  # Telegram Notifications
                self._tg_id,  # Self
            }
        ):
            is_pmbl = True
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            await self.p__pmbl(chat, user, message)
        if not is_pmbl:
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            await self.p__afk(chat, user, message)
        return

    async def p__pmbl(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
    ) -> bool:
        cid = chat.id
        if cid in self._whitelist:
            return

        contact, started_by_you, active_peer = None, None, None

        with contextlib.suppress(ValueError):
            if user.bot:
                return self._approve(cid, "bot")

            if self.config["ignore_contacts"]:
                if user.contact:
                    return self._approve(cid, "ignore_contacts")
                contact = False

        first_message = (
            await self._client.get_messages(
                message.peer_id,
                limit=1,
                reverse=True,
            )
        )[0]

        if (
            getattr(message, "raw_text", False)
            and first_message.sender_id == self._tg_id
        ):
            return self._approve(cid, "started_by_you")
        started_by_you = False

        active_peer = await self._active_peer(message, cid)
        if active_peer:
            return

        self._ratelimit_pmbl = list(
            filter(
                lambda x: x + self._ratelimit_pmbl_timeout < time.time(),
                self._ratelimit_pmbl,
            )
        )

        await self._send_pmbl_message(message, contact, started_by_you, active_peer, self._tg_id)
        await self._punish_handler(cid)

        self._approve(cid, "banned")
        logger.warning(self.strings("_log_msg_punished").format(cid))

    async def p__afk(
        self,
        chat: Union[Chat, int],
        user: Union[User, int],
        message: Union[None, Message] = None,
    ) -> bool:
        if not isinstance(message, Message) or not self.get("status", False):
            return
        if getattr(message.to_id, "user_id", None) == self._tg_id:
            if user.id in self._ratelimit_afk or user.is_self or user.bot or user.verified:
                return
        elif not message.mentioned:
            return
        if chat.id in self._ratelimit_afk:
            return
        now = datetime.datetime.now().replace(microsecond=0)
        gone = datetime.datetime.fromtimestamp(self.get("gone")).replace(microsecond=0)
        diff = now - gone

        if message.is_private or not self.config["afk_no_group"]:
            if self.config["afk_gone_time"]:
                m = await utils.answer(
                    message,
                    self.strings("afk_message_gone").format(self.get("texts", {"": ""})[self.get("status", "")], diff),
                )
            else:
                m = await utils.answer(
                    message,
                    self.strings("afk_message_nogone").format(self.get("texts", {"": ""})[self.get("status", "")]),
                )

            self._sent_messages += [m]

        if not self.get("notif", {"": False})[self.get("status", "")]:
            await self._client.send_read_acknowledge(
                message.peer_id,
                clear_mentions=True,
            )

        self._ratelimit_afk += [chat.id]
