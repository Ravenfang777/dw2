"""Preserve native event payloads and layouts while retiming main attack phases."""
import struct
from aqua_event_timing_v20 import tracks,retime as previous_retime

def retime(raw,slot):
    if slot not in [99,100,101,103,104]:return previous_retime(raw,slot)
    data=bytearray(raw);rows=[];frames=struct.unpack_from('<I',raw,4)[0]
    finish=24. if slot==99 else 33.6
    if slot in [99,100]:data=bytearray(previous_retime(raw,slot)[0])
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)]
        new=[struct.unpack_from('<f',data,at+i*16)[0] for i in range(count)]
        if slot in [99,100]:
            hit=finish*8./30.
            if kind==1:new=[hit-1.,finish]
            elif kind==5:new=[finish,float(frames)]
            elif kind==4:
                if slot==99:new=[hit-1.,hit-.5,hit,float(frames)] if track==0 else [hit-1.,hit,24.,float(frames)]
                else:new=[hit-1.,hit,hit+.5,hit+1.,hit+1.5] if track==0 else [hit-1.+i*.25 for i in range(count)]
        elif slot==101:
            cut=79.*15./47.
            new=[min(80.,max(0.,(v-cut)*47./32.)) for v in old]
        elif slot==103:
            if kind==1:new=[7.,22.]
            elif kind==5:new=[22.,float(frames)]
        elif slot==104 and kind==1:new=[16.,32.]
        assert len(new)==count and all(a<=b for a,b in zip(new,new[1:])),(slot,kind,new)
        for i,v in enumerate(new):struct.pack_into('<f',data,at+i*16,v)
        rows.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    report={'tracks':rows,'counts_pointers_and_payloads_preserved':True}
    if slot in [99,100]:report.update(source_range=[0,30],chain_opens=finish,chain_closes=frames,real_chain_opens_ticks=24.,recovery_tail_rate_multiplier=2.)
    if slot==101:report.update(source_first_frame=15,source_last_frame=47)
    if slot==103:report.update(chain_opens=22.,chain_closes=frames,donor='407')
    if slot==104:report.update(donor='353')
    return bytes(data),report
