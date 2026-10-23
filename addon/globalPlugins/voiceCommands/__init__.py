# -*- coding: UTF-8 -*-
"""Voice Commands: run NVDA commands by speaking their descriptions from the Input Gestures dialog."""
import difflib
import inspect
import json
import os
import re
import threading

import addonHandler
import api
import core
import globalCommands
import globalPluginHandler
import gui
import inputCore
import scriptHandler
import tones
import ui
import wx
from logHandler import log
from scriptHandler import script

from . import dialogs, download, ducking, phonetic, recognizer, storage, userCommands, windowsCommands
from .text import normalize

addonHandler.initTranslation()

USE_GRAMMAR = True			# restrict recognition to the available command descriptions
MATCH_THRESHOLD = 0.55		# minimum similarity (0-1) to run a command without asking
VERIFY_THRESHOLD = 0.45	   # a grammar hit must resemble the free recognition at least this much
AMBIGUITY_MARGIN = 0.06	   # the candidate list is shown when the two best scores are closer than this
LIST_MIN_SCORE = 0.35		 # lowest score that may appear in the candidate list
LIST_MAX_ITEMS = 7			# most candidates shown in the list
SHOW_CANDIDATE_LIST = True	# False: run the best match, or report that nothing matched
MAX_REPEAT = 5				# most times a command can be repeated by speech


# -------------------------------------------------------- repeat count
# "read current line twice" runs the script twice in a row; NVDA counts that as a double
# key press (scriptHandler.getLastScriptRepeatCount).

# Translators: The spoken words for the numbers 2, 3, 4 and 5, used to repeat a command ("read current line two times"). Give exactly four words separated by "|", in that order. Digits always work too.
_NUMBER_WORDS = _("two|three|four|five")
# Translators: Spoken words that mean "times" and follow the number when repeating a command ("read current line two times"). Give one or more alternatives separated by "|". The first one is added to the speech grammar.
_TIMES_WORDS = _("times|time")


def _repeat_vocabulary():
	values = {str(n): n for n in range(2, 6)}
	for offset, word in enumerate(_NUMBER_WORDS.split("|")[:4]):
		if word.strip():
			values[word.strip().lower()] = offset + 2
	times = [w.strip().lower() for w in _TIMES_WORDS.split("|") if w.strip()] or ["times"]
	return values, times


_REPEAT_VALUES, _REPEAT_TIMES = _repeat_vocabulary()
_REPEAT_RE = re.compile(r"(?:^|\s)(%s)\s+(?:%s)$" % (
	"|".join(map(re.escape, sorted(_REPEAT_VALUES, key=len, reverse=True))),
	"|".join(map(re.escape, sorted(_REPEAT_TIMES, key=len, reverse=True))),
))


def _spoken_number(value):
	for word, number in _REPEAT_VALUES.items():
		if number == value and not word.isdigit():
			return word
	return str(value)


_REPEAT_SUFFIXES = ["%s %s" % (_spoken_number(n), _REPEAT_TIMES[0]) for n in (2, 3)]


def split_repeat(text):
	"""Separates a trailing "two times" suffix: (text without it, repeat count)."""
	match = _REPEAT_RE.search(text)
	if not match:
		return text, 1
	return text[:match.start()].strip(), _REPEAT_VALUES[match.group(1)]


def _code_mentions(code, name, depth=0):
	if name in code.co_names:
		return True
	if depth < 3:
		for const in code.co_consts:
			if hasattr(const, "co_names") and _code_mentions(const, name, depth + 1):
				return True
	return False


_REPEAT_AWARE_CACHE = {}


