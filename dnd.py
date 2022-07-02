__version__ = (0, 1, 16)


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

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

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
        "name": "Apo DND",
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
        "banned": ("😊 <b>Hey there •ᴗ•</b>\n<b>i am Unit «SIGMA»<b>, the <b>guardian</b> of this account. You are <b>not approved</b>! "
                   "You can contact my owner <b>in a groupchat</b>, if you need help.\n<b>I need to ban you in terms of security.</b>"),
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
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_ru = {
        "_cls_doc": ("⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬ ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n"
                     "-> Запрещает людям отправлять вам нежелательные личные сообщения."
                     "-> Избавляет от беспокойства, когда вы недоступны."
                     "Смотрите `.config apodiktum dnd`."),
        "_cmd_doc_allowpm": "<ответ или username> - Разрешает пользователю писать вам в ЛС.",
        "_cmd_doc_cdnd": "Это откроет конфиг для модуля.",
        "_cmd_doc_denypm": "<ответ или username> - Запрещает пользователю писать вам в ЛС.",
        "_cmd_doc_report": "<ответ> - Отправляет жалобу на пользователя на СПАМ. Использовать только в ЛС.",
        "_cmd_doc_block": "<ответ> - Блокирует этого пользователя без предупреждения.",
        "_cmd_doc_unblock": "<ответ> - Разблокировать этого пользователя.",
        "_cmd_doc_delstatus": "<короткое_название> - Удаляет статус.",
        "_cmd_doc_newstatus": ("<короткое_название> <notif|0/1> <text>\n"
                               " - Новый статус\n"
                               " - Пример: .newstatus test 1 Привет!"),
        "_cmd_doc_pmbanlast": "<число> - Блокирует и удаляет диалоги с большим кол-вом новых пользователей.",
        "_cmd_doc_status": "<короткое_название> - Устанавливает статус.",
        "_cmd_doc_statuses": " - Показывает доступные статусы.",
        "_cmd_doc_unstatus": " - Удаляет статус.",
        "_cfg_active_threshold": "Какое количество Ваших сообщений необходимо, чтобы доверять пользователю.",
        "_cfg_afk_no_grp": "Если установлено True, AFK не будет отвечать в группах.",
        "_cfg_custom_msg": "Кастомное оповещение неодобренных пользователей. Оставьте пустым, чтобы оставить по умолчанию.",
        "_cfg_delete_dialog": "Если установлено true, диалог будет удалён после блокировки.",
        "_cfg_ignore_active": "Если установлено true, игнорирует диалоги, где вы участвовали.",
        "_cfg_ignore_contacts": "Если установлено true, игнорирует контакты.",
        "_cfg_gone": "Если установлено true, AFK сообщение будет включать время, когда вы ушли.",
        "_cfg_photo": "Фото, которое отправляется вместе с уведомлением о блокировке",
        "_cfg_pmbl": "Если установлено true, PMBL активирован.",
        "_cfg_report_spam": "Если установлено true, после блокировки на пользователя будет отправлена жалоба.",
        "_log_msg_approved": "Пользователь {} допущен в ЛС, фильтр: {}",
        "_log_msg_punished": "Нарушитель наказан: {}",
        "_log_msg_unapproved": "Пользователь {} не допущен к ЛС.",
        "afk_message_gone": "{}\n\n<b><u>Ушёл уже как:</u></b>\n<code>{}h</code>",
        "afk_message_nogone": "{}",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> допущен к ЛС.</b>',
        "args_pmban": "ℹ️ <b>Пример использования: </b><code>.pmbanlast 5</code>",
        "available_statuses": "<b>🦊 Доступные статусы:</b>\n\n",
        "banned": ("😊 <b>Привет •ᴗ•</b>\n<b>«SIGMA»<b>, <b>защитник</b> этого аккаунта. Вы <b>не допущены к ЛС</b>! "
                   "Вы можете связаться с моим владельцем<b>в чате</b>, если Вам нужна помощь.\n<b>По правилам безопасности, я должен заблокировать Вас.</b>"),
        "banned_log": ('👮 <b>Я заблокировал <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Контакт</b>\n<b>{} Начатый тобой</b>\n<b>{} '
                       'Активный диалог</b>\n\n<b>✊ Действия</b>\n\n<b>{} Сообщить о спаме</b>\n<b>{} Удалить диалог</b>\n<b>{} Заблокировать</b>\n\n<b>ℹ️ Сообщение</b>\n<code>{}</code>'),
        "blocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> заблокирован.</b>',
        "hello": "🔏 <b>«SIGMA»</b> защищает ваши личные сообщения от нежелательного контакта. Это будет блокировать всех, кто попытается связаться с Вами..\n\nИспользуй <code>.pmbanlast</code> если уже были попытки нежелательного вторжения.",
        "no_pchat": "<b>Эта команда работает только в ЛС.</b>",
        "no_reply": "ℹ️ <b>Ответьте на сообщение, чтобы заблокировать пользователя.</b>",
        "no_status": "<b>🚫 Нет активного статусп.</b>",
        "pm_reported": "⚠️ <b>Отправил жалобу на спам!</b>",
        "pzd_with_args": "<b>🚫 Аргументы некорректны.</b>",
        "removed": "😶‍🌫️ <b>Удалил {} последних диалогов!</b>",
        "removing": "😶‍🌫️ <b>Удаляю {} последних диалогов...</b>",
        "status_created": "<b>✅ Статус {} установлен.</b>\n<code>{}</code>\nNotify: {}",
        "status_not_found": "<b>🚫 Статус не найден.</b>",
        "status_removed": "<b>✅ Статус {} удалён.</b>",
        "status_set": "<b>✅ Статус установлен\n</b><code>{}</code>\nОповещение: {}",
        "status_unset": "<b>✅ Статус удалён.</b>",
        "unapproved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> не допущен к ЛС.</b>',
        "unblocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> разблокирован.</b>',
        "user_not_specified": "🚫 <b>Вы не указали пользователя.</b>",
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
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_log",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_log"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_debug",
                False,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_debug"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
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
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

    async def on_unload(self):
        self._pt_task.cancel()
        return

    def _strings(self, string, chat_id):
        languages = {"ru_chats": self.strings_ru}
        if self.lookup("Apo-Translations"):
            forced_translation_db = self.lookup("Apo-Translations").config
            for lang, strings in languages.items():
                if chat_id in forced_translation_db[lang]:
                    if string in strings:
                        return strings[string]
                    logger.debug(f"String: {string} not found in\n{strings}")
                    break
        else:
            logger.debug(f"Apo-Translations loaded: {self.lookup('Apo-Translations')}")
        return self.strings(string)

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

    async def cdndcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def pmbanlastcmd(self, message: Message):
        """
        <number> - Ban and delete dialogs with n most new users.
        """
        n = utils.get_args_raw(message)
        if not n or not n.isdigit():
            await utils.answer(message, self._strings("args_pmban", utils.get_chat_id(message)))
            return

        n = int(n)

        await utils.answer(message, self._strings("removing", utils.get_chat_id(message)).format(n))

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

        await utils.answer(message, self._strings("removed", utils.get_chat_id(message)).format(n))

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
                await utils.answer(message, self._strings("user_not_specified", utils.get_chat_id(message)))
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
                await utils.answer(message, self._strings("user_not_specified", utils.get_chat_id(message)))
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
        if not message.is_private:
            await utils.answer(message, self._strings("no_pchat", utils.get_chat_id(message)))
            return
        chat_id = utils.get_chat_id(message)
        user = await self._client.get_entity(chat_id)
        await message.client(ReportSpamRequest(peer=user.id))
        await utils.answer(message, self._strings("pm_reported", utils.get_chat_id(message)))

    async def blockcmd(self, message: Message):
        """
        <reply> - Block this user without being warned.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(message, self._strings("no_reply", utils.get_chat_id(message)))
            return
        await message.client(BlockRequest(user.id))
        await utils.answer(message, self._strings("blocked", utils.get_chat_id(message)).format(user.id, get_display_name(user)))

    async def unblockcmd(self, message: Message):
        """
        <reply> - Unblock this user.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(message, self._strings("no_reply", utils.get_chat_id(message)))
            return
        await message.client(UnblockRequest(user.id))
        await utils.answer(message, self._strings("unblocked", utils.get_chat_id(message)).format(user.id, get_display_name(user)))

    async def statuscmd(self, message: Message):
        """
        <short_name> - Set status.
        """
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(message, self._strings("status_not_found", utils.get_chat_id(message)))
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
            await utils.answer(message, self._strings("pzd_with_args", utils.get_chat_id(message)))
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
            await utils.answer(message, self._strings("status_not_found", utils.get_chat_id(message)))
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
            await utils.answer(message, self._strings("no_status", utils.get_chat_id(message)))
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

        await utils.answer(message, self._strings("status_unset", utils.get_chat_id(message)))

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
                try:
                    await self._global_queue_handler_process(self._global_queue.pop(0))
                except Exception as e:
                    logger.debug(f"global_queue_handler_process error:\n{str(e)}")
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
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            is_pmbl = await self.p__pmbl(chat, user, message)
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
        return True

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


class MigratorClass():
    """
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
    """

    strings = {
        "_log_doc_migrated_db": "Migrated {} database of {} -> {}:\n{}",
        "_log_doc_migrated_cfgv_val": "[Dynamic={}] Migrated default config value:\n{} -> {}",
        "_log_doc_no_dynamic_migration": "No module config found. Did not dynamic migrate:\n{{{}: {}}}",
        "_log_doc_migrated_db_not_found": "`{}` database not found. Did not migrate {} -> {}",
    }

    changes = {
    }

    def __init__(self):
        self._ratelimit = []

    async def init(
        self,
        client: "TelegramClient",  # type: ignore
        db: "Database",  # type: ignore
        modules: str,  # type: ignore
        classname: str,  # type: ignore
        name: str,  # type: ignore
        log: bool = False,  # type: ignore
        debug: bool = False,  # type: ignore
    ):
        self._client = client
        self._db = db
        self._classname = classname
        self._name = name
        self.modules = modules
        self.log = log
        self.debug = debug
        self.hashs = []
        self.hashs = self._db.get(self._classname, "hashs", [])
        self._migrate_to = list(self.changes)[-1] if self.changes else None

    async def migrate(self, log: bool = False, debug: bool = False):
        self.log = log
        self.debug = debug
        logger.error(f"Log: {self.log} | Debug: {self.debug}")
        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])

            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if migrate:
                await self._logger(f"Open migrations: {migrate}", self.debug, True)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug, True)
                    return True
            elif not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | Forcehash done: {self.hashs}", self.debug, True)
                return False
            else:
                await self._logger(f"Open migrations: {migrate} | Skip migration.", self.debug, True)
                return False
            return False
        await self._logger("No changes in `changes` dictionary found.", self.debug, True)
        return False

    async def auto_migrate_handler(self, auto_migrate: bool = False):
        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])
            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if auto_migrate and migrate:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate}", self.debug, True)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug, True)
                    return
            elif not auto_migrate and not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Forcehash done: {self.hashs}", self.debug, True)
                return
            else:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Skip migrate_handler.", self.debug, True)
                return
        await self._logger("No changes in `changes` dictionary found.", self.debug, True)
        return

    async def force_set_hashs(self):
        await self._set_missing_hashs()
        return True

    async def check_new_migration(self):
        chash = hashlib.sha256(self._migrate_to.encode('utf-8')).hexdigest()
        return chash not in self.hashs

    async def full_migrated(self):
        full_migrated = True
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self.changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        if category == "classname":
            if self._classname != old_classname and (old_classname in self._db.keys() and self._db[old_classname] and old_classname is not None):
                await self._logger(f"{migration} | {category} | old_value: {str(old_classname)} | new_value: {str(new_classname)}", self.debug, True)
                await self._copy_config(category, old_classname, new_classname, new_name)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_classname, new_classname))
        elif category == "name":
            await self._logger(f"{migration} | {category} | old_value: {str(old_name)} | new_value: {str(new_name)}", self.debug, True)
            if self._name != old_name and (old_name in self._db.keys() and self._db[old_name] and old_name is not None):
                await self._copy_config(category, old_name, new_name, new_classname)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_name, new_name))
        elif category == "config":
            await self._migrate_cfg_values(migration, category, new_name, new_classname)
        return

    async def _get_names(self, migration):
        old_name = None
        old_classname = None
        new_name = None
        new_classname = None
        for category in self.changes[migration]:
            if category == "classname":
                old_classname, new_classname = await self._get_changes(self.changes[migration][category].items())
            elif category == "name":
                old_name, new_name = await self._get_changes(self.changes[migration][category].items())
        if not new_name:
            new_name = self._name
        if not new_classname:
            new_classname = self._classname
        return old_classname, new_classname, old_name, new_name

    @staticmethod
    async def _get_changes(changes):
        old_value = None
        new_value = None
        for state, value in changes:
            if state == "old":
                old_value = value
            elif state == "new":
                new_value = value
        return old_value, new_value

    async def _migrate_cfg_values(self, migration, category, new_name, new_classname):
        if new_classname in self._db.keys() and "__config__" in self._db[new_classname]:
            if configdb := self._db[new_classname]["__config__"]:
                for cnfg_key in self.changes[migration][category]:
                    old_value, new_value = await self._get_changes(self.changes[migration][category][cnfg_key].items())
                    for key, value in configdb.items():
                        await self._logger(f"{migration} | {category} | ({{old_value: {str(old_value)}}} `==` {{new_value: {str(value)}}}) `and` {{key: {key}}} `==` {{cnfg_key: {cnfg_key}}}", self.debug, True)
                        if value == old_value and key == cnfg_key:
                            dynamic = False
                            self._db[new_classname]["__config__"][cnfg_key] = new_value
                            if (
                                self.modules.lookup(new_name)
                                and self.modules.lookup(new_name).config
                                and key in self.modules.lookup(new_name).config
                            ):
                                self.modules.lookup(new_name).config[cnfg_key] = new_value
                                dynamic = True
                            await self._logger(self.strings["_log_doc_migrated_cfgv_val"].format(dynamic, value, new_value))
        return

    async def _copy_config(self, category, old_name, new_name, name):
        if self._db[new_name]:
            temp_db = {new_name: copy.deepcopy(self._db[new_name])}
            self._db[new_name].clear()
            self._db[new_name] = await self._deep_dict_merge(temp_db[new_name], self._db[old_name])
            temp_db.pop(new_name)
        else:
            self._db[new_name] = copy.deepcopy(self._db[old_name])
        self._db.pop(old_name)
        await self._logger(self.strings["_log_doc_migrated_db"].format(category, old_name, new_name, self._db[new_name]))
        if category == "classname":
            await self._make_dynamic_config(name, new_name)
        if category == "name":
            await self._make_dynamic_config(new_name, name)
        return

    async def _deep_dict_merge(self, dct1, dct2, override=True) -> dict:
        merged = copy.deepcopy(dct1)
        for k, v2 in dct2.items():
            if k in merged:
                v1 = merged[k]
                if isinstance(v1, dict) and isinstance(v2, collections.Mapping):
                    merged[k] = await self._deep_dict_merge(v1, v2, override)
                elif isinstance(v1, list) and isinstance(v2, list):
                    merged[k] = v1 + v2
                elif override:
                    merged[k] = copy.deepcopy(v2)
            else:
                merged[k] = copy.deepcopy(v2)
        return merged

    async def _make_dynamic_config(self, new_name, new_classname=None):
        if new_classname is None:
            return
        if "__config__" in self._db[new_classname].keys():
            for key, value in self._db[new_classname]["__config__"].items():
                if (
                    self.modules.lookup(new_name)
                    and self.modules.lookup(new_name).config
                    and key in self.modules.lookup(new_name).config
                ):
                    self.modules.lookup(new_name).config[key] = value
                else:
                    await self._logger(self.strings["_log_doc_no_dynamic_migration"].format(key, value))
        return

    async def _set_hash(self, chash):
        self.hashs.append(chash)
        self._db.set(self._classname, "hashs", self.hashs)
        return

    async def _set_missing_hashs(self):
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)

    async def _logger(self, log_string, debug: bool = False, debug_msg: bool = False):
        if not debug_msg and self.log:
            return logger.info(log_string)
        if debug and debug_msg:
            return logger.info(log_string)
        return logger.debug(log_string)
