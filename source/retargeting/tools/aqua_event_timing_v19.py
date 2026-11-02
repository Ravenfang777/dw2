"""Main finisher trim and full-length native Guard; preserve key payloads."""
import struct
from aqua_event_timing_v18 import tracks,retime as previous_retime

def retime(raw,slot):
    if slot not in [101,110]:return previous_retime(raw,slot)
    data=bytearray(raw);rows=[]
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)]
        if slot==101:
            cut=79.*12./47.
            new=[min(80.,max(0.,(v-cut)*47./35.)) for v in old]
        elif kind==1:new=[0.,54.]
        elif kind==5:new=[54.]
        else:new=old
        assert len(new)==count and all(a<=b for a,b in zip(new,new[1:])),(slot,kind,new)
        for i,v in enumerate(new):struct.pack_into('<f',data,at+i*16,v)
        rows.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    return bytes(data),{'tracks':rows,'counts_pointers_and_payloads_preserved':True,
        'source_first_frame':12 if slot==101 else 0,'guard_window_frames':[0,54] if slot==110 else None}
