AQUA ABILITY TEST v5 - SOURCE AND REPRODUCTION

This is a small freestanding C Windows x64 DLL with Panacea's OnInit/OnFrame
exports. The game module is not a DirectInput proxy and installs no code hook.
It calls the existing verified native pointer-handle function to register its
encoded menu text. The table extension preserves the first 65 native records.
Only the new id 117 record and its own ability-list byte are added.

The ability is named exactly aqua, costs 0 AP, and is first learned unequipped.
It gates only the tested v4 curve payload. The asset files packaged for OpenKH
are the original Sora/HE inputs, not permanently edited v4 files. The runtime
controller admits a strict first-attack fingerprint, then toggles 60 existing
wrist-key value/tangent triples. Unknown data is rejected before any curve write.
The slot search admits only normal 98 or Olympus 60. Both original first-attack
records are byte-identical in the user-provided inputs. Current attacks finish
before a requested toggle. Cache readmission handles a record reloaded at the
same address. Actor control, root, events, damage, timing and input stay native.

REBUILD (LINUX)
Use Python 3, GCC supporting x86-64 -mabi=ms, and GNU ld with i386pep support.
From this source folder:
    python3 build.py
    python3 test_runtime.py
This produces kh1-aqua.dll and runtime_validation.json. No SDK, MinGW runtime,
Rust runtime or external package download is required by this build workflow.

The build translates GCC's ELF64 RELA records to AMD64 COFF with correct implicit
addends, writes standard Kernel32 import descriptors, and links a PE32+ DLL.
A DIR64 relocation is included for ASLR. The module imports only Kernel32.
The artifact has no C/C++ runtime dependency and no static constructors.

TEST LIMITS
The actual emitted PE image is loaded at a different address in a Linux test
host, its base relocations applied, and imports bound to Win64-ABI mocks.
Tests execute its actual OnInit/OnFrame through a Win64 calling bridge.
They check lowercase text encoding, native table preservation, initial unequip,
normal and Olympus/encoded pointers, ON/OFF exact roundtrip to the tested v4
bytes, safe full-list handling, rejection of foreign/schema changes, mid-attack
deferral, record reload, removal, unsupported-build and old-DLL suspension.
This is not a Windows loader, Panacea, or live-game test. Those remain pending.
fixtures/ contains the original and v4 user-provided first-attack records used
for exact-byte expectations. The provided aqua_data.h is sufficient to rebuild;
generate_data.py documents the optional derivation from the earlier workspace.

VERIFIED STEAM ADDRESSES / PROVENANCE
The build stamp 1721645006 and translations come from the user-provided v52
source notes and binary Rva mapping. They agree with the user's bank-safe Lua
controller and MP controller pointer addresses:
  Sora actor pointer:     0x2537E48
  Pointer-bank table:     0x2EE3980
  Ability table pointer:  0x2D36D48
  Pointer-to-handle:      0x38AD90
  Loaded save pointer:    0x2868BA0
  Fallback save block:    0x2DE9360 (ability bytes +0x44,48 slots)
  Actor motion array:     +0x1D4 (encoded pointer)
  Actor request:          +0x164
Only the verified Steam build is admitted. No game executable, executable
instruction dump, external process writer, or game code hook is included.

CREDITS / LICENSING
Ability-table layout, native text encoding and grant/removal behavior follow
the user's v52 source/reference for JamesPMx / PM2CRAZY's KH2-Combat-in-KH1,
upstream base 4adb946b642f6b9bd84f83d12ec16944e0638b8b,
user derivative 54d18b73d6b4359476e97a887332fefcc44a5cdd:
https://github.com/PM2CRAZY/KH2-Combat-in-KH1
The C gate, GCC/COFF builder and test host were added by OpenAI Codex.
licenses/ contains the upstream MIT OR Apache-2.0 license texts and the
unchanged historical notice describing that separate upstream project.
Game assets/fixtures are from the user's provided files. Kingdom Hearts is
owned by Disney / Square Enix. Source licenses do not license the game assets.
