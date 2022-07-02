__version__ = (1, 0, 13)


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
# requires: numpy scipy noisereduce soundfile pyrubberband

import logging
import numpy as np
import scipy.io.wavfile as wavfile
import os
import subprocess
import noisereduce as nr
import soundfile
import pyrubberband

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from telethon.tl.types import Message
from io import BytesIO
from pydub import AudioSegment, effects
from .. import loader, utils

logger = logging.getLogger(__name__)


async def getchattype(message):
    chattype = ""
    if message.is_group:
        chattype = "supergroup" if message.is_channel else "smallgroup"
    elif message.is_channel:
        chattype = "channel"
    elif message.is_private:
        chattype = "private"
    return chattype


def represents_nr(nr_lvl):
    try:
        float(nr_lvl)
        return 0.01 <= float(nr_lvl) <= 1
    except ValueError:
        return False


def represents_pitch(pitch_lvl):
    try:
        float(pitch_lvl)
        return -18 <= float(pitch_lvl) <= 18
    except ValueError:
        return False


def represents_speed(s):
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


def represents_gain(s):
    try:
        float(s)
        return -10 <= float(s) <= 10
    except ValueError:
        return False


async def audiohandler(bytes_io_file, fn, fe, new_fe, ac, codec):
    # return bytes_io_file, fn, fe, new_fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    out = fn + new_fe
    if fe != new_fe:
        new_fe_nodot = new_fe[1:]
        with open(fn + fe, "wb") as f:
            f.write(bytes_io_file.getbuffer())
        bytes_io_file.seek(0)
        subprocess.call([
                        "ffmpeg",
                        "-y",
                        "-i", fn + fe,
                        "-c:a", codec,
                        "-f", new_fe_nodot,
                        "-ar", "48000",
                        "-b:a", "320k",
                        "-ac", ac,
                        out,
                        ])
        with open(out, "rb") as f:
            bytes_io_file = BytesIO(f.read())
        bytes_io_file.seek(0)
        _, new_fe = os.path.splitext(out)
    if os.path.exists(out):
        os.remove(out)
    if os.path.exists(fn + fe):
        os.remove(fn + fe)
    return bytes_io_file, fn, new_fe


async def audiopitcher(bytes_io_file, fn, fe, pitch_lvl):
    # return bytes_io_file, fn, fe, pitch_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_shift = pyrubberband.pitch_shift(y, sr, pitch_lvl)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_shift, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    return bytes_io_file, fn, fe


async def audiodenoiser(bytes_io_file, fn, fe, nr_lvl):
    # return bytes_io_file, fn, fe, nr_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rate, data = wavfile.read(bytes_io_file)
    reduced_noise = nr.reduce_noise(y=data, sr=rate, prop_decrease=nr_lvl, stationary=False)
    wavfile.write(bytes_io_file, rate, reduced_noise)
    fn, fe = os.path.splitext(bytes_io_file.name)
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audionormalizer(bytes_io_file, fn, fe, gain):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    rawsound = AudioSegment.from_file(bytes_io_file, format_ext)
    normalizedsound = effects.normalize(rawsound)
    normalizedsound = normalizedsound + gain
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format=format_ext)
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audiospeedup(bytes_io_file, fn, fe, speed):
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    return bytes_io_file, fn, fe


async def dalekvoice(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]

    sound = AudioSegment.from_wav(bytes_io_file)
    sound = sound.set_channels(2)
    sound.export(bytes_io_file, format=format_ext)
    bytes_io_file.seek(0)
    VB = 0.2
    VL = 0.4
    H = 4
    LOOKUP_SAMPLES = 1024
    MOD_F = 50

    def diode_lookup(n_samples):
        result = np.zeros((n_samples,))
        for i in range(n_samples):
            v = float(i - float(n_samples) / 2) / (n_samples / 2)
            v = abs(v)
            if v < VB:
                result[i] = 0
            elif VB < v <= VL:
                result[i] = H * ((v - VB)**2) / (2 * VL - 2 * VB)
            else:
                result[i] = H * v - H * VL + (H * (VL - VB)**2) / (2 * VL - 2 * VB)
        return result

    rate, data = wavfile.read(bytes_io_file)
    data = data[:, 1]
    scaler = np.max(np.abs(data))
    data = data.astype(np.float) / scaler
    n_samples = data.shape[0]
    d_lookup = diode_lookup(LOOKUP_SAMPLES)
    diode = Waveshaper(d_lookup)
    tone = np.arange(n_samples)
    tone = np.sin(2 * np.pi * tone * MOD_F / rate)
    tone = tone * 0.5
    tone2 = tone.copy()
    data2 = data.copy()
    tone = -tone + data2
    data = data + tone2
    data = diode.transform(data) + diode.transform(-data)
    tone = diode.transform(tone) + diode.transform(-tone)
    result = data - tone
    result /= np.max(np.abs(result))
    result *= scaler
    wavfile.write(bytes_io_file, rate, result.astype(np.int16))
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


