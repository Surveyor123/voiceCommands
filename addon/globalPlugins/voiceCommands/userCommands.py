# -*- coding: UTF-8 -*-
"""Commands the user defines: open a program, file, folder or web address, or press a key combination.

They are stored in userCommands.json as a list of {"id", "name", "kind", "target"}. The name is what
the user says. Like the built-in Windows commands they take part in the speech grammar and can get
extra phrases in the phrase editor; their ids ("user:<id>") never change, so renaming a command
keeps its extra phrases.

Nothing here runs arbitrary shell commands: a command either hands its target to Windows, the way
double-clicking it would, or presses keys on the system keyboard."""
import os
import uuid

import addonHandler
from logHandler import log

from . import storage, windowsCommands

addonHandler.initTranslation()

SCRIPT_PREFIX = "user:"
KIND_OPEN = "open"
KIND_KEYS = "keys"


class UserCommands:
	"""Stands in for the script class of NVDA commands; only its name is used (in command ids)."""


class UserCommand:
	"""Looks like the script info NVDA hands out, so it can live next to NVDA's commands."""
	cls = UserCommands

	def __init__(self, command_id, name, kind, target):
		self.id = command_id
		self.scriptName = SCRIPT_PREFIX + command_id
		self.description = name
		self.kind = kind
		self.target = target
		# The key combination in NVDA key names; windowsCommands.press() uses it.
		self.keys = normalize_keys(target) if kind == KIND_KEYS else ""
		self.repeatable = kind == KIND_KEYS


def is_user_command(info):
	return isinstance(info, UserCommand)


def category():
	# Translators: Category shown next to the user's own commands in the command phrase editor.
	return _("My commands")


# Spellings people commonly type, mapped to NVDA key names.
_KEY_ALIASES = {
	"ctrl": "control", "win": "windows", "lwin": "windows", "esc": "escape", "return": "enter",
	"del": "delete", "ins": "insert", "pgup": "pageUp", "pgdn": "pageDown", "pageup": "pageUp",
	"pagedown": "pageDown", "up": "upArrow", "down": "downArrow", "left": "leftArrow",
	"right": "rightArrow", "spacebar": "space", "prtsc": "printScreen", "printscreen": "printScreen",
	"backspace": "backspace", "app": "applications", "menu": "applications",
}


def normalize_keys(text):
	""""Ctrl + Shift + N" -> "control+shift+n" (NVDA key names)."""
	parts = [p.strip() for p in text.replace(" ", "+").split("+") if p.strip()]
	result = []
	for part in parts:
		lowered = part.lower()
		result.append(_KEY_ALIASES.get(lowered, lowered if len(part) == 1 else part))
	return "+".join(result)


def validate_keys(text):
	"""None when NVDA understands the key combination, otherwise a short description of the problem."""
	keys = normalize_keys(text)
	if not keys:
		return "empty"
	try:
		import keyboardHandler
		keyboardHandler.KeyboardInputGesture.fromName(keys)
	except Exception as e:
		return str(e)
	return None


def load():
	"""[UserCommand] in the order the user created them."""
	result = []
	for entry in storage.load_user_commands():
		try:
			name, kind, target = entry["name"].strip(), entry["kind"], entry["target"].strip()
			if name and target and kind in (KIND_OPEN, KIND_KEYS):
				result.append(UserCommand(entry["id"], name, kind, target))
		except Exception:
			log.warning("Skipping an invalid user command: %r" % (entry,))
	return result


def save(entries):
	"""entries: [{"id", "name", "kind", "target"}]"""
	storage.save_user_commands(entries)


def new_id():
	return uuid.uuid4().hex[:10]


# Plain folder names people type instead of a path (English and Turkish) -> Windows shell folders.
_KNOWN_FOLDERS = {
	"music": "shell:My Music", "müzik": "shell:My Music", "muzik": "shell:My Music",
	"documents": "shell:Personal", "belgeler": "shell:Personal",
	"downloads": "shell:Downloads", "indirilenler": "shell:Downloads",
	"desktop": "shell:Desktop", "masaüstü": "shell:Desktop", "masaustu": "shell:Desktop",
	"pictures": "shell:My Pictures", "resimler": "shell:My Pictures",
	"videos": "shell:My Video", "videolar": "shell:My Video",
}


def resolve_target(target):
	"""Expands variables and turns a plain folder name ("music") into the Windows shell folder."""
	target = os.path.expandvars(target.strip().strip('"'))
	if not os.path.exists(target):
		target = _KNOWN_FOLDERS.get(target.lower(), target)
	return target


def open_target(target):
	"""Opens a program, file, folder or web address, as double-clicking it would."""
	os.startfile(resolve_target(target))


def run(info):
	if info.kind == KIND_KEYS:
		windowsCommands.press(info)
	else:
		open_target(info.target)
