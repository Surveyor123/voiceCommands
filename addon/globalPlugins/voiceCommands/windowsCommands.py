# -*- coding: UTF-8 -*-
"""Built-in Windows commands that can be spoken: show desktop, copy, paste, and so on.

NVDA's Input Gestures dialog only lists NVDA's own commands, so these system-wide shortcuts would
otherwise have to be spoken as raw key names. Each command here is a description (translatable,
so it is also what the user says) and the key combination Windows already uses for it.

The commands behave like the ones from Input Gestures: they take part in the speech grammar, can
be typed in the command box, can get the user's own phrases in the phrase editor, and some can be
repeated ("volume up three times"). Their ids do not depend on the interface language
("win:showDesktop"), so the user's own phrases stay attached when the language changes.
"""
import addonHandler

addonHandler.initTranslation()

SCRIPT_PREFIX = "win:"


class WindowsCommands:
	"""Stands in for the script class of NVDA commands; only its name is used (in command ids)."""


class WindowsCommand:
	"""Looks like the script info NVDA hands out, so it can live next to NVDA's commands."""
	cls = WindowsCommands

	def __init__(self, name, keys, description, repeatable=False):
		self.scriptName = SCRIPT_PREFIX + name
		self.keys = keys
		self.description = description
		self.repeatable = repeatable


def is_windows_command(info):
	return isinstance(info, WindowsCommand)


def category():
	# Translators: Category shown next to the built-in Windows commands in the command phrase editor.
	return _("Windows commands")


