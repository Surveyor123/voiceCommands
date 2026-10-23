# -*- coding: UTF-8 -*-
"""Lowers the volume of other applications while a voice command is being listened for.

Playing audio would otherwise reach the microphone and confuse the recognizer. Every audio
session except NVDA's own is set to DUCK_FACTOR of its volume when listening starts, and put
back when it stops. A session whose volume the user changed in the meantime is left alone.

Volumes are changed through the pycaw library bundled with NVDA. Because Windows remembers
per-application volumes, the ducked values are also written to a small recovery file; if NVDA
ends while ducked, the original volumes are restored the next time the add-on starts.

All audio work runs on one background thread, in order, so a quick "start" right after a
"restore" can never record the ducked volumes as the original ones."""
import os
import queue
import threading

from logHandler import log

from . import storage

DUCK_FACTOR = 0.2          # ducked volume = original volume * DUCK_FACTOR
TOLERANCE = 0.02           # how close a volume must be to the ducked value to be restored
RECOVERY_FILE = "ducking-recovery.json"


class AudioDucker:
    def __init__(self):
        self._jobs = queue.Queue()
        self._saved = []   # (volume interface, original, ducked, process name)
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

    def _duck(self):
        if self._saved:
            return  # already ducked
        for name, volume in self._sessions():
            try:
                original = volume.GetMasterVolume()
                ducked = original * DUCK_FACTOR
                volume.SetMasterVolume(ducked, None)
                self._saved.append((volume, original, ducked, name))
            except Exception:
                continue
        if self._saved:
            storage.write_json_list(RECOVERY_FILE, [
                {"process": name, "original": original, "ducked": ducked}
                for _volume, original, ducked, name in self._saved])
            log.debug("Voice command: lowered the volume of %d audio session(s)" % len(self._saved))

    def _restore(self):
        if not self._saved:
            return
        for volume, original, ducked, _name in self._saved:
            try:
                if abs(volume.GetMasterVolume() - ducked) < TOLERANCE:  # unchanged by the user
                    volume.SetMasterVolume(original, None)
            except Exception:
                continue  # the session has ended
        self._saved = []
        storage.delete_file(RECOVERY_FILE)
        log.debug("Voice command: restored the volume of audio sessions")

    def _recover(self):
        """After a crash or an abrupt exit, undo ducking left over from the previous run."""
        leftover = storage.read_json_list(RECOVERY_FILE)
        if not leftover:
            return
        for name, volume in self._sessions():
            for entry in leftover:
                try:
                    if entry.get("process") == name and name \
                            and abs(volume.GetMasterVolume() - float(entry["ducked"])) < TOLERANCE:
                        volume.SetMasterVolume(float(entry["original"]), None)
                        break
                except Exception:
                    continue
        storage.delete_file(RECOVERY_FILE)
        log.debug("Voice command: restored audio volumes left ducked by a previous run")
