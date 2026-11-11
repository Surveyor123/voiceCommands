# -*- coding: UTF-8 -*-
"""The press count of a phrase of the user: "say the date x2" presses the "say the time" command twice.

The count is stored as a trailing " x2" ... " x5" of the phrase, so the phrase files stay plain text.
The phrase editor offers the count as a list, so nobody has to type it. When it is typed or imported,
look-alikes of the x that exist on other keyboards are accepted too (Cyrillic and Greek letters, the
multiplication sign, an asterisk, full-width forms), and so are digits of other scripts."""
import re

MAX = 5  # most presses a phrase can stand for

CANONICAL = "x"  # what is written when a count is stored
_LETTERS = "xX\uff58\uff38\u0445\u0425\u03c7\u03a7"  # x X, full-width x X, Cyrillic ha, Greek chi
_SYMBOLS = "\u00d7\u2715\u2716\u2717*\uff0a"  # multiplication sign, ballot-x signs, asterisk, full-width asterisk
# A letter must be set apart from the phrase by a space ("windows x2"); a symbol need not be.
_RE = re.compile(r"(?:\s+[%s]|\s*[%s])\s*(\d)$" % (_LETTERS, _SYMBOLS))


def split(phrase):
	"""(phrase without its count, count); the count is 1 when the phrase has none."""
	text = phrase.strip()
	match = _RE.search(text)
	if match:
		count = int(match.group(1))  # int() reads the digits of any script
		if 2 <= count <= MAX:
			return text[:match.start()].strip(), count
	return text, 1


def join(text, count):
	"""The phrase as it is stored."""
	text = text.strip()
	return text if count <= 1 else "%s %s%d" % (text, CANONICAL, min(count, MAX))
