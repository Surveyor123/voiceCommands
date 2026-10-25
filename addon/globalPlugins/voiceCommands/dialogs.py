# -*- coding: UTF-8 -*-
"""Voice Commands dialogs: the candidate list and the command phrase editor."""
import copy

import addonHandler
import gui
import ui
import wx

from . import storage, userCommands
from .text import lower, normalize


def _lower(text):
	# Dotted and dotless i compare equal, so searching "input" also finds "Input" with Turkish casing.
	return lower(text).replace("ı", "i")

addonHandler.initTranslation()


class _BaseDialog(wx.Dialog):
	SINGLE_INSTANCE = False
	_open = {}

	def __init__(self, parent, title):
		super().__init__(parent, title=title)
		self.Bind(wx.EVT_CLOSE, self._onClose)

	def display(self):
		if self.SINGLE_INSTANCE:
			previous = _BaseDialog._open.get(type(self))
			if previous:
				try:
					previous.Raise()
					self.Destroy()
					return
				except Exception:
					pass  # the previous window has already been destroyed
			_BaseDialog._open[type(self)] = self
		gui.mainFrame.prePopup()
		self.Show()
		self.Raise()
		self.CentreOnScreen()

	def _onClose(self, evt):
		if _BaseDialog._open.get(type(self)) is self:
			del _BaseDialog._open[type(self)]
		gui.mainFrame.postPopup()
		self.Destroy()

	def _buttons(self, ok_label, ok_handler):
		sizer = wx.StdDialogButtonSizer()
		ok = wx.Button(self, wx.ID_OK, ok_label)
		ok.SetDefault()
		# Translators: Label of the button that closes a Voice Commands dialog without applying anything.
		cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
		sizer.AddButton(ok)
		sizer.AddButton(cancel)
		sizer.Realize()
		ok.Bind(wx.EVT_BUTTON, ok_handler)
		cancel.Bind(wx.EVT_BUTTON, lambda e: self.Close())
		return sizer


class CandidateListDialog(_BaseDialog):
	"""Lets the user choose when several commands could match what was said."""

	def __init__(self, parent, title, labels, on_selected):
		super().__init__(parent, title)
		self._on_selected = on_selected
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the list of possible commands the user can choose from.
		main.Add(wx.StaticText(self, label=_("Choose the command to run:")), 0, wx.ALL, 8)
		self.list = wx.ListBox(self, choices=labels, size=(520, 180))
		self.list.SetSelection(0)
		main.Add(self.list, 1, wx.ALL | wx.EXPAND, 8)
		# Translators: Label of the button that runs the command chosen in the list.
		main.Add(self._buttons(_("Run"), self._onOk), 0, wx.ALL | wx.ALIGN_RIGHT, 8)
		self.list.Bind(wx.EVT_LISTBOX_DCLICK, self._onOk)
		self.SetSizerAndFit(main)
		self.list.SetFocus()

	def _onOk(self, evt):
		index = self.list.GetSelection()
		if index < 0:
			return
		self.Close()
		self._on_selected(index)


