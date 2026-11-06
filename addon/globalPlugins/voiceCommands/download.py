# -*- coding: UTF-8 -*-
"""Finds the Vosk model for the NVDA language in the official model list, then downloads,
verifies and extracts it. Also installs the optional Turkish engine (sherpa-onnx runtime + the
turkish-stt model).

The network is only used after the user has agreed, and only to reach alphacephei.com (Vosk),
huggingface.co (the turkish-stt model files) and github.com (the sherpa-onnx runtime, pinned to one
version and checked against a fixed SHA-256)."""
import hashlib
import json
import os
import re
import shutil
import tarfile
import urllib.error
import urllib.request
import zipfile

import addonHandler

addonHandler.initTranslation()

LIST_URL = "https://alphacephei.com/vosk/models/model-list.json"
PAGE_URL = "https://alphacephei.com/vosk/models"
TIMEOUT = 30

# NVDA language code -> Vosk language code (only the ones that differ)
LANGUAGE_MAP = {"en": "en-us", "zh": "cn", "vi": "vn", "fil": "ph", "kk": "kz", "nb": "no", "nn": "no"}


def nvda_language():
	import languageHandler
	return languageHandler.getLanguage() or "en"


def vosk_code(language):
	base = language.replace("-", "_").split("_")[0].lower()
	return LANGUAGE_MAP.get(base, base)


def _request(url):
	return urllib.request.Request(url, headers={"User-Agent": "NVDA-VoiceCommands"})


def fetch_model_list():
	with urllib.request.urlopen(_request(LIST_URL), timeout=TIMEOUT) as response:
		data = json.loads(response.read().decode("utf-8"))
	if not isinstance(data, list):
		# Translators: Error shown when the downloaded list of speech models has an unexpected format.
		raise ValueError(_("Unexpected model list format"))
	return data


def pick_model(models, language):
	"""Best model for a language: exact language match first, then a small model, then the newest version."""
	code = vosk_code(language)
	candidates = []
	for model in models:
		if not isinstance(model, dict) or not model.get("url") or not model.get("name"):
			continue
		if str(model.get("obsolete", "false")).lower() == "true":
			continue
		lang = str(model.get("lang", "")).lower()
		if lang == code or lang.startswith(code + "-"):
			candidates.append(model)
	if not candidates:
		return None

	def rank(model):
		exact = 0 if str(model.get("lang", "")).lower() == code else 1
		small = 0 if model.get("type") == "small" else 1
		version = tuple(-int(x) for x in re.findall(r"\d+", str(model.get("version", ""))))
		return (exact, small, version)

	return sorted(candidates, key=rank)[0]


def size_text(model):
	return str(model.get("size_text") or "").strip()


def _download_file(url, path, progress, expected_size=0, algorithm="md5"):
	"""Downloads url to path and returns the hex digest of the content."""
	md5 = hashlib.new(algorithm)
	with urllib.request.urlopen(_request(url), timeout=TIMEOUT) as response, open(path, "wb") as f:
		total = int(response.headers.get("Content-Length") or expected_size or 0)
		received, last = 0, 0
		while True:
			block = response.read(1 << 16)
			if not block:
				break
			f.write(block)
			md5.update(block)
			received += len(block)
			if total:
				percent = received * 100 // total
				if percent // 25 > last and percent < 100:
					last = percent // 25
					progress(last * 25)
	return md5.hexdigest()


def _safe_extract(zip_path, target):
	"""Extracts a zip file, refusing any path that would end up outside the target (zip-slip)."""
	root = os.path.realpath(target)
	with zipfile.ZipFile(zip_path) as archive:
		for name in archive.namelist():
			path = os.path.realpath(os.path.join(root, name))
			if path != root and not path.startswith(root + os.sep):
				# Translators: Error shown when a downloaded archive contains a file path that points outside the target folder. {name} is that path.
				raise ValueError(_("Unsafe path in archive: {name}").format(name=name))
		archive.extractall(root)


