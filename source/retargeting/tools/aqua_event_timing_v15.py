"""Retime existing second-ground event keys without changing tables or payloads."""
import struct

def tracks(raw):
    at=struct.unpack_from('<I',raw,60)[0];result=[]
    for index in range(64):
        if struct.unpack_from('<I',raw,at)[0]==0xffffffff:return result
        track,kind,count,keys=struct.unpack_from('<HHII',raw,at)
        assert 0<count<1024 and keys+count*16<=len(raw)
        result.append((track,kind,count,keys));at+=12
    raise ValueError('Unterminated event descriptors')

def retime(raw):
    data=bytearray(raw);frames=struct.unpack_from('<I',raw,4)[0]
    assert frames in [48,64]
    # Native collision-state changes are track kind4. State0x16 marks the
    # active body/weapon state in these two original second-ground records.
    collision=[struct.unpack_from('<f',raw,at+i*16)[0] for track,kind,count,at in tracks(raw) if kind==4
               for i in range(count) if struct.unpack_from('<H',raw,at+i*16+6)[0]==0x16]
    assert collision
    old_hit=min(collision);new_hit=35. if frames==48 else 47.
    def warp(t):return t*new_hit/old_hit if t<=old_hit else new_hit+(t-old_hit)*(frames-new_hit)/(frames-old_hit)
    report=[]
    for track,kind,count,at in tracks(raw):
        old=[struct.unpack_from('<f',raw,at+i*16)[0] for i in range(count)]
        new=[warp(t) for t in old]
        if kind==5:
            assert count==2 and struct.unpack_from('<I',raw,at+4)[0]==1 and struct.unpack_from('<I',raw,at+20)[0]==0
            new=[float(frames-1),float(frames)]
        for i,t in enumerate(new):struct.pack_into('<f',data,at+i*16,t)
        assert all(a<=b for a,b in zip(new,new[1:]))
        report.append({'track':track,'kind':kind,'before_frames':old,'after_frames':new})
    changed={i for i,(a,b) in enumerate(zip(raw,data)) if a!=b}
    allowed={at+i*16+j for _,_,count,at in tracks(raw) for i in range(count) for j in range(4)}
    assert changed<=allowed and data[:80]==raw[:80] and len(data)==len(raw)
    return bytes(data),{'contact_before':old_hit,'contact_after':new_hit,'chain_opens':frames-1,'chain_closes':frames,
                        'tracks':report,'changed_bytes':len(changed),'counts_pointers_and_payloads_preserved':True}
