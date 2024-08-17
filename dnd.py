__version__ = (0, 3, 17)


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
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

import asyncio
import contextlib
import datetime
import logging
import re
import time
from typing import Union

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Channel, Message, PeerUser, User
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
    Check `.cdnd`.
    """

    strings = {
        "name": "Apo-DND",
        "developer": "@anon97945",
        "_cfg_active_threshold": (
            "What number of your messages is required to trust peer."
        ),
        "_cfg_afk_show_duration": (
            "If set to true, AFK message will include the the automatic removal time."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_custom_msg": (
            "Custom message to notify untrusted peers. Leave empty for default one."
        ),
        "_cfg_delete_dialog": "If set to true, dialog will be deleted after banning.",
        "_cfg_doc_afk_group_list": "React to Tags from chats in this list.",
        "_cfg_doc_whitelist": (
            "Whether the `afk_group_list`-list is for included(True) or"
            " excluded(False) chats."
        ),
        "_cfg_gone": (
            "If set to true, the AFK message will include the time you were gone."
        ),
        "_cfg_ignore_active": "If set to true, ignore peers, where you participated.",
        "_cfg_ignore_contacts": "If set to true, ignore contacts.",
        "_cfg_photo": "Photo, which is sent along with banned notification.",
        "_cfg_pmbl": "If set to true, PMBL is active.",
        "_cfg_report_spam": "If set to true, user will be reported after banning.",
        "_cfg_use_bio": "Show AFK message in bio.",
        "_log_msg_approved": "User approved in pm {}, filter: {}",
        "_log_msg_punished": "Intruder punished: {}",
        "_log_msg_unapproved": "User unapproved in pm {}.",
        "afk_message": "{}\n",
        "afk_message_duration": "\n<b><u>Duration:</u></b>\n<code>{}</code>",
        "afk_message_further": "\n<b><u>Further:</u></b>\n<code>{}</code>",
        "afk_message_gone": "\n<b><u>Gone since:</u></b>\n<code>{}</code>",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> approved in pm.</b>',
        "args_incorrect": "<b>🚫 Args are incorrect.</b>",
        "args_pmban": "ℹ️ <b>Example usage: </b><code>.pmbanlast 5</code>",
        "available_statuses": "<b>🦊 Available statuses:</b>\n\n",
        "banned": (
            "😊 <b>Hey there •ᴗ•</b>\n<b>i am Unit «SIGMA»<b>, the"
            " <b>guardian</b> of this account. You are <b>not approved</b>! You"
            " can contact my owner <b>in a groupchat</b>, if you need"
            " help.\n<b>I need to ban you in terms of security.</b>"
        ),
        "banned_log": (
            "👮 <b>I banned {}.</b>\n\n<b>{} Contact</b>\n<b>{} Started by"
            " you</b>\n<b>{} Active conversation</b>\n\n<b>✊"
            " Actions</b>\n\n<b>{} Reported spam</b>\n<b>{} Deleted"
            " dialog</b>\n<b>{} Blocked</b>\n\n<b>ℹ️"
            " Message</b>\n<code>{}</code>"
        ),
        "blocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> blocked.</b>',
        "hello": (
            "🔏 <b>Unit «SIGMA»</b> protects your personal messages from"
            " intrusions. It will block everyone, who's trying to invade"
            " you.\n\nUse <code>.pmbanlast</code> if you've already been"
            " pm-raided."
        ),
        "no_pchat": "<b>This command is only available in private chats.</b>",
        "no_reply": "ℹ️ <b>Reply to a message to block the user.</b>",
        "no_status": "<b>🚫 No status is active.</b>",
        "pm_reported": "⚠️ <b>You just got reported to spam !</b>",
        "removed": "😶‍🌫️ <b>Removed {} last dialogs!</b>",
        "removing": "😶‍🌫️ <b>Removing {} last dialogs...</b>",
        "status_created": "<b>✅ Status {} created.</b>\n<code>{}</code>\nNotify: {}",
        "status_not_found": "<b>🚫 Status not found.</b>",
        "status_removed": "<b>✅ Status {} deleted.</b>",
        "status_set": "<b>✅ Status set\n</b><code>{}</code>\nNotify: <code>{}</code>",
        "status_set_duration": "\nDuration: <code>{}</code>",
        "status_set_further": "\nFurther: <code>{}</code>",
        "status_unset": "<b>✅ Status removed.</b>",
        "unapproved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> unapproved in pm.</b>',
        "unblocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> unblocked.</b>',
        "user_not_specified": "🚫 <b>You haven't specified user.</b>",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {
        "_cfg_active_threshold": (
            "Какое количество Ваших сообщений необходимо, чтобы доверять пользователю."
        ),
        "_cfg_afk_show_duration": (
            "Если включено, сообщение AFK будет содержать время его окончания"
        ),
        "_cfg_custom_msg": (
            "Кастомное оповещение неодобренных пользователей. Оставьте пустым,"
            " чтобы оставить по умолчанию."
        ),
        "_cfg_delete_dialog": (
            "Если установлено true, диалог будет удалён после блокировки."
        ),
        "_cfg_gone": (
            "Если установлено true, AFK сообщение будет включать время, когда вы ушли."
        ),
        "_cfg_ignore_active": (
            "Если установлено true, игнорирует диалоги, где вы участвовали."
        ),
        "_cfg_ignore_contacts": "Если установлено true, игнорирует контакты.",
        "_cfg_photo": "Фото, которое отправляется вместе с уведомлением о блокировке",
        "_cfg_pmbl": "Если установлено true, PMBL активирован.",
        "_cfg_report_spam": (
            "Если установлено true, после блокировки на пользователя будет"
            " отправлена жалоба о спаме."
        ),
        "_cfg_use_bio": "Показывать сообщение об отсутствии в профиле.",
        "_cls_doc": (
            "⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬ ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n"
            "-> Запрещает людям отправлять вам нежелательные личные сообщения."
            "-> Избавляет от беспокойства, когда вы недоступны."
            "Смотрите `.config apodiktum dnd`."
        ),
        "_cmd_doc_allowpm": (
            "<ответ или username> - Разрешает пользователю писать вам в ЛС."
        ),
        "_cmd_doc_block": "<ответ> - Блокирует этого пользователя без предупреждения.",
        "_cmd_doc_cdnd": "Это откроет конфиг для модуля.",
        "_cmd_doc_delstatus": "<короткое_название> - Удаляет статус.",
        "_cmd_doc_denypm": (
            "<ответ или username> - Запрещает пользователю писать вам в ЛС."
        ),
        "_cmd_doc_newstatus": (
            "<короткое_название> <notif|0/1> <text>\n"
            " - Новый статус\n"
            " - Пример: .newstatus test 1 Привет!"
        ),
        "_cmd_doc_pmbanlast": (
            "<число> - Блокирует и удаляет диалоги с большим кол-вом новых"
            " пользователей."
        ),
        "_cmd_doc_report": (
            "<ответ> - Отправляет жалобу на пользователя на СПАМ. Использовать"
            " только в ЛС."
        ),
        "_cmd_doc_status": (
            "<короткое название> [необязательно длительность|1s/m/h/d] [необязательно"
            " дополнительная информация] - Установить статус"
        ),
        "_cmd_doc_statuses": " - Показывает доступные статусы.",
        "_cmd_doc_unblock": "<ответ> - Разблокировать этого пользователя.",
        "_cmd_doc_unstatus": " - Удаляет статус.",
        "_log_msg_approved": "Пользователь {} допущен в ЛС, фильтр: {}",
        "_log_msg_punished": "Нарушитель наказан: {}",
        "_log_msg_unapproved": "Пользователь {} не допущен к ЛС.",
        "afk_message": "{}\n",
        "afk_message_duration": "\n<b><u>Буду AFK:</u></b>\n<code>{}</code>",
        "afk_message_further": "\n<b><u>Подробнее:</u></b>\n<code>{}</code>",
        "afk_message_gone": "\n<b><u>Отсутствую:</u></b>\n<code>{}</code>",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> допущен к ЛС.</b>',
        "args_incorrect": "<b>🚫 Аргументы некорректны.</b>",
        "args_pmban": "ℹ️ <b>Пример использования: </b><code>.pmbanlast 5</code>",
        "available_statuses": "<b>🦊 Доступные статусы:</b>\n\n",
        "banned": (
            "😊 <b>Привет •ᴗ•</b>\n<b>«SIGMA»<b>, <b>защитник</b> этого"
            " аккаунта. Вы <b>не допущены к ЛС</b>! Вы можете связаться с моим"
            " владельцем<b>в чате</b>, если Вам нужна помощь.\n<b>По правилам"
            " безопасности, я должен заблокировать Вас.</b>"
        ),
        "banned_log": (
            "👮 <b>Я заблокировал {}.</b>\n\n<b>{} Контакт</b>\n<b>{} Начатый"
            " тобой</b>\n<b>{} Активный диалог</b>\n\n<b>✊"
            " Действия</b>\n\n<b>{} Сообщить о спаме</b>\n<b>{} Удалить"
            " диалог</b>\n<b>{} Заблокировать</b>\n\n<b>ℹ️"
            " Сообщение</b>\n<code>{}</code>"
        ),
        "blocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> заблокирован.</b>',
        "hello": (
            "🔏 <b>«SIGMA»</b> защищает ваши личные сообщения от нежелательного"
            " контакта. Это будет блокировать всех, кто попытается связаться с"
            " Вами..\n\nИспользуй <code>.pmbanlast</code> если уже были попытки"
            " нежелательного вторжения."
        ),
        "no_pchat": "<b>Эта команда работает только в ЛС.</b>",
        "no_reply": (
            "ℹ️ <b>Ответьте на сообщение, чтобы заблокировать пользователя.</b>"
        ),
        "no_status": "<b>🚫 Нет активного статуса.</b>",
        "pm_reported": "⚠️ <b>Отправил жалобу на спам!</b>",
        "removed": "😶‍🌫️ <b>Удалил {} последних диалогов!</b>",
        "removing": "😶‍🌫️ <b>Удаляю {} последних диалогов...</b>",
        "status_created": "<b>✅ Статус {} установлен.</b>\n<code>{}</code>\nNotify: {}",
        "status_not_found": "<b>🚫 Статус не найден.</b>",
        "status_removed": "<b>✅ Статус {} удалён.</b>",
        "status_set": (
            "<b>✅ Статус установлен\n</b><code>{}</code>\nУведомления: <code>{}</code>"
        ),
        "status_set_duration": "\nПродолжительность: <code>{}</code>",
        "status_set_further": "\nПодробнее: <code>{}</code>",
        "status_unset": "<b>✅ Статус удалён.</b>",
        "unapproved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> не допущен к ЛС.</b>',
        "unblocked": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> разблокирован.</b>',
        "user_not_specified": "🚫 <b>Вы не указали пользователя.</b>",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo DND",
                "new": "Apo-DND",
            },
        },
    }

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
                "afk_group_list",
                doc=lambda: self.strings("_cfg_doc_afk_group_list"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),
            loader.ConfigValue(
                "afk_show_duration",
                True,
                doc=lambda: self.strings("_cfg_afk_show_duration"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "afk_tag_whitelist",
                True,
                doc=lambda: self.strings("_cfg_doc_whitelist"),
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
                "use_bio",
                True,
                doc=lambda: self.strings("_cfg_use_bio"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
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
        self._ratelimit_afk = []
        self._ratelimit_pmbl = []
        self._ratelimit_pmbl_threshold = 10
        self._ratelimit_pmbl_timeout = 5 * 60
        self._sent_messages = []
        self._whitelist = self.get("whitelist", [])
        if not self.get("ignore_hello", False):
            await self.inline.bot.send_photo(
                self.tg_id,
                photo=(
                    r"https://github.com/hikariatama/assets/raw/master/unit_sigma.png"
                ),
                caption=self.strings("hello"),
                parse_mode="HTML",
            )
            self.set("ignore_hello", True)

    def _approve(self, user: int, reason: str = "unknown"):
        self._whitelist += [user]
        self._whitelist = list(set(self._whitelist))
        self.set("whitelist", self._whitelist)
        if reason != "blocked":
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("_log_msg_approved").format(user, reason),
            )

    def _unapprove(self, user: int):
        self._whitelist = list(set(self._whitelist))
        self._whitelist = list(filter(lambda x: x != user, self._whitelist))
        self.set("whitelist", self._whitelist)
        self.apo_lib.utils.log(
            logging.INFO, __name__, self.strings("_log_msg_unapproved").format(user)
        )

    async def _send_pmbl_message(
        self, message, peer, contact, started_by_you, active_peer, self_id
    ):
        if len(self._ratelimit_pmbl) < self._ratelimit_pmbl_threshold:
            try:
                await self._client.send_file(
                    peer,
                    self.config["photo"],
                    caption=self.config["custom_message"]
                    or self.apo_lib.utils.get_str("banned", self.all_strings, message),
                )
            except Exception:
                await utils.answer(
                    message,
                    self.config["custom_message"]
                    or self.apo_lib.utils.get_str("banned", self.all_strings, message),
                )

            self._ratelimit_pmbl += [round(time.time())]

            try:
                peer = await self._client.get_entity(peer)
            except ValueError:
                await asyncio.sleep(1)
                peer = await self._client.get_entity(peer)

            await self.inline.bot.send_message(
                self_id,
                self.apo_lib.utils.get_str(
                    "banned_log", self.all_strings, message
                ).format(
                    await self.apo_lib.utils.get_tag(peer, True),
                    format_(contact),
                    format_(started_by_you),
                    format_(active_peer),
                    format_(self.config["report_spam"]),
                    format_(self.config["delete_dialog"]),
                    format_(True),
                    self.apo_lib.utils.raw_text(message)[:3000],
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

    async def _active_peer(self, cid, peer):
        if self.config["ignore_active"]:
            q = 0

            async for msg in self._client.iter_messages(peer, limit=200):
                if msg.sender_id == self.tg_id:
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

    async def _unstatus_func(self, delay=None):
        if delay:
            await asyncio.sleep(delay)
        self.set("status", False)
        self.set("status_duration", "")
        self.set("gone", "")
        self.set("further", "")
        self._ratelimit_afk = []

        if self.get("old_bio"):
            await self._client(UpdateProfileRequest(about=self.get("old_bio")))
            self.set("old_bio", None)

        for m in self._sent_messages:
            try:
                await m.delete()
            except Exception as exc:  # skipcq: PYL-W0703
                self.apo_lib.utils.log(
                    logging.DEBUG,
                    __name__,
                    f"Message not deleted due to {exc}",
                    exc_info=True,
                )

        self._sent_messages = []

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
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("args_pmban", self.all_strings, message),
            )
            return

        n = int(n)

        await utils.answer(
            message,
            self.apo_lib.utils.get_str("removing", self.all_strings, message).format(n),
        )

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

        await utils.answer(
            message,
            self.apo_lib.utils.get_str("removed", self.all_strings, message).format(n),
        )

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
                user = await reply.get_sender() if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "user_not_specified", self.all_strings, message
                    ),
                )
                return

            user = chat

        self._approve(user.id, "manual_approve")
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("approved", self.all_strings, message).format(
                user.id, get_display_name(user)
            ),
        )

    async def denypmcmd(self, message: Message):
        """
        <reply or user> - Deny user to pm you.
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None

        try:
            user = await self._client.get_entity(int(args))
            if not isinstance(user, User):
                user = None
        except Exception:
            with contextlib.suppress(Exception):
                user = await reply.get_sender() if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "user_not_specified", self.all_strings, message
                    ),
                )
                return

            user = chat

        self._unapprove(user.id)
        await utils.answer(
            message,
            self.strings("unapproved").format(user.id, get_display_name(user)),
        )

    async def reportpmcmd(self, message: Message):
        """
        <reply> - Report the user to spam. Use only in PM.
        """
        if not message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_pchat", self.all_strings, message),
            )
            return
        user = await message.get_chat()
        await message.client(ReportSpamRequest(peer=user.id))
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("pm_reported", self.all_strings, message),
        )

    async def blockcmd(self, message: Message):
        """
        <reply> - Block this user without being warned.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
            return
        await message.client(BlockRequest(user.id))
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("blocked", self.all_strings, message).format(
                user.id, get_display_name(user)
            ),
        )

    async def unblockcmd(self, message: Message):
        """
        <reply> - Unblock this user.
        """
        user = await utils.get_target(message)
        user = await self._client.get_entity(user)
        if not user:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
            return
        await message.client(UnblockRequest(user.id))
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("unblocked", self.all_strings, message).format(
                user.id, get_display_name(user)
            ),
        )

    async def statuscmd(self, message: Message):
        """
        <short_name> [optional duration|1s/m/h/d] [optional further information] - Set status.
        """
        status_duration = ""
        status = ""
        t = ""
        args = utils.get_args_raw(self.apo_lib.utils.raw_text(message, True))
        args = args.split(" ", 2)
        t = sum(
            self.apo_lib.utils.convert_time(time_str) or 0
            for time_str in re.findall(
                r"(\d+[a-zA-Z])", args[1] if len(args) > 1 else ""
            )
        )
        if args[0] not in self.get("texts", {}):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "status_not_found", self.all_strings, message
                ),
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        if self.get("status"):
            await self._unstatus_func()
        if self.config["use_bio"] and not self.get("old_bio"):
            full = await self._client(GetFullUserRequest("me"))
            self.set("old_bio", getattr(full.full_user, "about", None))
        self.set("status", args[0])
        self.set("gone", time.time())
        if t and len(args) > 2:
            args = list(
                map(
                    lambda x: x.replace(
                        "<emoji document_id=", "</code><emoji document_id="
                    ).replace("</emoji>", "</emoji><code>")
                    if isinstance(x, str)
                    else x,
                    args,
                )
            )
            self.set("further", args[2])
        elif not t and len(args) > 1:
            args[1:] = [" ".join(args[1:])]
            args = list(
                map(
                    lambda x: x.replace(
                        "<emoji document_id=", "</code><emoji document_id="
                    ).replace("</emoji>", "</emoji><code>")
                    if isinstance(x, str)
                    else x,
                    args,
                )
            )
            self.set("further", args[1])

        self._ratelimit_afk = []

        if t:
            with contextlib.suppress(Exception):
                self._unstatus_task.cancel()
            self._unstatus_task = asyncio.ensure_future(self._unstatus_func(t))
            self.set("status_duration", time.time() + t)
            status_duration = (
                datetime.datetime.fromtimestamp(self.get("status_duration")).replace(
                    microsecond=0
                )
                - datetime.datetime.now().replace(microsecond=0)
            ).total_seconds()
        status += self.apo_lib.utils.get_str(
            "status_set", self.all_strings, message
        ).format(
            self.get("texts", {})[args[0]]
            .replace("<emoji document_id=", "</code><emoji document_id=")
            .replace("</emoji>", "</emoji><code>"),
            str(self.get("notif")[args[0]]),
        )
        if self.get("further"):
            status += self.apo_lib.utils.get_str(
                "status_set_further", self.all_strings, message
            ).format(self.get("further"))
        if status_duration:
            status += self.apo_lib.utils.get_str(
                "status_set_duration", self.all_strings, message
            ).format(self.apo_lib.utils.time_formatter(t, short=True))
        if self.config["use_bio"]:
            bio = self.get("texts", {})[args[0]]
            if self.get("further"):
                bio += f" | {self.apo_lib.utils.get_str('afk_message_further', self.all_strings, message).format(self.get('further'))}"
            bio = self.apo_lib.utils.remove_html(bio)
            bio_len = 140 if (await self._client.get_me()).premium else 70
            await self.client(UpdateProfileRequest(about=bio[:bio_len]))
        msg = await utils.answer(message, status)
        self._sent_messages += [msg]

    async def unstatuscmd(self, message: Message):
        """
        Remove status.
        """
        with contextlib.suppress(Exception):
            self._unstatus_task.cancel()
        if not self.get("status", False):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_status", self.all_strings, message),
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        await self._unstatus_func()

        msg = await utils.answer(
            message,
            self.apo_lib.utils.get_str("status_unset", self.all_strings, message),
        )
        await asyncio.sleep(10)
        await msg.delete()

    async def newstatuscmd(self, message: Message):
        """
        <short_name> <notif|0/1> <text> - New status.
        Example: .newstatus test 1 Hello!
        """
        args = utils.get_args_raw(self.apo_lib.utils.raw_text(message, True))
        args = args.split(" ", 2)
        if len(args) < 3 or args[1] not in ["1", "true", "yes", "+"]:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("args_incorrect", self.all_strings, message),
            )
            await asyncio.sleep(3)
            await message.delete()
            return

        args[1] = args[1] in ["1", "true", "yes", "+"]
        texts = self.get("texts", {})
        texts[args[0]] = args[2]
        self.set("texts", texts)

        notif = self.get("notif", {})
        notif[args[0]] = args[1]
        args = list(
            map(
                lambda x: x.replace(
                    "<emoji document_id=", "</code><emoji document_id="
                ).replace("</emoji>", "</emoji><code>")
                if isinstance(x, str)
                else x,
                args,
            )
        )
        self.set("notif", notif)
        await utils.answer(
            message,
            self.apo_lib.utils.get_str(
                "status_created", self.all_strings, message
            ).format(
                args[0],
                args[2],
                args[1],
            ),
        )

    async def delstatuscmd(self, message: Message):
        """
        <short_name> - Delete status.
        """
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "status_not_found", self.all_strings, message
                ),
            )
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
            self.apo_lib.utils.get_str(
                "status_removed", self.all_strings, message
            ).format(args),
        )

    async def statusescmd(self, message: Message):
        """
        Show available statuses.
        """
        res = self.apo_lib.utils.get_str(
            "available_statuses", self.all_strings, message
        )
        for short_name, status in self.get("texts", {}).items():
            res += (
                f"<b><u>{short_name}</u></b> | Notify:"
                f" <b>{self.get('notif', {})[short_name]}</b>\n{status}\n➖➖➖➖➖➖➖➖➖\n"
            )

        await utils.answer(message, res)

    @loader.watcher("only_messages", "in")
    async def watcher(self, message: Message):
        is_pmbl = False
        chat_id = utils.get_chat_id(message)
        if chat_id in {
            1271266957,  # @replies
            777000,  # Telegram Notifications
            self.tg_id,  # Self
        }:
            return
        try:
            if (
                self.config["PMBL_Active"]
                and message.is_private
                and not isinstance(message, Channel)
                and isinstance(message.peer_id, PeerUser)
            ):
                peer = (
                    getattr(getattr(message, "sender", None), "username", None)
                    or message.peer_id
                )
                is_pmbl = await self.p__pmbl(peer, message)

            if not is_pmbl and (
                message.is_private
                or (
                    self.config["afk_tag_whitelist"]
                    and chat_id in self.config["afk_group_list"]
                )
                or (
                    not self.config["afk_tag_whitelist"]
                    and chat_id not in self.config["afk_group_list"]
                )
            ):
                user_id = await self.apo_lib.utils.get_user_id(message)
                await self.p__afk(chat_id, user_id, message)
            return
        except ValueError as exc:  # skipcq: PYL-W0703
            self.apo_lib.utils.log(logging.DEBUG, __name__, exc)

    async def p__pmbl(
        self,
        peer,
        message: Union[None, Message] = None,
    ) -> bool:
        cid = utils.get_chat_id(message)
        if cid in self._whitelist:
            return

        contact, started_by_you, active_peer = None, None, None

        with contextlib.suppress(ValueError):
            entity = await message.get_sender()
            if entity.bot:
                return self._approve(cid, "bot")

            if self.config["ignore_contacts"]:
                if entity.contact:
                    return self._approve(cid, "ignore_contacts")
                contact = False

        first_message = (
            await self._client.get_messages(
                peer,
                limit=1,
                reverse=True,
            )
        )[0]

        if (
            getattr(message, "raw_text", False)
            and first_message.sender_id == self.tg_id
        ):
            return self._approve(cid, "started_by_you")
        started_by_you = False

        active_peer = await self._active_peer(cid, peer)
        if active_peer:
            return

        self._ratelimit_pmbl = list(
            filter(
                lambda x: x + self._ratelimit_pmbl_timeout < time.time(),
                self._ratelimit_pmbl,
            )
        )

        await self._send_pmbl_message(
            message, peer, contact, started_by_you, active_peer, self.tg_id
        )
        await self._punish_handler(cid)

        self._approve(cid, "blocked")
        self.apo_lib.utils.log(
            logging.WARNING, __name__, self.strings("_log_msg_punished").format(cid)
        )
        return True

    async def p__afk(
        self,
        chat_id: int,
        user_id: int,
        message: Union[None, Message] = None,
    ) -> bool:
        if (
            not isinstance(message, Message)
            or not self.get("status", False)
            or chat_id in self._ratelimit_afk
        ):
            return
        if getattr(message.to_id, "user_id", None) == self.tg_id:
            user = await message.get_sender()
            if (
                user_id in self._ratelimit_afk
                or user.is_self
                or user.bot
                or user.verified
            ):
                return
        elif not message.mentioned:
            return

        now = datetime.datetime.now().replace(microsecond=0)
        gone = datetime.datetime.fromtimestamp(self.get("gone")).replace(microsecond=0)
        if self.get("status_duration"):
            status_duration = datetime.datetime.fromtimestamp(
                self.get("status_duration")
            ).replace(microsecond=0)
            status_len_sec = (status_duration - gone).total_seconds()
            if now > status_duration:
                await self._unstatus_func()
                return
        diff = now - gone
        diff_sec = diff.total_seconds()
        further = self.get("further") or ""
        afk_string = self.apo_lib.utils.get_str(
            "afk_message", self.all_strings, message
        ).format(self.get("texts", {"": ""})[self.get("status", "")])
        if further:
            afk_string += self.apo_lib.utils.get_str(
                "afk_message_further", self.all_strings, message
            ).format(further)
        if self.config["afk_gone_time"]:
            afk_string += f"{self.apo_lib.utils.get_str('afk_message_gone', self.all_strings, message).format(self.apo_lib.utils.time_formatter(diff_sec, short=True))}"
        if not self.config["afk_gone_time"] and self.config["afk_show_duration"]:
            afk_string += "\n"
        if self.config["afk_show_duration"] and self.get("status_duration"):
            afk_string += f"{self.apo_lib.utils.get_str('afk_message_duration', self.all_strings, message).format(self.apo_lib.utils.time_formatter(status_len_sec, short=True))}"

        m = await message.reply(afk_string)

        self._sent_messages += [m]

        if not self.get("notif", {"": False})[self.get("status", "")]:
            await self._client.send_read_acknowledge(
                message.peer_id,
                clear_mentions=True,
            )

        self._ratelimit_afk += [chat_id]
