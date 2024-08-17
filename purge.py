__version__ = (0, 1, 34)


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

import asyncio
import contextlib
import logging

from telethon.tl.types import Message
from telethon.hints import EntityLike

from .. import loader, utils

logger = logging.getLogger(__name__)


def represents_int(s: str) -> bool:
    try:
        loader.validators.Integer().validate(s)
        return True
    except loader.validators.ValidationError:
        return False


@loader.tds
class ApodiktumPurgeMod(loader.Module):
    """
    Userbot module for purging unneeded messages(usually spam or ot).
    Check the `.config apodiktum purge` to enable/disable logging.
    """

    strings = {
        "name": "Apo-Purge",
        "developer": "@anon97945",
        "_cfg_log_edit": "Log `edit` as info.",
        "_cfg_log_purge": "Log purge `count` as info.",
        "_cfg_log_purgeme": "Log `purgeme `count as info.",
        "_cfg_log_sd": "Log `sd` as info.",
        "edit_success": (
            "Edit done successfully.\nOld message:\n{}\n\n\nNew message:\n{}"
        ),
        "err_cmd_wrong": "<b>Your command was wrong.</b>",
        "err_purge_start": "<b>Please reply to a message to start purging.</b>",
        "no_int": "<b>Your input was no integer.</b>",
        "permerror": "<b>You don't have permission to use this command.</b>",
        "purge_cmpl": "<b>Purge complete!</b>\nPurged <code>{}</code> messages.",
        "purge_success": "Purge of {} messages done successfully.",
        "sd_success": "Message after {} seconds successfully deleted.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_log_edit": "Protokollieren Sie `edit` Nachrichten als Info.",
        "_cfg_log_purge": (
            "Protokollieren Sie die Anzahl der `purge` Nachrichten als Info."
        ),
        "_cfg_log_purgeme": (
            "Protokollieren Sie die Anzahl der `purgeme` Nachrichten als Info."
        ),
        "_cfg_log_sd": "Protokollieren `self-destructive` Nachrichten als Info.",
        "_cls_doc:": (
            "Module zum entfernen von Nachrichten(normalerweise spam,"
            " etc.).\nCheck `.config apodiktum purge` um das Protokollieren zu"
            " aktivieren/deaktivieren."
        ),
        "_cmd_doc_cpurge": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "_cmd_doc_del": (
            "Löscht die beantwortete Nachricht.\n- Verwendung: .adel <Antwort>"
        ),
        "_cmd_doc_edit": (
            "Bearbeitet die letzte Nachricht.\n- Verwendung: .edit <Nachricht>"
        ),
        "_cmd_doc_purge": (
            "Löscht alle Nachrichten bis zu und inklusive der Antwort.\n"
            "- Verwendung: .apurge <Antwort>"
        ),
        "_cmd_doc_purgeme": (
            "Löscht x (oder alle) Nachrichten von dir.\n"
            "- Verwendung: .purgeme <anzahl/all>"
        ),
        "_cmd_doc_purgeuser": (
            "Löscht alle Nachrichten von einem Nutzer.\n"
            "- Verwendung: .purgeuser <Antwort>"
        ),
        "_cmd_doc_sd": (
            "Löscht die letzte Nachricht nach x Sekunden. Funktioniert auch mit"
            " Medien.\nVerwendung: .sd <Sekunden> <Nachricht>"
        ),
        "_cmd_doc_spurge": (
            "Löscht alle Nachrichten bis zu und inklusive der Antwort ohne"
            " Benachrichtigung.\n- Verwendung: .spurge <Antwort>"
        ),
        "_cmd_doc_spurgeme": (
            "Löscht x (oder alle) Nachrichten von dir ohne Benachrichtigung.\n"
            "- Verwendung: .spurgeme <anzahl/all>"
        ),
        "_cmd_doc_spurgeuser": (
            "Löscht alle Nachrichten von einem Nutzer ohne Benachrichtigung.\n"
            "- Verwendung: .spurgeuser <Antwort>"
        ),
        "edit_success": (
            "Bearbeitung erfolgreich.\nAlte Nachricht:\n{}\n\n\nNeue Nachricht:\n{}"
        ),
        "err_cmd_wrong": "<b>Deine Eingabe war falsch.</b>",
        "err_purge_start": (
            "<b>Bitte antworte auf eine Nachricht, um die Löschung zu starten.</b>"
        ),
        "no_int": "<b>Dein Eingabe war kein Integer.</b>",
        "permerror": "<b>Du hast keine Berechtigung, diesen Befehl zu verwenden.</b>",
        "purge_cmpl": (
            "<b>Purge fertig!</b>\n<code>{}</code> Nachrichten wurden gelöscht."
        ),
        "purge_success": "Löschung von {} Nachrichten erfolgreich durchgeführt.",
        "sd_success": "Nachricht nach {} Sekunden erfolgreich gelöscht.",
    }

    strings_ru = {
        "_cfg_log_edit": "Логировать редактирование сообщения как info.",
        "_cfg_log_purge": "Логировать количество очищенных сообщений как info.",
        "_cfg_log_purgeme": (
            "Логировать количество удаленных сообщений от вас как info."
        ),
        "_cfg_log_sd": "Логировать создание сообщения как info.",
        "_cls_doc": (
            "Модуль для очистки спама и т.д.Проверьте `.config apodiktum"
            " purge`, чтобы включить/выключить ведение журнала."
        ),
        "_cmd_doc_cpurge": "Это откроет конфиг для модуля.",
        "_cmd_doc_edit": (
            "Редактирует последнее сообщение.\n- Использование: .aedit <сообщение>"
        ),
        "_cmd_doc_purge": (
            "Удаляет все сообщения до и включая ответ.\n"
            "- Использование: .apurge <реплай>"
        ),
        "_cmd_doc_purgeme": (
            "Удаляет x (или все) сообщений от вас.\n"
            "- Использование: .purgeme <количество/все>"
        ),
        "_cmd_doc_purgeuser": (
            "Удаляет все сообщения от определенного пользователя.\n"
            "- Использование: .purgeuser <реплай>"
        ),
        "_cmd_doc_sd": (
            "Удаляет последнее сообщение через x секунд.\n"
            "- Использование: .sd <секунды> <сообщение>"
        ),
        "_cmd_doc_spurge": (
            "Удаляет все сообщения до и включая ответ без оповещения.\n"
            "- Использование: .spurge <реплай>"
        ),
        "_cmd_doc_spurgeme": (
            "Удаляет x (или все) сообщений от вас без оповещения.\n"
            "- Использование: .spurgeme <количество/все>"
        ),
        "_cmd_doc_spurgeuser": (
            "Удаляет все сообщения от определенного пользователя без"
            " оповещения.\n- Использование: .spurgeuser <реплай>"
        ),
        "edit_success": (
            "Редактирование завершено успешно.\n"
            "Старое сообщение:\n{}\n\n\nНовое сообщение:\n{}"
        ),
        "err_cmd_wrong": "<b>Ваш команда была неверной.</b>",
        "err_purge_start": (
            "<b>Пожалуйста, ответьте на сообщение для начала очистки.</b>"
        ),
        "no_int": "<b>Введенное значение не является целым числом (int)</b>",
        "permerror": "<b>У вас недостаточно прав для использования этой команды.</b>",
        "purge_cmpl": "<b>Очистка завершена!</b>\nОчищено <code>{}</code> сообщений.",
        "purge_success": "Очистка {} сообщений завершена успешно.",
        "sd_success": "Сообщение после {} секунд успешно удалено.",
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
                "old": "Apo Purge",
                "new": "Apo-Purge",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_edit",
                False,
                doc=lambda: self.strings("_cfg_log_edit"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_purge",
                False,
                doc=lambda: self.strings("_cfg_log_purge"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_purgeme",
                False,
                doc=lambda: self.strings("_cfg_log_purgeme"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_sd",
                False,
                doc=lambda: self.strings("_cfg_log_sd"),
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

    async def _purge_user_messages(
        self,
        chat: EntityLike,
        user_id: int,
        purge_count: int,
    ) -> int:
        msgs = []
        msg_count = 0
        itermsg = self._client.iter_messages(entity=chat)
        if purge_count == "all":
            async for msg in itermsg:
                if msg.sender_id == user_id:
                    msgs += [msg.id]
                    msg_count += 1
                    if len(msgs) >= 99:
                        await self._client.delete_messages(chat, msgs)
                        msgs.clear()
        else:
            i = 0
            async for msg in itermsg:
                if msg.sender_id == user_id:
                    if i == purge_count:
                        break
                    i += 1
                    msgs += [msg.id]
                    msg_count += 1
                    if len(msgs) >= 99:
                        await self._client.delete_messages(chat, msgs)
                        msgs.clear()

        if msgs:
            await self._client.delete_messages(chat, msgs)

        return msg_count

    async def _purge_messages(
        self,
        chat: EntityLike,
        self_id: int,
        can_delete: bool,
        message: Message,
    ) -> int:
        msg_count = 0
        itermsg = self._client.iter_messages(
            entity=chat,
            min_id=message.reply_to_msg_id,
            reverse=True,
        )
        msgs = [message.reply_to_msg_id]
        async for msg in itermsg:
            if can_delete:
                msgs.append(msg)
                msg_count += 1
            elif msg.sender_id == self_id:
                msgs.append(msg)
                if msg.id != message.id:
                    msg_count += 1
            if len(msgs) >= 99:
                await self._client.delete_messages(chat, msgs)
                msgs.clear()
        if msgs:
            await self._client.delete_messages(chat, msgs)
        return msg_count

    async def cpurgecmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def apurgecmd(self, message: Message):
        """
        Delete all messages up to and including the reply.
        - Usage: .apurge <reply>
        """
        chat = message.chat
        if message.reply_to_msg_id is not None:
            can_delete = bool(
                message.is_private
                or (
                    (chat.admin_rights or chat.creator)
                    and chat.admin_rights.delete_messages
                    or chat.admin_rights
                    and chat.creator
                )
            )

            msg_count = await self._purge_messages(
                chat, self.tg_id, can_delete, message
            )
        else:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "err_purge_start", self.all_strings, message
                ),
            )
            return

        done = await self._client.send_message(
            chat.id,
            self.apo_lib.utils.get_str("purge_cmpl", self.all_strings, message).format(
                msg_count
            ),
        )
        await asyncio.sleep(2)
        await done.delete()

        if self.config["log_purge"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def spurgecmd(self, message: Message):
        """
        Delete all messages up to and including the reply silently.
        - Usage: .spurge <reply>
        """
        chat = message.chat
        if message.reply_to_msg_id is not None:
            can_delete = bool(
                message.is_private
                or (
                    (chat.admin_rights or chat.creator)
                    and chat.admin_rights.delete_messages
                    or chat.admin_rights
                    and chat.creator
                )
            )

            msg_count = await self._purge_messages(
                chat,
                self.tg_id,
                can_delete,
                message,
            )
        else:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "err_purge_start",
                    self.all_strings,
                    message,
                ),
            )
            return

        if self.config["log_purge"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def purgemecmd(self, message: Message):
        """
        Delete x count (or all) of your latest messages.
        - Usage: .purgeme <count/all>
        """
        chat = message.chat
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not represents_int(args[0]) and "all" not in args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_int", self.all_strings, message),
            )
            return
        if len(args) > 1:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("err_cmd_wrong", self.all_strings, message),
            )
            return
        purge_count = "all" if len(args) == 1 and "all" in args else int(args[0])
        user_id = self.tg_id
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count)
        done = await self._client.send_message(
            chat.id,
            self.apo_lib.utils.get_str("purge_cmpl", self.all_strings, message).format(
                str(msg_count)
            ),
        )
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def spurgemecmd(self, message: Message):
        """
        Delete x count (or all) of your latest messages silently.
        - Usage: .spurgeme <count/all>
        """
        chat = message.chat
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not represents_int(args[0]) and "all" not in args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_int", self.all_strings, message),
            )
            return
        if len(args) > 1:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("err_cmd_wrong", self.all_strings, message),
            )
            return
        purge_count = "all" if len(args) == 1 and "all" in args else int(args[0])
        user_id = self.tg_id
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count)
        if self.config["log_purgeme"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def purgeusercmd(self, message: Message):
        """
        Delete all messages from the replied user.
        - Usage: .purgeuser <reply>
        """
        chat = message.chat
        if not message.is_reply:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
        reply = await message.get_reply_message()
        user_id = reply.sender_id
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )
        purge_count = "all"
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count)
        done = await self._client.send_message(
            chat.id,
            self.apo_lib.utils.get_str("purge_cmpl", self.all_strings, message).format(
                str(msg_count)
            ),
        )
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def spurgeusercmd(self, message: Message):
        """
        Delete all messages from the replied user silently.
          - Usage: .spurgeuser <reply>
        """
        chat = message.chat
        if not message.is_reply:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
        reply = await message.get_reply_message()
        user_id = reply.sender_id
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )
        purge_count = "all"
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count)
        if self.config["log_purgeme"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("purge_success").format(str(msg_count)),
            )

    async def adelcmd(self, message: Message):
        """
        Delete the replied message.
          - Usage: .adel <reply>
        """
        reply = await message.get_reply_message()
        if reply:
            with contextlib.suppress(Exception):
                await reply.delete()
                await message.delete()

    async def editcmd(self, message: Message):
        """
        Edit your last message.
          - Usage: .edit <text>
        """
        chat = message.chat
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("err_cmd_wrong", self.all_strings, message),
            )
            return
        i = 1
        async for msg in self._client.iter_messages(chat):
            if msg.out:
                if i == 2:
                    old_msg = self.apo_lib.utils.raw_text(msg)
                    new_msg = args
                    await msg.edit(new_msg)
                    await message.delete()
                    break
                i += 1
        if self.config["log_edit"]:
            self.apo_lib.utils.log(
                logging.INFO,
                __name__,
                self.strings("edit_success").format(old_msg, new_msg),
            )

    async def sdcmd(self, message: Message):
        """
        Make self-destructive messages. Also works for media when used in caption.
          - Usage: .sd <time> <text>
        """
        args = utils.get_args_raw(message).split()
        if len(args) < 2:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("err_cmd_wrong", self.all_strings, message),
            )
            return
        counter = int(" ".join(args[:1]))
        text = " ".join(args[1:])
        if (not counter or not text) and not represents_int(counter):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("err_cmd_wrong", self.all_strings, message),
            )
            return
        msg = await utils.answer(message, text)
        await asyncio.sleep(counter)
        await msg.delete()

        if self.config["log_sd"]:
            self.apo_lib.utils.log(
                logging.INFO, __name__, self.strings("sd_success").format(str(counter))
            )