def _build():
	# Every description is also the phrase the user says, so keep them short and natural.
	# The key names are NVDA key names (see keyboardHandler.KeyboardInputGesture.fromName).
	table = (
		# ---- desktop and shell
		# Translators: A spoken command. It shows the Windows desktop (Windows+D). Keep it short: it is what the user says.
		("showDesktop", "windows+d", _("Show desktop"), False),
		# Translators: A spoken command. It moves focus to the taskbar (Windows+T).
		("showTaskbar", "windows+t", _("Show taskbar"), False),
		# Translators: A spoken command. It moves focus to the system tray, the notification area of the taskbar (Windows+B).
		("showSystemTray", "windows+b", _("Show system tray"), False),
		# Translators: A spoken command. It opens the Windows Start menu.
		("openStartMenu", "windows", _("Open Start menu"), False),
		# Translators: A spoken command. It opens File Explorer (Windows+E).
		("openFileExplorer", "windows+e", _("Open File Explorer"), False),
		# Translators: A spoken command. It opens the Run dialog (Windows+R).
		("openRunDialog", "windows+r", _("Open Run dialog"), False),
		# Translators: A spoken command. It opens the Windows Settings app (Windows+I).
		("openSettings", "windows+i", _("Open Windows settings"), False),
		# Translators: A spoken command. It opens Windows search (Windows+S).
		("openSearch", "windows+s", _("Open Windows search"), False),
		# Translators: A spoken command. It opens the Windows quick settings panel (Windows+A).
		("openQuickSettings", "windows+a", _("Open quick settings"), False),
		# Translators: A spoken command. It opens the Windows notification center (Windows+N).
		("openNotifications", "windows+n", _("Open notification center"), False),
		# Translators: A spoken command. It opens the Windows clipboard history (Windows+V).
		("openClipboardHistory", "windows+v", _("Open clipboard history"), False),
		# Translators: A spoken command. It opens the Windows emoji panel (Windows+period).
		("openEmojiPanel", "windows+.", _("Open emoji panel"), False),
		# Translators: A spoken command. It starts Windows voice typing (Windows+H).
		("startVoiceTyping", "windows+h", _("Start Windows voice typing"), False),
		# Translators: A spoken command. It opens the menu for projecting the screen to another display (Windows+P).
		("openProjectMenu", "windows+p", _("Open display projection menu"), False),
		# Translators: A spoken command. It starts the screen snipping tool (Windows+Shift+S).
		("takeScreenshot", "windows+shift+s", _("Take a screenshot"), False),
		# Translators: A spoken command. It opens Task Manager (Control+Shift+Escape).
		("openTaskManager", "control+shift+escape", _("Open Task Manager"), False),
		# Translators: A spoken command. It locks the computer (Windows+L).
		("lockComputer", "windows+l", _("Lock computer"), False),
		# ---- windows and virtual desktops
		# Translators: A spoken command. It minimizes every open window (Windows+M).
		("minimizeAll", "windows+m", _("Minimize all windows"), False),
		# Translators: A spoken command. It brings back the windows that were minimized (Windows+Shift+M).
		("restoreAll", "windows+shift+m", _("Restore minimized windows"), False),
		# Translators: A spoken command. It shows Task View, the overview of open windows and virtual desktops (Windows+Tab).
		("showTaskView", "windows+tab", _("Show task view"), False),
		# Translators: A spoken command. It switches to the window that was used before the current one (Alt+Tab).
		("switchWindow", "alt+tab", _("Switch to the previous window"), True),
		# Translators: A spoken command. It closes the current window (Alt+F4).
		("closeWindow", "alt+f4", _("Close window"), False),
		# Translators: A spoken command. It maximizes the current window (Windows+Up).
		("maximizeWindow", "windows+upArrow", _("Maximize window"), False),
		# Translators: A spoken command. It minimizes the current window, or restores it if it is maximized (Windows+Down).
		("minimizeWindow", "windows+downArrow", _("Minimize window"), False),
		# Translators: A spoken command. It snaps the current window to the left half of the screen (Windows+Left).
		("snapLeft", "windows+leftArrow", _("Snap window to the left"), False),
		# Translators: A spoken command. It snaps the current window to the right half of the screen (Windows+Right).
		("snapRight", "windows+rightArrow", _("Snap window to the right"), False),
		# Translators: A spoken command. It switches to the next virtual desktop (Control+Windows+Right).
		("nextDesktop", "control+windows+rightArrow", _("Next virtual desktop"), True),
		# Translators: A spoken command. It switches to the previous virtual desktop (Control+Windows+Left).
		("previousDesktop", "control+windows+leftArrow", _("Previous virtual desktop"), True),
		# Translators: A spoken command. It creates a new virtual desktop (Control+Windows+D).
		("newDesktop", "control+windows+d", _("New virtual desktop"), False),
		# Translators: A spoken command. It closes the current virtual desktop (Control+Windows+F4).
		("closeDesktop", "control+windows+f4", _("Close virtual desktop"), False),
		# ---- sound and media
		# Translators: A spoken command. It raises the system volume.
		("volumeUp", "volumeUp", _("Volume up"), True),
		# Translators: A spoken command. It lowers the system volume.
		("volumeDown", "volumeDown", _("Volume down"), True),
		# Translators: A spoken command. It mutes the system volume, or unmutes it if it is already muted.
		("volumeMute", "volumeMute", _("Mute or unmute volume"), False),
		# Translators: A spoken command. It plays or pauses the current media.
		("mediaPlayPause", "mediaPlayPause", _("Play or pause media"), False),
		# Translators: A spoken command. It skips to the next media track.
		("mediaNext", "mediaNextTrack", _("Next track"), True),
		# Translators: A spoken command. It goes back to the previous media track.
		("mediaPrevious", "mediaPrevTrack", _("Previous track"), True),
		# ---- editing
		# Translators: A spoken command. It copies the selection to the clipboard (Control+C).
		("copy", "control+c", _("Copy"), False),
		# Translators: A spoken command. It cuts the selection to the clipboard (Control+X).
		("cut", "control+x", _("Cut"), False),
		# Translators: A spoken command. It pastes the clipboard contents (Control+V).
		("paste", "control+v", _("Paste"), False),
		# Translators: A spoken command. It selects everything (Control+A).
		("selectAll", "control+a", _("Select all"), False),
		# Translators: A spoken command. It undoes the last action (Control+Z).
		("undo", "control+z", _("Undo"), True),
		# Translators: A spoken command. It redoes the action that was undone (Control+Y).
		("redo", "control+y", _("Redo"), True),
		# Translators: A spoken command. It saves the current document (Control+S).
		("save", "control+s", _("Save"), False),
		# Translators: A spoken command. It opens the find box of the current application (Control+F).
		("find", "control+f", _("Find"), False),
		# Translators: A spoken command. It prints the current document (Control+P).
		("print", "control+p", _("Print"), False),
		# Translators: A spoken command. It creates a new document or window in the current application (Control+N).
		("createNew", "control+n", _("Create new"), False),
		# Translators: A spoken command. It opens the dialog for choosing a file to open (Control+O).
		("openFile", "control+o", _("Open file"), False),
		# Translators: A spoken command. It renames the selected item in File Explorer (F2).
		("rename", "f2", _("Rename"), False),
		# Translators: A spoken command. It shows the properties of the selected item (Alt+Enter).
		("properties", "alt+enter", _("Properties"), False),
		# Translators: A spoken command. It refreshes the current window or page (F5).
		("refresh", "f5", _("Refresh"), False),
		# ---- navigation and tabs
		# Translators: A spoken command. It goes back to the previous page or folder (Alt+Left).
		("goBack", "alt+leftArrow", _("Go back"), True),
		# Translators: A spoken command. It goes forward to the next page or folder (Alt+Right).
		("goForward", "alt+rightArrow", _("Go forward"), True),
		# Translators: A spoken command. It opens a new tab (Control+T).
		("newTab", "control+t", _("New tab"), False),
		# Translators: A spoken command. It closes the current tab (Control+W).
		("closeTab", "control+w", _("Close tab"), True),
		# Translators: A spoken command. It reopens the tab that was closed last (Control+Shift+T).
		("reopenTab", "control+shift+t", _("Reopen closed tab"), False),
		# Translators: A spoken command. It switches to the next tab (Control+Tab).
		("nextTab", "control+tab", _("Next tab"), True),
		# Translators: A spoken command. It switches to the previous tab (Control+Shift+Tab).
		("previousTab", "control+shift+tab", _("Previous tab"), True),
	)
	return [WindowsCommand(name, keys, description, repeatable) for name, keys, description, repeatable in table]


COMMANDS = _build()


def all_commands():
	"""[WindowsCommand]: the built-in Windows commands."""
	return COMMANDS


def press(info):
	"""Presses the key combination of a Windows command the way NVDA does for its emulated keys."""
	import inputCore
	import keyboardHandler
	gesture = keyboardHandler.KeyboardInputGesture.fromName(info.keys)
	inputCore.manager.emulateGesture(gesture)