def install_model(model, model_root, progress):
	"""Installs the model under model_root and returns the path of the installed folder."""
	os.makedirs(model_root, exist_ok=True)
	name = re.sub(r"[^\w.\-]", "_", str(model["name"]))
	size = int(model.get("size") or 0)
	if size and shutil.disk_usage(model_root).free < size * 3:
		# Translators: Error shown when there is not enough free disk space to install a speech model.
		raise OSError(_("Not enough free disk space"))
	zip_path = os.path.join(model_root, name + ".downloading.zip")
	temp_dir = os.path.join(model_root, name + ".tmp")
	final_dir = os.path.join(model_root, name)
	try:
		digest = _download_file(model["url"], zip_path, progress, size)
		expected = str(model.get("md5") or "").lower()
		if expected and digest.lower() != expected:
			# Translators: Error shown when a downloaded speech model file fails its integrity check.
			raise ValueError(_("The downloaded file is corrupt (checksum mismatch)"))
		shutil.rmtree(temp_dir, ignore_errors=True)
		_safe_extract(zip_path, temp_dir)
		content = os.listdir(temp_dir)
		source = os.path.join(temp_dir, content[0]) if len(content) == 1 and os.path.isdir(
			os.path.join(temp_dir, content[0])) else temp_dir
		shutil.rmtree(final_dir, ignore_errors=True)
		shutil.move(source, final_dir)
		return final_dir
	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)
		try:
			os.remove(zip_path)
		except OSError:
			pass


# ------------------------------------------------- turkish-stt (sherpa-onnx) engine
HF_MODEL = "mihuai/turkish-stt-66m-v2"
HF_URL = "https://huggingface.co/{repo}/resolve/main/{name}"
HF_FILES = ("encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx", "tokens.txt", "config.json")
# The ctypes structures in sherpa.py match exactly this release, so it is pinned and verified.
RUNTIME_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/v2.0.1/"
			   "sherpa-onnx-v2.0.1-win-x64-shared-MD-Release-no-tts.tar.bz2")
RUNTIME_SHA256 = "11fd6a50b97eed38b54fb16d8219f49b16aa7f6a8e43a042316469ef47652e82"
RUNTIME_DLLS = ("onnxruntime.dll", "onnxruntime_providers_shared.dll", "sherpa-onnx-c-api.dll")
RUNTIME_SIZE_TEXT = "21 MB"

_ARCHIVES = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"

# Streaming transducer models for the sherpa-onnx engine, by language (the part of the NVDA language
# before "-"/"_"). kind "files": loose files from Hugging Face, each checked against the checksum Hugging
# Face publishes. kind "archive": a .tar.bz2 from the sherpa-onnx release page, checked against the SHA-256
# below. "default": used without asking when the user has not chosen an engine (only where it was measured
# to be clearly better than the Vosk model). "license": shown in the download question.
SHERPA_MODELS = (
	{"id": "tr-mihu", "lang": "tr", "title": "turkish-stt (mihu AI)", "kind": "files", "default": True,
	 "folder": "sherpa-turkish-stt-66m-v2", "size_text": "68 MB", "site": "huggingface.co",
	 "license": "mihu Community License (free for personal use)"},
	{"id": "en-kroko", "lang": "en", "title": "Kroko English", "kind": "archive", "default": False,
	 "folder": "sherpa-en-kroko", "size_text": "57 MB", "site": "github.com",
	 "url": _ARCHIVES + "sherpa-onnx-streaming-zipformer-en-kroko-2025-08-06.tar.bz2",
	 "sha256": "c8676e5ff9ac2a85296e53ee0fd4d5fb1db6770e7a7647166eeafe349ade6834",
	 "license": "Kroko community model; terms: huggingface.co/Banafo/Kroko-ASR"},
	{"id": "fr-kroko", "lang": "fr", "title": "Kroko Français", "kind": "archive", "default": False,
	 "folder": "sherpa-fr-kroko", "size_text": "57 MB", "site": "github.com",
	 "url": _ARCHIVES + "sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06.tar.bz2",
	 "sha256": "e6ffd3dc43725cd6c8137b05c739f15607d0df946b9b90eb141e10059efca024",
	 "license": "Kroko community model; terms: huggingface.co/Banafo/Kroko-ASR"},
	{"id": "de-kroko", "lang": "de", "title": "Kroko Deutsch", "kind": "archive", "default": False,
	 "folder": "sherpa-de-kroko", "size_text": "58 MB", "site": "github.com",
	 "url": _ARCHIVES + "sherpa-onnx-streaming-zipformer-de-kroko-2025-08-06.tar.bz2",
	 "sha256": "9e27b783c20e67b0d0f13a258c1861fce199917c969d9176a438bee38df64962",
	 "license": "Kroko community model; terms: huggingface.co/Banafo/Kroko-ASR"},
	{"id": "es-kroko", "lang": "es", "title": "Kroko Español", "kind": "archive", "default": False,
	 "folder": "sherpa-es-kroko", "size_text": "124 MB", "site": "github.com",
	 "url": _ARCHIVES + "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06.tar.bz2",
	 "sha256": "31b2230a95d23290b308b393da930015a4b2105cb3abb9367aed35f7fcf29cf1",
	 "license": "Kroko community model; terms: huggingface.co/Banafo/Kroko-ASR"},
	{"id": "ru-vosk", "lang": "ru", "title": "Zipformer ru (Alpha Cephei)", "kind": "archive", "default": False,
	 "folder": "sherpa-ru-vosk", "size_text": "24 MB", "site": "github.com",
	 "url": _ARCHIVES + "sherpa-onnx-streaming-zipformer-small-ru-vosk-int8-2025-08-16.tar.bz2",
	 "sha256": "6ba68a01ff3c5445aaf2d61e9b97b026f1149dcc9049d11af3f44f55176341d8",
	 "license": "from alphacep/vosk-model-small-streaming-ru (see its page for the terms)"},
)


