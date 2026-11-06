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

from . import announce, dialogs, download, ducking, phonetic, recognizer, sherpa, storage, userCommands, windowsCommands
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
# Engines without a command list (the sherpa models) write ordinary text, so they are matched more strictly:
FREE_MATCH = 0.70				# minimum score_free() to run a command without asking
FREE_MARGIN = 0.10			# the best candidate must lead the second by this much, otherwise the user chooses
FREE_LIST_MIN = 0.55			# lowest score_free() that may appear in the candidate list (below it: nothing resembles a command)
FREE_PHONETIC_THRESHOLD = 0.65	# sound match, last resort: much stricter than the Vosk fallback
FRAGMENT_MIN_LENGTH = 4		# letters: a shorter fragment is too easily noise to run a command
FRAGMENT_WORD_MATCH = 0.8		# how closely each spoken word must match a word of the command

ENGINE_VOSK = "vosk"
ENGINE_SHERPA = "sherpa"	# a sherpa-onnx streaming model (free-form, no grammar); see download.SHERPA_MODELS


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
	entries = _all_entries()
	storage.resolve_pending(data, [(storage.command_id(info), category, description) for category, description, info in entries])
	for _category, description, info in entries:
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
			announce.say(_("Not found: {target}").format(target=info.target))
		except Exception:
			log.exception("Could not run the user command: %s" % description)
			# Translators: Spoken when a command of the user's own could not be run. {command} is the name of the command.
			announce.say(_("Could not run: {command}").format(command=description))
		return
	if windowsCommands.is_windows_command(info):
		log.debug("Running Windows command by voice: %r x%d" % (info.scriptName, repeat))
		try:
			for _repeat in range(max(1, min(repeat, MAX_REPEAT)) if info.repeatable else 1):
				windowsCommands.press(info)
		except Exception:
			log.exception("Could not run the Windows command: %s" % description)
			# Translators: Spoken when a Windows command could not be run.
			announce.say(_("Could not run the command"))
		return
	if is_key_emulation(info):
		log.debug("Pressing key by voice: %r x%d" % (info.scriptName, repeat))
		try:
			for _repeat in range(max(1, min(repeat, MAX_REPEAT))):
				press_key(info)
		except Exception:
			log.exception("Could not press the key: %s" % description)
			announce.say(_("Could not run the command"))
		return
	target = find_target(info.cls)
	if target is None:
		# Translators: Spoken when a voice command cannot run in the current context. {command} is the command description.
		announce.say(_("This command is not available right now: {command}").format(command=description))
		return
	func = getattr(target, "script_" + info.scriptName, None)
	if func is None:
		# Translators: Spoken when the script behind a voice command cannot be found. {command} is the command description.
		announce.say(_("Script not found: {command}").format(command=description))
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
		announce.say(_("Could not run the command"))


def score_free(spoken, phrase):
	"""Similarity (0-1) for text from an engine that is not restricted to the command list.

	score() asks only whether the spoken words occur in the command, which suits a grammar that already
	forces whole commands: a single word such as "right" then fully "matches" "Snap window to the right".
	Free text can be a fragment or a sentence, so the words of the command must be found in what was
	said as well: the two fractions are combined like precision and recall."""
	spoken, phrase = spoken.replace("ı", "i"), phrase.replace("ı", "i")
	spoken_words, phrase_words = spoken.split(), phrase.split()
	if not spoken_words or not phrase_words:
		return 0.0

	def covered(words, others):
		total = 0.0
		for word in words:
			best = max(difflib.SequenceMatcher(None, word, other).ratio() for other in others)
			total += best if best >= 0.75 else 0.0
		return total / len(words)

	heard, wanted = covered(spoken_words, phrase_words), covered(phrase_words, spoken_words)
	if not heard or not wanted:
		return 0.0
	words = 2 * heard * wanted / (heard + wanted)
	return 0.8 * words + 0.2 * difflib.SequenceMatcher(None, spoken, phrase).ratio()


