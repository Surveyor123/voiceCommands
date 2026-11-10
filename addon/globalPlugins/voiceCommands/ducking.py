# -*- coding: UTF-8 -*-
"""Lowers the volume of other applications while a voice command is being listened for.

Playing audio would otherwise reach the microphone and confuse the recognizer. Every audio
session except NVDA's own is set to DUCK_FACTOR of its volume when listening starts, and put
back when it stops. A session whose volume the user changed in the meantime is left alone.

Volumes are changed through the pycaw library bundled with NVDA. Because Windows remembers
per-application volumes, the ducked values are also written to a small recovery file; if NVDA
ends while ducked, the original volumes are restored the next time the add-on starts.

Players such as browsers close and reopen their audio session (pause, next track), and Windows
then opens the new session at the remembered, ducked volume. So restoring does not rely on the
saved session objects alone: the current sessions are searched for the same process still at
the ducked volume. Entries that could not be restored at all stay "pending" (and in the recovery
file) and are healed before the next ducking, so a lowered volume is never taken for the original.

All audio work runs on one background thread, in order, so a quick "start" right after a
"restore" can never record the ducked volumes as the original ones."""
import os
import queue
import threading
import time

from logHandler import log

from . import storage

DUCK_FACTOR = 0.2		  # ducked volume = original volume * DUCK_FACTOR
TOLERANCE = 0.02		   # how close a volume must be to the ducked value to be restored
RECOVERY_FILE = "ducking-recovery.json"
PENDING_MAX_AGE = 24 * 3600  # seconds after which an unrestored entry is given up
PENDING_MAX = 50
RESWEEP_DELAYS = (1.5, 4.0)  # seconds after a restore: look again for sessions a command (next track) opened
RESWEEP_WINDOW = 10.0		# a restore is swept again only within this many seconds


