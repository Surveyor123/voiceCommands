# -*- coding: UTF-8 -*-
"""Messages of the add-on that are not lost when NVDA speaks something else right after them."""

import ui
import wx
from speech.priorities import Spri

# A focus change, such as a dialog closing, makes NVDA cancel and replace what it is saying.
# A message that follows such a change is therefore sent a moment later.
AFTER_FOCUS_CHANGE = 700


_menuDelay = 0


class afterMenu:
	"""Messages spoken inside this block wait until the closing menu has returned focus."""

	def __enter__(self):
		global _menuDelay
		_menuDelay = AFTER_FOCUS_CHANGE

	def __exit__(self, *exc):
		global _menuDelay
		_menuDelay = 0


def say(text, delay=0):
	"""Speaks and brailles text now, or after delay milliseconds. Must be called on the main thread.

	Speech of NOW priority is not queued behind, or dropped for, the ordinary speech of events
	such as a focus change or a new window."""
	delay = delay or _menuDelay
	if delay:
		wx.CallLater(delay, say, text)
		return
	ui.message(text, speechPriority=Spri.NOW)
