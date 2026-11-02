AQUA v18 SOURCE
Runtime: aqua.c plus aqua_data.h, aqua_air_dodge.h, aqua_blizzard.h,
aqua_cast_requests.h and aqua_magic.h. Immutable before/after payloads fit the
original KH1 record capacities. Native Guard events and all damage reactions
pass through. Ground event changes are limited to existing time values.

Rebuild: Python3.12, GCC and GNU binutils; no Windows SDK required.
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
These tests use a Linux Win64 ABI mock; they do not run KH1.

Retarget source and supplied BBS/native KH1 fixtures are included under
retargeting. To regenerate a profile (0main,1..4numbered,5dodge,7Blizzard):
  python3 retargeting/tools/build_aqua_complete_v18.py --profile 0
Use profiles0..5 or7. Selective --slots is supported.
No sampling cache is required; source clipping/timing fingerprints prevent
reuse across different guards or combo timelines. Guard uses a forward/hold/
reverse source timeline without changing any native headers or action clocks.

The desired KH2 Sora reaction mapping is recorded in damage_reaction_validation.
json, but no KH2 source game assets are bundled or replacement claimed.
Collect_KH2_Sora_Source.ps1 is a Windows PowerShell5.1 helper for loose extracted
P_EX100.mdlx and P_EX100.mset. It never substitutes Valor or other characters.

For transparency, every runtime/visual/native validation marks game execution
as false. In-game testing remains necessary for feel, collision and hair mesh.