def is_fragment(spoken_words, phrase_words):
	"""True when every spoken word is (about) a word of the command: "yukarı" is a fragment of "yukarı çık"."""
	return all(
		max(difflib.SequenceMatcher(None, word, other).ratio() for other in phrase_words) >= FRAGMENT_WORD_MATCH
		for word in spoken_words)


def rank_candidates(spoken, commands, scorer=None):
	"""Unique command candidates ordered by similarity: [(score, description, info)]."""
	scorer = scorer or score
	scores = {key: scorer(spoken, key) for key in commands}
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
	announce.say(ngettext(
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
		announce.say(_("No command found"))
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
		announce.say(_("No matching command. Closest: {command}").format(command=candidates[0][1]))


_last_heard = []				# what the free recognizer heard last time, for "teach last phrase"


def _remember_heard(alternatives):
	"""Keeps the distinct texts the free recognizer produced, best first."""
	global _last_heard
	heard = []
	for text in alternatives:
		text = normalize(text)
		if text and text not in heard:
			heard.append(text)
	_last_heard = heard


def decide(grammar_text, alternatives, index):
	"""Picks the command to run from the output of the two recognizers.

	grammar_text  text from the grammar-restricted recognizer ("[unk]" marks unmatched speech)
	alternatives  n-best texts from the free recognizer
	index		 phonetic.CommandIndex over the current NVDA commands (matching by sound)

	Only NVDA commands listed in Input Gestures are ever executed."""
	grammar_text = grammar_text.strip()
	grammar_clean = bool(grammar_text) and "[unk]" not in grammar_text
	free = alternatives[0] if alternatives else ""
	_remember_heard(alternatives)
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
		announce.say(_("Not understood"))
		return
	run_phrase(text)


def decide_free(alternatives, index):
	"""Picks the command for an engine that cannot be restricted to the command list (the sherpa models).

	Such an engine writes ordinary text, spelled the usual way, and it can write anything: a fragment,
	a whole sentence, or words made up for silence. The words are therefore compared in both directions
	(score_free): a clear winner runs, a close call gives the candidate list, and text that resembles no
	command only reports what was heard. Matching by sound is a last resort with a strict threshold; the
	Vosk fallback in decide() trusts a loose sound match because there the free recognizer is only the
	second opinion next to the grammar."""
	_remember_heard(alternatives)
	log.debug("Voice command recognition (free-form): %r" % (alternatives,))
	text = next((a for a in alternatives if normalize(a)), "")
	commands = collect_commands()
	spoken, repeat = split_repeat(normalize(text))
	if not spoken:
		# Translators: Spoken when the speech recognizer did not understand what was said.
		announce.say(_("Not understood"))
		return
	if not commands:
		# Translators: Spoken when no command could be found for what was said.
		announce.say(_("No command found"))
		return
	if spoken in commands:
		description, info = commands[spoken]
		run_command(description, info, repeat)
		return
	candidates = rank_candidates(spoken, commands, score_free)
	for value, description, _info in candidates[:5]:
		log.debug("Voice command candidate (free-form): %.2f  %s" % (value, description))
	best = candidates[0][0]
	second = candidates[1][0] if len(candidates) > 1 else 0.0
	if best >= FREE_MATCH and best - second >= FREE_MARGIN:
		run_command(candidates[0][1], candidates[0][2], repeat)
		return
	# A fragment of exactly one command ("yukarı" for "yukarı çık", "cumhuriyet" for "cumhuriyet son haberler")
	# is not a guess: nothing else could have been meant, so it runs. A fragment of several commands is a
	# real choice and opens the list. Very short fragments are left out because they are too often noise.
	if len(spoken.replace(" ", "")) >= FRAGMENT_MIN_LENGTH:
		words = spoken.replace("ı", "i").split()
		containing = {}
		for key, (description, info) in commands.items():
			if is_fragment(words, key.replace("ı", "i").split()):
				containing.setdefault(id(info), (description, info))	# a command with several phrases counts once
		if len(containing) == 1:
			description, info = next(iter(containing.values()))
			log.debug("Voice command fragment of exactly one command: %s" % description)
			run_command(description, info, repeat)
			return
		if len(containing) > 1 and SHOW_CANDIDATE_LIST:
			fits = sorted(((score_free(spoken, normalize(d)), d, i) for d, i in containing.values()),
						  key=lambda c: -c[0])
			show_candidates(fits[:LIST_MAX_ITEMS], repeat)
			return
	listed = [c for c in candidates if c[0] >= FREE_LIST_MIN]
	if not listed and index is not None:
		found = index.search([spoken], threshold=FREE_PHONETIC_THRESHOLD)
		if found:
			log.debug("Voice command phonetic match: %r (%.2f)" % (found[1], found[2]))
			run_phrase(found[0] + (" %s %s" % (_spoken_number(repeat), _REPEAT_TIMES[0]) if repeat > 1 else ""))
			return
	if listed and SHOW_CANDIDATE_LIST:
		show_candidates(listed, repeat)
		return
	# Translators: Spoken when the speech recognizer heard something that is not a command. {text} is what was heard.
	announce.say(_("Heard: {text}. No matching command").format(text=text.strip()))


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


class SpeechModelDialog(wx.Dialog):
	"""One place for everything about the speech model: choose it, download it (a model that is not
	installed is downloaded after the choice is confirmed) and open the folder it is kept in."""

	def __init__(self, parent, labels, current, open_folder):
		# Translators: Title of the dialog where the speech model is chosen and managed.
		super().__init__(parent, title=_("Voice Commands: speech model"))
		self._open_folder = open_folder
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the list of speech models.
		label = wx.StaticText(self, label=_("Speech &model:"))
		main.Add(label, 0, wx.ALL, 8)
		self.list = wx.ListBox(self, choices=labels, size=(560, 140))
		self.list.SetSelection(current)
		main.Add(self.list, 1, wx.ALL | wx.EXPAND, 8)
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Button in the speech model dialog. It uses the selected model and downloads it first if it is not installed.
		use = wx.Button(self, wx.ID_OK, label=_("&Use"))
		use.SetDefault()
		# Translators: Button in the speech model dialog. It opens the folder the models are kept in.
		folder = wx.Button(self, wx.ID_ANY, label=_("Open model &folder"))
		folder.Bind(wx.EVT_BUTTON, lambda evt: self._open_folder())
		buttons.Add(use, 0, wx.ALL, 8)
		buttons.Add(folder, 0, wx.ALL, 8)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.ALL, 8)
		main.Add(buttons, 0, wx.ALIGN_RIGHT)
		self.list.Bind(wx.EVT_LISTBOX_DCLICK, lambda evt: self.EndModal(wx.ID_OK))
		self.SetSizerAndFit(main)
		self.CenterOnParent()
		self.list.SetFocus()

	def selection(self):
		return self.list.GetSelection()


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
		self.sherpa_entry = None
		self.engine = self._startEngine()
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

	def _startEngine(self):
		"""Picks the speech engine and, for sherpa, the model of the NVDA language.

		The user's choice wins. Without one, the sherpa model that is marked as default for the language
		(Turkish) is used, unless a Vosk model is already installed (no surprise download after an update).
		Every other language stays on Vosk until the user chooses a sherpa model."""
		entries = download.sherpa_models(download.nvda_language())
		settings = storage.load_settings()
		chosen = settings.get("engine")
		wanted = settings.get("sherpa_model")
		self.sherpa_entry = entries[0] if entries else None
		if chosen == ENGINE_SHERPA and entries:
			# The model the user chose, when it exists for the NVDA language (settings from before the model
			# was stored mean the first one). Another NVDA language falls back to Vosk instead of picking
			# a model the user never chose.
			match = next((e for e in entries if e["id"] == wanted), None) if wanted else entries[0]
			if match:
				self.sherpa_entry = match
				return ENGINE_SHERPA
		if chosen == ENGINE_VOSK or chosen == ENGINE_SHERPA:
			return ENGINE_VOSK
		if self.sherpa_entry and self.sherpa_entry["default"] and not recognizer.find_model_dir(storage.model_dir()):
			return ENGINE_SHERPA
		return ENGINE_VOSK

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
				(_("Teach the last spoken phrase..."), self._onToolsTeach),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("My commands..."), self._onToolsEditUserCommands),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu.
				(_("Toggle volume lowering"), self._onToolsToggleDucking),
				# Translators: Menu item in the Voice Commands submenu of the Tools menu. It opens one dialog to choose, download and manage the speech model.
				(_("Speech model..."), self._onToolsSpeechModel),
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
		with announce.afterMenu():
			self.script_listen(None)

	def _onToolsEditPhrases(self, evt):
		with announce.afterMenu():
			self.script_editPhrases(None)

	def _onToolsTeach(self, evt):
		with announce.afterMenu():
			self.script_teachLastPhrase(None)

	def _onToolsEditUserCommands(self, evt):
		with announce.afterMenu():
			self.script_editUserCommands(None)

	def _onToolsToggleDucking(self, evt):
		with announce.afterMenu():
			self.script_toggleDucking(None)

	def _onToolsSpeechModel(self, evt):
		with announce.afterMenu():
			self.script_speechModel(None)

	def _onToolsCommandBox(self, evt):
		with announce.afterMenu():
			self.script_commandBox(None)

	def _loadModel(self):
		try:
			if self.engine == ENGINE_SHERPA:
				self._loadSherpa()
				return
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

	def _loadSherpa(self):
		path = sherpa.find_model(self.sherpa_entry["folder"]) if sherpa.find_runtime() else None
		self.model_missing = not path
		if not path:
			# Translators: Spoken when a speech engine is selected but its files are not installed.
			self.error = _("The selected speech engine is not installed")
			log.warning("Speech engine not installed. Runtime: %r, model: %r" % (
				sherpa.find_runtime(), sherpa.model_path(self.sherpa_entry["folder"])))
			return
		self.model = sherpa.Model(path)
		log.debug("Speech engine loaded: " + path)

	def _modelInstalled(self):
		if self.engine == ENGINE_SHERPA:
			return sherpa.is_installed(self.sherpa_entry["folder"])
		return bool(recognizer.find_model_dir(storage.model_dir()))

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
		if self.engine == ENGINE_SHERPA:
			self._sherpaQuestion()
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
			announce.say(_("OK. I will ask again when you start voice listening."))

	def _sherpaQuestion(self):
		entry = self.sherpa_entry
		sites = {entry["site"]}
		size = entry["size_text"]
		if not sherpa.find_runtime():
			sites.add("github.com")
			size = "%s + %s" % (size, download.RUNTIME_SIZE_TEXT)
		# Translators: Question asked before a speech engine is downloaded. {name} is the model name, {size} the download size, {sites} the sites it is downloaded from, {license} the license of the model, {path} the folder the files are stored in.
		message = _(
			"The speech engine {name} is not installed.\n\n"
			"Download it now? Size: {size}. Sites: {sites}. The files are checked against fixed checksums.\n"
			"License: {license}\n"
			"Files are stored under:\n{path}\n\n"
			"An internet connection is required. The download runs in the background, so you can keep using NVDA."
		).format(name=entry["title"], size=size, sites=", ".join(sorted(sites)), license=entry["license"],
				 path=storage.config_dir())
		# Translators: Title of the question about downloading a speech engine.
		if ask_yes_no(message, _("Voice Commands: speech engine download")):
			self.downloading = True
			threading.Thread(target=self._download, daemon=True).start()

	def _downloadSherpa(self, say):
		entry = self.sherpa_entry
		# Translators: Spoken when the download of a speech engine starts. {name} is the model name.
		say(_("Downloading {name}").format(name=entry["title"]))
		# Translators: Spoken as download progress. {percent} is the percentage.
		progress_message = _("{percent} percent")
		spoken = [0]

		def report(overall):
			bucket = overall // 25
			if bucket > spoken[0] and overall < 100:
				spoken[0] = bucket
				say(progress_message.format(percent=bucket * 25))

		need_runtime = not sherpa.find_runtime()
		if need_runtime:
			download.install_sherpa_runtime(sherpa.runtime_dir(), report, 0, 25)
		if not sherpa.find_model(entry["folder"]):
			low = 25 if need_runtime else 0
			target = sherpa.model_path(entry["folder"])
			if entry["kind"] == "archive":
				download.install_sherpa_archive(entry, target, report, low, 100)
			else:
				download.install_sherpa_model(target, report, low, 100)

	def _download(self):
		def say(text):
			wx.CallAfter(announce.say, text)

		try:
			if self.engine == ENGINE_SHERPA:
				self._downloadSherpa(say)
				say(_("Model installed, loading it"))
				self.loading = True
				self.error = None
				self._loadModel()
				say(_("Voice commands are ready") if self.model else (self.error or _("Could not load the model")))
				return
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
		if not USE_GRAMMAR or self.engine == ENGINE_SHERPA:
			return None  # the Turkish engine is free-form; the text is matched to commands by words and by sound
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
		announce.say(_("Speech recognition error: {error}").format(error=message))

	def _handleResult(self, grammar_text, alternatives):
		if self.engine == ENGINE_SHERPA:
			decide_free(alternatives, self.index)
		else:
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
			announce.say(_("The model is loading, please wait"))
			return
		if not self.model:
			if self._modelInstalled():
				# The model may have been put in the folder later: load it again.
				# Translators: Spoken when the model is being loaded.
				announce.say(self.error or _("The model is loading, please wait"))
				self.loading = True
				self.error = None
				threading.Thread(target=self._loadModel, daemon=True).start()
			elif self.downloading:
				# Translators: Spoken when the user starts listening while the model is being downloaded.
				announce.say(_("The model is being downloaded, please wait"))
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
			announce.say(_("Could not get the list of commands"))
			return
		# Translators: Spoken after the phrases have been saved in the phrase editor.
		dialogs.PhraseEditorDialog(gui.mainFrame, commands, lambda: announce.say(_("Phrases saved"), announce.AFTER_FOCUS_CHANGE)).display()

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens a dialog that adds what the recognizer heard last as a spoken phrase of a command you choose"))
	def script_teachLastPhrase(self, gesture):
		if not _last_heard:
			# Translators: Spoken when the user wants to teach a phrase but nothing has been recognized yet.
			announce.say(_("Nothing heard yet. Say a command first"))
			return
		commands = list_commands()
		if not commands:
			announce.say(_("Could not get the list of commands"))
			return
		# Translators: Spoken after the phrases have been saved in the teach dialog.
		dialogs.TeachDialog(gui.mainFrame, commands, list(_last_heard), lambda: announce.say(_("Phrases saved"), announce.AFTER_FOCUS_CHANGE)).display()

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens the dialog for adding your own commands: open a program, file, folder or web address, or press a key combination"))
	def script_editUserCommands(self, gesture):
		# Translators: Spoken after the user's own commands have been saved.
		dialogs.UserCommandsDialog(gui.mainFrame, lambda: announce.say(_("Commands saved"), announce.AFTER_FOCUS_CHANGE)).display()

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
			announce.say(_("Volume lowering on"))
		else:
			# Translators: Spoken when lowering other applications' volume while listening is turned off.
			announce.say(_("Volume lowering off"))

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens the speech model dialog: choose, download and manage the model"))
	def script_speechModel(self, gesture):
		wx.CallAfter(self._showSpeechModel)

	def _modelChoices(self):
		"""[(engine, sherpa entry or None, installed, label)]: Vosk first, then the sherpa models of the NVDA language."""
		# Translators: Speech model in the speech model dialog. Vosk is the default engine; recognition is restricted to the command list.
		choices = [(ENGINE_VOSK, None, bool(recognizer.find_model_dir(storage.model_dir())),
					_("Vosk: small model for the NVDA language, restricted to the command list"))]
		for entry in download.sherpa_models(download.nvda_language()):
			# Translators: Speech model in the speech model dialog. {name} is the model name, {size} its download size.
			label = _("{name} ({size}): free speech recognition, not restricted to the command list").format(
				name=entry["title"], size=entry["size_text"])
			choices.append((ENGINE_SHERPA, entry, sherpa.is_installed(entry["folder"]), label))
		return choices

	def _showSpeechModel(self):
		if self.downloading:
			# Translators: Spoken when the user opens the speech model dialog while a model is being downloaded.
			announce.say(_("The model is already being downloaded"))
			return
		if self.listener and self.listener.is_alive():
			# Translators: Spoken when the user wants to change the speech model while listening.
			announce.say(_("Stop listening first"))
			return
		choices = self._modelChoices()
		labels, current = [], 0
		for index, (engine, entry, installed, label) in enumerate(choices):
			if engine == self.engine and entry is self.sherpa_entry:
				current = index
				# Translators: Status shown after a model in the speech model dialog: it is the model in use.
				status = _("in use")
			elif installed:
				# Translators: Status shown after a model in the speech model dialog: it is downloaded.
				status = _("installed")
			else:
				# Translators: Status shown after a model in the speech model dialog: it must be downloaded first.
				status = _("not installed")
			labels.append("%s - %s" % (label, status))
		gui.mainFrame.prePopup()
		dialog = SpeechModelDialog(gui.mainFrame, labels, current, self._openModelFolder)
		try:
			accepted = dialog.ShowModal() == wx.ID_OK
			engine, entry, installed, _label = choices[dialog.selection()]
		finally:
			dialog.Destroy()
			gui.mainFrame.postPopup()
		if not accepted:
			return
		unchanged = engine == self.engine and (entry is None or entry is self.sherpa_entry)
		if unchanged and installed and self.model:
			return  # already in use
		# A model that is not installed is downloaded after the user agrees (see _loadAfterSwitch).
		self._switchEngine(engine, entry)

	def _openModelFolder(self):
		path = storage.model_dir()
		os.makedirs(path, exist_ok=True)
		# Translators: Spoken when the model folder is opened. {path} is the folder.
		announce.say(_("Opening the model folder: {path}").format(path=path))
		os.startfile(path)

	def _switchEngine(self, engine, entry):
		try:
			settings = storage.load_settings()
			settings["engine"] = engine
			if entry is not None:
				settings["sherpa_model"] = entry["id"]
			storage.save_settings(settings)
		except Exception:
			log.exception("Could not save the settings")
		old, self.model = self.model, None
		if old:
			try:
				old.close()
			except Exception:
				log.exception("Could not close the previous model")
		self.engine = engine
		if entry is not None:
			self.sherpa_entry = entry
		self.error = None
		self.loading = True
		threading.Thread(target=self._loadAfterSwitch, daemon=True).start()

	def _loadAfterSwitch(self):
		self._loadModel()
		if self.model:
			# Translators: Spoken when voice commands are ready to use.
			wx.CallAfter(announce.say, _("Voice commands are ready"))
		elif self.model_missing and not self.downloading:
			self._askDownload(True)
		else:
			wx.CallAfter(announce.say, self.error or _("Could not load the model"))

	@script(
		# Translators: Description of a command in the Input Gestures dialog.
		description=_("Opens a box where you can type a command phrase"))
	def script_commandBox(self, gesture):
		gui.mainFrame.prePopup()
		dialog = CommandBox(gui.mainFrame)
		dialog.Show()
		dialog.Raise()