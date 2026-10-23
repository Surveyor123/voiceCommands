# Voice Commands for NVDA

Run NVDA commands by speaking instead of pressing keys.

NVDA already has a description for every command in its Input Gestures dialog. Voice Commands listens through your microphone, turns your speech into text with the offline [Vosk](https://alphacephei.com/vosk/) engine, matches that text against those descriptions (and against phrases you define yourself), and runs the command that fits best. Your voice is processed on your computer and never leaves it.

## How it works

1.  When you start listening, the add-on collects the commands that are available right now. That includes the commands of the application you are working in, so a command of another application is only offered while that application has focus.
2.  You speak, then stop listening. Vosk converts your speech to text.
3.  The text is compared with the command descriptions and with your own phrases. The recognizer is also told which phrases to expect, which makes it much more accurate than free dictation.
4.  If one command clearly fits, it runs. If several fit about equally well, a list opens and you choose.

## Requirements

- NVDA 2026.1 or later, 64-bit, on Windows.
- A microphone set as the default recording device in Windows.
- An internet connection once, to download the speech model (a small model is about 40 to 100 MB).

## Installation and first run

1.  Open the `.nvda-addon` file and confirm the installation. Restart NVDA when asked.
2.  A few seconds after NVDA starts, the add-on notices that no speech model is installed and asks whether it may download one for your NVDA language. Choose **Yes**. The download runs in the background; NVDA announces the progress and tells you when voice commands are ready.

If you choose **No**, the add-on does not ask again at startup. You are asked again when you start listening, or when you use the "Downloads the speech recognition model" command.

## Quick start

No keys are assigned by default, so choose your own:

1.  Open the NVDA menu, then Preferences, then Input gestures.
2.  Expand the **Voice Commands** category and assign a key to **Starts listening for a voice command**. Assign keys to the other commands there too if you want them.

Then, to give a voice command:

1.  Press your key. A high beep tells you that listening has started.
2.  Say the command.
3.  Press the key again. A low beep tells you that listening has stopped, and the command runs.

If nothing is recognized, NVDA says "Not understood".

## Choosing what to say

NVDA's descriptions are often full sentences, for example "Reports the current line under the application cursor. Pressing this key twice will spell the current line." You do not have to say all of it.

| What you say                                                                                           | What to expect                                                                     |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| The first sentence of the description, such as "Reports the current line under the application cursor" | Usually works well. For many commands the first sentence is the whole description. |
| A short phrase you defined in the [phrase editor](#your-own-phrases), such as "read line"              | Exact and the most reliable. **Recommended for the commands you use every day.**   |
| A short paraphrase of your own that is not defined anywhere, such as "read the current line"           | Less reliable. It may open the list, or be matched to a similar command.           |

Two things help in practice. Say the phrase at a steady pace, in a quiet moment, and do not leave out the distinctive words. And define short phrases for the commands you use most: it takes a minute and makes everything faster.

## Your own phrases

Use the phrase editor to say commands your way. Assign a key to **Opens the dialog for editing the phrases (aliases) used for commands** and open it from the application whose commands you want to edit.

1.  In **Search commands**, type a few words to filter the list, then select the command in **Commands**.
2.  Type your phrase in **New phrase** and choose **Add phrase**. You can add several phrases to one command. To change or remove one, select it in **Phrases you say for this command** and choose **Edit selected phrase** or **Delete selected phrase**.
3.  Clear **Also use the original description** if the command should only answer to your phrases.
4.  Choose **Save**.

Good phrases are short, two to four words, and sound different from each other. Your phrases take precedence over the original descriptions, and they work with the repeat feature and the list of candidates like any other command. The editor shows the commands that are available where you opened it, so open it inside an application to edit that application's commands.

## Keeping commands out of voice control

Some commands you never want to run by voice, for example because they are risky ("close window", "lock computer") or because they sound too much like others and keep getting picked by mistake. To exclude one:

1.  Open the phrase editor and select the command, as described in Your own phrases.
2.  Clear **Also use the original description**, and do not add any phrase of your own.
3.  Choose **Save**.

The command is then no longer part of what the add-on listens for, so it is never run, never offered in the candidate list, and not matched by sound. It still works with its own key from the Input Gestures dialog. This works for NVDA commands, the built-in Windows commands and your own commands. To bring a command back, select it again and turn **Also use the original description** on, or add a phrase. A command of your own can also simply be deleted in its dialog.

Excluding a command also makes recognition more reliable: the fewer commands there are to choose from, the less often a similar one is mistaken for the one you said.

## Repeating a command

End the phrase with a number and "times": "read line two times", "next line three times". The number can be from two to five, and digits work too ("3 times"). The command runs that many times in a row.

For commands that react to being pressed several times, NVDA counts this as repeated key presses. For example, the command that reports the current line reads it once, spells it twice, and gives character descriptions three times. For other commands, such as moving to the next line, the effect is simply that it happens several times.

## Pressing keys by voice

The commands in the Input Gestures category **Emulated system keyboard keys** press a key on the system keyboard for you, such as an arrow key, Tab or Escape. They work like any other command, and repeating is especially handy here: "down arrow three times" presses the key three times. Say the name of the key as it appears in the Input Gestures dialog. NVDA treats the press the way it treats its own emulated keys: it lets its own commands handle the key first and otherwise sends it to the system.

## Built-in Windows commands

NVDA's Input Gestures dialog only lists NVDA's own commands, so the add-on brings a set of system-wide Windows commands of its own. You say them like any other command, for example "show desktop", "show taskbar", "show system tray", "copy" or "paste". Each one simply presses the shortcut Windows already uses for it, so it works in any application.

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

When several commands fit about equally well, or none fits well enough to run by itself, a list of the best candidates opens. Use the arrow keys and press Enter to run the one you want, or press Escape to cancel. If you chose a repeat, it applies to the command you pick.

## Typing instead of speaking

Assign a key to **Opens a box where you can type a command phrase**. What you type goes through the same matching as speech, which makes it useful for trying out phrases and for situations where you cannot speak.

## Commands reference

All of these are in the Input Gestures dialog, in the Voice Commands category.

| Command                                                                                                                | What it does                                             |
|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| Starts listening for a voice command; press again to stop listening and run the command                                | The main command. Press once to start and again to stop. |
| Opens a box where you can type a command phrase                                                                        | Runs a typed phrase through the same matching.           |
| Opens the dialog for editing the phrases (aliases) used for commands                                                   | Opens the phrase editor.                                 |
| Toggles lowering the volume of other applications while listening for a voice command                                  | Turns volume lowering on or off.                         |
| Downloads the speech recognition model for the NVDA language                                                           | Starts the model download, after asking.                 |
| Opens the dialog for adding your own commands: open a program, file, folder or web address, or press a key combination | Opens the dialog for your own commands.                  |
| Opens the model folder in File Explorer                                                                                | For installing a model by hand.                          |

## Lowering other applications' volume

Music and videos would be picked up by the microphone and confuse the recognizer. While you are listening, every audio session except NVDA's own is lowered to 20% of its volume, and it is put back when you stop. A session whose volume you change yourself in the meantime is left alone.

Windows remembers per-application volumes, so the add-on also saves a small recovery file. If NVDA ends while the volume is lowered, the original volumes are restored the next time NVDA starts.

The feature uses a library that comes with NVDA. If it is missing, listening still works, just without lowering anything. You can turn it off with the toggle command.

## The speech model

- The add-on looks for the model in the `voiceCommands\model` folder inside NVDA's configuration folder, for example `%AppData%\nvda\voiceCommands\model`. The command "Opens the model folder in File Explorer" takes you there.
- The automatic download uses the official model list at <https://alphacephei.com/vosk/models>. It picks a small model for your NVDA language, verifies its checksum and extracts it into that folder.
- To install a model yourself, download one from that page and extract it into the model folder. Both Vosk model layouts are recognized, and the files may be in a subfolder.
- Large models are more accurate but need much more memory and take longer to load.
- If there is no ready-made model for your language, the add-on offers to open the model page.

## Settings and data

Stored in `%AppData%\nvda\voiceCommands`, or in the configuration folder of a portable NVDA:

| Item                | Contents                                                                         |
|---------------------|----------------------------------------------------------------------------------|
| `aliases.json`      | Your phrases from the phrase editor.                                             |
| `userCommands.json` | Your own commands.                                                               |
| `settings.json`     | Whether volume lowering is on, and whether to ask about the download at startup. |
| `model\`            | The speech model.                                                                |

The values at the top of `globalPlugins/voiceCommands/__init__.py`, such as the matching thresholds and the size of the candidate list, can be edited if you want to tune the behavior.

## Troubleshooting

| Problem                                   | What to check                                                                                                                                                                                                                                                                                                        |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Vosk model not found"                    | Install a model as described above. The message names the exact folder.                                                                                                                                                                                                                                              |
| Nothing is recognized                     | Make sure the right microphone is the Windows default and not muted.                                                                                                                                                                                                                                                 |
| The wrong command runs                    | Define a short phrase of your own for that command in the phrase editor.                                                                                                                                                                                                                                             |
| "This command is not available right now" | The command belongs to another application. Say it while that application has focus.                                                                                                                                                                                                                                 |
| Music or video still gets in the way      | Some applications do not expose an audio session that can be lowered. Pause them before listening.                                                                                                                                                                                                                   |
| You want to see what was heard            | These lines are written only at the Debug logging level, so first set it in NVDA menu, Preferences, Settings, General, Logging level. Then open the NVDA log (NVDA+F1). "Voice command recognition" lines show what each recognizer heard, and "Voice command candidate" lines show how close the best matches were. |

## Privacy

Audio from the microphone is processed on your computer by Vosk and is never sent anywhere. The network is used only when you allow the model download, and only to reach alphacephei.com.

## Translating

The add-on is written in English and comes with a Turkish translation. To translate it, copy `voiceCommands.pot` to `locale/<language>/LC_MESSAGES/nvda.po` and translate the messages; each one has a comment for translators. The words used for repeating a command ("two times") are translatable too, so speaking works naturally in your language.

## License

Voice Commands is licensed under the GNU General Public License, version 2 or later (GPL-2.0-or-later), as NVDA's own license requires of plugins. The bundled third-party components and their licenses are listed in [THIRD_PARTY_NOTICES.md](addon/THIRD_PARTY_NOTICES.md).
