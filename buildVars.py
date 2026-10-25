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
	addon_description=_("""Runs NVDA commands and common Windows actions by voice, using the offline Vosk speech recognition engine; your voice never leaves your computer. You can say any command from the Input Gestures dialog, built-in Windows commands such as "show desktop", "show taskbar" or "paste", and your own commands that open a program, file, folder or web address, or press a key combination. A speech model for your NVDA language is downloaded on first use. Assign keys in the Input Gestures dialog, under the Voice Commands category."""),

	# version
	addon_version="1.0.0",

	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
Initial release
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
	addon_lastTestedNVDAVersion="2026.2.0",

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