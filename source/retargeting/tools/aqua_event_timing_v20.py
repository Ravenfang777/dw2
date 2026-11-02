"""Retain payloads/counts/pointers; change only time fields in main events."""
import struct
from aqua_event_timing_v19 import tracks,retime as previous_retime

def retime(raw,slot):
    if slot not in [99,100,102,103]:return previous_retime(raw,slot)
    data=bytearray(raw);rows=[];finish=30. if slot==99 else 42.
    frames=struct.unpack_from('<I',raw,4)[0]
    if slot in [99,100]:
        data=bytearray(previous_retime(raw,slot)[0])
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)]
        new=[struct.unpack_from('<f',data,at+i*16)[0] for i in range(count)]
        if slot in [99,100]:
            hit=finish*8./37.
            if kind==1:new=[hit-1.,finish]
            elif kind==5:new=[finish,float(frames)]
            elif kind==4:
                if slot==99:new=[hit-1.,hit-.5,hit,float(frames)] if track==0 else [hit-1.,hit,24.,float(frames)]
                else:new=[hit-1.,hit,hit+.5,hit+1.,hit+1.5] if track==0 else [hit-1.+i*.25 for i in range(count)]
        elif kind==5:new=[18. if slot==102 else 24.,float(frames)]
        if slot==103 and kind==1:new=[12.,25.]
        assert len(new)==count and all(a<=b for a,b in zip(new,new[1:])),(slot,kind,new)
        for i,v in enumerate(new):struct.pack_into('<f',data,at+i*16,v)
        rows.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    return bytes(data),{'tracks':rows,'counts_pointers_and_payloads_preserved':True,
        'source_range':[0,37] if slot in [99,100] else None,
        'chain_opens':finish if slot in [99,100] else 18. if slot==102 else 24.,'chain_closes':frames}
