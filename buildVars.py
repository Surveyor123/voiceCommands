# -*- coding: utf-8 -*-
# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="voiceCommands",

	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	addon_summary=_("Voice Commands"),

	# Add-on description
	# Translators: Long description to be shown for this add-on
	addon_description=_("""Runs NVDA commands and common Windows actions by voice, using an offline speech recognition engine (Vosk or sherpa-onnx); your voice never leaves your computer. You can say any command from the Input Gestures dialog, built-in Windows commands such as "show desktop", "show taskbar" or "paste", and your own commands that open a program, file, folder or web address, or press a key combination. A speech model for your NVDA language is downloaded on first use. Assign keys in the Input Gestures dialog, under the Voice Commands category."""),

	# version
	addon_version="1.1.0",

	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
- Listening now stops by itself when you stay silent for about a second after speaking, as if you had pressed the key again. It can be turned off with a new toggle command (Input Gestures or the Tools menu); the silence length is the silence_seconds setting.
- Added a Voice Commands submenu under NVDA's Tools menu with the add-on's commands.
- Fixed Windows commands that use a letter, such as Windows+I, not working on keyboard layouts like Turkish Q.
- Added "Teach the last spoken phrase" (Tools menu or an assignable gesture) to save what the recognizer heard as a phrase of a command, for names the speech model cannot recognize.
- Added import and export of phrases in the phrase editor, with shortcuts Ctrl+I, Ctrl+E and Ctrl+S. Importing only adds; nothing you already have is changed or removed.
- Phrase files can now name a command by its text ("description - category") instead of its id. Entries for commands that are not available yet are kept until they appear.
- The heard-phrases list in the teach dialog now reports its checked state in every NVDA version.
- Messages are no longer cut off by NVDA's focus speech after a dialog, file chooser or menu closes.
- Added a Turkish set of short phrases that can be imported from the phrase editor.
- Added a second speech engine, sherpa-onnx, with a Turkish model (turkish-stt) and models for English, French, German, Spanish and Russian. It is the default for a Turkish NVDA that has no Vosk model installed.
- Added the Speech model dialog to the Tools menu, to choose, download and manage the speech model. It replaces the separate download and model folder items.
- Text from the sherpa models is matched to commands more strictly, so an invented sentence no longer runs a wrong command; NVDA says what it heard instead. A word or two that fit exactly one command still run it, and a list opens when they fit several.
"""),

	# Author(s)
	addon_author="Çağrı Doğan <cagrid@hotmail.com>",

	# URL for the add-on documentation support
	addon_url="https://github.com/Surveyor123/voiceCommands",

	# URL for the add-on repository where the source code can be found
	addon_sourceURL="https://github.com/Surveyor123/voiceCommands",

	# Documentation file name
	addon_docFileName="readme.html",

	# Minimum NVDA version supported
	addon_minimumNVDAVersion="2026.1.0",

	# Last NVDA version supported/tested
	addon_lastTestedNVDAVersion="2026.3.0",

	# Add-on update channel (None denotes stable releases)
	addon_updateChannel=None,

	# Add-on license
	addon_license="GPL-2.0-or-later",
	addon_licenseURL="https://github.com/Surveyor123/voiceCommands/blob/main/LICENSE",
)

# Define the python files that are the sources of your add-on.
# We point to the specific directory where your code lives.
pythonSources: list[str] = [
	"addon/globalPlugins/voiceCommands/*.py",
	"addon/appModules/*.py",
]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
excludedFiles: list[str] = []

# Base language for the NVDA add-on
# Since your code strings (e.g. _("Table")) are in English, we keep this as "en".
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
markdownExtensions: list[str] = []

# Custom braille translation tables
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}