AQUA v19 SOURCE
Build with Python3.12, GCC and GNU binutils:
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
No Windows SDK is needed. Tests use a Linux Win64 ABI mock, not KH1.

New main-only controller: aqua_guard.h. It observes native row0x3D at2A3980,
scales the actor-motion delta at29F0A0 and scopes the facing-angle check at
2B4640 to Sora's own live Guard objects. No HP/hurt interceptor or direct
animation-clock/position writes. The three hooks admit all original prefixes
and protect all destinations before publishing; failures restore permissions
without a partial patch. Guard delta53/156 yields source30fps forward/reverse;
finisher delta47/35 preserves the remaining source's prior speed after trim.

Retarget tools are under retargeting/tools. Regenerate with:
  python3 retargeting/tools/build_aqua_complete_v19.py --profile 0
Profiles1..4 are numbered,5 is dodge,7 is main Blizzard. Selective --slots works.
Native motion headers, sizes and pointer/descriptor counts remain unchanged.
Event time edits use existing keys and preserve their payloads. Numbered poses
that would otherwise inherit new main changes explicitly retain v18 payloads.

Main head turns use real SKIN skull150. The run swap preserves native travel,
closed loops, authored source head mapping and original segment lengths.
Tap dodge uses504 in the existing fall record and native collision callbacks.
Numbered profiles retain v18 behavior. Default KH2 reactions remain pending.
