__version__ = (0, 1, 79)


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

# scope: libsndfile1 gcc ffmpeg rubberband-cli
# scope: hikka_only
# scope: hikka_min 1.1.28

# requires: gtts pydub soundfile pyrubberband numpy AudioSegment wave

import logging
import os
import soundfile
import pyrubberband

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from gtts import gTTS
from io import BytesIO
from .. import loader, utils
from subprocess import Popen, PIPE
from pydub import AudioSegment, effects
from telethon.tl.types import Message


logger = logging.getLogger(__name__)


async def audionormalizer(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rawsound = AudioSegment.from_file(bytes_io_file, "wav")
    normalizedsound = effects.normalize(rawsound)
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format="wav")
    bytes_io_file.name = f"{fn}.wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audiohandler(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = ['ffmpeg', '-y', '-i', 'pipe:', '-acodec', 'pcm_s16le', '-f', 'wav', '-ac', '1', 'pipe:']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{fn}.wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe if out.startswith(b'RIFF\xff\xff\xff') else None


async def makewaves(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = ['ffmpeg', '-y', '-i', 'pipe:', '-c:a', 'libopus', '-f', 'opus', '-ac', '2', 'pipe:']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{fn}.ogg"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe


def represents_speed(s):
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


async def speedup(bytes_io_file, fn, fe, speed):
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format='wav')
    bytes_io_file.seek(0)
    bytes_io_file.name = f"{fn}.wav"
    return bytes_io_file, fn, fe


@loader.tds
class ApodiktumTTSMod(loader.Module):
    strings = {
        "name": "Apo TextToSpeech",
        "developer": "@anon97945",
        "_cfg_tts_lang": "Set your language code for the TTS here.",
        "_cfg_tts_speed": "Set the desired speech speed.",
        "needspeed": "You need to provide a speed value between 0.25 and 3.0.",
        "needvoice": "<b>[TTS]</b> This command needs a voicemessage.",
        "no_reply": "<b>[TTS]</b> You need to reply to a voicemessage.",
        "no_speed": "<b>[TTS]</b> Your input was an unsupported speed value.",
        "processing": "<b>[TTS]</b> Message is being processed ...",
        "tts_needs_text": "<b>[TTS]</b> I need text to convert to speech!",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_en = {
        "needspeed": "You need to provide a speed value between 0.25 and 3.0.",
        "needvoice": "<b>[TTS]</b> This command needs a voicemessage.",
        "no_reply": "<b>[TTS]</b> You need to reply to a voicemessage.",
        "no_speed": "<b>[TTS]</b> Your input was an unsupported speed value.",
        "processing": "<b>[TTS]</b> Message is being processed ...",
        "tts_needs_text": "<b>[TTS]</b> I need text to convert to speech!",
    }

    strings_de = {
        "_cfg_tts_lang": "Stellen Sie hier Ihren Sprachcode für TTS ein.",
        "_cfg_tts_speed": "Stellen Sie die gewünschte Sprechgeschwindigkeit ein.",
        "_cmd_doc_ctts": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "needspeed": "Sie müssen einen Geschwindigkeitswert zwischen 0.25 und 3.0 angeben.",
        "needvoice": "<b>[TTS]</b> Dieser Befehl benötigt eine Sprachnachricht.",
        "no_reply": "<b>[TTS]</b> Sie müssen auf eine Sprachnachricht antworten.",
        "no_speed": "<b>[TTS]</b> Ihre Eingabe war ein nicht unterstützter Geschwindigkeitswert.",
        "processing": "<b>[TTS]</b> Nachricht wird verarbeitet ...",
        "tts_needs_text": "<b>[TTS]</b> Ich brauche Text, um ihn in Sprache umzuwandeln!",
    }

    strings_ru = {
        "_cfg_tts_lang": "Установите ваш код страны для TTS здесь.",
        "_cfg_tts_speed": "Установите желаемую скорость речи.",
        "_cmd_doc_ctts": "Это откроет конфиг для модуля.",
        "needspeed": "Вам нужно предоставить значение скорости между 0.25 и 3.0",
        "needvoice": "<b>[TTS]</b> Этой команде нужно голосовое сообщение.",
        "no_reply": "<b>[TTS]</b> Вам нужно сделать реплай на голосовое сообщение.",
        "no_speed": "<b>[TTS]</b> Ваш ввод является неподдерживаемым значением скорости.",
        "processing": "<b>[TTS]</b> Сообщение обрабатывается...",
        "tts_needs_text": "<b>[TTS]</b> Мне нужен текст для преобразования в речь!",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "tts_lang",
                "en",
                doc=lambda: self.strings("_cfg_tts_lang"),
            ),
            loader.ConfigValue(
                "tts_speed",
                "1",
                doc=lambda: self.strings("_cfg_tts_speed"),
                validator=loader.validators.Float(minimum=0.25, maximum=3),
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

    async def cttscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def ttscmd(self, message: Message):
        """Convert text to speech with Google APIs"""
        speed = self.config["tts_speed"]
        text = utils.get_args_raw(message.message)
        if len(text) == 0:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                await utils.answer(message, self._strings("tts_needs_text", utils.get_chat_id(message)))
                return
        msg = await utils.answer(message, self._strings("processing", utils.get_chat_id(message)))
        tts = await utils.run_sync(gTTS, text, lang=self.config["tts_lang"])
        voice = BytesIO()
        await utils.run_sync(tts.write_to_fp, voice)
        voice.seek(0)
        voice.name = "voice.mp3"
        fn, fe = os.path.splitext(voice.name)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(msg, voice, voice_note=True)
        if msg.out:
            await msg.delete()

    async def speedvccmd(self, message: Message):
        """Speed up voice by x"""
        speed = utils.get_args_raw(message)
        if not message.is_reply:
            await utils.answer(message, self._strings("no_reply", utils.get_chat_id(message)))
            return
        replymsg = await message.get_reply_message()
        if not replymsg.voice:
            await utils.answer(message, self._strings("needvoice", utils.get_chat_id(message)))
            return
        if len(speed) == 0:
            await utils.answer(message, self._strings("needspeed", utils.get_chat_id(message)))
            return
        if not represents_speed(speed):
            await utils.answer(message, self._strings("no_speed", utils.get_chat_id(message)))
            return
        msg = await utils.answer(message, self._strings("processing", utils.get_chat_id(message)))
        ext = replymsg.file.ext
        voice = BytesIO()
        voice.name = replymsg.file.name
        await replymsg.client.download_file(replymsg, voice)
        voice.name = f"voice{ext}"
        fn, fe = os.path.splitext(voice.name)
        voice.seek(0)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(msg, voice, voice_note=True)
        if msg.out:
            await msg.delete()


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
