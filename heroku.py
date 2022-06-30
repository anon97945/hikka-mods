__version__ = (0, 0, 17)


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
# scope: hikka_min 1.2.4
# requires: heroku3


import asyncio
import requests
import math
import logging
import heroku3
import os

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from .. import loader, utils, main, heroku
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumHerokuManagerMod(loader.Module):
    """
    Show Remaining Dyno Usage And Manage The Settings Of Your 🦸🏼‍♂️ Hero!ku Hikka Instance.
    """
    strings = {
        "name": "Apo HerokuManager",
        "developer": "@anon97945",
        "args_error": "<b>[🦸🏼‍♂️ Hero!ku]</b> Too many args are given.",
        "dyno_usage": ("<b><i><u>Dyno Usage</u></i></b>:\n"
                       "\nDyno usage for <code>Hikka Userbot</code>:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]\n"
                       "Dyno hours quota remaining this month:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]"),
        "get_usage": "<b>[🦸🏼‍♂️ Hero!ku]</b> Getting Dyno usage...</b>",
        "get_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Getting variable...</b>",
        "no_args": "<b>[🦸🏼‍♂️ Hero!ku]</b> No args are given...</b>",
        "no_force": "<b>[🦸🏼‍♂️ Hero!ku]</b> You must use '--force' but this will leak credentials!</b>",
        "restarted": "<b>[🦸🏼‍♂️ Hero!ku]</b> Restart finished.",
        "set_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Setting variable...</b>",
        "usage_error": ("<b>Error:</b> An error occured.\n"
                        "<code>{}</code>"),
        "var_added": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully added:\n"
                      "<code>{}</code> = <code>{}</code>\n\n"
                      "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_changed": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully changed to:\n"
                        "<code>{}</code> = <code>{}</code>\n\n"
                        "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_deleted": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully deleted:\n"
                        "<code>{}</code>\n\n"
                        "<b>The Heroku Dyno will now be restarted.</b>"),
        "var_not_exists": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Variable does not exist:\n"
                           "<code>{}</code>"),
        "var_settings": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Current Config:\n"
                         "<code>{}</code> = <code>{}</code>"),
        "wrong_platform": "[🦸🏼‍♂️ Hero!ku] This module only works on Heroku. {} is not supported.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_ru = {
        "_cls_doc": "Показать оставшееся использование Dyno и управлять настройками вашего экземпляра 🦸🏼‍♂️ Hero!ku Hikka.",
        "_cmd_doc_herodel": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Удалить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herodel <variable>"),
        "_cmd_doc_heroget": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroget <variable>"),
        "_cmd_doc_herogetall": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить все переменные настроек Heroku. Это может привести к утечке API!\n"
                                "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herogetall --force"),
        "_cmd_doc_heroset": ("⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Установить переменную настроек Heroku.\n"
                             "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroset <variable> <some settings>"),
        "_cmd_doc_herousage": "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить использование Heroku Dyno.",
        "args_error": "<b>[🦸🏼‍♂️ Hero!ku]</b> Задано слишком много аргументов.",
        "dyno_usage": ("<b><i><u>Dyno Usage</u></i></b>:\n"
                       "\nИспользование Дино для <code>Hikka Userbot</code>:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]\n"
                       "Осталось часов Дино по квоте в месяц:\n"
                       "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]"),
        "get_usage": "<b>[🦸🏼‍♂️ Hero!ku]</b> Получение использования Dyno...</b>",
        "get_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Получение переменной...</b>",
        "no_args": "<b>[🦸🏼‍♂️ Hero!ku]</b> Аргументы не указаны...</b>",
        "no_force": "<b>[🦸🏼‍♂️ Hero!ku]</b> Вы должны использовать '--force', но это приведет к утечке учетных данных!</b>",
        "restarted": "<b>[🦸🏼‍♂️ Hero!ku]</b> Перезагрузка завершена.",
        "set_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Настройка переменной...</b>",
        "usage_error": ("<b>Error:</b> Произошла ошибка.\n"
                        "<code>{}</code>"),
        "var_added": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно добавлена:\n"
                      "<code>{}</code> = <code>{}</code>\n\n"
                      "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_changed": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно изменена на:\n"
                        "<code>{}</code> = <code>{}</code>\n\n"
                        "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_deleted": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно удалена:\n"
                        "<code>{}</code>\n\n"
                        "<b>Теперь Heroku Dyno будет перезапущен.</b>"),
        "var_not_exists": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная не существует:\n"
                           "<code>{}</code>"),
        "var_settings": ("<b>[🦸🏼‍♂️ Hero!ku]</b> Текущая конфигурацияТекущая конфигурация:\n"
                         "<code>{}</code> = <code>{}</code>"),
        "wrong_platform": "[🦸🏼‍♂️ Hero!ku] Этот модуль работает только на Heroku. {} не поддерживается.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
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
        platform = utils.get_named_platform()
        if "Heroku" not in platform:
            raise loader.LoadError(self.strings("wrong_platform").format(platform))
        self._db = db
        self._happ, self._hconfig = heroku.get_app(api_token=main.hikka.api_token)
        self._heroku_api = "https://api.heroku.com"
        self._heroku_app_name = self._happ.name
        self._heroku_app_id = self._happ.id
        self._heroku_api_key = os.environ["heroku_api_token"]
        self._heroku = heroku3.from_key(self._heroku_api_key)
        self._heroku_app = self._heroku.app(self._heroku_app_name)
        self._platform = utils.get_named_platform()
        self._herokuid = self._heroku.account().id
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

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
        logger.error(result)
        App = result["apps"]
        try:
            for app in App:
                if app["app_uuid"] == self._heroku_app_id:
                    app_quota_used = app["quota_used"]
                    break
        except IndexError:
            AppQuotaUsed = 0
            AppPercentage = 0
        else:
            AppQuotaUsed = app_quota_used / 60
            AppPercentage = math.floor(app_quota_used * 100 / quota)
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
                await self._logger(f"Open migrations: {migrate}", self.debug)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug)
                    return True
            elif not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | Forcehash done: {self.hashs}", self.debug)
                return False
            else:
                await self._logger(f"Open migrations: {migrate} | Skip migration.", self.debug)
                return False
            return False
        await self._logger("No changes in `changes` dictionary found.", self.debug)
        return False

    async def auto_migrate_handler(self, auto_migrate: bool = False):
        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])
            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if auto_migrate and migrate:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate}", self.debug)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug)
                    return
            elif not auto_migrate and not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Forcehash done: {self.hashs}", self.debug)
                return
            else:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Skip migrate_handler.", self.debug)
                return
        await self._logger("No changes in `changes` dictionary found.", self.debug)
        return

    async def force_set_hashs(self):
        await self._set_missing_hashs()
        return True

    async def check_new_migration(self):
        chash = hashlib.md5(self._migrate_to.encode('utf-8')).hexdigest()
        return chash not in self.hashs

    async def full_migrated(self):
        full_migrated = True
        for migration in self.changes:
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        for migration in self.changes:
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self.changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        if category == "classname":
            if self._classname != old_classname and (old_classname in self._db.keys() and self._db[old_classname] and old_classname is not None):
                await self._logger(f"{migration} | {category} | old_value: {str(old_classname)} | new_value: {str(new_classname)}", self.debug)
                await self._copy_config(category, old_classname, new_classname, new_name)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_classname, new_classname))
        elif category == "name":
            await self._logger(f"{migration} | {category} | old_value: {str(old_name)} | new_value: {str(new_name)}", self.debug)
            if self._name != old_name and (old_name in self._db.keys() and self._db[old_name] and old_name is not None):
                await self._copy_config(category, old_name, new_name, new_classname)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_name, new_name))
        elif category == "config":
            await self._migrate_cfg_values(migration, category, new_name, new_classname)
        return

    async def _get_names(self, migration):
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
                        await self._logger(f"{migration} | {category} | ({{old_value: {str(old_value)}}} `==` {{new_value: {str(value)}}}) `and` {{key: {key}}} `==` {{cnfg_key: {cnfg_key}}}", self.debug)
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
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)

    async def _logger(self, log_string, debug: bool = False):
        if debug or self.log:
            return logger.info(log_string)
        return logger.debug(log_string)