class AudioDucker:
	def __init__(self):
		self._jobs = queue.Queue()
		self._saved = []	# (volume interface, original, ducked, process name)
		self._pending = []  # entries {"process", "original", "ducked", "time"} not restored yet
		self._recent = None  # (entries, time) of the last restore, swept again shortly after
		self._unavailable = False
		self._thread = threading.Thread(target=self._worker, daemon=True)
		self._thread.start()
		self._jobs.put("recover")

	def duck(self):
		"""Lowers the volume of other applications (in the background)."""
		self._jobs.put("duck")

	def restore(self):
		"""Puts the volumes back (in the background). Safe to call when nothing is ducked."""
		self._jobs.put("restore")

	def close(self):
		"""Restores volumes and stops the worker; waits briefly so NVDA does not exit while ducked."""
		self._jobs.put("restore")
		self._jobs.put("stop")
		self._thread.join(3)

	# ------------------------------------------------------------ worker
	def _worker(self):
		try:
			import comtypes
			comtypes.CoInitialize()
		except Exception:
			comtypes = None
		try:
			while True:
				job = self._jobs.get()
				if job == "stop":
					return
				if self._unavailable:
					continue
				try:
					getattr(self, "_" + job)()
				except ImportError:
					self._unavailable = True
					log.warning("Audio ducking is unavailable: pycaw/comtypes not found")
				except Exception:
					log.exception("Audio ducking job failed: %s" % job)
		finally:
			if comtypes is not None:
				try:
					comtypes.CoUninitialize()
				except Exception:
					pass

	@staticmethod
	def _sessions():
		from pycaw.api.audioclient import ISimpleAudioVolume
		from pycaw.utils import AudioUtilities
		own_pid = os.getpid()
		for session in AudioUtilities.GetAllSessions():
			try:
				pid = session.ProcessId
				if pid in (0, own_pid):  # pid 0 is the system sounds session
					continue
				try:
					name = session.Process.name() if session.Process is not None else ""
				except Exception:
					name = ""
				yield name, session._ctl.QueryInterface(ISimpleAudioVolume)
			except Exception:
				continue

	# ------------------------------------------------------------ helpers
	def _entries(self):
		now = time.time()
		return [{"process": name, "original": original, "ducked": ducked, "time": now}
				for _volume, original, ducked, name in self._saved]

	def _sweep(self, entries):
		"""Restores every current session that belongs to a process of *entries* and is still at that
		entry's ducked volume, whether or not it is the session that was ducked. Returns the set of
		indexes of the entries that matched a session."""
		matched = set()
		if not entries:
			return matched
		for name, volume in self._sessions():
			if not name:
				continue
			try:
				current = volume.GetMasterVolume()
			except Exception:
				continue
			for index, entry in enumerate(entries):
				try:
					if entry["process"] == name and abs(current - float(entry["ducked"])) < TOLERANCE:
						volume.SetMasterVolume(float(entry["original"]), None)
						matched.add(index)
						log.debug("Voice command: restored %s (%.2f -> %.2f)" % (name, current, float(entry["original"])))
						break
				except Exception:
					continue
		return matched

	def _store_pending(self):
		now = time.time()
		self._pending = [e for e in self._pending if now - float(e.get("time", now)) < PENDING_MAX_AGE]
		self._pending = self._pending[-PENDING_MAX:]
		if self._pending:
			storage.write_json_list(RECOVERY_FILE, self._pending)
		else:
			storage.delete_file(RECOVERY_FILE)

	def _heal_pending(self):
		if not self._pending:
			return
		matched = self._sweep(self._pending)
		self._pending = [e for i, e in enumerate(self._pending) if i not in matched]
		self._store_pending()

	# ------------------------------------------------------------ jobs
	def _duck(self):
		if self._saved:
			return  # already ducked
		# A volume left lowered by an earlier failed restore must not be taken for the original.
		self._heal_pending()
		self._recent = None
		for name, volume in self._sessions():
			try:
				original = volume.GetMasterVolume()
				ducked = original * DUCK_FACTOR
				volume.SetMasterVolume(ducked, None)
				self._saved.append((volume, original, ducked, name))
			except Exception:
				continue
		if self._saved:
			storage.write_json_list(RECOVERY_FILE, self._pending + self._entries())
			log.debug("Voice command: lowered the volume of %d audio session(s)" % len(self._saved))

	def _restore(self):
		if not self._saved:
			return
		entries = self._entries()
		failed = set()
		for index, (volume, original, ducked, name) in enumerate(self._saved):
			try:
				current = volume.GetMasterVolume()
				if abs(current - ducked) < TOLERANCE:  # unchanged by the user
					volume.SetMasterVolume(original, None)
				else:
					log.debug("Voice command: %s left alone, volume is %.2f (ducked %.2f)" % (name, current, ducked))
			except Exception:
				failed.add(index)  # the session ended, or was replaced by a new one
		self._saved = []
		# Sessions the player opened again meanwhile start at the remembered, ducked volume.
		matched = self._sweep(entries)
		for index in sorted(failed - matched):
			log.debug("Voice command: could not restore %s yet, keeping it pending" % entries[index]["process"])
			self._pending.append(entries[index])
		self._store_pending()
		log.debug("Voice command: restored the volume of audio sessions")
		# The command that was just spoken (e.g. next track) may open a new audio session after this
		# point, at the ducked volume. Look again a little later.
		self._recent = (entries, time.time())
		for delay in RESWEEP_DELAYS:
			timer = threading.Timer(delay, self._jobs.put, ("resweep",))
			timer.daemon = True
			timer.start()

	def _resweep(self):
		if self._saved or not self._recent:
			return
		entries, stamp = self._recent
		if time.time() - stamp > RESWEEP_WINDOW:
			self._recent = None
			return
		matched = self._sweep(entries)
		if matched:
			log.debug("Voice command: restored %d session(s) opened after the restore" % len(matched))

	def _recover(self):
		"""After a crash or an abrupt exit, undo ducking left over from the previous run."""
		leftover = storage.read_json_list(RECOVERY_FILE)
		if not leftover:
			return
		matched = self._sweep(leftover)
		self._pending = [e for i, e in enumerate(leftover) if i not in matched]
		self._store_pending()
		log.debug("Voice command: restored audio volumes left ducked by a previous run")