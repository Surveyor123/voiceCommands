# -*- coding: UTF-8 -*-
"""Speech recognition for voice commands: Vosk (through ctypes) plus the Windows waveIn
microphone API. It uses no compiled Python modules, so it does not depend on NVDA's
Python version."""
import ctypes
import json
import os
import threading
import time
from ctypes import wintypes

import addonHandler
from logHandler import log

addonHandler.initTranslation()

SAMPLE_RATE = 16000
BUFFER_BYTES = 3200  # 100 ms of 16-bit mono audio
WHDR_DONE = 0x1
CALLBACK_NULL = 0
WAVE_MAPPER = 0xFFFFFFFF
WAVE_FORMAT_PCM = 1
ALTERNATIVES = 5  # n-best size of the free (grammar-less) recognizer


# ---------------------------------------------------------------- Vosk
_vosk = None


def _load_vosk():
    global _vosk
    if _vosk:
        return _vosk
    lib_dir = os.path.join(os.path.dirname(__file__), "lib")
    try:
        os.add_dll_directory(lib_dir)
    except Exception:
        pass
    for name in ("libwinpthread-1.dll", "libgcc_s_seh-1.dll", "libstdc++-6.dll"):
        ctypes.CDLL(os.path.join(lib_dir, name))
    v = ctypes.CDLL(os.path.join(lib_dir, "libvosk.dll"))
    v.vosk_model_new.argtypes = [ctypes.c_char_p]
    v.vosk_model_new.restype = ctypes.c_void_p
    v.vosk_model_free.argtypes = [ctypes.c_void_p]
    v.vosk_recognizer_new.argtypes = [ctypes.c_void_p, ctypes.c_float]
    v.vosk_recognizer_new.restype = ctypes.c_void_p
    v.vosk_recognizer_new_grm.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_char_p]
    v.vosk_recognizer_new_grm.restype = ctypes.c_void_p
    v.vosk_model_find_word.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    v.vosk_model_find_word.restype = ctypes.c_int
    v.vosk_recognizer_free.argtypes = [ctypes.c_void_p]
    v.vosk_recognizer_accept_waveform.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    v.vosk_recognizer_accept_waveform.restype = ctypes.c_int
    v.vosk_recognizer_final_result.argtypes = [ctypes.c_void_p]
    v.vosk_recognizer_final_result.restype = ctypes.c_char_p
    v.vosk_set_log_level.argtypes = [ctypes.c_int]
    v.vosk_set_log_level(-1)
    try:
        v.vosk_recognizer_set_max_alternatives.argtypes = [ctypes.c_void_p, ctypes.c_int]
    except AttributeError:
        pass  # older libvosk: only the single best result is available
    _vosk = v
    return v


def find_model_dir(root):
    """Looks for a Vosk model under root (up to 5 levels deep).
    New layout: am/final.mdl. Old (flat) layout: final.mdl directly in the folder."""
    if not os.path.isdir(root):
        return None
    root = os.path.normpath(root)
    for path, folders, files in os.walk(root):
        if path[len(root):].count(os.sep) > 5:
            folders[:] = []
            continue
        if os.path.isfile(os.path.join(path, "am", "final.mdl")):
            return path
        if "final.mdl" in files and ("ivector" in folders or "mfcc.conf" in files):
            return path
    return None


def folder_summary(root, limit=15):
    """For troubleshooting: lists the first entries under root."""
    try:
        result = []
        for path, folders, files in os.walk(root):
            for name in folders + files:
                result.append(os.path.relpath(os.path.join(path, name), root))
                if len(result) >= limit:
                    return result
        return result
    except Exception as e:
        return ["unreadable: %s" % e]


class Model:
    def __init__(self, path):
        self.v = _load_vosk()
        self.m = self.v.vosk_model_new(path.encode("utf-8"))
        if not self.m:
            # Translators: Error shown when the Vosk speech recognition model cannot be loaded. {path} is the model folder.
            raise RuntimeError(_("Could not load the Vosk model: {path}").format(path=path))

    def find_unknown_words(self, words):
        """Words that are not in the model's vocabulary."""
        return [w for w in words if self.v.vosk_model_find_word(self.m, w.encode("utf-8")) < 0]

    def new_recognizer(self, grammar=None, alternatives=0):
        if grammar:
            r = self.v.vosk_recognizer_new_grm(self.m, ctypes.c_float(SAMPLE_RATE), grammar.encode("utf-8"))
        else:
            r = self.v.vosk_recognizer_new(self.m, ctypes.c_float(SAMPLE_RATE))
        if not r:
            # Translators: Error shown when the speech recognizer cannot be created.
            raise RuntimeError(_("Could not create the speech recognizer"))
        if alternatives and hasattr(self.v, "vosk_recognizer_set_max_alternatives"):
            self.v.vosk_recognizer_set_max_alternatives(r, int(alternatives))
        return r

    def close(self):
        if self.m:
            self.v.vosk_model_free(self.m)
            self.m = None


# ---------------------------------------------------------------- waveIn
class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", wintypes.WORD), ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD), ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD), ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


class WAVEHDR(ctypes.Structure):
    pass


