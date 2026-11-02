"""Edit only hit and chain keys. Leave sound, payloads and descriptors intact."""
import struct

def tracks(raw):
    at=struct.unpack_from('<I',raw,60)[0];result=[]
    for index in range(64):
        if struct.unpack_from('<I',raw,at)[0]==0xffffffff:return result
        track,kind,count,keys=struct.unpack_from('<HHII',raw,at)
        assert 0<count<1024 and keys+count*16<=len(raw)
        result.append((track,kind,count,keys));at+=12
    raise ValueError('Unterminated event descriptors')

def retime(raw,slot):
    assert slot in [98,99,100]
    data=bytearray(raw);frames=struct.unpack_from('<I',raw,4)[0]
    report=[]
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)];new=list(old)
        if slot==98:
            if kind==1:new[0]=10.
            if kind==4:new=[12. if t==18. else t for t in old]
        else:
            hit=24. if slot==99 else 36.
            finish=32. if slot==99 else 44.
            if kind==1:new=[hit,finish]
            elif kind==5:new=[finish,float(frames)]
            elif kind==4:
                if slot==99:
                    if track==1:new=[24. if t==8. else 25. if t==24. else t for t in old]
                else:new=[t+12. if t>=24. else t for t in old]
        assert all(a<=b for a,b in zip(new,new[1:])),(slot,track,kind,new)
        for i,t in enumerate(new):struct.pack_into('<f',data,at+i*16,t)
        report.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    changed={i for i,(a,b) in enumerate(zip(raw,data)) if a!=b}
    allowed={at+i*16+j for _,kind,count,at in tracks(raw) if kind in [1,4,5] for i in range(count) for j in range(4)}
    assert changed<=allowed and data[:80]==raw[:80] and len(data)==len(raw)
    return bytes(data),{'contact_after':12 if slot==98 else 24 if slot==99 else 36,
        'chain_opens':22 if slot==98 else 32 if slot==99 else 44,
        'chain_closes':40 if slot==98 else frames,'tracks':report,'changed_bytes':len(changed),
        'counts_pointers_and_payloads_preserved':True,'sound_and_effect_tracks_unchanged':True}
