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

import asyncio
import logging
import contextlib

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from telethon.tl.types import Message

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
        "name": "Apo Purge",
        "developer": "@anon97945",
        "_cfg_log_edit": "Log `edit` as info.",
        "_cfg_log_purge": "Log purge `count` as info.",
        "_cfg_log_purgeme": "Log `purgeme `count as info.",
        "_cfg_log_sd": "Log `sd` as info.",
        "edit_success": ("Edit done successfully.\n"
                         "Old message:\n{}\n\n\nNew message:\n{}"),
        "err_cmd_wrong": "<b>Your command was wrong.</b>",
        "err_purge_start": "<b>Please reply to a message to start purging.</b>",
        "no_int": "<b>Your input was no integer.</b>",
        "permerror": "<b>You don't have permission to use this command.</b>",
        "purge_cmpl": "<b>Purge complete!</b>\nPurged <code>{}</code> messages.",
        "purge_success": "Purge of {} messages done successfully.",
        "sd_success": "Message after {} seconds successfully deleted.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_en = {
        "edit_success": ("Edit done successfully.\n"
                         "Old message:\n{}\n\n\nNew message:\n{}"),
        "err_cmd_wrong": "<b>Your command was wrong.</b>",
        "err_purge_start": "<b>Please reply to a message to start purging.</b>",
        "no_int": "<b>Your input was no integer.</b>",
        "permerror": "<b>You don't have permission to use this command.</b>",
        "purge_cmpl": "<b>Purge complete!</b>\nPurged <code>{}</code> messages.",
        "purge_success": "Purge of {} messages done successfully.",
        "sd_success": "Message after {} seconds successfully deleted.",
    }

    strings_de = {
        "_cfg_log_edit": "Protokollieren Sie `edit` Nachrichten als Info.",
        "_cfg_log_purge": "Protokollieren Sie die Anzahl der `purge` Nachrichten als Info.",
        "_cfg_log_purgeme": "Protokollieren Sie die Anzahl der `purgeme` Nachrichten als Info.",
        "_cfg_log_sd": "Protokollieren `self-destructive` Nachrichten als Info.",
        "_cls_doc:": ("Module zum entfernen von Nachrichten(normalerweise spam, etc.).\n"
                      "Check `.config apodiktum purge` um das Protokollieren zu aktivieren/deaktivieren."),
        "_cmd_doc_cpurge": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "_cmd_doc_del": ("Löscht die beantwortete Nachricht.\n"
                         "- Verwendung: .adel <Antwort>"),
        "_cmd_doc_edit": ("Bearbeitet die letzte Nachricht.\n"
                          "- Verwendung: .edit <Nachricht>"),
        "_cmd_doc_purge": ("Löscht alle Nachrichten bis zu und inklusive der Antwort.\n"
                           "- Verwendung: .apurge <Antwort>"),
        "_cmd_doc_purgeme": ("Löscht x (oder alle) Nachrichten von dir.\n"
                             "- Verwendung: .purgeme <anzahl/all>"),
        "_cmd_doc_purgeuser": ("Löscht alle Nachrichten von einem Nutzer.\n"
                               "- Verwendung: .purgeuser <Antwort>"),
        "_cmd_doc_sd": ("Löscht die letzte Nachricht nach x Sekunden. Funktioniert auch mit Medien.\n"
                        "Verwendung: .sd <Sekunden> <Nachricht>"),
        "_cmd_doc_spurge": ("Löscht alle Nachrichten bis zu und inklusive der Antwort ohne Benachrichtigung.\n"
                            "- Verwendung: .spurge <Antwort>"),
        "_cmd_doc_spurgeme": ("Löscht x (oder alle) Nachrichten von dir ohne Benachrichtigung.\n"
                              "- Verwendung: .spurgeme <anzahl/all>"),
        "_cmd_doc_spurgeuser": ("Löscht alle Nachrichten von einem Nutzer ohne Benachrichtigung.\n"
                                "- Verwendung: .spurgeuser <Antwort>"),
        "edit_success": ("Bearbeitung erfolgreich.\n"
                         "Alte Nachricht:\n{}\n\n\nNeue Nachricht:\n{}"),
        "err_cmd_wrong": "<b>Deine Eingabe war falsch.</b>",
        "err_purge_start": "<b>Bitte antworte auf eine Nachricht, um die Löschung zu starten.</b>",
        "no_int": "<b>Dein Eingabe war kein Integer.</b>",
        "permerror": "<b>Du hast keine Berechtigung, diesen Befehl zu verwenden.</b>",
        "purge_cmpl": "<b>Purge fertig!</b>\n<code>{}</code> Nachrichten wurden gelöscht.",
        "purge_success": "Löschung von {} Nachrichten erfolgreich durchgeführt.",
        "sd_success": "Nachricht nach {} Sekunden erfolgreich gelöscht.",
    }

    strings_ru = {
        "_cfg_log_edit": "Логировать редактирование сообщения как info.",
        "_cfg_log_purge": "Логировать количество очищенных сообщений как info.",
        "_cfg_log_purgeme": "Логировать количество удаленных сообщений от вас как info.",
        "_cfg_log_sd": "Логировать создание сообщения как info.",
        "_cls_doc": ("Модуль для очистки спама и т.д."
                     "Проверьте `.config apodiktum purge`, чтобы включить/выключить ведение журнала."),
        "_cmd_doc_cpurge": "Это откроет конфиг для модуля.",
        "_cmd_doc_edit": ("Редактирует последнее сообщение.\n"
                          "- Использование: .aedit <сообщение>"),
        "_cmd_doc_purge": ("Удаляет все сообщения до и включая ответ.\n"
                           "- Использование: .apurge <реплай>"),
        "_cmd_doc_purgeme": ("Удаляет x (или все) сообщений от вас.\n"
                             "- Использование: .purgeme <количество/все>"),
        "_cmd_doc_purgeuser": ("Удаляет все сообщения от определенного пользователя.\n"
                               "- Использование: .purgeuser <реплай>"),
        "_cmd_doc_sd": ("Удаляет последнее сообщение через x секунд.\n"
                        "- Использование: .sd <секунды> <сообщение>"),
        "_cmd_doc_spurge": ("Удаляет все сообщения до и включая ответ без оповещения.\n"
                            "- Использование: .spurge <реплай>"),
        "_cmd_doc_spurgeme": ("Удаляет x (или все) сообщений от вас без оповещения.\n"
                              "- Использование: .spurgeme <количество/все>"),
        "_cmd_doc_spurgeuser": ("Удаляет все сообщения от определенного пользователя без оповещения.\n"
                                "- Использование: .spurgeuser <реплай>"),
        "edit_success": ("Редактирование завершено успешно.\n"
                         "Старое сообщение:\n{}\n\n\nНовое сообщение:\n{}"),
        "err_cmd_wrong": "<b>Ваш команда была неверной.</b>",
        "err_purge_start": "<b>Пожалуйста, ответьте на сообщение для начала очистки.</b>",
        "no_int": "<b>Ваш ввод не является целочисленным типом (int)</b>",
        "permerror": "<b>У вас нет прав на использование этой команды.</b>",
        "purge_cmpl": "<b>Очистка завершена!</b>\nОчищено <code>{}</code> сообщений.",
        "purge_success": "Очистка< {} сообщений завершена успешно.",
        "sd_success": "Сообщение после {} секунд успешно удалено.",
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
        self._db = db
        self._client = client
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

    def _strings(self, string: str, chat_id: int = None):
        if self.lookup("Apo-Translations") and chat_id:
            forced_translation_db = self.lookup("Apo-Translations").config
            languages = {"en_chats": self.strings_en, "de_chats": self.strings_de, "ru_chats": self.strings_ru}
            for lang, strings in languages.items():
                if chat_id in forced_translation_db[lang]:
                    if string in strings:
                        return strings[string]
                    logger.debug(f"String: {string} not found in\n{strings}")
                    break
        return self.strings(string)

    @staticmethod
    async def _purge_user_messages(chat, user_id, purge_count, message):
        msgs = []
        msg_count = 0
        itermsg = message.client.iter_messages(entity=chat)
        if purge_count == "all":
            async for msg in itermsg:
                if msg.sender_id == user_id:
                    msgs += [msg.id]
                    msg_count += 1
                    if len(msgs) >= 99:
                        await message.client.delete_messages(chat, msgs)
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
                        await message.client.delete_messages(chat, msgs)
                        msgs.clear()
        if msgs:
            await message.client.delete_messages(chat, msgs)
        return msg_count

    @staticmethod
    async def _purge_messages(chat, self_id, can_delete, message):
        msg_count = 0
        itermsg = message.client.iter_messages(entity=chat, min_id=message.reply_to_msg_id, reverse=True)
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
                await message.client.delete_messages(chat, msgs)
                msgs.clear()
        if msgs:
            await message.client.delete_messages(chat, msgs)
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
                (
                    (chat.admin_rights or chat.creator)
                    and chat.admin_rights.delete_messages
                    or chat.admin_rights
                    and chat.creator
                )
            )

            msg_count = await self._purge_messages(chat, self._tg_id, can_delete, message)
        else:
            await utils.answer(message, self._strings("err_purge_start", utils.get_chat_id(message)))
            return

        done = await message.client.send_message(chat.id, self._strings("purge_cmpl", utils.get_chat_id(message)).format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purge"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def spurgecmd(self, message: Message):
        """
        Delete all messages up to and including the reply silently.
        - Usage: .spurge <reply>
        """
        chat = message.chat
        if message.reply_to_msg_id is not None:
            can_delete = bool(
                (
                    (chat.admin_rights or chat.creator)
                    and chat.admin_rights.delete_messages
                    or chat.admin_rights
                    and chat.creator
                )
            )

            msg_count = await self._purge_messages(chat, self._tg_id, can_delete, message)
        else:
            await utils.answer(message, self._strings("err_purge_start", utils.get_chat_id(message)))
            return

        if self.config["log_purge"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def purgemecmd(self, message: Message):
        """
        Delete x count (or all) of your latest messages.
        - Usage: .purgeme <count/all>
        """
        chat = message.chat
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not represents_int(args[0]) and "all" not in args:
            await utils.answer(message, self._strings("no_int", utils.get_chat_id(message)))
            return
        if len(args) > 1:
            await utils.answer(message, self._strings("err_cmd_wrong", utils.get_chat_id(message)))
            return
        purge_count = "all" if len(args) == 1 and "all" in args else int(args[0])
        user_id = self._tg_id
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count, message)
        done = await message.client.send_message(chat.id, self._strings("purge_cmpl", utils.get_chat_id(message)).format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def spurgemecmd(self, message: Message):
        """
        Delete x count (or all) of your latest messages silently.
        - Usage: .spurgeme <count/all>
        """
        chat = message.chat
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not represents_int(args[0]) and "all" not in args:
            await utils.answer(message, self._strings("no_int", utils.get_chat_id(message)))
            return
        if len(args) > 1:
            await utils.answer(message, self._strings("err_cmd_wrong", utils.get_chat_id(message)))
            return
        purge_count = "all" if len(args) == 1 and "all" in args else int(args[0])
        user_id = self._tg_id
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count, message)
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def purgeusercmd(self, message: Message):
        """
        Delete all messages from the replied user.
        - Usage: .purgeuser <reply>
        """
        chat = message.chat
        if not message.is_reply:
            return await utils.answer(message, self._strings("no_reply", utils.get_chat_id(message)))
        reply = await message.get_reply_message()
        user_id = reply.sender_id
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(message, self._strings("permerror", utils.get_chat_id(message)))
        purge_count = "all"
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count, message)
        done = await message.client.send_message(chat.id, self._strings("purge_cmpl", utils.get_chat_id(message)).format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def spurgeusercmd(self, message: Message):
        """
        Delete all messages from the replied user silently.
          - Usage: .spurgeuser <reply>
        """
        chat = message.chat
        if not message.is_reply:
            return await utils.answer(message, self._strings("no_reply", utils.get_chat_id(message)))
        reply = await message.get_reply_message()
        user_id = reply.sender_id
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(message, self._strings("permerror", utils.get_chat_id(message)))
        purge_count = "all"
        await message.delete()
        msg_count = await self._purge_user_messages(chat, user_id, purge_count, message)
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

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
            await utils.answer(message, self._strings("err_cmd_wrong", utils.get_chat_id(message)))
            return
        i = 1
        async for msg in message.client.iter_messages(chat):
            if msg.sender_id == self._tg_id:
                if i == 2:
                    old_msg = msg.raw_text
                    new_msg = args
                    await msg.edit(new_msg)
                    await message.delete()
                    break
                i = i + 1
        if self.config["log_edit"]:
            return logger.info(self.strings("edit_success").format(str(old_msg), str(new_msg)))
        return

    async def sdcmd(self, message: Message):
        """
        Make self-destructive messages. Also works for media when used in caption.
          - Usage: .sd <time> <text>
        """
        args = utils.get_args_raw(message)
        args = str(args).split()
        if len(args) < 2:
            await utils.answer(message, self._strings("err_cmd_wrong", utils.get_chat_id(message)))
            return
        counter = int(" ".join(args[:1]))
        text = " ".join(args[1:])
        if (not counter or not text) and not represents_int(counter):
            await utils.answer(message, self._strings("err_cmd_wrong", utils.get_chat_id(message)))
            return
        msg = await utils.answer(message, text)
        await asyncio.sleep(counter)
        await msg.delete()
        if self.config["log_sd"]:
            return logger.info(self.strings("sd_success").format(str(counter)))
        return


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
                if isinstance(v1, dict) and isinstance(v2, collections.abc.Mapping):
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
