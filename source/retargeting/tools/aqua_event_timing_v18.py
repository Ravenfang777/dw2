"""Keep existing native hit payloads, match 301's main strike at source frame8."""
import struct
from aqua_event_timing_v17 import tracks,retime as previous_retime

def retime(raw,slot):
    if slot==98:return previous_retime(raw,slot)
    assert slot in [99,100]
    data=bytearray(raw);frames=struct.unpack_from('<I',raw,4)[0]
    finish=32. if slot==99 else 44.
    hit=finish*8./40. #301 has41 source frames (40 intervals), strike phase8.
    report=[]
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)];new=list(old)
        if kind==1:new=[hit-1.,finish]
        elif kind==5:new=[finish,float(frames)]
        elif kind==4:
            if slot==99:
                new=[hit-1.,hit-.5,hit,float(frames)] if track==0 else [hit-1.,hit,24.,float(frames)]
            else:new=[hit-1.,hit,hit+.5,hit+1.,hit+1.5] if track==0 else [hit-1.+i*.25 for i in range(count)]
        assert len(new)==count and all(a<=b for a,b in zip(new,new[1:])),(slot,track,kind,new)
        for i,t in enumerate(new):struct.pack_into('<f',data,at+i*16,t)
        report.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    changed={i for i,(a,b) in enumerate(zip(raw,data)) if a!=b}
    allowed={at+i*16+j for _,kind,count,at in tracks(raw) if kind in [1,4,5] for i in range(count) for j in range(4)}
    assert changed<=allowed and data[:80]==raw[:80] and len(data)==len(raw)
    return bytes(data),{'contact_after':hit,'source_contact_frame':8.,'source_frame_count':41,
        'chain_opens':finish,'chain_closes':frames,'tracks':report,'changed_bytes':len(changed),
        'counts_pointers_and_payloads_preserved':True,'sound_and_effect_tracks_unchanged':True}
