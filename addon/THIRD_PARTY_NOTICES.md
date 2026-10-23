# Third-party notices

Voice Commands is licensed under the GNU General Public License, version 2 or later (see
`LICENSE.txt`), as required for NVDA add-ons by the NVDA license.

This add-on bundles the following third-party binaries in `globalPlugins/voiceCommands/lib/`.
They are taken **unmodified** from the official `vosk` 0.3.45 package for 64-bit Windows
(`vosk-0.3.45-py3-none-win_amd64.whl`, SHA-256
`6994ddc68556c7e5730c3b6f6bad13320e3519b13ce3ed2aa25a86724e7c10ac`, published on
<https://pypi.org/project/vosk/>). They are loaded by the add-on at run time and are separate works
from the add-on's own code.

| File | Component | License | SHA-256 |
| --- | --- | --- | --- |
| `libvosk.dll` | Vosk API, with Kaldi and OpenBLAS linked in statically | Apache-2.0, BSD-3-Clause | `9331c2f6a32cf77141af27c9750e79532718f51bbc2e3cea3c60f14ca4251e4e` |
| `libstdc++-6.dll` | GNU C++ standard library (GCC runtime) | GPL-3.0-or-later with the GCC Runtime Library Exception 3.1 | `a1d96a848a567d7657e152cfe92e2fd62da412968cc11ec8bdb04bf20ebc5747` |
| `libgcc_s_seh-1.dll` | GCC low-level runtime library | GPL-3.0-or-later with the GCC Runtime Library Exception 3.1 | `201bf8a54ebb490f93ea4beb20740a483bf67036b90b5720f32d0c746a72d1e9` |
| `libwinpthread-1.dll` | winpthreads (mingw-w64) | MIT-style | `92caeb8a4ea281c674003462a233f3b445b685b0a6f93eb11254feda2dda9cde` |

The complete license texts are in the `licenses/` folder.

## Vosk API

Speech recognition engine. Copyright Alpha Cephei Inc. and contributors.
Licensed under the Apache License, Version 2.0 (`licenses/Apache-2.0-Vosk.txt`).
Source code: <https://github.com/alphacep/vosk-api>

## Kaldi

Linked statically into `libvosk.dll`. Copyright the Kaldi contributors, licensed under the
Apache License, Version 2.0. See `licenses/Kaldi-COPYING.txt` for Kaldi's notice about its
copyright headers; the license text is the same as `licenses/Apache-2.0-Vosk.txt`.
Source code: <https://github.com/kaldi-asr/kaldi>

## OpenBLAS

Linked statically into `libvosk.dll`. Copyright (c) 2011-2014, The OpenBLAS Project. All rights
reserved. Licensed under the BSD 3-Clause license (`licenses/BSD-3-Clause-OpenBLAS.txt`).
Source code: <https://github.com/OpenMathLib/OpenBLAS>

> Kaldi and OpenBLAS are the components that were identified inside `libvosk.dll`. The Vosk build
> may link further libraries statically; their licenses are listed in the Vosk repository
> (<https://github.com/alphacep/vosk-api>), which is the authority for the contents of the binary.

## GCC runtime libraries (`libstdc++-6.dll`, `libgcc_s_seh-1.dll`)

Copyright (C) Free Software Foundation, Inc. These libraries are licensed under the GNU General
Public License, version 3 or later, **with the GCC Runtime Library Exception, version 3.1**
(`licenses/GPL-3.0.txt`, `licenses/GCC-Runtime-Library-Exception-3.1.txt`). The exception allows
programs that use these libraries to be distributed under other terms.

The binaries were built with GCC 10 for MinGW-w64. The corresponding source code of the GCC
runtime libraries is available from <https://ftp.gnu.org/gnu/gcc/> (GCC 10 series) and
<https://gcc.gnu.org/>; the MinGW-w64 build recipe is part of the Vosk project
(<https://github.com/alphacep/vosk-api>). The binaries are redistributed exactly as published on
PyPI, without modification.

## winpthreads (`libwinpthread-1.dll`)

Copyright (c) 2011 mingw-w64 project. Licensed under an MIT-style license
(`licenses/MIT-winpthreads.txt`).
Source code: <https://github.com/mingw-w64/mingw-w64> (`mingw-w64-libraries/winpthreads`)

## Components that are not bundled

* **pycaw, comtypes and psutil** are used for lowering the volume of other applications. They are
  provided by NVDA itself; this add-on does not redistribute them.
* **Vosk speech recognition models** are downloaded on request, with your consent, from
  <https://alphacephei.com/vosk/models>. They are not part of this add-on. Each model has its own
  license, listed on that page.