class PhraseEditorDialog(_BaseDialog):
	"""Lets the user define their own spoken phrases (aliases) for commands.

	commands: [(command_id, category, description)] of the currently available commands."""
	SINGLE_INSTANCE = True

	def __init__(self, parent, commands, on_done):
		# Translators: Title of the dialog where the user edits the phrases that trigger commands.
		super().__init__(parent, _("Command phrase editor"))
		self.commands = commands
		self.on_done = on_done
		self.data = copy.deepcopy(storage.load_aliases())
		self.visible = []

		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the edit field used to filter the list of commands.
		main.Add(wx.StaticText(self, label=_("Search commands:")), 0, wx.ALL, 6)
		self.search = wx.TextCtrl(self)
		main.Add(self.search, 0, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the list of commands in the phrase editor.
		main.Add(wx.StaticText(self, label=_("Commands:")), 0, wx.ALL, 6)
		self.commandList = wx.ListBox(self, size=(560, 170))
		main.Add(self.commandList, 1, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of a check box. When it is cleared, the command can only be triggered by the user's own phrases.
		self.keepOriginal = wx.CheckBox(self, label=_("Also use the original description"))
		main.Add(self.keepOriginal, 0, wx.ALL, 6)
		# Translators: Label of the list of phrases the user has defined for the selected command.
		main.Add(wx.StaticText(self, label=_("Phrases you say for this command:")), 0, wx.ALL, 6)
		self.phraseList = wx.ListBox(self, size=(560, 100))
		main.Add(self.phraseList, 0, wx.ALL | wx.EXPAND, 6)
		row = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label of a button that moves the selected phrase into the edit field so it can be changed.
		self.editButton = wx.Button(self, label=_("Edit selected phrase"))
		# Translators: Label of a button that deletes the selected phrase.
		self.deleteButton = wx.Button(self, label=_("Delete selected phrase"))
		row.Add(self.editButton, 0, wx.ALL, 4)
		row.Add(self.deleteButton, 0, wx.ALL, 4)
		main.Add(row, 0)
		# Translators: Label of the edit field where a new phrase for a command is typed.
		main.Add(wx.StaticText(self, label=_("New phrase:")), 0, wx.ALL, 6)
		self.newPhrase = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		main.Add(self.newPhrase, 0, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the button that adds the typed phrase to the selected command.
		self.addButton = wx.Button(self, label=_("Add phrase"))
		main.Add(self.addButton, 0, wx.ALL, 6)
		# Translators: Label of the button that saves the changes in the phrase editor.
		main.Add(self._buttons(_("Save"), self._onSave), 0, wx.ALL | wx.ALIGN_RIGHT, 6)

		self.search.Bind(wx.EVT_TEXT, lambda e: self._refreshCommands())
		self.commandList.Bind(wx.EVT_LISTBOX, lambda e: self._commandSelected())
		self.keepOriginal.Bind(wx.EVT_CHECKBOX, self._onKeepOriginal)
		self.addButton.Bind(wx.EVT_BUTTON, self._onAdd)
		self.newPhrase.Bind(wx.EVT_TEXT_ENTER, self._onAdd)
		self.deleteButton.Bind(wx.EVT_BUTTON, self._onDelete)
		self.editButton.Bind(wx.EVT_BUTTON, self._onEdit)
		self.SetSizerAndFit(main)
		self._refreshCommands()
		self.search.SetFocus()

	# ---- helpers
	def _entry(self, command_id):
		return self.data.setdefault(command_id, {"aliases": [], "keep_original": True})

	def _currentId(self):
		index = self.commandList.GetSelection()
		if index < 0 or index >= len(self.visible):
			return None
		return self.visible[index][0]

	def _label(self, command):
		count = len(self.data.get(command[0], {}).get("aliases", []))
		if not count:
			# Translators: Entry in the list of commands. {description} is the command description, {category} its category.
			return _("{description} - {category}").format(description=command[2], category=command[1])
		# Translators: Entry in the list of commands that has user-defined phrases. {count} is the number of phrases.
		return ngettext(
			"{description} - {category} ({count} phrase)",
			"{description} - {category} ({count} phrases)",
			count,
		).format(description=command[2], category=command[1], count=count)

	def _refreshCommands(self):
		needle = _lower(self.search.GetValue().strip())
		self.visible = [c for c in self.commands if not needle or needle in _lower(c[2] + " " + c[1])]
		self.commandList.Set([self._label(c) for c in self.visible])
		if self.visible:
			self.commandList.SetSelection(0)
		self._commandSelected()

	def _commandSelected(self):
		command_id = self._currentId()
		entry = self.data.get(command_id, {}) if command_id else {}
		self.phraseList.Set(list(entry.get("aliases", [])))
		self.keepOriginal.SetValue(entry.get("keep_original", True) if command_id else True)
		for control in (self.keepOriginal, self.addButton, self.deleteButton, self.editButton,
						self.newPhrase, self.phraseList):
			control.Enable(command_id is not None)

	def _updateLabel(self):
		index = self.commandList.GetSelection()
		if 0 <= index < len(self.visible):
			self.commandList.SetString(index, self._label(self.visible[index]))
			self.commandList.SetSelection(index)

	# ---- events
	def _onKeepOriginal(self, evt):
		command_id = self._currentId()
		if command_id:
			self._entry(command_id)["keep_original"] = self.keepOriginal.GetValue()

	def _onAdd(self, evt):
		command_id = self._currentId()
		text = self.newPhrase.GetValue().strip()
		if not command_id:
			return
		if not text:
			# Translators: Spoken when the user tries to add an empty phrase.
			ui.message(_("The phrase is empty"))
			return
		phrases = self._entry(command_id)["aliases"]
		if text not in phrases:
			phrases.append(text)
		self.newPhrase.SetValue("")
		self.phraseList.Set(list(phrases))
		self._updateLabel()
		# Translators: Spoken after a phrase has been added to a command.
		ui.message(_("Added"))

	def _removeSelected(self):
		command_id, index = self._currentId(), self.phraseList.GetSelection()
		if not command_id or index < 0:
			return None
		phrases = self._entry(command_id)["aliases"]
		text = phrases.pop(index)
		self.phraseList.Set(list(phrases))
		if phrases:
			self.phraseList.SetSelection(min(index, len(phrases) - 1))
		self._updateLabel()
		return text

	def _onDelete(self, evt):
		if self._removeSelected() is not None:
			# Translators: Spoken after a phrase has been deleted from a command.
			ui.message(_("Deleted"))

	def _onEdit(self, evt):
		text = self._removeSelected()
		if text is not None:
			self.newPhrase.SetValue(text)
			self.newPhrase.SetFocus()
			self.newPhrase.SetInsertionPointEnd()

	def _onSave(self, evt):
		cleaned = {k: v for k, v in self.data.items() if v["aliases"] or not v["keep_original"]}
		try:
			storage.save_aliases(cleaned)
		except Exception:
			# Translators: Spoken when the phrases could not be saved.
			ui.message(_("Could not save"))
			raise
		self.Close()
		self.on_done()


class TeachDialog(_BaseDialog):
	"""Adds what the recognizer heard as spoken phrases of a command the user picks.

	The model cannot learn new words, but it always writes names it does not know as words it does
	know ("Zülfü Livaneli" becomes "gül suyu divane izi"). Saving those words as a phrase puts them
	into the speech grammar, so the same pronunciation finds the command next time.

	commands: [(command_id, category, description)]; heard: [str] texts the recognizer produced."""
	SINGLE_INSTANCE = True

	def __init__(self, parent, commands, heard, on_done):
		# Translators: Title of the dialog that teaches the add-on a spoken phrase.
		super().__init__(parent, _("Teach the last spoken phrase"))
		self.commands = commands
		self.on_done = on_done
		self.visible = []
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the list of texts the recognizer heard; the checked ones are saved as phrases.
		main.Add(wx.StaticText(self, label=_("Heard (check the ones to save as phrases):")), 0, wx.ALL, 6)
		self.heardList = wx.CheckListBox(self, choices=heard, size=(560, 110))
		self.heardList.SetCheckedItems(list(range(len(heard))))
		main.Add(self.heardList, 0, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the edit field used to filter the list of commands.
		main.Add(wx.StaticText(self, label=_("Search commands:")), 0, wx.ALL, 6)
		self.search = wx.TextCtrl(self)
		main.Add(self.search, 0, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the list of commands the heard phrases can be added to.
		main.Add(wx.StaticText(self, label=_("Command to run when you say this:")), 0, wx.ALL, 6)
		self.commandList = wx.ListBox(self, size=(560, 170))
		main.Add(self.commandList, 1, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the button that saves the checked phrases for the selected command.
		main.Add(self._buttons(_("Save phrases"), self._onSave), 0, wx.ALL | wx.ALIGN_RIGHT, 6)
		self.search.Bind(wx.EVT_TEXT, lambda e: self._refresh())
		self.commandList.Bind(wx.EVT_LISTBOX_DCLICK, self._onSave)
		self.SetSizerAndFit(main)
		self._refresh()
		self.heardList.SetFocus()

	def _refresh(self):
		needle = _lower(self.search.GetValue().strip())
		self.visible = [c for c in self.commands if not needle or needle in _lower(c[2] + " " + c[1])]
		# Translators: Entry in the list of commands. {description} is the command description, {category} its category.
		self.commandList.Set([_("{description} - {category}").format(description=c[2], category=c[1]) for c in self.visible])
		if self.visible:
			self.commandList.SetSelection(0)

	def _onSave(self, evt):
		index = self.commandList.GetSelection()
		if index < 0 or index >= len(self.visible):
			return
		phrases = [self.heardList.GetString(i) for i in self.heardList.GetCheckedItems()]
		if not phrases:
			# Translators: Spoken when the user saves without checking any heard text.
			ui.message(_("Check at least one phrase"))
			return
		data = storage.load_aliases()
		entry = data.setdefault(self.visible[index][0], {"aliases": [], "keep_original": True})
		for phrase in phrases:
			if phrase not in entry["aliases"]:
				entry["aliases"].append(phrase)
		try:
			storage.save_aliases(data)
		except Exception:
			# Translators: Spoken when the phrases could not be saved.
			ui.message(_("Could not save"))
			raise
		self.Close()
		self.on_done()


class UserCommandEditDialog(wx.Dialog):
	"""Adds or edits one user command: what to say, what it does, and its target."""

	def __init__(self, parent, entry, taken_names):
		# Translators: Title of the dialog for adding a command of your own.
		title = _("Edit command") if entry else _("Add command")
		super().__init__(parent, title=title)
		self.entry = entry
		self.taken_names = taken_names
		self.result = None
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the edit field where the user types the phrase they will say for their own command.
		main.Add(wx.StaticText(self, label=_("What you say:")), 0, wx.ALL, 6)
		self.name = wx.TextCtrl(self, size=(460, -1))
		main.Add(self.name, 0, wx.ALL | wx.EXPAND, 6)
		# Translators: Label of the list where the user chooses what their own command does.
		main.Add(wx.StaticText(self, label=_("What it does:")), 0, wx.ALL, 6)
		self.kind = wx.Choice(self, choices=[
			# Translators: A choice for what a command of your own does.
			_("Open a program, file, folder or web address"),
			# Translators: A choice for what a command of your own does.
			_("Press a key combination"),
		])
		main.Add(self.kind, 0, wx.ALL | wx.EXPAND, 6)

		self.openPanel = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the edit field for the program, file, folder or web address a command opens.
		self.openPanel.Add(wx.StaticText(self, label=_("Program, file, folder or web address:")), 0, wx.ALL, 6)
		self.target = wx.TextCtrl(self)
		self.openPanel.Add(self.target, 0, wx.ALL | wx.EXPAND, 6)
		row = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label of a button that lets the user pick a file or program with a file dialog.
		self.fileButton = wx.Button(self, label=_("Choose file..."))
		# Translators: Label of a button that lets the user pick a folder with a folder dialog.
		self.folderButton = wx.Button(self, label=_("Choose folder..."))
		row.Add(self.fileButton, 0, wx.ALL, 4)
		row.Add(self.folderButton, 0, wx.ALL, 4)
		self.openPanel.Add(row, 0)
		main.Add(self.openPanel, 0, wx.EXPAND)

		self.keysPanel = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the edit field for the key combination a command presses. Keep "control+shift+n" as it is: key names are not translated.
		self.keysPanel.Add(wx.StaticText(self, label=_("Keys (for example control+shift+n):")), 0, wx.ALL, 6)
		self.keys = wx.TextCtrl(self)
		self.keysPanel.Add(self.keys, 0, wx.ALL | wx.EXPAND, 6)
		main.Add(self.keysPanel, 0, wx.EXPAND)

		main.Add(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.ALIGN_RIGHT, 6)
		self.SetSizerAndFit(main)
		self._main = main

		if entry:
			self.name.SetValue(entry["name"])
			self.kind.SetSelection(1 if entry["kind"] == "keys" else 0)
			(self.keys if entry["kind"] == "keys" else self.target).SetValue(entry["target"])
		else:
			self.kind.SetSelection(0)
		self._showKind()
		self.kind.Bind(wx.EVT_CHOICE, lambda e: self._showKind())
		self.fileButton.Bind(wx.EVT_BUTTON, self._onFile)
		self.folderButton.Bind(wx.EVT_BUTTON, self._onFolder)
		self.Bind(wx.EVT_BUTTON, self._onOk, id=wx.ID_OK)
		self.name.SetFocus()

	def _isKeys(self):
		return self.kind.GetSelection() == 1

	def _showKind(self):
		keys = self._isKeys()
		self._main.Show(self.openPanel, not keys, recursive=True)
		self._main.Show(self.keysPanel, keys, recursive=True)
		self.Layout()
		self.Fit()

	def _onFile(self, evt):
		# Translators: Title of the dialog for choosing a file or program.
		with wx.FileDialog(self, _("Choose a file or program"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.target.SetValue(dlg.GetPath())

	def _onFolder(self, evt):
		# Translators: Title of the dialog for choosing a folder.
		with wx.DirDialog(self, _("Choose a folder")) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.target.SetValue(dlg.GetPath())

	def _problem(self, message, control):
		wx.MessageBox(message, self.GetTitle(), wx.OK | wx.ICON_WARNING, self)
		control.SetFocus()

	def _onOk(self, evt):
		name = self.name.GetValue().strip()
		if not name:
			# Translators: Shown when the user did not type what they will say for their own command.
			return self._problem(_("Type what you say for this command."), self.name)
		if normalize(name) in self.taken_names:
			# Translators: Shown when another command of the user already has the same name.
			return self._problem(_("You already have a command with this name."), self.name)
		if self._isKeys():
			keys = self.keys.GetValue().strip()
			if not keys:
				# Translators: Shown when the user did not type the keys a command should press.
				return self._problem(_("Type the keys to press."), self.keys)
			error = userCommands.validate_keys(keys)
			if error:
				# Translators: Shown when NVDA does not understand the typed keys. {error} describes the problem.
				return self._problem(_("These keys are not valid: {error}").format(error=error), self.keys)
			kind, target = userCommands.KIND_KEYS, keys
		else:
			target = self.target.GetValue().strip()
			if not target:
				# Translators: Shown when the user did not type what a command should open.
				return self._problem(_("Type what the command should open."), self.target)
			kind = userCommands.KIND_OPEN
		self.result = {
			"id": self.entry["id"] if self.entry else userCommands.new_id(),
			"name": name, "kind": kind, "target": target,
		}
		self.EndModal(wx.ID_OK)


class UserCommandsDialog(_BaseDialog):
	"""Lists the user's own commands and lets them add, change and delete them."""
	SINGLE_INSTANCE = True

	def __init__(self, parent, on_done):
		# Translators: Title of the dialog where the user manages their own commands.
		super().__init__(parent, _("My commands"))
		self.on_done = on_done
		self.entries = [
			{"id": c.id, "name": c.description, "kind": c.kind, "target": c.target} for c in userCommands.load()]
		main = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of the list of the user's own commands.
		main.Add(wx.StaticText(self, label=_("Your commands:")), 0, wx.ALL, 6)
		self.list = wx.ListBox(self, size=(560, 180))
		main.Add(self.list, 1, wx.ALL | wx.EXPAND, 6)
		row = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label of a button that adds a command of the user's own.
		self.addButton = wx.Button(self, label=_("Add"))
		# Translators: Label of a button that changes the selected command.
		self.editButton = wx.Button(self, label=_("Edit"))
		# Translators: Label of a button that deletes the selected command.
		self.deleteButton = wx.Button(self, label=_("Delete"))
		for button in (self.addButton, self.editButton, self.deleteButton):
			row.Add(button, 0, wx.ALL, 4)
		main.Add(row, 0)
		# Translators: Label of the button that saves the user's own commands.
		main.Add(self._buttons(_("Save"), self._onSave), 0, wx.ALL | wx.ALIGN_RIGHT, 6)
		self.addButton.Bind(wx.EVT_BUTTON, self._onAdd)
		self.editButton.Bind(wx.EVT_BUTTON, self._onEdit)
		self.deleteButton.Bind(wx.EVT_BUTTON, self._onDelete)
		self.list.Bind(wx.EVT_LISTBOX_DCLICK, self._onEdit)
		self.SetSizerAndFit(main)
		self._refresh()
		self.list.SetFocus()

	def _label(self, entry):
		if entry["kind"] == userCommands.KIND_KEYS:
			# Translators: Entry in the list of the user's commands that press keys. {name} is what the user says, {keys} the key combination.
			return _("{name} - presses {keys}").format(name=entry["name"], keys=entry["target"])
		# Translators: Entry in the list of the user's commands that open something. {name} is what the user says, {target} what is opened.
		return _("{name} - opens {target}").format(name=entry["name"], target=entry["target"])

	def _refresh(self, select=0):
		self.list.Set([self._label(e) for e in self.entries])
		if self.entries:
			self.list.SetSelection(max(0, min(select, len(self.entries) - 1)))
		for button in (self.editButton, self.deleteButton):
			button.Enable(bool(self.entries))

	def _edit(self, index):
		entry = self.entries[index] if index is not None else None
		taken = {normalize(e["name"]) for i, e in enumerate(self.entries) if i != index}
		with UserCommandEditDialog(self, entry, taken) as dlg:
			if dlg.ShowModal() == wx.ID_OK and dlg.result:
				if index is None:
					self.entries.append(dlg.result)
					index = len(self.entries) - 1
				else:
					self.entries[index] = dlg.result
				self._refresh(index)

	def _onAdd(self, evt):
		self._edit(None)

	def _onEdit(self, evt):
		index = self.list.GetSelection()
		if index >= 0:
			self._edit(index)

	def _onDelete(self, evt):
		index = self.list.GetSelection()
		if index >= 0:
			del self.entries[index]
			self._refresh(index)
			# Translators: Spoken after one of the user's own commands has been deleted.
			ui.message(_("Deleted"))

	def _onSave(self, evt):
		try:
			userCommands.save(self.entries)
		except Exception:
			# Translators: Spoken when the phrases could not be saved.
			ui.message(_("Could not save"))
			raise
		self.Close()
		self.on_done()
