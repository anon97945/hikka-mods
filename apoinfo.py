__version__ = (0, 1, 24)


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

# scope: inline
# scope: hikka_only
# scope: hikka_min 1.3.3

import logging

import git
from telethon.tl.types import Message
from telethon.utils import get_display_name

from .. import loader, main, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumInfoMod(loader.Module):
    """
    Show userbot info
    """

    strings = {
        "name": "Apo-Info",
        "developer": "@anon97945",
        "_cfg_banner": "Set `True` in order to disable an media banner.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_bnr": "Custom Banner.",
        "_cfg_cst_btn": "Custom button. Leave empty to remove button.",
        "_cfg_cst_frmt": "Custom fileformat for Banner.",
        "_cfg_cst_msg": (
            "Custom message for info. May contain {me}, {version}, {build},"
            " {prefix}, {platform}, {upd}, {uptime} keywords."
        ),
        "_cfg_inline_banner": "Set `True` in order to disable an inline media banner.",
        "build": "Build",
        "description": "ℹ This will not compromise any sensitive info.",
        "owner": "Owner",
        "prefix": "Prefix",
        "send_info": "Send userbot info.",
        "up-to-date": "😌 Up-to-date.",
        "update_required": "😕 Update required: <code>{}update</code>",
        "uptime": "Uptime",
        "version": "Version",
    }

    strings_en = {}

    strings_de = {
        "_cfg_banner": "Setzen Sie `True`, um das Media Banner zu deaktivieren.",
        "_cfg_cst_bnr": "Benutzerdefiniertes Banner.",
        "_cfg_cst_btn": (
            "Benutzerdefinierte Schaltfläche für Informationen. Leer lassen, um"
            " die Schaltfläche zu entfernen."
        ),
        "_cfg_cst_frmt": "Benutzerdefiniertes Dateiformat für das Banner.",
        "_cfg_cst_msg": (
            "Benutzerdefinierte Nachricht für Info. Kann die Schlüsselwörter"
            " {me}, {version}, {build}, {prefix}, {platform}, {upd}, {uptime}"
            " enthalten."
        ),
        "_cfg_inline_banner": (
            "Setzen Sie `True`, um das Inline Media Banner zu deaktivieren."
        ),
        "_cmd_doc_capoinfo": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "_ihandle_doc_info": "Отправить информацию о юзерботе",
        "build": "Build",
        "description": "ℹ Dadurch werden keine sensiblen Daten gefährdet.",
        "owner": "Eigentümer",
        "prefix": "Prefix",
        "send_info": "Benutzerbot-Informationen senden.",
        "up-to-date": "😌 Up-to-date",
        "update_required": "😕 Aktualisierung erforderlich: <code>{}update</code>",
        "uptime": "Betriebszeit",
        "version": "Version",
    }

    strings_ru = {
        "_cfg_banner": "Поставь `True`, чтобы отключить баннер-картинку.",
        "_cfg_cst_bnr": "Кастомный баннер.",
        "_cfg_cst_btn": (
            "Кастомная кнопка в сообщении в info. Оставь пустым, чтобы убрать кнопку."
        ),
        "_cfg_cst_frmt": "Кастомный формат файла для баннера.",
        "_cfg_cst_msg": (
            "Кастомный текст сообщения в info. Может содержать ключевые слова"
            " {me}, {version}, {build}, {prefix}, {platform}, {upd}, {uptime}."
        ),
        "_cfg_inline_banner": (
            "Установите `True`, чтобы отключить встроенный медиа-баннер"
        ),
        "_cmd_doc_capoinfo": "Это откроет конфиг для модуля.",
        "_ihandle_doc_info": "Отправить информацию о юзерботе.",
        "build": "Сборка",
        "description": "ℹ Это не раскроет никакой личной информации.",
        "owner": "Владелец",
        "prefix": "Префикс",
        "send_info": "Отправить информацию о юзерботе.",
        "up-to-date": "😌 Актуальная версия.",
        "update_required": "😕 Требуется обновление: <code>{}update</code>",
        "uptime": "Аптайм",
        "version": "Версия",
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
                "old": "Apo Info",
                "new": "Apo-Info",
            },
        },
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_banner",
                "https://t.me/apodiktum_dumpster/6",
                lambda: self.strings("_cfg_cst_bnr"),
                validator=loader.validators.Link(),
            ),
            loader.ConfigValue(
                "custom_format",
                "video",
                lambda: self.strings("_cfg_cst_frmt"),
                validator=loader.validators.Choice(["photo", "video", "audio", "gif"]),
            ),
            loader.ConfigValue(
                "custom_message",
                None,
                doc=lambda: self.strings("_cfg_cst_msg"),
                validator=loader.validators.Union(
                    loader.validators.String(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "disable_banner",
                False,
                lambda: self.strings("_cfg_banner"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "disable_inline_banner",
                False,
                lambda: self.strings("_cfg_inline_banner"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_button1",
                [
                    "🔥 Apodiktum Hikka Modules 🔥",
                    "https://t.me/apodiktum_modules",
                ],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button2",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button3",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button4",
                ["🌘 Hikka EN Support chat", "https://t.me/hikka_en"],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button5",
                ["🌘 Hikka. userbot", "https://t.me/hikka_ub"],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button6",
                ["🌘 Hikka RU Support chat", "https://t.me/hikka_talks"],
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button7",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button8",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button9",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button10",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button11",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_button12",
                None,
                lambda: self.strings("_cfg_cst_btn"),
                validator=loader.validators.Union(
                    loader.validators.Series(fixed_len=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self, client, _):
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
        self._me = await client.get_me()

    def _render_info(self) -> str:
        ver = utils.get_git_hash() or "Unknown"

        try:
            repo = git.Repo()
            diff = repo.git.log(["HEAD..origin/master", "--oneline"])
            upd = (
                self.strings("update_required").format(
                    utils.escape_html(self.get_prefix())
                )
                if diff
                else self.strings("up-to-date")
            )
        except Exception:
            upd = ""

        me = (
            "<b><a"
            f' href="tg://user?id={self._me.id}">{utils.escape_html(get_display_name(self._me))}</a></b>'
        )
        version = f'<i>{".".join(list(map(str, list(main.__version__))))}</i>'
        build = f'<a href="https://github.com/hikariatama/Hikka/commit/{ver}">#{ver[:8]}</a>'  # fmt: skip
        prefix = f"«<code>{utils.escape_html(self.get_prefix())}</code>»"
        platform = utils.get_named_platform()
        uptime = self.apo_lib.utils.get_uptime(short=True)

        return (
            self.config["custom_message"].format(
                me=me,
                version=version,
                build=build,
                prefix=prefix,
                platform=platform,
                upd=upd,
                uptime=uptime,
            )
            if self.config["custom_message"] and self.config["custom_message"] != "no"
            else (
                "<b>🌚 Apodiktum Hikka Info</b>\n"
                f"<b>🤴 {self.strings('owner')}: </b>{me}\n\n"
                f"<b>🕰 {self.strings('uptime')}: </b><code>{uptime}</code>\n"
                f"<b>🔮 {self.strings('version')}: </b>{version} {build}\n"
                f"<b>{upd}</b>\n\n"
                f"<b>📼 {self.strings('prefix')}: </b>{prefix}\n"
                f"<b>{platform}</b>\n"
            )
        )

    def _get_mark(self, btn_count: int) -> dict:
        btn_count = str(btn_count)
        return (
            {
                "text": self.config[f"custom_button{btn_count}"][0],
                "url": self.config[f"custom_button{btn_count}"][1],
            }
            if self.config[f"custom_button{btn_count}"]
            else None
        )

    @loader.inline_everyone
    async def apoinfo_inline_handler(self, _) -> dict:
        """Send userbot info"""
        m = {x: self._get_mark(x) for x in range(13)}
        btns = [
            [
                *([m[1]] if m[1] else []),
                *([m[2]] if m[2] else []),
                *([m[3]] if m[3] else []),
            ],
            [
                *([m[4]] if m[4] else []),
                *([m[5]] if m[5] else []),
                *([m[6]] if m[6] else []),
            ],
            [
                *([m[7]] if m[7] else []),
                *([m[8]] if m[8] else []),
                *([m[9]] if m[9] else []),
            ],
            [
                *([m[10]] if m[10] else []),
                *([m[11]] if m[11] else []),
                *([m[12]] if m[12] else []),
            ],
        ]
        msg_type = "message" if self.config["disable_inline_banner"] else "caption"
        return {
            "title": self.strings("send_info"),
            "description": self.strings("description"),
            msg_type: self._render_info(),
            self.config["custom_format"]: self.config["custom_banner"],
            "thumb": (
                "https://github.com/hikariatama/Hikka/raw/master/assets/hikka_pfp.png"
            ),
            "reply_markup": btns,
        }

    async def capoinfocmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @loader.unrestricted
    async def apoinfocmd(self, message: Message):
        """Send userbot info"""
        m = {x: self._get_mark(x) for x in range(13)}
        btns = [
            [
                *([m[1]] if m[1] else []),
                *([m[2]] if m[2] else []),
                *([m[3]] if m[3] else []),
            ],
            [
                *([m[4]] if m[4] else []),
                *([m[5]] if m[5] else []),
                *([m[6]] if m[6] else []),
            ],
            [
                *([m[7]] if m[7] else []),
                *([m[8]] if m[8] else []),
                *([m[9]] if m[9] else []),
            ],
            [
                *([m[10]] if m[10] else []),
                *([m[11]] if m[11] else []),
                *([m[12]] if m[12] else []),
            ],
        ]
        await self.inline.form(
            message=message,
            text=self._render_info(),
            reply_markup=btns,
            **{}
            if self.config["disable_banner"]
            else {self.config["custom_format"]: self.config["custom_banner"]},
        )
