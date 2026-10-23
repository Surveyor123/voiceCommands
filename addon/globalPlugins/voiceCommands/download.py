# -*- coding: UTF-8 -*-
"""Finds the Vosk model for the NVDA language in the official model list, then downloads,
verifies and extracts it.

The network is only used after the user has agreed, and only to reach alphacephei.com."""
import hashlib
import json
import os
import re
import shutil
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


def _download_file(url, path, progress, expected_size=0):
	md5 = hashlib.md5()
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
