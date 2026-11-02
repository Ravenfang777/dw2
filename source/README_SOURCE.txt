AQUA V15 DEVELOPMENT SOURCE

BUILD / CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
Requires Python/GCC/GNU ld i386pep; geometry needs NumPy/SciPy.
Runtime checks execute the actual emitted PE and Win64 ABI entry detours with
native-control mocks. The native event sampler fixture is real supplied EXE code.

REBUILD POSES (optional; NumPy/SciPy/Pillow)
From this source directory, run retargeting/tools/build_aqua_complete_v15.py
with --profile0 --output .; profiles1..4 use outputs sets/p1..p4,profile5 uses
dodge and profile6 uses glide_stop. Arguments have spaces: --profile 0.
Then regenerate data, build and run both checks. --slots limits rebuilt records.
Model/source inputs are under retargeting; original MSETs are ../assets.
The exported builder resolves its paths relative to this source layout.

NEW SECOND-AIR / SPELL POSES
Main103 uses352 from p02ex_352.arc. The v15 plan inherits v14's other sources.
Main Blizzard requests37/84 now use Fire release records54/79, retaining native
request flags. cast_followup detects a verified main Blizzard queue, calls the
checked native append0x29FA30 to add recovery3D/8A, then places it before the
unchanged original terminal record. The logical spell stays37/84; original
terminal payloads, spell scripts, MP, targeting and element are retained.
Numbered profile body overrides and request tables retain their previous casts.

EVENT RETIMING WITHOUT NATIVE ALLOCATION/PATH CHANGES
Main99/100 keep their exact existing48/64-frame headers and source365 poses.
aqua_event_timing_v15.py changes only the first float of existing16-byte event
records. It warps the earliest kind4 state0x16 contact from8->35 or24->47 and
keeps all other timed state/trail/sound records aligned. Kind5 opens at47/63
and closes at48/64. All descriptor words/counts/pointers and payload bytes stay.
The actual native sampler0x394770 reads these fixtures in the runtime tests.
Native kind5 sets model+14 bit0x400000 at0x3922AF, copied to actor+1CC by0x29F515;
0x29EFB0 reads that bit for native cancellation/chain decisions.

AquaMotion.part_count is5 normally and6 for the two second-ground records.
The sixth AquaPart uses header field60 as an event-descriptor indirection.
The generated schema verifies descriptor type/count, terminator and every live
key pointer against the known contiguous layout. Only the key stream is copied;
live encoded descriptor pointers are never overwritten. Original and main
retimed streams are known immutable variants; numbered profiles use original
event times. This changes DLL admission metadata, not native MSET counts.
Unknown event schema/payload blocks the whole body transaction. All motion
headers, sizes, eleven helpers and existing travel remain original.

DEFERRED GLIDE GUARD FOR504
V14's accepted504 was immediately replaced by Glide71 in kh1-aqua(4).log.
0x2AFD79 reads cached global0x2D5EC10 bit0x80;0x2AFD82 calls native regular Glide
at0x2B26C0 independently of the temporary input mask. V15 hooks that constructor
only for an admitted live Sora504 session. Otherwise its original code resumes.
The14-byte span40534883ec20488bd9e862060000 contains the nine-byte prologue and
a relative call. The trampoline copies9bytes, calls original0x2B2D30 via absolute
RAX, then jumps to0x2B26CE without destroying the returned EAX. The native subtype
AND at+1D is checked too. The existing control0x2A6220 span and both constructor
anchors are admitted before either patch; protection failure leaves both intact.
Tests exercise a deferred native constructor after the input callback returns,
and the relocated successful original constructor including its subtype clear.
No Superglide constructor is hooked. Native state/velocity/defense are retained.

GLIDE / MAGIC
Glide starts with the existing350 source0..20 opening, reaching frame40. Then
all four original Sora Glide body parts are restored and the native clock and
steering resume. The fast cache recognizes that known temporary original-body
state. Native Glide ending restores the opening fixtures for next use and plays
the existing350[20,40] fall overlay before506. The frame/header counts stay native.
Magic attachment detours are removed. Native point/matrix attachment0x30 is used
for every spell/profile; legacy hand_magic INI values are ignored.

OTHER RETAINED SYSTEMS
Zero-AP ids117..121, exclusive selection, saved states, native ability-list size,
original request pointer restoration, item007/395, falling506, wrist/hair
refinements and all unrelated motion data remain. Guard/Cartwheel records keep
native defensive windows. The main second-ground cancel window is later, so
other commands using it are also delayed. Only idle transactions change profiles.

Evidence and scope are in the validation JSON files; all current action/source
assignments are the root CSVs. The supplied full EXE and user log are not included.
Existing upstream licenses remain in licenses. Format reference:
https://openkh.dev/bbs/file/type/pam.html