def is_repeat_aware(info):
	"""True if the script reacts to being pressed several times (it uses getLastScriptRepeatCount)."""
	key = (info.cls, info.scriptName)
	if key not in _REPEAT_AWARE_CACHE:
		aware = False
		try:
			func = getattr(info.cls, "script_" + info.scriptName, None)
			func = inspect.unwrap(getattr(func, "__func__", func))
			code = getattr(func, "__code__", None)
			aware = bool(code and _code_mentions(code, "getLastScriptRepeatCount"))
		except Exception:
			log.debugWarning("Could not determine whether a script is repeat aware", exc_info=True)
		_REPEAT_AWARE_CACHE[key] = aware
	return _REPEAT_AWARE_CACHE[key]


# -------------------------------------------------------------- commands
KEY_EMULATION_PREFIX = "kb:"


def is_key_emulation(info):
	"""True for the commands of the "Emulated system keyboard keys" category.

	These are not scripts: NVDA stores the key to press as the script name ("kb:downArrow"),
	and runs them by emulating that key on the system keyboard."""
	return info.scriptName.startswith(KEY_EMULATION_PREFIX)


def supports_repeat(info):
	"""Whether "... two times" makes sense: keys can be pressed several times, and some scripts count presses."""
	if windowsCommands.is_windows_command(info) or userCommands.is_user_command(info):
		return info.repeatable
	return is_key_emulation(info) or is_repeat_aware(info)


def press_key(info):
	"""Presses the emulated key the way NVDA does (see scriptHandler._makeKbEmulateScript)."""
	import keyboardHandler
	gesture = keyboardHandler.KeyboardInputGesture.fromName(info.scriptName[len(KEY_EMULATION_PREFIX):])
	inputCore.manager.emulateGesture(gesture)


class SyntheticGesture(inputCore.InputGesture):
	"""Gesture handed to scripts when they are run by voice; no key was actually pressed."""
	shouldReportAsCommand = False
	isModifier = False

	def _get_identifiers(self):
		return ("kb:f24",)

	def send(self):
		pass


def _gesture_mappings():
	try:
		return inputCore.manager.getAllGestureMappings()
	except Exception:
		log.exception("Could not get the gesture mappings")
		return {}


def _all_entries():
	"""[(category, description, info)]: the commands of the Input Gestures dialog, then the built-in Windows commands."""
	entries = []
	for category, items in _gesture_mappings().items():
		for description, info in items.items():
			if getattr(info, "cls", None) and getattr(info, "scriptName", None):
				entries.append((str(category), description, info))
	# They come last, so a command of NVDA with the same description wins.
	windows_category = windowsCommands.category()
	for info in windowsCommands.all_commands():
		entries.append((windows_category, info.description, info))
	user_category = userCommands.category()
	for info in userCommands.load():
		entries.append((user_category, info.description, info))
	return entries


def collect_commands():
	"""{normalized phrase: (phrase, info)}: original descriptions plus the user's own phrases."""
	commands, extras = {}, []
	data = storage.load_aliases()
	for _category, description, info in _all_entries():
		settings = data.get(storage.command_id(info), {})
		if settings.get("keep_original", True):
			if userCommands.is_user_command(info):
				extras.append((normalize(description), (description, info)))  # the user's own name wins
			else:
				commands.setdefault(normalize(description), (description, info))
		for phrase in settings.get("aliases", []):
			extras.append((normalize(phrase), (phrase, info)))
	for key, value in extras:  # the user's phrases take precedence over original descriptions
		if key:
			commands[key] = value
	return commands


def list_commands():
	"""For the phrase editor: [(command_id, category, description)] of the available commands."""
	result, seen = [], set()
	for category, description, info in _all_entries():
		command_id = storage.command_id(info)
		if command_id not in seen:
			seen.add(command_id)
			result.append((command_id, category, description))
	result.sort(key=lambda item: (item[1], item[2]))
	return result


def find_target(cls):
	focus = api.getFocusObject()
	candidates = [
		focus,
		getattr(focus, "appModule", None),
		getattr(focus, "treeInterceptor", None),
		api.getNavigatorObject(),
		globalCommands.commands,
	]
	candidates += list(globalPluginHandler.runningPlugins)
	for candidate in candidates:
		if candidate is not None and isinstance(candidate, cls):
			return candidate
	return None


