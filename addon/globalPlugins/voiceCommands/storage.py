# -*- coding: UTF-8 -*-
"""User-defined command phrases (aliases) and add-on settings.

aliases.json:  {command_id: {"aliases": [phrase, ...], "keep_original": true/false}}
settings.json: {"duck_audio": true/false, "ask_download": true/false}

The command id is derived from the script name, so phrases stay attached to the right
command even when the interface language or the description text changes."""
import json
import os

import globalVars
from logHandler import log


def config_dir():
	try:
		root = globalVars.appArgs.configPath
	except Exception:
		root = os.path.join(os.environ.get("APPDATA", ""), "nvda")
	return os.path.join(root, "voiceCommands")


def model_dir():
	return os.path.join(config_dir(), "model")


def _path(name):
	return os.path.join(config_dir(), name)


def _read_json(name):
	try:
		with open(_path(name), encoding="utf-8") as f:
			data = json.load(f)
		return data if isinstance(data, dict) else {}
	except FileNotFoundError:
		return {}
	except Exception:
		log.exception("Could not read %s" % name)
		return {}


def _write_json(name, data):
	os.makedirs(config_dir(), exist_ok=True)
	temp = _path(name) + ".tmp"
	with open(temp, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)
	os.replace(temp, _path(name))


def command_id(info):
	cls = info.cls
	return "%s.%s.%s" % (cls.__module__, cls.__name__, info.scriptName)


def load_aliases():
	"""Cleaned alias data: {id: {"aliases": [str], "keep_original": bool}}."""
	result = {}
	for cid, entry in _read_json("aliases.json").items():
		if not isinstance(entry, dict):
			continue
		phrases = [p.strip() for p in entry.get("aliases", []) if isinstance(p, str) and p.strip()]
		result[cid] = {"aliases": phrases, "keep_original": bool(entry.get("keep_original", True))}
	return result


def save_aliases(data):
	_write_json("aliases.json", data)


def load_user_commands():
	"""The commands the user defined: [{"id", "name", "kind", "target"}]."""
	entries = _read_json("userCommands.json").get("commands", [])
	return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def save_user_commands(entries):
	_write_json("userCommands.json", {"commands": entries})


def load_settings():
	return _read_json("settings.json")


def save_settings(settings):
	_write_json("settings.json", settings)


def read_json_list(name):
	"""Reads a JSON file that holds a list (used for the audio ducking recovery file)."""
	try:
		with open(_path(name), encoding="utf-8") as f:
			data = json.load(f)
		return data if isinstance(data, list) else []
	except FileNotFoundError:
		return []
	except Exception:
		log.exception("Could not read %s" % name)
		return []


def write_json_list(name, data):
	os.makedirs(config_dir(), exist_ok=True)
	with open(_path(name), "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)


def delete_file(name):
	try:
		os.remove(_path(name))
	except OSError:
		pass