class Waveshaper():
    def __init__(self, curve):
        self.curve = curve
        self.n_bins = self.curve.shape[0]

    def transform(self, samples):
        # normalize to 0 < samples < 2
        max_val = np.max(np.abs(samples))
        if max_val >= 1.0:
            result = samples / np.max(np.abs(samples)) + 1.0
        else:
            result = samples + 1.0
        result = result * (self.n_bins - 1) / 2
        return self.curve[result.astype(np.int)]


@loader.tds
class ApodiktumVoiceToolsMod(loader.Module):
    """
    Change, pitch, enhance your Voice. Also includes optional automatic modes.
    """
    strings = {
        "name": "Apo VoiceTools",
        "developer": "@anon97945",
        "_cfg_gain_lvl": "Set the desired volume gain level for auto normalize.",
        "_cfg_nr_lvl": "Set the desired noisereduction level.",
        "_cfg_pitch_lvl": "Set the desired pitch level for auto pitch.",
        "_cfg_speed_lvl": "Set the desired speed level for auto speed.",
        "audiodenoiser_txt": "<b>[VoiceTools] Background noise is being removed.</b>",
        "audiohandler_txt": "<b>[VoiceTools] Audio is being transcoded.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Audiovolume is being changed.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": "<b>[VoiceTools]</b> Current AutoVoiceTools in this Chat are:\n\n{}",
        "dalek_start": "<b>[VoiceTools]</b> Auto DalekVoice activated.",
        "dalek_stopped": "<b>[VoiceTools]</b> Auto DalekVoice deactivated.",
        "dalekvoice_txt": "<b>[VoiceTools] Dalek Voice is being applied.</b>",
        "downloading": "<b>[VoiceTools] Message is being downloaded...</b>",
        "error_file": "<b>[VoiceTools]</b> No file in the reply detected.",
        "gain_start": "<b>[VoiceTools]</b> Auto VolumeGain activated.",
        "gain_stopped": "<b>[VoiceTools]</b> Auto VolumeGain deactivated.",
        "makewaves_txt": "<b>[VoiceTools] Speech waves are being applied.</b>",
        "no_nr": "<b>[VoiceTools]</b> Your input was an unsupported noise reduction level.",
        "no_pitch": "<b>[VoiceTools]</b> Your input was an unsupported pitch level.",
        "no_speed": "<b>[VoiceTools]</b> Your input was an unsupported speed level.",
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer activated.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deactivated.",
        "nr_level": "<b>[VoiceTools]</b> Noise reduction level set to {}.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer activated.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deactivated.",
        "pitch_level": "<b>[VoiceTools]</b> Pitch level set to {}.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch activated.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deactivated.",
        "pitch_txt": "<b>[VoiceTools] Pitch is being applied.</b>",
        "speed_start": "<b>[VoiceTools]</b> Auto VoiceSpeed activated.",
        "speed_stopped": "<b>[VoiceTools]</b> Auto VoiceSpeed deactivated.",
        "speed_txt": "<b>[VoiceTools] Speed is being applied.</b>",
        "uploading": "<b>[VoiceTools] File is uploading.</b>",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice activated.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deactivated.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deactivated.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_de = {
        "_cfg_gain_lvl": "Stellen Sie den gewünschten Lautstärkepegel für die automatische Normalisierung ein.",
        "_cfg_nr_lvl": "Stellen Sie den gewünschten Rauschunterdrückungspegel ein.",
        "_cfg_pitch_lvl": "Stellen Sie den gewünschten Tonhöhenpegel für die automatische Tonhöheneinstellung ein.",
        "_cfg_speed_lvl": "Stellen Sie die gewünschte Geschwindigkeitsstufe für die automatische Geschwindigkeit ein.",
        "_cmd_doc_cvoicetoolscmd": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "audiodenoiser_txt": "<b>[VoiceTools] Die Hintergrundgeräusche werden entfernt.</b>",
        "audiohandler_txt": "<b>[VoiceTools] Der Ton wird transkodiert.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Das Audiovolumen wird angepasst.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": "<b>[VoiceTools]</b> Aktuelle AutoVoiceTools in diesem Chat sind:\n\n{}",
        "dalek_start": "<b>[VoiceTools]</b> Auto DalekVoice aktiviert.",
        "dalek_stopped": "<b>[VoiceTools]</b> Auto DalekVoice ist deaktiviert.",
        "dalekvoice_txt": "<b>[VoiceTools] Die Dalek-Stimme wird angewendet.</b>",
        "downloading": "<b>[VoiceTools] Die Nachricht wird heruntergeladen...</b>",
        "error_file": "<b>[VoiceTools]</b> Keine Datei in der Antwort gefunden.",
        "gain_start": "<b>[VoiceTools]</b> Auto VolumeGain aktiviert.",
        "gain_stopped": "<b>[VoiceTools]</b> Auto VolumeGain deaktiviert.",
        "makewaves_txt": "<b>[VoiceTools] Es werden Sprachwellen erstellt.</b>",
        "no_nr": "<b>[VoiceTools]</b> Ihre Eingabe war ein nicht unterstützter Rauschunterdrückungspegel.",
        "no_pitch": "<b>[VoiceTools]</b> Ihre Eingabe war ein nicht unterstützter Tonhöhenpegel.",
        "no_speed": "<b>[VoiceTools]</b> Ihre Eingabe war eine nicht unterstützte Geschwindigkeitswert.",
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer aktiviert.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deaktiviert.",
        "nr_level": "<b>[VoiceTools]</b> Rauschunterdrückungspegel auf {} eingestellt.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer aktiviert.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deaktiviert.",
        "pitch_level": "<b>[VoiceTools]</b> Die Tonhöhe ist auf {} eingestellt.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch aktiviert.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deaktiviert.",
        "pitch_txt": "<b>[VoiceTools] Pitch wird angewandt.</b>",
        "speed_start": "<b>[VoiceTools]</b> Auto VoiceSpeed aktiviert.",
        "speed_stopped": "<b>[VoiceTools]</b> Auto VoiceSpeed deaktiviert.",
        "speed_txt": "<b>[VoiceTools] Geschwindigkeit wird angewendet.</b>",
        "uploading": "<b>[VoiceTools] Datei wird hochgeladen.</b>",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice aktiviert.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deaktiviert.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deaktiviert.",
    }

    strings_ru = {
        "_cfg_gain_lvl": "Установите желаемый уровень усиления громкости для автоматического питча. (Высоты тона)",
        "_cfg_nr_lvl": "Установите желаемый уровень шумоподавления.",
        "_cfg_pitch_lvl": "Установите желаемый уровень высоты тона для автонастройки.",
        "_cfg_speed_lvl": "Установите желаемый уровень скорости для автоматической скорости.",
        "_cmd_doc_cvoicetoolscmd": "Это откроет конфиг для модуля.",
        "audiodenoiser_txt": "<b>[VoiceTools] Фоновый шум удаляется.</b>",
        "audiohandler_txt": "<b>[VoiceTools] Аудио перекодируется.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Аудиогромкость изменяется.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": "<b>[VoiceTools]</b> Текущие авто-инструменты для работы с голосом в этом чате:\n\n{}",
        "dalek_start": "<b>[VoiceTools]</b> Активирован автоматический голос «Далека».",
        "dalek_stopped": "<b>[VoiceTools]</b> Деактивирован автоматический голос «Далека».",
        "dalekvoice_txt": "<b>[VoiceTools] Голос «Далека» применяется.</b>",
        "downloading": "<b>[VoiceTools] Сообщение загружается...</b>",
        "error_file": "<b>[VoiceTools]</b> Не обнаружен файл в реплае.",
        "gain_start": "<b>[VoiceTools]</b> Активировано автоматическое усиление громкости.",
        "gain_stopped": "<b>[VoiceTools]</b> Деактивировано автоматическое усиление громкости.",
        "makewaves_txt": "<b>[VoiceTools] Речевые волны применяются.</b>",
        "no_nr": "<b>[VoiceTools]</b> Ваш ввод является неподдерживаемым уровнем шумоподавления.",
        "no_pitch": "<b>[VoiceTools]</b> Ваш ввод является неподдерживаемым уровнем высоты тона.",
        "no_speed": "<b>[VoiceTools]</b> Ваш ввод является неподдерживаемым уровнем скорости звука.",
        "norm_start": "<b>[VoiceTools]</b> Активирована автонормализация голоса.",
        "norm_stopped": "<b>[VoiceTools]</b> Деактивирована автонормализация голоса.",
        "nr_level": "<b>[VoiceTools]</b> Уровень шумоподавления установлен на {}.",
        "nr_start": "<b>[VoiceTools]</b> Активировано автоматическое усиление голоса.",
        "nr_stopped": "<b>[VoiceTools]</b> Деактивировано автоматическое усиление голоса.",
        "pitch_level": "<b>[VoiceTools]</b> Уровень высоты тона установлен на {}.",
        "pitch_start": "<b>[VoiceTools]</b> Активирован авто-питч. (Высота тона)",
        "pitch_stopped": "<b>[VoiceTools]</b> Деактивирован авто-питч. (Высота тона)",
        "pitch_txt": "<b>[VoiceTools] Высота тона применяется.</b>",
        "speed_start": "<b>[VoiceTools]</b> Активировано автоускорение голоса.",
        "speed_stopped": "<b>[VoiceTools]</b> Деактивировано автоускорение голоса.",
        "speed_txt": "<b>[VoiceTools] Скорость применяется.</b>",
        "uploading": "<b>[VoiceTools] Файл загружается.</b>",
        "vcanon_start": "<b>[VoiceTools]</b> Активирован автоматический «анонимный голос»",
        "vcanon_stopped": "<b>[VoiceTools]</b> Деактивирован автоматический «анонимный голос»",
        "vtauto_stopped": "<b>[VoiceTools]</b> Деактивированы все автоматические инструменты для работы с голосом.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "pitch_lvl",
                "4",
                doc=lambda: self.strings("_cfg_pitch_lvl"),
                validator=loader.validators.Float(minimum=-18, maximum=18),
            ),
            loader.ConfigValue(
                "nr_lvl",
                "0.85",
                doc=lambda: self.strings("_cfg_nr_lvl"),
                validator=loader.validators.Float(minimum=0.01, maximum=1),
            ),
            loader.ConfigValue(
                "gain_lvl",
                "1.5",
                doc=lambda: self.strings("_cfg_gain_lvl"),
                validator=loader.validators.Float(minimum=-10, maximum=10),
            ),
            loader.ConfigValue(
                "speed_lvl",
                "1",
                doc=lambda: self.strings("_cfg_speed_lvl"),
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
        self._id = (await client.get_me(True)).user_id
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

    def _strings(self, string, chat_id):
        languages = {"de_chats": self.strings_de, "ru_chats": self.strings_ru}
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

    async def get_media(self, message: Message, inline_msg, silent):
        reply = await message.get_reply_message()
        m = None
        if reply and reply.media:
            m = reply
        elif message.media:
            m = message
        else:
            return
        if not m:
            file = BytesIO(bytes(reply.raw_text, "utf-8"))
        else:
            file = (
                BytesIO((await self.fast_download(m.document)).getvalue())
                if silent
                else BytesIO(
                    (
                        await self.fast_download(
                            m.document, message_object=inline_msg
                        )
                    ).getvalue()
                )
            )
        file.seek(0)
        return file

    async def cvoicetoolscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def vtdalekcmd(self, message):
        """reply to a file to change the voice"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        nr_lvl = self.config["nr_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt"))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("dalekvoice_txt"))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtanoncmd(self, message):
        """reply to a file to change the voice into anonymous"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = BytesIO()
        file.name = replymsg.file.name
        nr_lvl = 0.8
        pitch_lvl = -4.5
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt"))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("dalekvoice_txt"))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        file, fn, fe = await audiopitcher(file, fn, fe, pitch_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtpitchcmd(self, message):
        """reply to a file to pitch voice
          - Example: .vtpitch 12
            Possible values between -18 and 18"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        pitch_lvl = utils.get_args_raw(message)
        if not represents_pitch(pitch_lvl):
            return await utils.answer(message, self._strings("no_pitch", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("pitch_txt"))
        file, fn, fe = await audiopitcher(file, fn, fe, float(pitch_lvl))
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtspeedcmd(self, message):
        """reply to a file to increase speed and reduce length
          - Example: .vtspeed 1.5
            Possible values between 0.25 - 3"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        speed_lvl = utils.get_args_raw(message)
        if not represents_speed(speed_lvl):
            return await utils.answer(message, self._strings("no_speed", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("speed_txt"))
        file, fn, fe = await audiospeedup(file, fn, fe, float(speed_lvl))
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtgaincmd(self, message):
        """reply to a file to change the volume
          - Example: .vtgain 1
            Possible values between -10 - 10"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        gain_lvl = utils.get_args_raw(message)
        if not represents_gain(gain_lvl):
            return await utils.answer(message, self._strings("no_speed", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtenhcmd(self, message):
        """reply to a file to enhance voice quality with
         - Volume normalize
         - Background NoiseReduce (set your noisereduce level before)"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        nr_lvl = self.config["nr_lvl"]
        gain_lvl = 0
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt"))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtnormcmd(self, message):
        """reply to a file to normalize volume"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiovolume_txt"))
        file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        else:
            inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
            file, fn, fe = await audiohandler(file, fn, fe, ext, "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtmp3cmd(self, message: Message):
        """reply to a file to convert it to mp3"""
        chatid = utils.get_chat_id(message)
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=False)
        await inline_msg.delete()

    async def vtspeechcmd(self, message):
        """reply to a file to convert it to speech"""
        chatid = utils.get_chat_id(message)
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(message, self._strings("error_file", utils.get_chat_id(message)))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading"), reply_markup={"text": "\u0020\u2800", "callback": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt"))
        file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading"))
        await message.client.send_file(chatid, file, voice_note=True)
        await inline_msg.delete()

    async def vtautodalekcmd(self, message):
        """Turns on AutoDalekVoice for your own Voicemessages in the chat"""
        dalek_chats = self._db.get(__name__, "dalek_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in dalek_chats:
            dalek_chats.append(chatid_str)
            self._db.set(__name__, "dalek_watcher", dalek_chats)
            await utils.answer(message, self._strings("dalek_start", utils.get_chat_id(message)))
        else:
            dalek_chats.remove(chatid_str)
            self._db.set(__name__, "dalek_watcher", dalek_chats)
            await utils.answer(message, self._strings("dalek_stopped", utils.get_chat_id(message)))

    async def vtautoanoncmd(self, message):
        """Turns on AutoAnonVoice for your own Voicemessages in the chat"""
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in vcanon_chats:
            vcanon_chats.append(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self._strings("vcanon_start", utils.get_chat_id(message)))
        else:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self._strings("vcanon_stopped", utils.get_chat_id(message)))

    async def vtautonrcmd(self, message):
        """Turns on AutoNoiseReduce for your own Voicemessages in the chat"""
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in nr_chats:
            nr_chats.append(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self._strings("nr_start", utils.get_chat_id(message)))
        else:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self._strings("nr_stopped", utils.get_chat_id(message)))

    async def vtautonormcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in norm_chats:
            norm_chats.append(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self._strings("norm_start", utils.get_chat_id(message)))
        else:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self._strings("norm_stopped", utils.get_chat_id(message)))

    async def vtautospeedcmd(self, message):
        """Turns on AutoSpeed for your own Voicemessages in the chat"""
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in speed_chats:
            speed_chats.append(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
            await utils.answer(message, self._strings("speed_start", utils.get_chat_id(message)))
        else:
            speed_chats.remove(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
            await utils.answer(message, self._strings("speed_stopped", utils.get_chat_id(message)))

    async def vtautopitchcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in pitch_chats:
            pitch_chats.append(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self._strings("pitch_start", utils.get_chat_id(message)))
        else:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self._strings("pitch_stopped", utils.get_chat_id(message)))

    async def vtautogaincmd(self, message):
        """Turns on AutoVolumeGain for your own Voicemessages in the chat"""
        gain_chats = self._db.get(__name__, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in gain_chats:
            gain_chats.append(chatid_str)
            self._db.set(__name__, "gain_watcher", gain_chats)
            await utils.answer(message, self._strings("gain_start", utils.get_chat_id(message)))
        else:
            gain_chats.remove(chatid_str)
            self._db.set(__name__, "gain_watcher", gain_chats)
            await utils.answer(message, self._strings("gain_stopped", utils.get_chat_id(message)))

    async def vtautocmd(self, message):
        """Displays all enabled AutoVoice settings in the chat"""
        current = ""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        dalek_chats = self._db.get(__name__, "dalek_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        gain_chats = self._db.get(__name__, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str in vcanon_chats:
            current = current + self.strings("auto_anon_on") + "\n"
        else:
            current = current + self.strings("auto_anon_off") + "\n"
        if chatid_str in dalek_chats:
            current = current + self.strings("auto_dalek_on") + "\n"
        else:
            current = current + self.strings("auto_dalek_off") + "\n"
        if chatid_str in pitch_chats:
            current = current + self.strings("auto_pitch_on") + "\n"
        else:
            current = current + self.strings("auto_pitch_off") + "\n"
        if chatid_str in speed_chats:
            current = current + self.strings("auto_speed_on") + "\n"
        else:
            current = current + self.strings("auto_speed_off") + "\n"
        if chatid_str in norm_chats:
            current = current + self.strings("auto_norm_on") + "\n"
        else:
            current = current + self.strings("auto_norm_off") + "\n"
        if chatid_str in gain_chats:
            current = current + self.strings("auto_gain_on") + "\n"
        else:
            current = current + self.strings("auto_gain_off") + "\n"
        if chatid_str in nr_chats:
            current = current + self.strings("auto_nr_on") + "\n"
        else:
            current = current + self.strings("auto_nr_off") + "\n"
        return await utils.answer(message, self._strings("current_auto", utils.get_chat_id(message)).format(current))

    async def vtautostopcmd(self, message):
        """Turns off AutoVoice for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        dalek_chats = self._db.get(__name__, "dalek_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        gain_chats = self._db.get(__name__, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str in norm_chats:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
        if chatid_str in nr_chats:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
        if chatid_str in dalek_chats:
            dalek_chats.remove(chatid_str)
            self._db.set(__name__, "dalek_watcher", dalek_chats)
        if chatid_str in pitch_chats:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
        if chatid_str in vcanon_chats:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
        if chatid_str in speed_chats:
            speed_chats.remove(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
        if chatid_str in gain_chats:
            gain_chats.remove(chatid_str)
            self._db.set(__name__, "gain_watcher", gain_chats)
        await utils.answer(message, self._strings("vtauto_stopped", utils.get_chat_id(message)))

    async def watcher(self, message: Message):
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        dalek_chats = self._db.get(__name__, "dalek_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        gain_chats = self._db.get(__name__, "gain_watcher", [])
        chat = await message.get_chat()
        chattype = await getchattype(message)
        if (not isinstance(message, Message)
                or chatid_str not in nr_chats
                and chatid_str not in dalek_chats
                and chatid_str not in norm_chats
                and chatid_str not in pitch_chats
                and chatid_str not in vcanon_chats
                and chatid_str not in speed_chats
                and chatid_str not in gain_chats):
            return
        if (chattype != "channel"
                and message.sender_id != self._id
                or chattype == "channel"
                and not chat.admin_rights.delete_messages):
            return
        if not message.voice or message.via_bot or message.forward:
            return
        if message.reply:
            reply = await message.get_reply_message()
        nr_lvl = self.config["nr_lvl"]
        pitch_lvl = self.config["pitch_lvl"]
        speed_lvl = self.config["speed_lvl"]
        gain_lvl = self.config["gain_lvl"]
        if chatid_str in dalek_chats:
            nr_lvl = 0.8
        if chatid_str in vcanon_chats:
            nr_lvl = 0.8
            pitch_lvl = -4.5
        msgs = await message.forward_to(self._id)
        await message.client.delete_messages(chatid, message)
        file = BytesIO()
        file.name = msgs.file.name
        file = await self.get_media(msgs, msgs, True)
        filename = msgs.file.name or "voice"
        ext = msgs.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file.seek(0)
        await message.client.delete_messages(self._id, msgs)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        if chatid_str in nr_chats or chatid_str in vcanon_chats or chatid_str in dalek_chats:
            file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
            file.seek(0)
        if chatid_str in norm_chats or chatid_str in vcanon_chats or chatid_str in dalek_chats or chatid_str in gain_chats:
            file, fn, fe = await audionormalizer(file, fn, fe, gain_lvl)
            file.seek(0)
        if chatid_str in dalek_chats or chatid_str in vcanon_chats:
            file, fn, fe = await dalekvoice(file, fn, fe)
            file.seek(0)
        if chatid_str in pitch_chats or chatid_str in vcanon_chats:
            file, fn, fe = await audiopitcher(file, fn, fe, pitch_lvl)
            file.seek(0)
        if chatid_str in speed_chats:
            file, fn, fe = await audiospeedup(file, fn, fe, speed_lvl)
            file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        if reply:
            await message.client.send_file(chatid, file, voice_note=True, reply_to=reply)
        else:
            await message.client.send_file(chatid, file, voice_note=True)


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