def score(spoken, phrase):
	"""Word-based fuzzy similarity (0-1)."""
	# Turkish casing turns "Input" into "ınput" while the recognizer writes "input":
	# compare with the dotless i folded away.
	spoken, phrase = spoken.replace("ı", "i"), phrase.replace("ı", "i")
	spoken_words, phrase_words = spoken.split(), phrase.split()
	if not spoken_words or not phrase_words:
		return 0.0
	coverage = 0.0
	for word in spoken_words:
		best = max(difflib.SequenceMatcher(None, word, other).ratio() for other in phrase_words)
		coverage += best if best >= 0.75 else 0.0
	coverage /= len(spoken_words)
	whole = difflib.SequenceMatcher(None, spoken, phrase).ratio()
	length = min(len(spoken_words), len(phrase_words)) / max(len(spoken_words), len(phrase_words))
	return 0.6 * coverage + 0.25 * whole + 0.15 * length


def run_command(description, info, repeat=1):
	"""Runs a command; with repeat > 1 the script runs several times in a row (like multiple key presses)."""
	if userCommands.is_user_command(info):
		log.debug("Running user command by voice: %r x%d" % (description, repeat))
		try:
			for _repeat in range(max(1, min(repeat, MAX_REPEAT)) if info.repeatable else 1):
				userCommands.run(info)
		except FileNotFoundError:
			log.warning("User command target not found: %r" % (info.target,))
			# Translators: Spoken when the program, file or folder of a command of the user's own does not exist. {target} is what the command should open.
			ui.message(_("Not found: {target}").format(target=info.target))
		except Exception:
			log.exception("Could not run the user command: %s" % description)
			# Translators: Spoken when a command of the user's own could not be run. {command} is the name of the command.
			ui.message(_("Could not run: {command}").format(command=description))
		return
	if windowsCommands.is_windows_command(info):
		log.debug("Running Windows command by voice: %r x%d" % (info.scriptName, repeat))
		try:
			for _repeat in range(max(1, min(repeat, MAX_REPEAT)) if info.repeatable else 1):
				windowsCommands.press(info)
		except Exception:
			log.exception("Could not run the Windows command: %s" % description)
			# Translators: Spoken when a Windows command could not be run.
			ui.message(_("Could not run the command"))
		return
	if is_key_emulation(info):
		log.debug("Pressing key by voice: %r x%d" % (info.scriptName, repeat))
		try:
			for _repeat in range(max(1, min(repeat, MAX_REPEAT))):
				press_key(info)
		except Exception:
			log.exception("Could not press the key: %s" % description)
			ui.message(_("Could not run the command"))
		return
	target = find_target(info.cls)
	if target is None:
		# Translators: Spoken when a voice command cannot run in the current context. {command} is the command description.
		ui.message(_("This command is not available right now: {command}").format(command=description))
		return
	func = getattr(target, "script_" + info.scriptName, None)
	if func is None:
		# Translators: Spoken when the script behind a voice command cannot be found. {command} is the command description.
		ui.message(_("Script not found: {command}").format(command=description))
		return
	log.debug("Running voice command: %r x%d" % (description, repeat))
	try:
		clear_last = getattr(scriptHandler, "clearLastScript", None)
		if clear_last:
			clear_last()  # the repeat counter starts from 0
		for _repeat in range(max(1, min(repeat, MAX_REPEAT))):
			scriptHandler.executeScript(func, SyntheticGesture())
	except Exception:
		log.exception("Could not run the script: %s" % description)
		# Translators: Spoken when running a voice command failed.
		ui.message(_("Could not run the command"))


def rank_candidates(spoken, commands):
	"""Unique command candidates ordered by similarity: [(score, description, info)]."""
	scores = {key: score(spoken, key) for key in commands}
	candidates, seen = [], set()
	for key in sorted(scores, key=scores.get, reverse=True):
		description, info = commands[key]
		command_id = storage.command_id(info)
		if command_id in seen:
			continue
		seen.add(command_id)
		candidates.append((scores[key], description, info))
		if len(candidates) >= LIST_MAX_ITEMS:
			break
	return candidates