def base_language(language):
	return language.replace("-", "_").split("_")[0].lower()


def sherpa_models(language):
	"""The sherpa-onnx models available for an NVDA language code, the default one first."""
	code = base_language(language)
	return sorted((m for m in SHERPA_MODELS if m["lang"] == code), key=lambda m: not m["default"])


class _NoRedirect(urllib.request.HTTPRedirectHandler):
	def redirect_request(self, *args, **kwargs):
		return None


def _hf_sha256(url):
	"""SHA-256 that Hugging Face publishes for a large file (header of the first, redirecting answer), or ""."""
	opener = urllib.request.build_opener(_NoRedirect)
	request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "NVDA-VoiceCommands"})
	try:
		response = opener.open(request, timeout=TIMEOUT)
		headers = response.headers
	except urllib.error.HTTPError as e:  # the redirect itself arrives as an error here
		headers = e.headers
	value = (headers.get("X-Linked-ETag") or "").strip('"').lower()
	return value if re.fullmatch(r"[0-9a-f]{64}", value) else ""


def _stepped(progress, low, high):
	"""Maps 0-100 of one file to low-high of the whole install (the caller decides what to announce)."""
	return lambda percent: progress(low + (high - low) * percent // 100)


def _content_length(url):
	"""Size of a file in bytes (0 when unknown), asked before downloading so progress can be weighted."""
	try:
		request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "NVDA-VoiceCommands"})
		with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
			return int(response.headers.get("Content-Length") or 0)
	except Exception:
		return 0


def install_sherpa_runtime(runtime_dir, progress, low=0, high=100):
	"""Downloads the sherpa-onnx release and keeps only its three DLLs in runtime_dir.

	progress gets values from low to high (the part of the whole install this download covers)."""
	os.makedirs(runtime_dir, exist_ok=True)
	archive = os.path.join(runtime_dir, "runtime.downloading.tar.bz2")
	try:
		digest = _download_file(RUNTIME_URL, archive, _stepped(progress, low, high), 21 * 1024 * 1024, "sha256")
		if digest.lower() != RUNTIME_SHA256:
			# Translators: Error shown when a downloaded speech engine file fails its integrity check.
			raise ValueError(_("The downloaded file is corrupt (checksum mismatch)"))
		found = set()
		with tarfile.open(archive, "r:bz2") as tar:
			for member in tar:
				name = os.path.basename(member.name)
				if member.isfile() and name in RUNTIME_DLLS and "/lib/" in "/" + member.name.replace("\\", "/"):
					# Written under our own file name: nothing from the archive decides the path.
					temp = os.path.join(runtime_dir, name + ".tmp")
					with tar.extractfile(member) as source, open(temp, "wb") as target:
						shutil.copyfileobj(source, target)
					os.replace(temp, os.path.join(runtime_dir, name))
					found.add(name)
		if found != set(RUNTIME_DLLS):
			# Translators: Error shown when the downloaded speech engine package lacks files.
			raise ValueError(_("The speech engine package is incomplete"))
	finally:
		try:
			os.remove(archive)
		except OSError:
			pass


