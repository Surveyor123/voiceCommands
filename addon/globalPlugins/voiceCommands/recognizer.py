# -*- coding: UTF-8 -*-
"""Speech recognition for voice commands: Vosk (through ctypes) plus the Windows waveIn
microphone API. It uses no compiled Python modules, so it does not depend on NVDA's
Python version."""
import array
import ctypes
import json
import math
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

# Automatic stop after silence (see SilenceDetector).
DEFAULT_SILENCE_SECONDS = 1.2  # trailing silence that counts as "the command is finished"
MIN_SILENCE_SECONDS = 0.5
MAX_SILENCE_SECONDS = 5.0
MIN_SPEECH_SECONDS = 0.3  # less voiced audio than this is a click or the beep, not a command
WARMUP_SECONDS = 0.2  # the start beep and the key press are ignored
MIN_LEVEL = 250  # smallest RMS (of 32768) that can count as speech
NOISE_FACTOR = 3.0  # speech must be this many times louder than the background noise


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

	def new_session(self, grammar=None):
		"""A recognition session for one utterance (see Listener)."""
		return VoskSession(self, grammar)

	def close(self):
		if self.m:
			self.v.vosk_model_free(self.m)
			self.m = None


class VoskSession:
	"""Two recognizers listening to the same audio: one restricted to the command grammar
	(accurate for commands) and one free-form with n-best alternatives (needed for names
	that are not in the model vocabulary).

	Every engine offers the same three methods: accept(pcm16 bytes), finish() and close(),
	so the Listener does not need to know which engine it drives."""

	def __init__(self, model, grammar):
		self.v = model.v
		self.grammar_rec = model.new_recognizer(grammar) if grammar else None
		self.free_rec = model.new_recognizer(None, ALTERNATIVES)
		self.recognizers = [r for r in (self.grammar_rec, self.free_rec) if r]

	def accept(self, data):
		for r in self.recognizers:
			self.v.vosk_recognizer_accept_waveform(r, data, len(data))

	def finish(self):
		"""(grammar text, [free-form alternatives])."""
		grammar_text = _read_result(self.v, self.grammar_rec).get("text", "") if self.grammar_rec else ""
		free = _read_result(self.v, self.free_rec)
		if "alternatives" in free:
			alternatives = [a.get("text", "").strip() for a in free["alternatives"]]
		else:
			alternatives = [free.get("text", "").strip()]
		return grammar_text, alternatives

	def close(self):
		for r in self.recognizers:
			self.v.vosk_recognizer_free(r)
		self.recognizers = []


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


class SilenceDetector:
	"""Tells when the user has finished speaking: some speech was heard, then it was quiet for
	`silence_seconds`. The background noise is estimated from the quietest tenth of what was
	heard so far, so a noisy room or a quiet microphone needs no setting, and it works even when
	the user starts speaking at once. Feed it the same 16-bit mono chunks the recognizer gets."""

	HISTORY = 300  # chunks kept (30 s of 100 ms)

	def __init__(self, silence_seconds=DEFAULT_SILENCE_SECONDS):
		self.silence_seconds = silence_seconds
		self.levels = []
		self.skip = WARMUP_SECONDS
		self.chunk = 0.0

	@staticmethod
	def level(data):
		pcm = array.array("h")
		pcm.frombytes(data[:len(data) - len(data) % 2])
		if not pcm:
			return 0.0
		return math.sqrt(sum(v * v for v in pcm) / len(pcm))

	def feed(self, data):
		"""True when the command can be considered finished."""
		seconds = len(data) / 2.0 / SAMPLE_RATE
		if self.skip > 0:
			self.skip -= seconds
			return False
		self.chunk = seconds
		self.levels.append(self.level(data))
		del self.levels[:-self.HISTORY]
		floor = sorted(self.levels)[len(self.levels) // 10]
		threshold = max(MIN_LEVEL, floor * NOISE_FACTOR)
		loud = [level > threshold for level in self.levels]
		quiet_run = 0
		for flag in reversed(loud):
			if flag:
				break
			quiet_run += 1
		return sum(loud) * seconds >= MIN_SPEECH_SECONDS and quiet_run * seconds >= self.silence_seconds


class Listener(threading.Thread):
	"""start() opens the microphone; after stop() it calls result_cb(grammar_text, alternatives).

	With silence_seconds set, it stops by itself when the user has spoken and then stayed quiet for
	that long (the same as calling stop()), and calls silence_cb() first.

	The recognition itself is done by a session of the model (model.new_session), so the same
	microphone code serves Vosk and the other speech engines."""

	def __init__(self, model, grammar, result_cb, error_cb, silence_seconds=0, silence_cb=None):
		super().__init__(daemon=True)
		self.model = model
		self.grammar = grammar
		self.result_cb = result_cb
		self.error_cb = error_cb
		self.silence_seconds = silence_seconds
		self.silence_cb = silence_cb
		self._stop_event = threading.Event()

	def stop(self):
		self._stop_event.set()

	def run(self):
		session = None
		hwi = ctypes.c_void_p()
		opened = False
		headers = []
		try:
			session = self.model.new_session(self.grammar)
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

			detector = SilenceDetector(self.silence_seconds) if self.silence_seconds else None

			def process(header, buf):
				count = header.dwBytesRecorded
				if count:
					data = ctypes.string_at(buf, count)
					session.accept(data)
					if detector and not self._stop_event.is_set() and detector.feed(data):
						self._stop_event.set()
						if self.silence_cb:
							try:
								self.silence_cb()
							except Exception:
								log.exception("Silence callback error")

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
			grammar_text, alternatives = session.finish()
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
				if session:
					session.close()
			except Exception:
				log.exception("Cleanup error")
