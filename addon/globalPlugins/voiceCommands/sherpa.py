# -*- coding: UTF-8 -*-
"""Second speech engine: streaming transducer models (the Turkish "turkish-stt-66m-v2" of mihuai and the
other languages listed in download.SHERPA_MODELS) run with the sherpa-onnx C library, through ctypes like Vosk (no compiled Python modules, so it does not depend
on NVDA's Python version).

A model is free-form: it cannot be restricted to a grammar. The command decision in __init__.py
already handles that case (the grammar text is empty), matching the recognized text by words and by
sound. The runtime DLLs and the model files are downloaded on request (see download.py)."""
import array
import ctypes
import json
import os

import addonHandler
from logHandler import log

from . import storage

addonHandler.initTranslation()

SAMPLE_RATE = 16000
TAIL_SECONDS = 0.5	# silence appended at the end so the model emits its last words
RUNTIME_DLLS = ("onnxruntime.dll", "onnxruntime_providers_shared.dll", "sherpa-onnx-c-api.dll")


def model_path(folder):
	return os.path.join(storage.model_dir(), folder)


def runtime_dir():
	return os.path.join(storage.config_dir(), "sherpa-runtime")


def _runtime_folders():
	"""Where the DLLs may be: next to the add-on (bundled) or in the user's configuration (downloaded)."""
	return [os.path.join(os.path.dirname(__file__), "lib", "sherpa"), runtime_dir()]


def find_runtime():
	for folder in _runtime_folders():
		if all(os.path.isfile(os.path.join(folder, name)) for name in RUNTIME_DLLS):
			return folder
	return None


def _pick(names, prefix):
	"""The int8 file is preferred (smaller and faster), then any other file of that kind."""
	matches = sorted(n for n in names if n.startswith(prefix) and n.endswith(".onnx"))
	return next((n for n in matches if ".int8." in n), matches[0] if matches else None)


def model_files(path):
	"""{"encoder", "decoder", "joiner", "tokens"} file names in a model folder, or None when one is missing."""
	try:
		names = os.listdir(path)
	except OSError:
		return None
	files = {"encoder": _pick(names, "encoder"), "decoder": _pick(names, "decoder"),
			 "joiner": _pick(names, "joiner"), "tokens": "tokens.txt" if "tokens.txt" in names else None}
	return files if all(files.values()) else None


def find_model(folder):
	"""The path of the installed model in the given folder name, otherwise None."""
	path = model_path(folder)
	return path if model_files(path) else None


def is_installed(folder):
	return bool(find_runtime() and find_model(folder))


# --------------------------------------------------------------- C API
# The structures follow sherpa-onnx v2.0.1 (c-api.h). A different version can lay them out
# differently, which is why download.py installs exactly that version.
class _Transducer(ctypes.Structure):
	_fields_ = [("encoder", ctypes.c_char_p), ("decoder", ctypes.c_char_p), ("joiner", ctypes.c_char_p)]


class _Paraformer(ctypes.Structure):
	_fields_ = [("encoder", ctypes.c_char_p), ("decoder", ctypes.c_char_p)]


class _SingleModel(ctypes.Structure):
	_fields_ = [("model", ctypes.c_char_p)]


class _ModelConfig(ctypes.Structure):
	_fields_ = [
		("transducer", _Transducer), ("paraformer", _Paraformer), ("zipformer2_ctc", _SingleModel),
		("tokens", ctypes.c_char_p), ("num_threads", ctypes.c_int32), ("provider", ctypes.c_char_p),
		("debug", ctypes.c_int32), ("model_type", ctypes.c_char_p), ("modeling_unit", ctypes.c_char_p),
		("bpe_vocab", ctypes.c_char_p), ("tokens_buf", ctypes.c_char_p), ("tokens_buf_size", ctypes.c_int32),
		("nemo_ctc", _SingleModel), ("t_one_ctc", _SingleModel),
	]


class _FeatureConfig(ctypes.Structure):
	_fields_ = [("sample_rate", ctypes.c_int32), ("feature_dim", ctypes.c_int32)]


