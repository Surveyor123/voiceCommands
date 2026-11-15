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
	addon_version="1.1.1",

	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
## New
- Phrases can now carry a press count. A phrase such as "say the date" can be stored on the "say the time" command with a count of 2, so saying it presses that command twice. A count you speak or type takes precedence.
- The phrase editor has a new "Times the command is pressed" list (1 to 5), so nothing has to be typed. Phrases with a count are shown as "<phrase> (pressed N times)". Edit restores the count, and adding the same words with a different count replaces the earlier phrase.
- The command box accepts the same suffix (for example "... x2").
- Added 64 Turkish phrases for the extra presses of NVDA and add-on commands (date, spell, character descriptions, copy, open in browser, and so on). Existing phrases are unchanged. There is no phrase for the factory reset, so a misrecognition cannot trigger it.

## Changes
- Repeating a command by voice now behaves like real key presses. Saying "read title three times" previously ran the script three times in a row, so the work of the first and second press (speak, spell) was done as well. For scripts that react to multiple presses, only the Nth press is now performed. Other commands, key emulation included, still run N times.
- If NVDA's internals are not available, the add-on falls back to running the command N times and cancels speech between runs, as a key press does.

## Bug fixes
- Fixed the volume of other applications sometimes staying lowered after a voice command. Players that close and reopen their audio session (on pause, next track or stream restart, such as media played through python.exe) left the new session at the ducked volume, because Windows remembers per-application volumes. The lowered volume could also be recorded as the "original" volume the next time listening started.
- Volumes are now restored by also searching the current audio sessions for the same process still at the ducked volume, not only the sessions saved when ducking started.
- Sessions that could not be restored stay pending (and in the recovery file) and are restored before the next ducking.
- The volumes are checked again 1.5 and 4 seconds after a restore, to catch sessions opened by the spoken command itself (for example "next track").
- Pending entries are dropped after 24 hours and their number is capped.
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