WAVEHDR._fields_ = [
    ("lpData", ctypes.c_void_p), ("dwBufferLength", wintypes.DWORD),
    ("dwBytesRecorded", wintypes.DWORD), ("dwUser", ctypes.c_size_t),
    ("dwFlags", wintypes.DWORD), ("dwLoops", wintypes.DWORD),
    ("lpNext", ctypes.c_void_p), ("reserved", ctypes.c_size_t),
]

_winmm = ctypes.WinDLL("winmm")
_winmm.waveInOpen.argtypes = [ctypes.POINTER(ctypes.c_void_p), wintypes.UINT,
                              ctypes.POINTER(WAVEFORMATEX), ctypes.c_size_t,
                              ctypes.c_size_t, wintypes.DWORD]
for _name in ("waveInPrepareHeader", "waveInAddBuffer", "waveInUnprepareHeader"):
    getattr(_winmm, _name).argtypes = [ctypes.c_void_p, ctypes.POINTER(WAVEHDR), wintypes.UINT]
for _name in ("waveInStart", "waveInStop", "waveInReset", "waveInClose"):
    getattr(_winmm, _name).argtypes = [ctypes.c_void_p]
for _name in ("waveInOpen", "waveInPrepareHeader", "waveInAddBuffer", "waveInUnprepareHeader",
              "waveInStart", "waveInStop", "waveInReset", "waveInClose"):
    getattr(_winmm, _name).restype = wintypes.UINT


def _read_result(v, recognizer):
    raw = v.vosk_recognizer_final_result(recognizer)
    return json.loads(raw.decode("utf-8")) if raw else {}


class Listener(threading.Thread):
    """start() opens the microphone; after stop() it calls result_cb(grammar_text, alternatives).

    Two recognizers listen to the same audio: one restricted to the command grammar
    (accurate for commands) and one free-form with n-best alternatives (needed for names
    that are not in the model vocabulary)."""

    def __init__(self, model, grammar, result_cb, error_cb):
        super().__init__(daemon=True)
        self.model = model
        self.grammar = grammar
        self.result_cb = result_cb
        self.error_cb = error_cb
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        v = self.model.v
        grammar_rec = None  # grammar-restricted recognizer (may stay None)
        free_rec = None
        hwi = ctypes.c_void_p()
        opened = False
        headers = []
        try:
            if self.grammar:
                grammar_rec = self.model.new_recognizer(self.grammar)
            free_rec = self.model.new_recognizer(None, ALTERNATIVES)
            recognizers = [r for r in (grammar_rec, free_rec) if r]
            wfx = WAVEFORMATEX(WAVE_FORMAT_PCM, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16, 0)
            if _winmm.waveInOpen(ctypes.byref(hwi), WAVE_MAPPER, ctypes.byref(wfx), 0, 0, CALLBACK_NULL):
                # Translators: Error shown when the microphone cannot be opened.
                raise RuntimeError(_("Could not open the microphone"))
            opened = True
            buffers = []
            for _index in range(5):
                buf = ctypes.create_string_buffer(BUFFER_BYTES)
                header = WAVEHDR()
                header.lpData = ctypes.cast(buf, ctypes.c_void_p).value
                header.dwBufferLength = BUFFER_BYTES
                _winmm.waveInPrepareHeader(hwi, ctypes.byref(header), ctypes.sizeof(header))
                _winmm.waveInAddBuffer(hwi, ctypes.byref(header), ctypes.sizeof(header))
                buffers.append(buf)
                headers.append(header)
            _winmm.waveInStart(hwi)

            def process(header, buf):
                count = header.dwBytesRecorded
                if count:
                    data = ctypes.string_at(buf, count)
                    for r in recognizers:
                        v.vosk_recognizer_accept_waveform(r, data, len(data))

            while not self._stop_event.is_set():
                for header, buf in zip(headers, buffers):
                    if header.dwFlags & WHDR_DONE:
                        process(header, buf)
                        header.dwBytesRecorded = 0
                        _winmm.waveInAddBuffer(hwi, ctypes.byref(header), ctypes.sizeof(header))
                time.sleep(0.02)

            _winmm.waveInStop(hwi)
            _winmm.waveInReset(hwi)
            for header, buf in zip(headers, buffers):
                if header.dwFlags & WHDR_DONE:
                    process(header, buf)
            grammar_text = _read_result(v, grammar_rec).get("text", "") if grammar_rec else ""
            free = _read_result(v, free_rec)
            if "alternatives" in free:
                alternatives = [a.get("text", "").strip() for a in free["alternatives"]]
            else:
                alternatives = [free.get("text", "").strip()]
            self.result_cb(grammar_text, [a for a in alternatives if a])
        except Exception as e:
            log.exception("Speech recognition error")
            self.error_cb(str(e))
        finally:
            try:
                if opened:
                    for header in headers:
                        _winmm.waveInUnprepareHeader(hwi, ctypes.byref(header), ctypes.sizeof(header))
                    _winmm.waveInClose(hwi)
                for r in (grammar_rec, free_rec):
                    if r:
                        v.vosk_recognizer_free(r)
            except Exception:
                log.exception("Cleanup error")