class _CtcFstDecoder(ctypes.Structure):
	_fields_ = [("graph", ctypes.c_char_p), ("max_active", ctypes.c_int32)]


class _Homophone(ctypes.Structure):
	_fields_ = [("dict_dir", ctypes.c_char_p), ("lexicon", ctypes.c_char_p), ("rule_fsts", ctypes.c_char_p)]


class _RecognizerConfig(ctypes.Structure):
	_fields_ = [
		("feat_config", _FeatureConfig), ("model_config", _ModelConfig),
		("decoding_method", ctypes.c_char_p), ("max_active_paths", ctypes.c_int32),
		("enable_endpoint", ctypes.c_int32), ("rule1_min_trailing_silence", ctypes.c_float),
		("rule2_min_trailing_silence", ctypes.c_float), ("rule3_min_utterance_length", ctypes.c_float),
		("hotwords_file", ctypes.c_char_p), ("hotwords_score", ctypes.c_float),
		("ctc_fst_decoder_config", _CtcFstDecoder), ("rule_fsts", ctypes.c_char_p),
		("rule_fars", ctypes.c_char_p), ("blank_penalty", ctypes.c_float),
		("hotwords_buf", ctypes.c_char_p), ("hotwords_buf_size", ctypes.c_int32), ("hr", _Homophone),
	]


_lib = None


def _load_library():
	global _lib
	if _lib:
		return _lib
	folder = find_runtime()
	if not folder:
		# Translators: Error shown when the sherpa-onnx runtime files are missing.
		raise RuntimeError(_("The speech engine files are missing"))
	try:
		os.add_dll_directory(folder)
	except Exception:
		pass
	# onnxruntime first: the sherpa library depends on it, and the bundled copy must win over any other.
	for name in RUNTIME_DLLS[:-1]:
		ctypes.CDLL(os.path.join(folder, name))
	lib = ctypes.CDLL(os.path.join(folder, "sherpa-onnx-c-api.dll"))
	p = ctypes.c_void_p
	lib.SherpaOnnxCreateOnlineRecognizer.argtypes = [ctypes.POINTER(_RecognizerConfig)]
	lib.SherpaOnnxCreateOnlineRecognizer.restype = p
	lib.SherpaOnnxDestroyOnlineRecognizer.argtypes = [p]
	lib.SherpaOnnxCreateOnlineStream.argtypes = [p]
	lib.SherpaOnnxCreateOnlineStream.restype = p
	lib.SherpaOnnxDestroyOnlineStream.argtypes = [p]
	lib.SherpaOnnxOnlineStreamAcceptWaveform.argtypes = [p, ctypes.c_int32, ctypes.POINTER(ctypes.c_float), ctypes.c_int32]
	lib.SherpaOnnxIsOnlineStreamReady.argtypes = [p, p]
	lib.SherpaOnnxIsOnlineStreamReady.restype = ctypes.c_int32
	lib.SherpaOnnxDecodeOnlineStream.argtypes = [p, p]
	lib.SherpaOnnxOnlineStreamInputFinished.argtypes = [p]
	lib.SherpaOnnxGetOnlineStreamResultAsJson.argtypes = [p, p]
	lib.SherpaOnnxGetOnlineStreamResultAsJson.restype = p
	lib.SherpaOnnxDestroyOnlineStreamResultJson.argtypes = [p]
	_lib = lib
	return lib


def _native_path(path):
	"""The path as the C library can open it.

	The library reads file names as plain bytes, so a user name with letters such as ş, ğ or ı would break
	it. Windows can give the same folder a short ASCII name (8.3), which is used instead."""
	if path.isascii():
		return path.encode("ascii")
	try:
		buffer = ctypes.create_unicode_buffer(1024)
		if ctypes.windll.kernel32.GetShortPathNameW(path, buffer, 1024) and buffer.value.isascii():
			return buffer.value.encode("ascii")
	except Exception:
		log.debugWarning("GetShortPathNameW failed", exc_info=True)
	log.warning("The model path has non-ASCII characters and no short name; trying UTF-8: %s" % path)
	return path.encode("utf-8")


