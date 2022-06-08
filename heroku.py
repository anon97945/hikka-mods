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
# scope: hikka_min 1.2.4
# requires: heroku3


import asyncio
import requests
import math
import logging
import heroku3
import os

from .. import loader, utils, main, heroku
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class herokumanagerMod(loader.Module):
    """
    Show Remaining Dyno Usage And Manage The Settings Of Your Heroku Hikka Instance.
    """
    strings = {
        "name": "Heroku Manager",
        "dev_channel": "@apodiktum_modules",
        "restarted": "<b>[Heroku]</b> Restart finished.",
        "args_error": "<b>[Heroku]</b> Too many args are given.",
        "no_args": "<b>[Heroku]</b> No args are given...</b>",
        "no_force": "<b>[Heroku]</b> You must use '--force' but this will leak credentials!</b>",
        "set_var": "<b>[Heroku]</b> Setting variable...</b>",
        "get_var": "<b>[Heroku]</b> Getting variable...</b>",
        "get_usage": "<b>[Heroku]</b> Getting Dyno usage...</b>",
        "wrong_platform": "[Heroku] This module only works on Heroku. {} is not supported.",
        "dyno_usage": ("<b><i><u>Dyno Usage</u></i></b>:\n"
                       # "\nDyno usage for <code>{}</code>:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]\n"
                       "Dyno hours quota remaining this month:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]"),
        "usage_error": ("<b>Error:</b> An error occured.\n"
                        "<code>{}</code>"),
        "var_changed": ("<b>[Heroku]</b> Variable successfully changed to:\n"
                        "<code>{}</code> = <code>{}</code>\n\n"
                        "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_added": ("<b>[Heroku]</b> Variable successfully added:\n"
                      "<code>{}</code> = <code>{}</code>\n\n"
                      "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_settings": ("<b>[Heroku]</b> Current Config:\n"
                         "<code>{}</code> = <code>{}</code>"),
        "var_deleted": ("<b>[Heroku]</b> Variable successfully deleted:\n"
                        "<code>{}</code>\n\n"
                        "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_not_exists": ("<b>[Heroku]</b> Variable does not exist:\n"
                           "<code>{}</code>"),
    }

    strings_ru = {
        "restarted": "<b>[Heroku]</b> Перезагрузка завершена.",
        "args_error": "<b>[Heroku]</b> Задано слишком много аргументов.",
        "no_args": "<b>[Heroku]</b> Аргументы не указаны...</b>",
        "no_force": "<b>[Heroku]</b> Вы должны использовать '--force', но это приведет к утечке учетных данных!</b>",
        "set_var": "<b>[Heroku]</b> Настройка переменной...</b>",
        "get_var": "<b>[Heroku]</b> Получение переменной...</b>",
        "get_usage": "<b>[Heroku]</b> Получение использования Dyno...</b>",
        "wrong_platform": "[Heroku] Этот модуль работает только на Heroku. {} не поддерживается.",
        "usage_error": ("<b>Error:</b> Произошла ошибка.\n"
                        "<code>{}</code>"),
        "var_changed": ("<b>[Heroku]</b> Переменная успешно изменена на:\n"
                        "<code>{}</code> = <code>{}</code>\n\n"
                        "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_added": ("<b>[Heroku]</b> Переменная успешно добавлена:\n"
                      "<code>{}</code> = <code>{}</code>\n\n"
                      "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_settings": ("<b>[Heroku]</b> Текущая конфигурацияТекущая конфигурация:\n"
                         "<code>{}</code> = <code>{}</code>"),
        "var_deleted": ("<b>[Heroku]</b> Переменная успешно удалена:\n"
                        "<code>{}</code>\n\n"
                        "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_not_exists": ("<b>[Heroku]</b> Переменная не существует:\n"
                           "<code>{}</code>"),
        "_cmd_doc_heroset": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Установить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroset <variable> <some settings>"),
        "_cmd_doc_heroget": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroget <variable>"),
        "_cmd_doc_herogetall": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить все переменные настроек Heroku. Это может привести к утечке API!\n"
                                "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herogetall --force"),
        "_cmd_doc_herodel": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Удалить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herodel <variable>"),
        "_cmd_doc_herousage": "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить использование Heroku Dyno.",
        "_cls_doc": "Показать оставшееся использование Dyno и управлять настройками вашего экземпляра Heroku Hikka.",
    }

    def __init__(self):
        self._ratelimit = []

    async def on_dlmod(self, client: TelegramClient, _):
        await client(JoinChannelRequest(channel=self.strings("dev_channel")))

    async def client_ready(self, client, db):
        platform = utils.get_named_platform()
        if "Heroku" not in platform:
            raise loader.LoadError(self.strings("wrong_platform").format(platform))
        self._db = db
        self._happ, self._hconfig = heroku.get_app(api_token=main.hikka.api_token)
        self._heroku_api = "https://api.heroku.com"
        self._heroku_app_name = self._happ.name
        self._heroku_api_key = os.environ["heroku_api_token"]
        self._heroku = heroku3.from_key(self._heroku_api_key)
        self._heroku_app = self._heroku.app(self._heroku_app_name)
        self._platform = utils.get_named_platform()
        self._herokuid = self._heroku.account().id

    async def herousagecmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Get Heroku Dyno Usage.
        """
        msg = await utils.answer(message, self.strings("get_usage"))
        useragent = ("Mozilla/5.0 (Linux; Android 10; SM-G975F)"
                     "AppleWebKit/537.36 (KHTML, like Gecko)"
                     "Chrome/80.0.3987.149 Mobile Safari/537.36"
                     )
        headers = {
         "User-Agent": useragent,
         "Authorization": f"Bearer {self._heroku_api_key}",
         "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        path = f"/accounts/{self._herokuid}/actions/get-quota"
        r = requests.get(self._heroku_api + path, headers=headers)
        if r.status_code != 200:
            return await utils.answer(message, self.strings("usage_error").format(str(r.reason)))
        result = r.json()
        quota = result["account_quota"]
        quota_used = result["quota_used"]

        # Used
        remaining_quota = quota - quota_used
        percentage = math.floor(remaining_quota / quota * 100)
        minutes_remaining = remaining_quota / 60
        hours = math.floor(minutes_remaining / 60)
        minutes = math.floor(minutes_remaining % 60)

        # Current
        App = result["apps"]
        try:
            App[0]["quota_used"]
        except IndexError:
            AppQuotaUsed = 0
            AppPercentage = 0
        else:
            AppQuotaUsed = App[0]["quota_used"] / 60
            AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
        AppHours = math.floor(AppQuotaUsed / 60)
        AppMinutes = math.floor(AppQuotaUsed % 60)
        # AppName = self._heroku_app_name
        await asyncio.sleep(1.5)
        return await utils.answer(msg, self.strings("dyno_usage").format(AppHours, AppMinutes, AppPercentage, hours, minutes, percentage))

    @loader.owner
    async def herosetcmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Set Heroku Settings Variable.
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroset <variable> <some settings>
        """
        args = utils.get_args_raw(message.message)
        if args := str(args).split():
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(message, self.strings("set_var"))
            await asyncio.sleep(1.5)
            if args[0] in heroku_var:
                msg = await utils.answer(msg, self.strings("var_changed").format(args[0], " ".join(args[1:])))
            else:
                msg = await utils.answer(msg, self.strings("var_added").format(args[0], " ".join(args[1:])))
            heroku_var[args[0]] = " ".join(args[1:])
            return
        return await utils.answer(message, self.strings("no_var"))

    @loader.owner
    async def herogetcmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ Get Heroku Settings Variable.
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroget <variable>
        """
        args = utils.get_args_raw(message.message)
        if args := str(args).split():
            if len(args) > 1:
                return await utils.answer(message, self.strings("args_error"))
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(message, self.strings("get_var"))
            await asyncio.sleep(1.5)
            if args[0] in heroku_var:
                return await utils.answer(msg, self.strings("var_settings").format(args[0], heroku_var[args[0]]))
            return await utils.answer(msg, self.strings("var_not_exists").format(args[0]))
        return await utils.answer(message, self.strings("no_var"))

    @loader.owner
    async def herogetallcmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ Get All Heroku Settings Variable. This may leak API!
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herogetall --force
        """
        args = utils.get_args_raw(message.message)
        args = str(args).split()
        if args and args[0] == "--force":
            if len(args) > 1:
                return await utils.answer(message, self.strings("args_error"))
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(message, self.strings("get_var"))
            await asyncio.sleep(1.5)
            cmpl_cnfg = ""
            for x in heroku_var.to_dict():
                cmpl_cnfg = (
                    f"{cmpl_cnfg}<code>{x}</code>"
                    + ":\n<code>"
                    + heroku_var.to_dict()[x]
                    + "</code>\n\n"
                )
            return await utils.answer(msg, cmpl_cnfg)
        return await utils.answer(message, self.strings("no_force"))

    @loader.owner
    async def herodelcmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ Delete Heroku Settings Variable.
        ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herodel <variable>
        """
        args = utils.get_args_raw(message.message)
        if args := str(args).split():
            if len(args) > 1:
                return await utils.answer(message, self.strings("args_error"))
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(message, self.strings("get_var"))
            await asyncio.sleep(1.5)
            if args[0] in heroku_var:
                msg = await utils.answer(msg, self.strings("var_deleted").format(args[0]))
                del heroku_var[args[0]]
                return
            return await utils.answer(message, self.strings("var_not_exists").format(args[0]))
        return await utils.answer(message, self.strings("no_var"))
