# Voice Commands for NVDA

Run NVDA commands by speaking instead of pressing keys.

NVDA already has a description for every command in its Input Gestures dialog. Voice Commands listens through your microphone, turns your speech into text with an offline speech engine ([Vosk](https://alphacephei.com/vosk/) by default, or a [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) model that you choose, see The speech model), matches that text against those descriptions (and against phrases you define yourself), and runs the command that fits best. Your voice is processed on your computer and never leaves it.

## How it works

1.  When you start listening, the add-on collects the commands that are available right now. That includes the commands of the application you are working in, so a command of another application is only offered while that application has focus.
2.  You speak, then stop listening. The speech engine converts your speech to text.
3.  The text is compared with the command descriptions and with your own phrases. With Vosk the recognizer is also told which phrases to expect, which makes it much more accurate than free dictation. The sherpa models cannot be restricted that way: they write ordinary text, so the add-on compares it more strictly (see Choosing what to say).
4.  If one command clearly fits, it runs. If several fit about equally well, a list opens and you choose.

## Requirements

- NVDA 2026.1 or later, 64-bit, on Windows.
- A microphone set as the default recording device in Windows.
- An internet connection once, to download the speech model (a small Vosk model is about 40 to 100 MB; the sherpa models are 24 to 124 MB, plus a 21 MB runtime that all of them share).

## Installation and first run

1.  Open the `.nvda-addon` file and confirm the installation. Restart NVDA when asked.
2.  A few seconds after NVDA starts, the add-on notices that no speech model is installed and asks whether it may download one for your NVDA language. With a Turkish NVDA this is the turkish-stt model; for other languages it is a Vosk model. Choose **Yes**. The download runs in the background; NVDA announces the progress and tells you when voice commands are ready.

If you choose **No**, the add-on does not ask again at startup. You are asked again when you start listening, or when you choose a model that is not installed in the speech model dialog (see The speech model).

## Quick start

No keys are assigned by default, so choose your own:

1.  Open the NVDA menu, then Preferences, then Input gestures.
2.  Expand the **Voice Commands** category and assign a key to **Starts listening for a voice command**. Assign keys to the other commands there too if you want them.

Without keys you can also use the Tools menu (see The Tools menu).

Then, to give a voice command:

1.  Press your key. A high beep tells you that listening has started.
2.  Say the command.
3.  Press the key again, or just stay silent for a moment (about a second) after speaking. A low beep tells you that listening has stopped, and the command runs.

Stopping after silence can be turned off with the Input Gestures command "Toggles stopping the listening automatically when you stay silent after speaking" (or in the Tools menu). To change how long the silence must be, set `silence_seconds` (0.5 to 5, default 1.2) in `settings.json`.

If nothing was understood, NVDA says "Not understood". If what it heard fits no command well enough, NVDA says "No matching command" and names the closest one, or opens a list of candidates (see When it is not sure).

## The Tools menu

Open the NVDA menu, then Tools, then **Voice Commands** to use the add-on without assigning keys:

- **Start or stop listening** works like the key: choose it once to start and again to stop. A key is faster, because the menu has to be opened each time.
- **Command phrase editor...** opens the phrase editor.
- **Teach the last spoken phrase...** opens the dialog for names the recognizer does not know.
- **My commands...** opens the dialog for your own commands.
- **Toggle volume lowering** turns the lowering of other applications' volume on or off.
- **Toggle stop after silence** turns stopping the listening by itself after a pause on or off.
- **Speech model...** opens the dialog where you choose, download and manage the speech model (see The speech model).
- **Type a command...** opens the box where you can type a command phrase.

These do the same as the commands in the Input Gestures dialog (see Commands reference).

## Choosing what to say

NVDA's descriptions are often full sentences, for example "Reports the current line under the application cursor. Pressing this key twice will spell the current line." You do not have to say all of it.

| What you say                                                                                           | What to expect                                                                     |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| The first sentence of the description, such as "Reports the current line under the application cursor" | Usually works well. For many commands the first sentence is the whole description. |
| A short phrase you defined in the [phrase editor](#your-own-phrases), such as "read line"              | Exact and the most reliable. **Recommended for the commands you use every day.**   |
| A short paraphrase of your own that is not defined anywhere, such as "read the current line"           | Less reliable. It may open the list, or be matched to a similar command.           |

Two things help in practice. Say the phrase at a steady pace, in a quiet moment, and do not leave out the distinctive words. And define short phrases for the commands you use most: it takes a minute and makes everything faster.

**With a sherpa model** (see The speech model) you can say a command more naturally, because the text is compared with the command in both directions: the words you said must be found in the command, and the words of the command must be found in what you said. Extra words such as "please" are tolerated. A fragment that fits exactly one command also runs it, for example "music" for your own command "Open music folder" when no other command has that word; a fragment that fits several commands opens a list, and fragments shorter than four letters are ignored. A different spelling or spacing, such as "masa üstünü göster" for "Masaüstünü göster", also works when one command is clearly the closest by sound. Text that resembles no command is not guessed at; NVDA says what it heard instead, for example "Heard: thank you. No matching command".

## Your own phrases

Use the phrase editor to say commands your way. Assign a key to **Opens the dialog for editing the phrases (aliases) used for commands** and open it from the application whose commands you want to edit.

1.  In **Search commands**, type a few words to filter the list, then select the command in **Commands**.
2.  Type your phrase in **New phrase** and choose **Add phrase**. You can add several phrases to one command. To change or remove one, select it in **Phrases you say for this command** and choose **Edit selected phrase** or **Delete selected phrase**.
3.  Clear **Also use the original description** if the command should only answer to your phrases.
4.  Choose **Save**.

**Phrases that press the command several times.** Some commands do something different when their key is pressed twice or three times: the command that reports the time says the date on the second press. To give that second action a phrase of its own, type the phrase, choose a number from **Times the command is pressed**, then choose **Add phrase**. For the command that reports the time, the phrase "say the date" with 2 runs it as if its key had been pressed twice, so only the date is spoken. The list shows such a phrase as "say the date (pressed 2 times)", and **Edit selected phrase** puts the number back in the list. Adding the same words again with another number replaces the earlier one. The number can be from 2 to 5; see Repeating a command for what it does to each kind of command.

The number is stored at the end of the phrase, as " x2" to " x5". You can also type it yourself in **New phrase**, or write it in a file you import. Besides the letter x it can be written with the multiplication sign (×), an asterisk, the Cyrillic and Greek letters that look like x, or digits of other scripts, so it can be typed on any keyboard.

Good phrases are short, two to four words, and sound different from each other. Your phrases take precedence over the original descriptions, and they work with the repeat feature and the list of candidates like any other command. The editor shows the commands that are available where you opened it, so open it inside an application to edit that application's commands.

## Names the recognizer does not know

The speech model has a fixed vocabulary and cannot learn new words. A command that contains a rare or foreign name, such as an artist or a song title, is therefore often heard as other words that sound similar. For example, "Zülfü Livaneli" may be written as "gül suyu divane izi". The add-on does try to match such text by sound, which works when the model writes something close to the name ("inti ilimani" for "Inti Illimani"), but not when it writes completely different words. The sherpa models have no fixed word list, but they too may write an unfamiliar name differently than you expect.

When a command is not recognized, teach the add-on what the recognizer heard:

1.  Say the command that failed.
2.  Open the Tools menu, then Voice Commands, then **Teach the last spoken phrase**. You can also assign a key to **Opens a dialog that adds what the recognizer heard last as a spoken phrase of a command you choose** in the Input Gestures dialog.
3.  The list at the top shows the texts the recognizer produced, all checked. Clear the ones that look wrong.
4.  In **Search commands**, find the command, select it in the list below, and choose **Save phrases**.

The checked texts are saved as phrases of that command, exactly as if you had typed them in the phrase editor, and you can edit or delete them there later. Because they are words the model already knows, the same pronunciation is found directly the next time. The list always shows what the recognizer heard the last time you spoke a command, whether or not that command was recognized, so open the dialog right after the one that failed. It is also a quick way to see what the recognizer made of your speech, with no need to look at the NVDA log. Commands you type in the command box are not included.

## Sharing and backing up your phrases

The phrase editor can save your phrases to a file and load them again, so you can back them up, move them to another computer or share them with other people.

- **Export phrases...** (Ctrl+E) saves the phrases that are in the editor, together with the commands whose original description you switched off, to a `.json` file. Commands without phrases are left out.
- **Import phrases...** (Ctrl+I) reads such a file and adds its phrases to the editor. Nothing you already have is removed or changed: phrases you already have are skipped, and for a command you already have settings for, your own **Also use the original description** choice stays. NVDA tells you how many changes were imported. For a file that names commands by their text, such as the Turkish set below, the number counts every phrase in the file, including the ones you already have; those are still skipped. Nothing is stored until you choose **Save** (Ctrl+S), so you can look through the result first, and choose Cancel to throw it away.

In the phrase editor these shortcuts work wherever the focus is.

The file has the same format as `aliases.json` in the Voice Commands settings folder (see Settings and data), so a copy of that file can be imported too. Phrases are tied to commands by an id that does not depend on the interface language, so a file made by the editor works with any NVDA language. A file can also name a command by its text instead of its id, written as it appears in the editor's list: `description - category`, for example `Show desktop - Windows commands`. Such an entry only matches when NVDA uses the language of that text. A phrase for a command that does not exist on your computer, such as a command of an application you have not installed, is kept but does nothing until that command exists. The editor lists only the commands available where you opened it, so open it inside an application to see the imported phrases of that application's commands. Your own commands (see Your own commands) get a different id on every computer, so phrases for them are not carried over; add the same phrases to the commands on the other computer instead.

**A ready-made Turkish set.** The add-on comes with `tr-phrases.json` in its `locale\tr\LC_MESSAGES` folder: short Turkish phrases (two or three words) for NVDA's own commands and many popular add-ons. Import it like any other file. It names commands by their text (see above), so it works with a Turkish NVDA. For a command you have no settings for, it also switches off the long original description, so that command answers only to the short phrase; turn **Also use the original description** back on in the editor if you want both. The set also has phrases for the extra presses of commands, written with a press count at the end, such as "tarihi söyle x2" for the command that reports the time (see Your own phrases).

## Keeping commands out of voice control

Some commands you never want to run by voice, for example because they are risky ("close window", "lock computer") or because they sound too much like others and keep getting picked by mistake. To exclude one:

1.  Open the phrase editor and select the command, as described in Your own phrases.
2.  Clear **Also use the original description**, and do not add any phrase of your own.
3.  Choose **Save**.

The command is then no longer part of what the add-on listens for, so it is never run, never offered in the candidate list, and not matched by sound. It still works with its own key from the Input Gestures dialog. This works for NVDA commands, the built-in Windows commands and your own commands. To bring a command back, select it again and turn **Also use the original description** on, or add a phrase. A command of your own can also simply be deleted in its dialog.

Excluding a command also makes recognition more reliable: the fewer commands there are to choose from, the less often a similar one is mistaken for the one you said.

## Repeating a command

End the phrase with a number and "times": "read line two times", "next line three times". The number can be from two to five, and digits work too ("3 times"). You can also build the repeat into a phrase of your own (see Your own phrases); if you say a repeat as well, the one you said is used.

What happens depends on the command. A command that reacts to being pressed several times, because it does something different on the second or third press, is run once, and NVDA is told that its key was pressed that many times. The command that reports the current line reads it on one press, spells it on two and gives character descriptions on three, so "read line three times" gives only the character descriptions, as pressing the key three times does; it does not read and spell the line first. Any other command, such as moving to the next line, simply runs that many times in a row.

If the add-on cannot tell that a command reacts to repeated presses, it treats the command like any other and runs it that many times in a row. At the Debug logging level the log line "Voice command repeat" says what it found (see Troubleshooting).

## Pressing keys by voice

The commands in the Input Gestures category **Emulated system keyboard keys** press a key on the system keyboard for you, such as an arrow key, Tab or Escape. They work like any other command, and repeating is especially handy here: "down arrow three times" presses the key three times. Say the name of the key as it appears in the Input Gestures dialog. NVDA treats the press the way it treats its own emulated keys: it lets its own commands handle the key first and otherwise sends it to the system.

## Built-in Windows commands

NVDA's Input Gestures dialog only lists NVDA's own commands, so the add-on brings a set of system-wide Windows commands of its own. You say them like any other command, for example "show desktop", "show taskbar", "show system tray", "copy" or "paste". Each one simply presses the shortcut Windows already uses for it, so it works in any application. Shortcuts that end in a letter (such as Windows+I) are pressed by the key's virtual key code rather than by the character, so they work with any keyboard layout, including Turkish.

- **Desktop and shell:** show desktop, show taskbar, show system tray, open Start menu, open File Explorer, open Run dialog, open Windows settings, open Windows search, open quick settings, open notification center, open clipboard history, open emoji panel, start Windows voice typing, open display projection menu, take a screenshot, open Task Manager, lock computer.
- **Windows and virtual desktops:** minimize all windows, restore minimized windows, show task view, switch to the previous window, close window, maximize window, minimize window, snap window to the left or right, next, previous, new and close virtual desktop.
- **Sound and media:** volume up, volume down, mute or unmute volume, play or pause media, next track, previous track.
- **Editing:** copy, cut, paste, select all, undo, redo, save, find, print, create new, open file, rename, properties, refresh.
- **Navigation and tabs:** go back, go forward, new tab, close tab, reopen closed tab, next tab, previous tab.

Commands where repeating makes sense accept "two times" and so on, for example "volume up three times" or "next tab two times". These commands appear in the command phrase editor under the category **Windows commands**, so you can add your own phrases for them or switch off their original phrase. A command of NVDA with the same description takes precedence. The descriptions are translatable, so the phrases you say are in your language.

## Your own commands

You can add commands of your own. Assign a key to **Opens the dialog for adding your own commands** in the Voice Commands category of the Input Gestures dialog, press it, and choose **Add**. Type what you will say, then choose what the command does:

- **Open a program, file, folder or web address:** type it or use the buttons to browse. It is opened as if you had double-clicked it, so a web address opens in your browser. Environment variables such as `%USERPROFILE%` work, and so do the plain folder names `music`, `documents`, `downloads`, `desktop`, `pictures` and `videos` and Windows `shell:` addresses. A program that is on the system path, such as `notepad`, needs no folder.
- **Press a key combination:** type the keys with NVDA's key names, for example `control+shift+n`. Common spellings such as `ctrl`, `win`, `esc` and `left` are understood. Key commands can be repeated ("two times").

Your commands are listed in the phrase editor under **My commands**, where you can give them extra phrases. If a command of yours has the same name as an NVDA command, yours is used. Nothing here runs scripts or shell commands: a command either hands its target to Windows or presses keys. Your commands are stored in `userCommands.json` in the Voice Commands settings folder (see Settings and data).

## When it is not sure

When several commands fit about equally well, or none fits well enough to run by itself, a list of the best candidates opens. (With a sherpa model the list opens only when something resembles a command; otherwise NVDA just says what it heard.) Use the arrow keys and press Enter to run the one you want, or press Escape to cancel. If you chose a repeat, it applies to the command you pick.

## Typing instead of speaking

Assign a key to **Opens a box where you can type a command phrase**. What you type goes through the same matching as speech, which makes it useful for trying out phrases and for situations where you cannot speak. A repeat works here too: end the phrase with "two times" as described in Repeating a command, or with a press count such as "x2" (see Your own phrases).

## Commands reference

All of these are in the Input Gestures dialog, in the Voice Commands category.

| Command                                                                                                                | What it does                                                                     |
|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Starts listening for a voice command; press again, or stay silent for a moment after speaking, to stop listening and run the command                                | The main command. Press once to start and again to stop.                         |
| Opens a box where you can type a command phrase                                                                        | Runs a typed phrase through the same matching.                                   |
| Opens the dialog for editing the phrases (aliases) used for commands                                                   | Opens the phrase editor.                                                         |
| Toggles lowering the volume of other applications while listening for a voice command                                  | Turns volume lowering on or off.                                                 |
| Toggles stopping the listening automatically when you stay silent after speaking                                       | Turns stopping after a silence on or off.                                        |
| Opens the speech model dialog: choose, download and manage the model                                                   | Chooses the speech model, downloads it after asking, and opens the model folder. |
| Opens a dialog that adds what the recognizer heard last as a spoken phrase of a command you choose                     | Teaches the add-on a name it does not recognize.                                 |
| Opens the dialog for adding your own commands: open a program, file, folder or web address, or press a key combination | Opens the dialog for your own commands.                                          |

## Lowering other applications' volume

Music and videos would be picked up by the microphone and confuse the recognizer. While you are listening, every audio session except NVDA's own is lowered to 20% of its volume, and it is put back when you stop. A session whose volume you change yourself in the meantime is left alone.

Some players, such as browsers and media played through python.exe, close their audio session and open a new one, for example when you pause, when the track changes, or when the command you spoke changes it. Windows opens the new session at the lowered volume it remembered. The add-on therefore also looks for such sessions by the application's name and raises them too: right after listening stops, and again 1.5 and 4 seconds later, because a command such as "next track" opens its session only after listening has stopped. A session that could not be restored at all is remembered and put right before the next lowering, so the lowered volume is never mistaken for the original one. These records are kept for 24 hours at most.

Windows remembers per-application volumes, so the add-on also saves a small recovery file. If NVDA ends while the volume is lowered, the original volumes are restored the next time NVDA starts.

The feature uses a library that comes with NVDA. If it is missing, listening still works, just without lowering anything. You can turn it off with the toggle command.

## The speech model

Open **Speech model...** in the Tools menu, or assign a key to **Opens the speech model dialog: choose, download and manage the model**. The dialog lists the models available for your NVDA language and shows for each one whether it is in use, installed or not installed.

- **Use** switches to the selected model (double-clicking a model does the same). A model that is not installed is downloaded first: the add-on tells you its size, where it comes from and its license, and downloads it only after you agree. The model cannot be changed while you are listening or while a download is running.
- **Open model folder** opens the folder where the models are kept, for installing a model by hand.

| Model                                     | Languages                                        | Download              | License                                                         |
|-------------------------------------------|--------------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Vosk (small model)                        | Every language that has one on the official list | Usually 40 to 100 MB  | See the model list                                              |
| turkish-stt (mihu AI)                     | Turkish                                          | 68 MB                 | mihu Community License (free for personal use)                  |
| Kroko English, Français, Deutsch, Español | English, French, German, Spanish                 | 57, 57, 58 and 124 MB | Kroko community model; terms at huggingface.co/Banafo/Kroko-ASR |
| Zipformer ru (Alpha Cephei)               | Russian                                          | 24 MB                 | See huggingface.co/alphacep/vosk-model-small-streaming-ru       |

**Vosk or a sherpa model.** Vosk is restricted to the command list, which suits short commands. The sherpa models write free text, which usually copes better with ordinary speech and unfamiliar words but is matched to commands more strictly (see Choosing what to say). Try both and keep the one that works better with your voice and microphone. The default is turkish-stt for a Turkish NVDA that has no Vosk model installed yet; an installed Vosk model is never replaced behind your back, and every other language stays on Vosk until you choose a sherpa model. Your choice is remembered. If NVDA is switched to a language that the chosen sherpa model does not cover, the add-on falls back to Vosk.

**Installing a sherpa model.** The first sherpa model also needs the sherpa-onnx runtime (three DLL files, 21 MB). It is downloaded from github.com, always the same version, and checked against a fixed checksum; the model files come from huggingface.co or github.com and are checked too. The runtime is kept in `voiceCommands\sherpa-runtime` and each model in its own `sherpa-...` folder inside `voiceCommands\model`. The runtime needs 64-bit NVDA. If your Windows user name contains letters such as ş, ğ or ı, the add-on uses the short (8.3) name of the folder, which some drives have switched off (see Troubleshooting).

**Vosk models.**

- The add-on looks for the model in the `voiceCommands\model` folder inside NVDA's configuration folder, for example `%AppData%\nvda\voiceCommands\model`. **Open model folder** in the dialog takes you there.
- The automatic download uses the official model list at <https://alphacephei.com/vosk/models>. It picks a small model for your NVDA language, verifies its checksum and extracts it into that folder.
- To install a model yourself, download one from that page and extract it into the model folder. Both Vosk model layouts are recognized, and the files may be in a subfolder.
- Large models are more accurate but need much more memory and take longer to load.
- If there is no ready-made model for your language, the add-on offers to open the model page.

## Settings and data

Stored in `%AppData%\nvda\voiceCommands`, or in the configuration folder of a portable NVDA:

| Item                    | Contents                                                                                                                                                                        |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `aliases.json`          | Your phrases from the phrase editor and the teach dialog.                                                                                                                       |
| `userCommands.json`     | Your own commands.                                                                                                                                                              |
| `settings.json`         | Whether volume lowering is on, whether to ask about the download at startup, whether listening stops after silence and for how long, and the speech engine and model you chose. |
| `ducking-recovery.json` | Temporary: exists only while other applications' volume is lowered, and while a volume could not be restored yet (24 hours at most), to restore it after a crash.               |
| `model\`                | The speech models: Vosk models and the `sherpa-...` folders.                                                                                                                    |
| `sherpa-runtime\`       | The sherpa-onnx runtime, downloaded together with the first sherpa model.                                                                                                       |

The values at the top of `globalPlugins/voiceCommands/__init__.py`, such as the matching thresholds and the size of the candidate list, can be edited if you want to tune the behavior.

## Troubleshooting

| Problem                                                      | What to check                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Vosk model not found"                                       | Install a model as described above. The message names the exact folder.                                                                                                                                                                                                                                                                                                                                                                                                    |
| "The selected speech engine is not installed"                | Open **Speech model...** and choose **Use**: the add-on offers to download it again. If that keeps failing, delete the model's folder under `model\` and the `sherpa-runtime` folder, then download again.                                                                                                                                                                                                                                                                 |
| "Could not load the model" with a sherpa model               | Make sure NVDA is 64-bit. If your Windows user name has letters such as ş, ğ or ı, the model may not load when short folder names are switched off on the drive; check the log (see below) and use Vosk if it keeps failing.                                                                                                                                                                                                                                               |
| "Heard: ... No matching command"                             | A sherpa model wrote text that matches no command by its words. If the text is what you said, the command is called something else: add your own short phrase (see Your own phrases). If not, say it again, or try another model.                                                                                                                                                                                                                                          |
| Nothing is recognized                                        | Make sure the right microphone is the Windows default and not muted.                                                                                                                                                                                                                                                                                                                                                                                                       |
| A name is never recognized                                   | The model may write it as other words. Open **Teach the last spoken phrase** right after saying it to see what was heard, and save it as a phrase (see Names the recognizer does not know).                                                                                                                                                                                                                                                                                |
| The wrong command runs                                       | Define a short phrase of your own for that command in the phrase editor.                                                                                                                                                                                                                                                                                                                                                                                                   |
| "This command is not available right now"                    | The command belongs to another application. Say it while that application has focus.                                                                                                                                                                                                                                                                                                                                                                                       |
| Music or video still gets in the way                         | Some applications do not expose an audio session that can be lowered. Pause them before listening.                                                                                                                                                                                                                                                                                                                                                                         |
| A repeated command also does the work of the earlier presses | The add-on could not tell that the command reacts to repeated presses, so it ran it that many times in a row (for example, "window title three times" read the title, spelled it and copied it). At the Debug logging level, the line "Voice command repeat: 3, script counts presses: False" confirms it. Such a command can only be repeated by running it several times: press its key instead of saying it, or tell the author of the add-on which command it is.      |
| A player stays quiet after a command                         | The player reopened its audio session while the volume was lowered. The add-on raises such sessions right after listening stops, and again 1.5 and 4 seconds later. If one is still quiet, raise its volume once in the Windows volume mixer. At the Debug logging level, the line "Voice command: could not restore ... keeping it pending" names the application.                                                                                                        |
| You want to see what was heard                               | Open **Teach the last spoken phrase** right after speaking: its list shows the texts the recognizer produced. For more detail, set NVDA's Logging level to Debug (NVDA menu, Preferences, Settings, Privacy and Security, Logging level), speak, and open the log (NVDA+F1): "Voice command recognition" lines show what each recognizer heard, and "Voice command candidate" lines show how close the best matches were. These lines are only written at the Debug level. |

## Privacy

Audio from the microphone is processed on your computer by the speech engine (Vosk or sherpa-onnx) and is never sent anywhere. The network is used only when you allow a download, and only to reach alphacephei.com (Vosk models), huggingface.co (the turkish-stt model) and github.com (the sherpa-onnx runtime and the other sherpa models).

## Translating

The add-on is written in English and comes with a Turkish translation. To translate it, copy `voiceCommands.pot` to `locale/<language>/LC_MESSAGES/nvda.po` and translate the messages; each one has a comment for translators. The words used for repeating a command ("two times") are translatable too, so speaking works naturally in your language.

## License

Voice Commands is licensed under the GNU General Public License, version 2.

The sherpa-onnx runtime that the add-on downloads is licensed under the Apache License 2.0, and the ONNX Runtime library inside it under the MIT license. Each speech model has its own license (see The speech model).