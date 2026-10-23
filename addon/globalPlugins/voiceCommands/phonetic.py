# -*- coding: UTF-8 -*-
"""Phonetic matching of spoken text against NVDA command descriptions.

A Vosk model cannot learn new words, so a command whose description contains a foreign
or rare name ("Inti Illimani") is decoded as the closest sounding word sequence of the
model's language. Both the recognized text and the command descriptions are therefore
reduced to a coarse phonetic key and compared, so "inti ilimani" and "inti li mani" still
land on the "Inti-Illimani" command.

Only commands that NVDA itself lists in Input Gestures are ever matched.
"""
import heapq
import re
import unicodedata
from difflib import SequenceMatcher

from logHandler import log

THRESHOLD = 0.75			# minimum final score to accept a name match (0-1)
SHORT_PENALTY = 0.03		# extra threshold per phonetic-key character below SHORT_LIMIT
SHORT_LIMIT = 8			 # short queries are ambiguous, so they must match more closely
MIN_LENGTH = 4			  # shortest phonetic key worth matching
PREFILTER_CANDIDATES = 15   # candidates kept per query after the cheap n-gram pass

# --------------------------------------------------------------- phonetics
_FOLD = str.maketrans({
	"ı": "i", "İ": "i", "I": "i", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u",
	"ş": "s", "Ş": "s", "ç": "c", "Ç": "c", "ğ": "", "Ğ": "",
	"â": "a", "Â": "a", "î": "i", "Î": "i", "û": "u", "Û": "u",
})

# Applied after folding to plain ASCII. Order matters (longest first).
_DIGRAPHS = (("tch", "c"), ("sch", "s"), ("sh", "s"), ("ch", "c"), ("ph", "f"),
			 ("th", "t"), ("ck", "k"), ("qu", "k"), ("dj", "c"), ("zh", "c"))

# Consonants that speech recognition and spelling conventions commonly confuse share a class.
_CONSONANTS = {"b": "p", "p": "p", "d": "t", "t": "t", "g": "k", "k": "k", "q": "k",
			   "c": "c", "j": "c", "s": "s", "z": "s", "f": "f", "v": "f", "w": "f",
			   "m": "m", "n": "n", "l": "l", "r": "r"}
_VOWELS = {"a": "a", "e": "a", "i": "i", "y": "i", "o": "o", "u": "o"}


def _fold(text):
	text = text.translate(_FOLD).lower()
	text = unicodedata.normalize("NFKD", text)
	return "".join(c for c in text if not unicodedata.combining(c))


def _collapse(s):
	out = []
	for ch in s:
		if not out or out[-1] != ch:
			out.append(ch)
	return "".join(out)


def phonetic_keys(text):
	"""Return (full_key, consonant_key) for *text*.
	full_key keeps coarse vowels, consonant_key keeps consonants only; both ignore spaces
	so a name split differently by the recognizer still matches."""
	t = re.sub(r"[^a-z]+", " ", _fold(text))
	t = t.replace("x", "ks")
	for a, b in _DIGRAPHS:
		t = t.replace(a, b)
	full, consonants = [], []
	for ch in t:
		if ch in _CONSONANTS:
			full.append(_CONSONANTS[ch])
			consonants.append(_CONSONANTS[ch])
		elif ch in _VOWELS:
			full.append(_VOWELS[ch])
		# spaces and "h" are dropped on purpose
	return _collapse("".join(full)), _collapse("".join(consonants))


def _ngrams(s, n):
	if not s:
		return frozenset()
	if len(s) <= n:
		return frozenset((s,))
	return frozenset(s[i:i + n] for i in range(len(s) - n + 1))


def _coverage(query, target):
	"""Fraction of the query n-grams that also occur in the target."""
	if not query:
		return 0.0
	return len(query & target) / float(len(query))


def _partial_ratio(q, t):
	"""Best similarity of *q* against any window of *t* of the same length."""
	if not q or not t:
		return 0.0
	if len(q) >= len(t):
		return SequenceMatcher(None, q, t).ratio()
	best = 0.0
	for i in range(len(t) - len(q) + 1):
		r = SequenceMatcher(None, q, t[i:i + len(q)]).ratio()
		if r > best:
			best = r
			if r >= 0.999:
				break
	return best


# ------------------------------------------------------------------- index
class CommandIndex:
	"""Phonetic index over the command descriptions NVDA currently knows."""

	def __init__(self, commands):
		"""commands: {normalized description: (description, info)} as returned by collect_commands()."""
		self._items = []
		for key, (description, _info) in commands.items():
			full, consonants = phonetic_keys(description)
			if full:
				self._items.append((key, description, full, _ngrams(full, 3), _ngrams(consonants, 2)))

	def search(self, alternatives, threshold=THRESHOLD):
		"""Best command for the recognizer alternatives: (key, description, score) or None."""
		queries = []
		for alternative in alternatives:
			full, consonants = phonetic_keys(alternative)
			if len(full) >= MIN_LENGTH:
				queries.append((alternative, full, _ngrams(full, 3), _ngrams(consonants, 2)))
		if not queries or not self._items:
			return None
		best = None
		candidates = []
		for alternative, full, g3, g2 in queries:
			quick = ((0.5 * _coverage(g3, item[3]) + 0.5 * _coverage(g2, item[4]), i)
					 for i, item in enumerate(self._items))
			for quick_score, i in heapq.nlargest(PREFILTER_CANDIDATES, quick):
				key, description, item_full, _g3, _g2 = self._items[i]
				# Whole-string similarity matters most: a command must be said, not merely contained.
				score = 0.25 * quick_score + 0.35 * _partial_ratio(full, item_full) \
					+ 0.40 * SequenceMatcher(None, full, item_full).ratio()
				margin = score - (threshold + SHORT_PENALTY * max(0, SHORT_LIMIT - len(full)))
				candidates.append((score, description, alternative))
				if best is None or margin > best[3]:
					best = (key, description, score, margin)
		for score, description, alternative in sorted(candidates, reverse=True)[:3]:
			log.debug("Voice command phonetic candidate: %.2f  %s  <- %r" % (score, description, alternative))
		if best and best[3] >= 0:
			return best[0], best[1], best[2]
		return None
