# Third-party notices

Voice Commands is licensed under the GNU General Public License, version 2 or later (see
`LICENSE.txt`), as NVDA's own license requires of plugins
(<https://download.nvaccess.org/documentation/copying.txt>).

This add-on bundles the following third-party binaries in `globalPlugins/voiceCommands/lib/`.
They are based on the official `vosk` 0.3.45 package for 64-bit Windows
(`vosk-0.3.45-py3-none-win_amd64.whl`, SHA-256
`6994ddc68556c7e5730c3b6f6bad13320e3519b13ce3ed2aa25a86724e7c10ac`, published on
<https://pypi.org/project/vosk/>). `libvosk.dll`, `libgcc_s_seh-1.dll` and
`libwinpthread-1.dll` are unmodified; `libstdc++-6.dll` has had its debugging sections
removed with `strip --strip-debug` (see the GCC Runtime section below). The code, data, and
the import and export tables of that file are unchanged. All binaries are loaded by the add-on
at run time (`libstdc++-6.dll`, `libgcc_s_seh-1.dll` and `libwinpthread-1.dll` as dependencies of
`libvosk.dll`) and are separate works from the add-on's own code.

> Note on license compatibility: the add-on's own code is licensed under GPL-2.0-or-later.
> NVDA's license allows a plugin to use components under other licenses, such as the
> Apache-2.0 Vosk library, as long as they do not prevent the plugin from being licensed under
> GPL v2 or later and are not used directly by NVDA itself outside the plugin. The Vosk binaries
> are loaded and called only by this add-on, through `ctypes`, never by NVDA. The bundled GCC
> runtime DLLs are licensed under GPL-3.0-or-later with the GCC Runtime Library Exception 3.1,
> which permits their distribution together with programs under other licenses (see the GCC
> Runtime section below).

| File | Component | License | SHA-256 |
| --- | --- | --- | --- |
| `libvosk.dll` | Vosk API, with Kaldi and OpenBLAS linked in statically | Apache-2.0, BSD-3-Clause | `9331c2f6a32cf77141af27c9750e79532718f51bbc2e3cea3c60f14ca4251e4e` |
| `libstdc++-6.dll` (stripped) | GNU C++ standard library (GCC runtime) | GPL-3.0-or-later with the GCC Runtime Library Exception 3.1 | `7d52c34cd1c55585f95e9580ed10d747fb61406d8b4aee483a409e1ed74c74a3` |
| `libgcc_s_seh-1.dll` | GCC low-level runtime library | GPL-3.0-or-later with the GCC Runtime Library Exception 3.1 | `201bf8a54ebb490f93ea4beb20740a483bf67036b90b5720f32d0c746a72d1e9` |
| `libwinpthread-1.dll` | winpthreads (mingw-w64) | MIT-style, with portions under BSD-3-Clause (Lockless Inc.) | `92caeb8a4ea281c674003462a233f3b445b685b0a6f93eb11254feda2dda9cde` |

The complete license texts are in the `licenses/` folder.

## Vosk API

Speech recognition engine. Copyright Alpha Cephei Inc. and contributors.
Licensed under the Apache License, Version 2.0 (`licenses/Apache-2.0-Vosk.txt`).
Source code: <https://github.com/alphacep/vosk-api>

## Kaldi

Linked statically into `libvosk.dll`. Copyright the Kaldi contributors, licensed under the
Apache License, Version 2.0. The full notice, including the list of contributors and the
Apache 2.0 text, is in `licenses/Kaldi-COPYING.txt`.
Source code: <https://github.com/kaldi-asr/kaldi>

## OpenBLAS

Linked statically into `libvosk.dll`. Copyright (c) 2011-2014, The OpenBLAS Project. All rights
reserved. Licensed under the BSD 3-Clause license (`licenses/BSD-3-Clause-OpenBLAS.txt`).
Source code: <https://github.com/OpenMathLib/OpenBLAS>

> Kaldi and OpenBLAS are the components that were identified inside `libvosk.dll`. The Vosk build
> may link further libraries statically; their licenses are listed in the Vosk repository
> (<https://github.com/alphacep/vosk-api>), which is the authority for the contents of the binary.

## GCC Runtime (libstdc++-6.dll, libgcc_s_seh-1.dll)

These DLLs are based on the official Vosk 0.3.45 Windows package on PyPI.
`libstdc++-6.dll` has had its debugging sections (`.debug_*`) removed with
`strip --strip-debug` to reduce its size from about 26.6 MB to 3.9 MB. The code, data, and the
import and export tables are unchanged. SHA-256 of the original file from the PyPI package:
`a1d96a848a567d7657e152cfe92e2fd62da412968cc11ec8bdb04bf20ebc5747`. SHA-256 of the file in this add-on:
`7d52c34cd1c55585f95e9580ed10d747fb61406d8b4aee483a409e1ed74c74a3`.
`libgcc_s_seh-1.dll` is unmodified.

License: GPL-3.0-or-later with the GCC Runtime Library Exception 3.1.
See `licenses/GPL-3.0.txt` for the GNU General Public License version 3 and
`licenses/GCC-Runtime-Library-Exception-3.1.txt` for the exception.
Source: <https://pypi.org/project/vosk/0.3.45/>

## winpthreads (`libwinpthread-1.dll`)

Copyright (c) 2011 mingw-w64 project. Licensed under an MIT-style license.
Portions are derived from the Posix Threads library for Microsoft Windows by
Lockless Inc., licensed under a BSD 3-Clause license.
See `licenses/MIT-winpthreads.txt` for both notices.
Source code: <https://github.com/mingw-w64/mingw-w64> (`mingw-w64-libraries/winpthreads`)

## Components that are not bundled

* **pycaw and comtypes** are used for lowering the volume of other applications. They are
  provided by NVDA itself; this add-on does not redistribute them.
* **Vosk speech recognition models** are downloaded on request, with your consent, from
  <https://alphacephei.com/vosk/models>. They are not part of this add-on. Each model has its own
  license, listed on that page; check the license of a model before using it, as some models use
  different terms (for example CC-BY-SA).