def show_candidates(candidates, repeat):
	suffix = ""
	if repeat > 1:
		# Translators: Appended to a command in the candidate list when it will be repeated. {count} is the number of repeats.
		suffix = _(" ({count} times)").format(count=repeat)
	labels = [c[1] + suffix for c in candidates]

	def selected(index):
		_score, description, info = candidates[index]
		# Wait a moment so that focus returns to the previous window after the dialog closes.
		core.callLater(300, run_command, description, info, repeat)

	# Translators: Spoken when the candidate list opens. {count} is the number of possible commands.
	ui.message(ngettext(
		"{count} possible command, choose one",
		"{count} possible commands, choose one",
		len(candidates),
	).format(count=len(candidates)))
	# Translators: Title of the dialog that lists the possible commands when it is unclear which one was meant.
	dialogs.CandidateListDialog(gui.mainFrame, _("Choose a command"), labels, selected).display()


def run_phrase(text):
	commands = collect_commands()
	spoken = normalize(text)
	spoken, repeat = split_repeat(spoken)
	if not spoken or not commands:
		# Translators: Spoken when no command could be found for what was said.
		ui.message(_("No command found"))
		return
	if spoken in commands:
		description, info = commands[spoken]
		run_command(description, info, repeat)
		return
	candidates = rank_candidates(spoken, commands)
	for value, description, _info in candidates[:5]:
		log.debug("Voice command candidate: %.2f  %s" % (value, description))
	best = candidates[0][0]
	second = candidates[1][0] if len(candidates) > 1 else 0.0
	# A clear winner runs directly.
	if best >= MATCH_THRESHOLD and (best - second) >= AMBIGUITY_MARGIN:
		run_command(candidates[0][1], candidates[0][2], repeat)
		return
	# Unclear or low confidence: list the candidates and run the one the user picks.
	listed = [c for c in candidates if c[0] >= LIST_MIN_SCORE]
	if SHOW_CANDIDATE_LIST and listed:
		show_candidates(listed, repeat)
		return
	if best >= MATCH_THRESHOLD:
		run_command(candidates[0][1], candidates[0][2], repeat)
	else:
		# Translators: Spoken when nothing matches closely enough. {command} is the closest command description.
		ui.message(_("No matching command. Closest: {command}").format(command=candidates[0][1]))


def decide(grammar_text, alternatives, index):
	"""Picks the command to run from the output of the two recognizers.

	grammar_text  text from the grammar-restricted recognizer ("[unk]" marks unmatched speech)
	alternatives  n-best texts from the free recognizer
	index		 phonetic.CommandIndex over the current NVDA commands (matching by sound)

	Only NVDA commands listed in Input Gestures are ever executed."""
	grammar_text = grammar_text.strip()
	grammar_clean = bool(grammar_text) and "[unk]" not in grammar_text
	free = alternatives[0] if alternatives else ""
	log.debug("Voice command recognition: grammar=%r free=%r" % (grammar_text, alternatives))
	if grammar_clean:
		normalized = normalize(grammar_text)
		# The grammar always force-fits speech to some command; trust it only when the free
		# recognizer heard something similar (or heard nothing at all).
		if not alternatives or any(score(normalize(a), normalized) >= VERIFY_THRESHOLD for a in alternatives):
			run_phrase(grammar_text)
			return
	# The grammar had unknown words: commands that contain words missing from the model
	# vocabulary (foreign names) can only be found by sound. The repeat
	# suffix is split off so they do not disturb the phonetic match.
	stems, repeat = [], 1
	for alternative in alternatives:
		text = normalize(alternative)
		text, count = split_repeat(text)
		repeat = max(repeat, count)
		stems.append(text)
	found = index.search(stems) if index is not None else None
	if found:
		log.debug("Voice command phonetic match: %r (%.2f)" % (found[1], found[2]))
		run_phrase(found[0] + (" %s %s" % (_spoken_number(repeat), _REPEAT_TIMES[0]) if repeat > 1 else ""))
		return
	if grammar_clean:
		run_phrase(grammar_text)
		return
	text = grammar_text.replace("[unk]", " ").strip() or free
	if not text:
		# Translators: Spoken when the speech recognizer did not understand what was said.
		ui.message(_("Not understood"))
		return
	run_phrase(text)