def _check_space(parent, needed=300 * 1024 * 1024):
	"""Raises OSError when the disk holding parent has less than `needed` bytes free."""
	os.makedirs(parent, exist_ok=True)
	if shutil.disk_usage(parent).free < needed:
		# Translators: Error shown when there is not enough free disk space to install a speech model.
		raise OSError(_("Not enough free disk space"))


def install_hf_files(repo, files, model_dir, progress, low=0, high=100):
	"""Downloads the given files of a Hugging Face repository into model_dir.

	Each file is checked against the SHA-256 that Hugging Face publishes for it. progress gets values
	from low to high (the part of the whole install this covers), weighted by file size."""
	os.makedirs(os.path.dirname(model_dir), exist_ok=True)
	urls = [HF_URL.format(repo=repo, name=name) for name in files]
	sizes = [_content_length(url) or 1024 for url in urls]
	total = sum(sizes)
	_check_space(os.path.dirname(model_dir), 2 * total)
	temp_dir = model_dir + ".tmp"
	shutil.rmtree(temp_dir, ignore_errors=True)
	os.makedirs(temp_dir)
	try:
		done = 0
		for name, url, size in zip(files, urls, sizes):
			expected = _hf_sha256(url)
			start = low + (high - low) * done // total
			end = low + (high - low) * (done + size) // total
			digest = _download_file(url, os.path.join(temp_dir, name), _stepped(progress, start, end), size, "sha256")
			if expected and digest.lower() != expected:
				# Translators: Error shown when a downloaded speech engine file fails its integrity check.
				raise ValueError(_("The downloaded file is corrupt (checksum mismatch)"))
			done += size
		shutil.rmtree(model_dir, ignore_errors=True)
		shutil.move(temp_dir, model_dir)
	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)


def install_sherpa_model(model_dir, progress, low=0, high=100):
	"""Downloads the turkish-stt model files into model_dir."""
	install_hf_files(HF_MODEL, HF_FILES, model_dir, progress, low, high)


_MODEL_FILE = re.compile(r"(encoder|decoder|joiner)[\w.\-]*\.onnx|tokens\.txt|config\.json")


def install_sherpa_archive(model, model_dir, progress, low=0, high=100):
	"""Downloads a model archive and keeps only the model files (flat) in model_dir."""
	_check_space(os.path.dirname(model_dir), 3 * int(model.get("size_mb", 100)) * 1024 * 1024)
	archive = model_dir + ".downloading.tar.bz2"
	temp_dir = model_dir + ".tmp"
	shutil.rmtree(temp_dir, ignore_errors=True)
	os.makedirs(temp_dir)
	try:
		digest = _download_file(model["url"], archive, _stepped(progress, low, high), 0, "sha256")
		if digest.lower() != model["sha256"]:
			# Translators: Error shown when a downloaded speech engine file fails its integrity check.
			raise ValueError(_("The downloaded file is corrupt (checksum mismatch)"))
		with tarfile.open(archive, "r:bz2") as tar:
			for member in tar:
				name = os.path.basename(member.name)
				if member.isfile() and _MODEL_FILE.fullmatch(name):
					# Written under our own file name: nothing from the archive decides the path.
					with tar.extractfile(member) as source, open(os.path.join(temp_dir, name), "wb") as target:
						shutil.copyfileobj(source, target)
		if not (os.path.isfile(os.path.join(temp_dir, "tokens.txt")) and any(n.startswith("encoder") for n in os.listdir(temp_dir))):
			# Translators: Error shown when the downloaded speech engine package lacks files.
			raise ValueError(_("The speech engine package is incomplete"))
		shutil.rmtree(model_dir, ignore_errors=True)
		shutil.move(temp_dir, model_dir)
	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)
		try:
			os.remove(archive)
		except OSError:
			pass
