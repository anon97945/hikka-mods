__version__ = (0, 0, 1)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
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

import asyncio
import logging

from telethon.tl.types import Message
from telethon.errors import rpcbaseerrors

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
    """
    strings = {
        "name": "Apodiktum Purge",
        "developer": "@anon97945",
        "no_int": "<b>Your input was no integer.</b>",
        "permerror": "<b>You don't have permission to use this command.</b>",
        "purge_cmpl": "<b>Purge complete!</b>\nPurged <code>{}</code> messages.",
        "purge_success": "Purge of {} messages done successfully.",
        "edit_success": ("Edit done successfully.\n"
                         "Old message:\n{}\n\n\nNew message:\n{}"),
        "sd_success": "Message after {} seconds successfully deleted.",
        "err_purge_start": "<b>Please reply to a message to start purging.</b>",
        "err_cmd_wrong": "<b>Your command was wrong.</b>",
        "_cfg_log_purge": "Log purge `count` as info.",
        "_cfg_log_purgeme": "Log `purgeme `count as info.",
        "_cfg_log_edit": "Log `edit` as info.",
        "_cfg_log_sd": "Log `sd` as info.",
    }

    strings_de = {
        "no_int": "<b>Dein Eingabe war kein Integer.</b>",
        "purge_cmpl": "<b>Purge fertig!</b>\n<code>{}</code> Nachrichten wurden gelöscht.",
        "permerror": "<b>Du hast keine Berechtigung, diesen Befehl zu verwenden.</b>",
        "purge_success": "Purge von {} Nachrichten erfolgreich durchgeführt.",
        "edit_success": ("Bearbeitung erfolgreich.\n"
                         "Alte Nachricht:\n{}\n\n\nNeue Nachricht:\n{}"),
        "sd_success": "Nachricht nach {} Sekunden erfolgreich gelöscht.",
        "err_purge_start": "<b>Bitte antworte auf eine Nachricht, um den Purge zu starten.</b>",
        "err_cmd_wrong": "<b>Deine Eingabe war falsch.</b>",
        "_cmd_doc_purge": "Löscht alle Nachrichten bis zu und inklusive der Antwort.",
        "_cmd_doc_purge_me": "Löscht x Nachrichten von dir.",
        "_cmd_doc_edit": "Bearbeitet die letzte Nachricht.",
        "_cmd_doc_sd": "Erstellt eine Nachricht die sich in den nächsten X Sekunden löscht.",
        "_cfg_log_purge": "Protokollieren Sie die Anzahl der `purge` Nachrichten als Info.",
        "_cfg_log_purgeme": "Protokollieren Sie die Anzahl der `purgeme` Nachrichten als Info.",
        "_cfg_log_edit": "Protokollieren Sie `edit` Nachrichten als Info.",
        "_cfg_log_sd": "Protokollieren `self-destructive` Nachrichten als Info.",
        "_cls_doc:": "Module zum entfernen von Nachrichten(normalerweise spam, etc.).",
    }

    strings_ru = {
        "no_int": "<b>Ваш ввод не является целочисленным типом (int)</b>",
        "purge_cmpl": "<b>Очистка завершена!</b>\nОчищено <code>{}</code> сообщений.",
        "permerror": "<b>У вас нет прав на использование этой команды.</b>",
        "purge_success": "Очистка< {} сообщений завершена успешно.",
        "edit_success": ("Редактирование завершено успешно.\n"
                         "Старое сообщение:\n{}\n\n\nНовое сообщение:\n{}"),
        "sd_success": "Сообщение после {} секунд успешно удалено.",
        "err_purge_start": "<b>Пожалуйста, ответьте на сообщение для начала очистки.</b>",
        "err_cmd_wrong": "<b>Ваш команда была неверной.</b>",
        "_cmd_doc_purge": "Удалить все сообщения до ответа включительно.",
        "_cmd_doc_purge_me": "Удалить x сообщений от вас.",
        "_cmd_doc_edit": "Редактировать последнее сообщение.",
        "_cmd_doc_sd": "Создать сообщение, которое удалится через X секунд.",
        "_cfg_log_purge": "Логировать количество очищенных сообщений как info.",
        "_cfg_log_purgeme": "Логировать количество удаленных сообщений от вас как info.",
        "_cfg_log_edit": "Логировать редактирование сообщения как info.",
        "_cfg_log_sd": "Логировать создание сообщения как info.",
        "_cls_doc": "Модуль для очистки спама и т.д.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_purge",
                True,
                doc=lambda: self.strings("_cfg_log_purge"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_purgeme",
                True,
                doc=lambda: self.strings("_cfg_log_purgeme"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_edit",
                True,
                doc=lambda: self.strings("_cfg_log_edit"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_sd",
                True,
                doc=lambda: self.strings("_cfg_log_sd"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def _purge_messages(self, message, chat, user_id, purge_count):
        itermsg = message.client.iter_messages(entity=chat, limit=None)
        msgs = []
        msg_count = 0
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

    async def purgecmd(self, message: Message):
        """
        Delete all messages up to and including the reply.
        """
        chat = message.chat
        msgs = []
        itermsg = message.client.iter_messages(chat, min_id=message.reply_to_msg_id, reverse=True)
        msg_count = 0

        if message.reply_to_msg_id is not None:
            async for msg in itermsg:
                msgs.append(msg)
                msg_count += 1
                msgs.append(message.reply_to_msg_id)
                if len(msgs) == 100:
                    await message.client.delete_messages(chat, msgs)
                    msgs = []
        else:
            await utils.answer(message, self.strings("err_purge_start"))
            return
        if msgs:
            await message.client.delete_messages(chat, msgs)
        done = await message.client.send_message(chat.id, self.strings("purge_cmpl").format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purge"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def purgemecmd(self, message: Message):
        """
        Delete x count of your latest messages.
        .purgeme all - delete all messages.
        """
        chat = message.chat
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not represents_int(args[0]) and "all" not in args:
            await utils.answer(message, self.strings("no_int"))
            return
        if len(args) > 1:
            await utils.answer(message, self.strings("err_cmd_wrong"))
            return
        purge_count = "all" if len(args) == 1 and "all" in args else int(args[0])
        user_id = self._tg_id
        await message.delete()
        msg_count = await self._purge_messages(message, chat, user_id, purge_count)
        done = await message.client.send_message(chat.id, self.strings("purge_cmpl").format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def purgeusercmd(self, message: Message):
        """
        Delete all messages from the replied user.
        """
        chat = message.chat
        if not message.is_reply:
            return await utils.answer(message, self.strings("no_reply"))
        reply = await message.get_reply_message()
        user_id = reply.sender_id
        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ):
            return await utils.answer(message, self.strings("permerror"))
        purge_count = "all"
        await message.delete()
        msg_count = await self._purge_messages(message, chat, user_id, purge_count)
        done = await message.client.send_message(chat.id, self.strings("purge_cmpl").format(str(msg_count)))
        await asyncio.sleep(2)
        await done.delete()
        if self.config["log_purgeme"]:
            return logger.info(self.strings("purge_success").format(str(msg_count)))
        return

    async def delcmd(self, message: Message):
        """
        Delete the replied message.
        """
        reply = await message.get_reply_message()
        if reply:
            try:
                await reply.delete()
                await message.delete()
            except rpcbaseerrors.RPCError:
                pass

    async def editcmd(self, message: Message):
        """
        Edit your last message.
        """
        chat = message.chat
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("err_cmd_wrong"))
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
        Make self-destructive messages.
        """
        args = utils.get_args_raw(message)
        args = str(args).split()
        if len(args) < 2:
            await utils.answer(message, self.strings("err_cmd_wrong"))
            return
        counter = int(" ".join(args[:1]))
        text = " ".join(args[1:])
        if (not counter or not text) and not represents_int(counter):
            await utils.answer(message, self.strings("err_cmd_wrong"))
            return
        msg = await utils.answer(message, text)
        await asyncio.sleep(counter)
        await msg.delete()
        if self.config["log_sd"]:
            return logger.info(self.strings("sd_success").format(str(counter)))
        return