def ask_yes_no(message, caption):
	"""Asks a Yes/No question; True means Yes."""
	try:
		try:
			from gui.message import messageBox
		except ImportError:
			messageBox = gui.messageBox
		return messageBox(message, caption, wx.YES_NO | wx.ICON_QUESTION, gui.mainFrame) == wx.YES
	except Exception:
		gui.mainFrame.prePopup()
		try:
			return wx.MessageBox(message, caption, wx.YES_NO | wx.ICON_QUESTION, gui.mainFrame) == wx.YES
		finally:
			gui.mainFrame.postPopup()


class CommandBox(wx.Dialog):
	def __init__(self, parent):
		# Translators: Title of the dialog where a command phrase can be typed instead of spoken.
		super().__init__(parent, title=_("Voice Command"))
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the edit field where a command phrase is typed.
		main.Add(wx.StaticText(self, label=_("Command phrase:")), 0, wx.ALL, 8)
		self.box = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(400, -1))
		main.Add(self.box, 0, wx.ALL | wx.EXPAND, 8)
		self.box.Bind(wx.EVT_TEXT_ENTER, self.onEnter)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKey)
		self.SetSizerAndFit(main)
		self.CentreOnScreen()

	def onKey(self, evt):
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
		else:
			evt.Skip()

	def onEnter(self, evt):
		text = self.box.GetValue()
		self.Close()
		# Wait a moment so that focus returns to the previous window.
		core.callLater(400, run_phrase, text)

	def Close(self, *args, **kwargs):
		gui.mainFrame.postPopup()
		self.Destroy()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Name of the category of Voice Commands in the Input Gestures dialog.
	scriptCategory = _("Voice Commands")

	def __init__(self):
		super().__init__()
		self.model = None
		self.listener = None
		self.index = None
		self.loading = True
		self.error = None
		self.model_missing = False
		self.downloading = False
		self.question_open = False
		self.closing = False
		self.ducker = ducking.AudioDucker()
		self.duck_audio = bool(storage.load_settings().get("duck_audio", True))
		try:
			os.makedirs(storage.model_dir(), exist_ok=True)
		except Exception:
			log.exception("Could not create the model folder")
		threading.Thread(target=self._loadModel, daemon=True).start()
		# Give NVDA's interface time to become ready, then ask about the model if it is missing.
		core.callLater(6000, self._startupCheck)
		# Add a submenu under NVDA's Tools menu, following the same pattern
		# as the freeAudio add-on (gui.mainFrame.sysTrayIcon.toolsMenu).
		self._voiceCommandsMenu = None
		self._toolsMenuItem = None
		wx.CallAfter(self._buildToolsMenu)

	def _buildToolsMenu(self):
		"""Add a Voice Commands submenu under NVDA's Tools menu."""
		try:
			tools_menu = gui.mainFrame.sysTrayIcon.toolsMenu
			self._voiceCommandsMenu = wx.Menu()

			items = [
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Start or stop listening"), self._onToolsListen),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Command phrase editor..."), self._onToolsEditPhrases),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("My commands..."), self._onToolsEditUserCommands),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Toggle volume lowering"), self._onToolsToggleDucking),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Download speech model..."), self._onToolsDownloadModel),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Open model folder"), self._onToolsOpenModelFolder),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Type a command..."), self._onToolsCommandBox),
			]
			for label, handler in items:
				item = self._voiceCommandsMenu.Append(wx.ID_ANY, label)
				gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, handler, item)

			self._toolsMenuItem = tools_menu.AppendSubMenu(
				self._voiceCommandsMenu,
				_("Voice Commands"),
			)
		except Exception:
			log.exception("Could not add the Voice Commands menu to the Tools menu")

	def _onToolsListen(self, evt):
		self.script_listen(None)

	def _onToolsEditPhrases(self, evt):
		self.script_editPhrases(None)

	def _onToolsEditUserCommands(self, evt):
		self.script_editUserCommands(None)

	def _onToolsToggleDucking(self, evt):
		self.script_toggleDucking(None)

	def _onToolsDownloadModel(self, evt):
		self.script_downloadModel(None)

	def _onToolsOpenModelFolder(self, evt):
		self.script_openModelFolder(None)

	def _onToolsCommandBox(self, evt):
		self.script_commandBox(None)

	def _loadModel(self):
		try:
			path = recognizer.find_model_dir(storage.model_dir())
			self.model_missing = not path
			if not path:
				# Translators: Spoken when no speech recognition model is installed. {path} is the folder that was searched.
				self.error = _("Vosk model not found. Searched folder: {path}").format(path=storage.model_dir())
				log.warning("Model not found. Folder: %s, contents: %r" % (
					storage.model_dir(), recognizer.folder_summary(storage.model_dir())))
			else:
				self.model = recognizer.Model(path)
				log.debug("Vosk model loaded: " + path)
		except Exception as e:
			log.exception("Could not load the model")
			# Translators: Spoken when the speech recognition model could not be loaded. {error} describes the problem.
			self.error = _("Could not load the model: {error}").format(error=e)
		finally:
			self.loading = False

	def terminate(self):
		self.closing = True
		try:
			if self.listener and self.listener.is_alive():
				self.listener.stop()
				self.listener.join(3)
			if self.model:
				self.model.close()
		except Exception:
			log.exception("Error while shutting down")
		self.ducker.close()  # puts volumes back if they are still lowered
		# Remove the Voice Commands submenu from the Tools menu.
		try:
			if self._toolsMenuItem is not None:
				tools_menu = gui.mainFrame.sysTrayIcon.toolsMenu
				tools_menu.Delete(self._toolsMenuItem.GetId())
				self._toolsMenuItem = None
		except Exception:
			log.debug("Could not remove the Voice Commands menu", exc_info=True)
		try:
			if self._voiceCommandsMenu is not None:
				self._voiceCommandsMenu.Destroy()
				self._voiceCommandsMenu = None
		except Exception:
			pass
		super().terminate()

	# ------------------------------------------------------ model download
	def _startupCheck(self):
		if self.model is None and self.model_missing and not self.downloading:
			if storage.load_settings().get("ask_download", True):
				self._askDownload(False)

	def _askDownload(self, manual):
		"""Asks the user and, if they agree, downloads the model in the background.

		Scripts and core.callLater run on NVDA's core queue, where a modal dialog would block
		the core (NVDA falls silent). The dialog is therefore opened from the wx event loop."""
		if self.downloading or self.question_open:
			return
		self.question_open = True
		wx.CallAfter(self._showDownloadQuestion, manual)

	def _showDownloadQuestion(self, manual):
		try:
			self._downloadQuestion(manual)
		finally:
			self.question_open = False

	def _downloadQuestion(self, manual):
		if self.downloading:
			return
		language = download.nvda_language()
		# Translators: Question asked when no speech recognition model is installed. {language} is the NVDA language code, {path} the folder the model will be extracted to.
		message = _(
			"The Vosk speech recognition model is not installed.\n\n"
			"Download the model for the NVDA language ({language}) from alphacephei.com "
			"and extract it to the following folder?\n{path}\n\n"
			"An internet connection is required; small models are usually 40-100 MB. "
			"The download runs in the background, so you can keep using NVDA."
		).format(language=language, path=storage.model_dir())
		# Translators: Title of the question about downloading the speech recognition model.
		if ask_yes_no(message, _("Voice Commands: model download")):
			self.downloading = True
			threading.Thread(target=self._download, daemon=True).start()
		elif not manual:
			try:
				settings = storage.load_settings()
				settings["ask_download"] = False
				storage.save_settings(settings)
			except Exception:
				log.exception("Could not save the settings")
			# Translators: Spoken when the user declines the model download at startup.
			ui.message(_("OK. I will ask again when you start voice listening."))

	def _download(self):
		def say(text):
			wx.CallAfter(ui.message, text)

		try:
			# Translators: Spoken while the add-on looks for a suitable speech model online.
			say(_("Searching for a model"))
			model = download.pick_model(download.fetch_model_list(), download.nvda_language())
			if not model:
				wx.CallAfter(self._noModelForLanguage)
				return
			size = download.size_text(model)
			if size:
				# Translators: Spoken when a model download starts. {name} is the model name, {size} its size.
				say(_("Downloading {name}, {size}").format(name=model["name"], size=size))
			else:
				# Translators: Spoken when a model download starts. {name} is the model name.
				say(_("Downloading {name}").format(name=model["name"]))
			# Translators: Spoken as download progress. {percent} is the percentage.
			progress_message = _("{percent} percent")
			path = download.install_model(
				model, storage.model_dir(),
				lambda percent: say(progress_message.format(percent=percent)))
			log.debug("Vosk model downloaded: " + path)
			# Translators: Spoken when the model has been downloaded and is being loaded.
			say(_("Model installed, loading it"))
			self.loading = True
			self.error = None
			self._loadModel()
			if self.model:
				# Translators: Spoken when voice commands are ready to use.
				say(_("Voice commands are ready"))
			else:
				# Translators: Spoken when the model could not be loaded.
				say(self.error or _("Could not load the model"))
		except Exception as e:
			log.exception("Could not download the model")
			# Translators: Spoken when the model download failed. {error} describes the problem.
			say(_("Could not download the model: {error}").format(error=e))
		finally:
			self.downloading = False

	def _noModelForLanguage(self):
		# Translators: Question asked when no ready-made model exists for the NVDA language. {language} is the NVDA language code, {path} the folder to extract a model into.
		message = _(
			"No ready-made Vosk model was found for the NVDA language ({language}).\n\n"
			"Open the model page in the browser? You can download a model there and extract it "
			"to this folder:\n{path}"
		).format(language=download.nvda_language(), path=storage.model_dir())
		# Translators: Title of the question shown when no model exists for the NVDA language.
		if ask_yes_no(message, _("Voice Commands: no suitable model")):
			os.startfile(download.PAGE_URL)

	# --------------------------------------------------------- recognition
	def _prepareGrammar(self, commands):
		"""Builds a Vosk grammar from the command descriptions that are available right now."""
		if not USE_GRAMMAR:
			return None
		try:
			phrases = list(commands.keys())
			if not phrases:
				return None
			# Keys and commands that react to several key presses also get "two times / three times" variants.
			for key, (_description, info) in list(commands.items()):
				if supports_repeat(info):
					phrases += [key + " " + suffix for suffix in _REPEAT_SUFFIXES]
			words = sorted({w for p in phrases for w in p.split()})
			unknown = self.model.find_unknown_words(words)
			log.debug("Grammar: %d phrases, %d words, %d not in the vocabulary: %r" % (
				len(phrases), len(words), len(unknown), unknown[:30]))
			return json.dumps(phrases + ["[unk]"], ensure_ascii=False)
		except Exception:
			log.exception("Could not build the grammar; falling back to free recognition")
			return None

	def _onResult(self, grammar_text, alternatives):
		# Runs on the listener thread.
		wx.CallAfter(self._handleResult, grammar_text, alternatives)

	def _onError(self, message):
		wx.CallAfter(self._handleError, message)

	def _handleError(self, message):
		self.ducker.restore()
		# Translators: Spoken when speech recognition failed. {error} describes the problem.
		ui.message(_("Speech recognition error: {error}").format(error=message))

	def _handleResult(self, grammar_text, alternatives):
		decide(grammar_text, alternatives, self.index)

	# ------------------------------------------------------------- scripts
	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Starts listening for a voice command; press again to stop listening and run the command"))
	def script_listen(self, gesture):
		if self.listener and self.listener.is_alive():
			tones.beep(500, 80)
			self.listener.stop()
			self.ducker.restore()
			return
		if self.loading:
			# Translators: Spoken when the user starts listening while the model is still loading.
			ui.message(_("The model is loading, please wait"))
			return
		if not self.model:
			if recognizer.find_model_dir(storage.model_dir()):
				# The model may have been put in the folder later: load it again.
				# Translators: Spoken when the model is being loaded.
				ui.message(self.error or _("The model is loading, please wait"))
				self.loading = True
				self.error = None
				threading.Thread(target=self._loadModel, daemon=True).start()
			elif self.downloading:
				# Translators: Spoken when the user starts listening while the model is being downloaded.
				ui.message(_("The model is being downloaded, please wait"))
			else:
				self._askDownload(True)
			return
		commands = collect_commands()
		try:
			self.index = phonetic.CommandIndex(commands)
		except Exception:
			log.exception("Could not build the phonetic command index")
			self.index = None
		grammar = self._prepareGrammar(commands)
		if self.duck_audio:
			self.ducker.duck()
		tones.beep(1000, 80)
		self.listener = recognizer.Listener(self.model, grammar, self._onResult, self._onError)
		self.listener.start()

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens the dialog for editing the phrases (aliases) used for commands"))
	def script_editPhrases(self, gesture):
		commands = list_commands()
		if not commands:
			# Translators: Spoken when the list of commands could not be obtained.
			ui.message(_("Could not get the list of commands"))
			return
		# Translators: Spoken after the phrases have been saved in the phrase editor.
		dialogs.PhraseEditorDialog(gui.mainFrame, commands, lambda: ui.message(_("Phrases saved"))).display()

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens the dialog for adding your own commands: open a program, file, folder or web address, or press a key combination"))
	def script_editUserCommands(self, gesture):
		# Translators: Spoken after the user's own commands have been saved.
		dialogs.UserCommandsDialog(gui.mainFrame, lambda: ui.message(_("Commands saved"))).display()

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Toggles lowering the volume of other applications while listening for a voice command"))
	def script_toggleDucking(self, gesture):
		self.duck_audio = not self.duck_audio
		try:
			settings = storage.load_settings()
			settings["duck_audio"] = self.duck_audio
			storage.save_settings(settings)
		except Exception:
			log.exception("Could not save the settings")
		if self.duck_audio:
			# Translators: Spoken when lowering other applications' volume while listening is turned on.
			ui.message(_("Volume lowering on"))
		else:
			# Translators: Spoken when lowering other applications' volume while listening is turned off.
			ui.message(_("Volume lowering off"))

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Downloads the speech recognition model for the NVDA language"))
	def script_downloadModel(self, gesture):
		if self.downloading:
			# Translators: Spoken when the user asks for a model download while one is already running.
			ui.message(_("The model is already being downloaded"))
		else:
			self._askDownload(True)

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens the model folder in File Explorer"))
	def script_openModelFolder(self, gesture):
		path = storage.model_dir()
		os.makedirs(path, exist_ok=True)
		# Translators: Spoken when the model folder is opened. {path} is the folder.
		ui.message(_("Opening the model folder: {path}").format(path=path))
		os.startfile(path)

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens a box where you can type a command phrase"))
	def script_commandBox(self, gesture):
		gui.mainFrame.prePopup()
		dialog = CommandBox(gui.mainFrame)
		dialog.Show()
		dialog.Raise()