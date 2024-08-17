__version__ = (0, 0, 36)


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
import logging
import math
import os

import heroku3
import requests
from telethon.tl.types import Message

from .. import heroku, loader, main, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumHerokuManagerMod(loader.Module):
    """
    Show Remaining Dyno Usage And Manage The Settings Of Your 🦸🏼‍♂️ Hero!ku Hikka Instance.
    """

    strings = {
        "name": "Apo-HerokuManager",
        "developer": "@anon97945",
        "args_error": "<b>[🦸🏼‍♂️ Hero!ku]</b> Too many args are given.",
        "dyno_usage": (
            "<b><i><u>Dyno Usage</u></i></b>:\n"
            "\nDyno usage for <code>Hikka Userbot</code>:\n"
            "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]\n"
            "Dyno hours quota remaining this month:\n"
            "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]"
        ),
        "get_usage": "<b>[🦸🏼‍♂️ Hero!ku]</b> Getting Dyno usage...</b>",
        "get_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Getting variable...</b>",
        "no_args": "<b>[🦸🏼‍♂️ Hero!ku]</b> No args are given...</b>",
        "no_force": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> You must use '--force' but this will leak"
            " credentials!</b>"
        ),
        "restarted": "<b>[🦸🏼‍♂️ Hero!ku]</b> Restart finished.",
        "set_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Setting variable...</b>",
        "usage_error": "<b>Error:</b> An error occured.\n<code>{}</code>",
        "var_added": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully added:\n"
            "<code>{}</code> = <code>{}</code>\n\n"
            "<b>The Heroku Dyno will now be restarted.</b>"
        ),
        "var_changed": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully changed to:\n"
            "<code>{}</code> = <code>{}</code>\n\n"
            "<b>The Heroku Dyno will now be restarted.</b>"
        ),
        "var_deleted": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Variable successfully deleted:\n"
            "<code>{}</code>\n\n"
            "<b>The Heroku Dyno will now be restarted.</b>"
        ),
        "var_not_exists": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Variable does not exist:\n<code>{}</code>"
        ),
        "var_settings": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Current Config:\n<code>{}</code> = <code>{}</code>"
        ),
        "wrong_platform": (
            "[🦸🏼‍♂️ Hero!ku] This module only works on Heroku. {} is not supported."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {
        "_cls_doc": (
            "Показать оставшееся использование Dyno и управлять настройками"
            " вашего экземпляра 🦸🏼‍♂️ Hero!ku Hikka."
        ),
        "_cmd_doc_herodel": (
            "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Удалить переменную настроек"
            " Heroku.\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .herodel <variable>"
        ),
        "_cmd_doc_heroget": (
            "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить переменную настроек"
            " Heroku.\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroget <variable>"
        ),
        "_cmd_doc_herogetall": (
            "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить все переменные настроек"
            " Heroku. Это может привести к утечке API!\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example:"
            " .herogetall --force"
        ),
        "_cmd_doc_heroset": (
            "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Установить переменную настроек"
            " Heroku.\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬   - Example: .heroset <variable> <some settings>"
        ),
        "_cmd_doc_herousage": (
            "⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭"
            " ⁭⁫⁪⁫⁬⁭⁫⁪ ⁭ ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Получить использование Heroku"
            " Dyno."
        ),
        "args_error": "<b>[🦸🏼‍♂️ Hero!ku]</b> Задано слишком много аргументов.",
        "dyno_usage": (
            "<b><i><u>Dyno Usage</u></i></b>:\n"
            "\nИспользование Дино для <code>Hikka Userbot</code>:\n"
            "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]\n"
            "Осталось часов Дино по квоте в месяц:\n"
            "    • <code>{}h {}m</code> <b>|</b> [<code>{}%</code>]"
        ),
        "get_usage": "<b>[🦸🏼‍♂️ Hero!ku]</b> Получение использования Dyno...</b>",
        "get_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Получение переменной...</b>",
        "no_args": "<b>[🦸🏼‍♂️ Hero!ku]</b> Аргументы не указаны...</b>",
        "no_force": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Вы должны использовать '--force', но это"
            " приведет к утечке учетных данных!</b>"
        ),
        "restarted": "<b>[🦸🏼‍♂️ Hero!ku]</b> Перезагрузка завершена.",
        "set_var": "<b>[🦸🏼‍♂️ Hero!ku]</b> Настройка переменной...</b>",
        "usage_error": "<b>Error:</b> Произошла ошибка.\n<code>{}</code>",
        "var_added": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно добавлена:\n"
            "<code>{}</code> = <code>{}</code>\n\n"
            "<b>Теперь Heroku Dyno будет перезапущен.</b>"
        ),
        "var_changed": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно изменена на:\n"
            "<code>{}</code> = <code>{}</code>\n\n"
            "<b>Теперь Heroku Dyno будет перезапущен.</b>"
        ),
        "var_deleted": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная успешно удалена:\n"
            "<code>{}</code>\n\n"
            "<b>Теперь Heroku Dyno будет перезапущен.</b>"
        ),
        "var_not_exists": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Переменная не существует:\n<code>{}</code>"
        ),
        "var_settings": (
            "<b>[🦸🏼‍♂️ Hero!ku]</b> Текущая конфигурацияТекущая конфигурация:\n"
            "<code>{}</code> = <code>{}</code>"
        ),
        "wrong_platform": (
            "[🦸🏼‍♂️ Hero!ku] Этот модуль работает только на Heroku. {} не"
            " поддерживается."
        ),
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
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
        )

    async def client_ready(self):
        platform = utils.get_named_platform()
        if "DYNO" not in os.environ:
            raise loader.LoadError(self.strings("wrong_platform").format(platform))
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self._init_heroku_vars()

    def _init_heroku_vars(self):
        self._happ, self._hconfig = heroku.get_app(api_token=main.hikka.api_token)
        self._heroku_api = "https://api.heroku.com"
        self._heroku_app_name = self._happ.name
        self._heroku_app_id = self._happ.id
        self._heroku_api_key = os.environ["heroku_api_token"]
        self._heroku = heroku3.from_key(self._heroku_api_key)
        self._heroku_app = self._heroku.app(self._heroku_app_name)
        self._platform = utils.get_named_platform()
        self._herokuid = self._heroku.account().id

    async def herousagecmd(self, message: Message):
        """⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Get Heroku Dyno Usage."""
        msg = await utils.answer(
            message,
            self.apo_lib.utils.get_str("get_usage", self.all_strings, message),
        )
        useragent = (
            "Mozilla/5.0 (Linux; Android 10; SM-G975F)"
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
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "usage_error", self.all_strings, message
                ).format(r.reason),
            )
        result = r.json()
        quota = result["account_quota"]
        quota_used = result["quota_used"]

        # Used
        remaining_quota = quota - quota_used
        app_quota_used = 0
        percentage = math.floor(remaining_quota / quota * 100)
        minutes_remaining = remaining_quota / 60
        hours = math.floor(minutes_remaining / 60)
        minutes = math.floor(minutes_remaining % 60)

        # Current
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
        return await utils.answer(
            msg,
            self.apo_lib.utils.get_str("dyno_usage", self.all_strings, message).format(
                AppHours, AppMinutes, AppPercentage, hours, minutes, percentage
            ),
        )

    @loader.owner
    async def herosetcmd(self, message: Message):
        """
        ⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬Set Heroku Settings Variable.
        - Example: .heroset <variable> <some settings>
        """
        args = utils.get_args_raw(message)
        if args := str(args).split():
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(
                message,
                self.apo_lib.utils.get_str("set_var", self.all_strings, message),
            )
            await asyncio.sleep(1.5)
            if args[0] in heroku_var:
                msg = await utils.answer(
                    msg,
                    self.apo_lib.utils.get_str(
                        "var_changed", self.all_strings, message
                    ).format(args[0], " ".join(args[1:])),
                )
            else:
                msg = await utils.answer(
                    msg,
                    self.apo_lib.utils.get_str(
                        "var_added", self.all_strings, message
                    ).format(args[0], " ".join(args[1:])),
                )
            heroku_var[args[0]] = " ".join(args[1:])
            return
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("no_var", self.all_strings, message),
        )

    @loader.owner
    async def herogetcmd(self, message: Message):
        """
        Get Heroku Settings Variable.
        - Example: .heroget <variable>
        """
        args = utils.get_args_raw(message)
        if args := str(args).split():
            if len(args) > 1:
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("args_error", self.all_strings, message),
                )
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(
                message,
                self.apo_lib.utils.get_str("get_var", self.all_strings, message),
            )
            await asyncio.sleep(1.5)
            if args[0] in heroku_var:
                return await utils.answer(
                    msg,
                    self.apo_lib.utils.get_str(
                        "var_settings", self.all_strings, message
                    ).format(args[0], heroku_var[args[0]]),
                )
            return await utils.answer(
                msg,
                self.apo_lib.utils.get_str(
                    "var_not_exists", self.all_strings, message
                ).format(args[0]),
            )
        return await utils.answer(
            message,
            self.apo_lib.utils.get_str("no_var", self.all_strings, message),
        )

    @loader.owner
    async def herogetallcmd(self, message: Message):
        """
        Get All Heroku Settings Variable. This may leak API!
        - Example: .herogetall --force
        """
        args = utils.get_args_raw(message)
        args = str(args).split()
        if args and args[0] == "--force":
            if len(args) > 1:
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("args_error", self.all_strings, message),
                )
            heroku_var = self._heroku_app.config()
            msg = await utils.answer(
                message,
                self.apo_lib.utils.get_str("get_var", self.all_strings, message),
            )
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
        return await utils.answer(
            message,
            self.apo_lib.utils.get_str("no_force", self.all_strings, message),
        )

    @loader.owner
    async def herodelcmd(self, message: Message):
        """
        Delete Heroku Settings Variable.
        - Example: .herodel <variable>
        """
        args = utils.get_args_raw(message)
        if not (args := str(args).split()):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_var", self.all_strings, message),
            )
            return

        if len(args) > 1:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("args_error", self.all_strings, message),
            )
        heroku_var = self._heroku_app.config()
        msg = await utils.answer(
            message,
            self.apo_lib.utils.get_str("get_var", self.all_strings, message),
        )
        await asyncio.sleep(1.5)
        if args[0] in heroku_var:
            msg = await utils.answer(
                msg,
                self.apo_lib.utils.get_str(
                    "var_deleted", self.all_strings, message
                ).format(args[0]),
            )
            del heroku_var[args[0]]
            return

        await utils.answer(
            message,
            self.apo_lib.utils.get_str(
                "var_not_exists", self.all_strings, message
            ).format(args[0]),
        )