class Model:
	"""Same role as recognizer.Model: loaded once, then a session is made for every utterance."""

	def __init__(self, path):
		self.lib = _load_library()
		try:
			with open(os.path.join(path, "config.json"), encoding="utf-8") as f:
				settings = json.load(f)
		except Exception:
			settings = {}
		config = _RecognizerConfig()
		config.feat_config.sample_rate = int(settings.get("sample_rate", SAMPLE_RATE))
		config.feat_config.feature_dim = int(settings.get("feature_dim", 80))
		files = model_files(path)
		model = config.model_config
		model.transducer.encoder = _native_path(os.path.join(path, files["encoder"]))
		model.transducer.decoder = _native_path(os.path.join(path, files["decoder"]))
		model.transducer.joiner = _native_path(os.path.join(path, files["joiner"]))
		model.tokens = _native_path(os.path.join(path, files["tokens"]))
		model.num_threads = 2
		model.provider = b"cpu"
		config.decoding_method = str(settings.get("decoding_method", "modified_beam_search")).encode("ascii")
		config.max_active_paths = int(settings.get("max_active_paths", 4))
		# The listener decides where an utterance ends (the user presses the key again), not the model.
		config.enable_endpoint = 0
		# The structure keeps the byte strings alive only while it exists: it is used right here.
		self.rec = self.lib.SherpaOnnxCreateOnlineRecognizer(ctypes.byref(config))
		if not self.rec:
			# Translators: Error shown when the speech recognition model cannot be loaded. {path} is the model folder.
			raise RuntimeError(_("Could not load the model: {path}").format(path=path))
		self.sample_rate = config.feat_config.sample_rate

	def find_unknown_words(self, words):
		return []  # a free-form model has no word list to check against

	def new_session(self, grammar=None):
		return Session(self)  # the grammar is not used: these models cannot be restricted

	def close(self):
		if self.rec:
			self.lib.SherpaOnnxDestroyOnlineRecognizer(self.rec)
			self.rec = None


class Session:
	"""One utterance: accept() takes microphone audio, finish() returns the recognized text."""

	def __init__(self, model):
		self.model = model
		self.lib = model.lib
		self.stream = self.lib.SherpaOnnxCreateOnlineStream(model.rec)
		if not self.stream:
			# Translators: Error shown when the speech recognizer cannot be created.
			raise RuntimeError(_("Could not create the speech recognizer"))

	def _feed(self, samples):
		count = len(samples)
		if count:
			data = (ctypes.c_float * count)(*samples)
			self.lib.SherpaOnnxOnlineStreamAcceptWaveform(self.stream, self.model.sample_rate, data, count)

	def _decode(self):
		while self.lib.SherpaOnnxIsOnlineStreamReady(self.model.rec, self.stream):
			self.lib.SherpaOnnxDecodeOnlineStream(self.model.rec, self.stream)

	def accept(self, data):
		pcm = array.array("h")
		pcm.frombytes(data[:len(data) - len(data) % 2])
		self._feed([value / 32768.0 for value in pcm])
		self._decode()  # decoding while the user speaks keeps the delay after the key press short

	def finish(self):
		"""("", [text]): there is no grammar text, and the model gives only its best result."""
		self._feed([0.0] * int(self.model.sample_rate * TAIL_SECONDS))
		self.lib.SherpaOnnxOnlineStreamInputFinished(self.stream)
		self._decode()
		pointer = self.lib.SherpaOnnxGetOnlineStreamResultAsJson(self.model.rec, self.stream)
		text = ""
		if pointer:
			try:
				text = json.loads(ctypes.string_at(pointer).decode("utf-8")).get("text", "").strip()
			finally:
				self.lib.SherpaOnnxDestroyOnlineStreamResultJson(pointer)
		return "", [text]

	def close(self):
		if self.stream:
			self.lib.SherpaOnnxDestroyOnlineStream(self.stream)
			self.stream = None

