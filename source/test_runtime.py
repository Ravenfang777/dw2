"""Execute the built PE's real OnInit/OnFrame with a controlled Win64 mock host.

This checks the DLL's actual calling convention, relocations, imports, ability
entry, curve admission and reversible gate. It is not a Windows/game test.
"""
from pathlib import Path
import ctypes as C,json,struct,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parent
subprocess.run(['gcc','-std=c11','-O2','-shared','-fPIC','test_bridge.c','-o','test_bridge.so','-lm'],cwd=ROOT,check=True)
bridge=C.CDLL(str(ROOT/'test_bridge.so'))
for name,args,ret in [('bridge_reset',[C.c_size_t],None),('bridge_range',[C.c_size_t,C.c_size_t,C.c_uint],None),('bridge_modes',[C.c_int,C.c_int],None),('bridge_log',[],C.c_char_p),('bridge_queries',[],C.c_uint),('bridge_encode',[C.c_size_t],C.c_uint),('bridge_symbol',[C.c_char_p],C.c_size_t),('bridge_call0',[C.c_size_t],None),('bridge_init',[C.c_size_t],None)]:
    f=getattr(bridge,name);f.argtypes=args;f.restype=ret
bridge.bridge_test_options.argtypes=[C.c_int,C.c_int];bridge.bridge_test_options.restype=None
bridge.bridge_ability_count.argtypes=[C.c_size_t,C.c_uint,C.c_uint];bridge.bridge_ability_count.restype=C.c_uint
for name,args,ret in [('bridge_magic_modes',[C.c_int,C.c_int,C.c_int],None),('bridge_matrix',[C.c_size_t,C.c_size_t,C.c_uint,C.POINTER(C.c_float)],None),('bridge_point',[C.c_size_t,C.c_size_t,C.c_uint,C.c_float,C.POINTER(C.c_float)],None),('bridge_matrix_code',[],C.c_uint),('bridge_point_code',[],C.c_uint),('bridge_point_fraction',[],C.c_float)]:
    f=getattr(bridge,name);f.argtypes=args;f.restype=ret
for name,args,ret in [('bridge_air_modes',[C.c_int,C.c_uint],None),('bridge_control',[C.c_size_t,C.c_size_t,C.c_size_t],None),('bridge_control_calls',[],C.c_uint),('bridge_control_word',[C.c_uint],C.c_uint),('bridge_queue_calls',[],C.c_uint),('bridge_commit',[C.c_size_t],None),('bridge_native_glide_calls',[],C.c_uint),('bridge_glide',[C.c_size_t,C.c_size_t],None),('bridge_event',[C.c_size_t,C.c_size_t,C.c_uint,C.c_float],C.c_size_t)]:
    f=getattr(bridge,name);f.argtypes=args;f.restype=ret
bridge.bridge_move.argtypes=[C.c_size_t,C.c_size_t,C.POINTER(C.c_float)];bridge.bridge_move.restype=C.c_float
bridge.bridge_move_calls.argtypes=[];bridge.bridge_move_calls.restype=C.c_uint
bridge.bridge_guard_row.argtypes=[C.c_size_t,C.c_size_t,C.c_uint];bridge.bridge_guard_row.restype=C.c_size_t
bridge.bridge_motion_advance.argtypes=[C.c_size_t,C.c_size_t,C.c_float];bridge.bridge_motion_advance.restype=C.c_size_t
bridge.bridge_guard_angle.argtypes=[C.c_size_t,C.c_size_t,C.c_size_t];bridge.bridge_guard_angle.restype=C.c_int
bridge.bridge_guard_pool.argtypes=[C.c_size_t];bridge.bridge_guard_pool.restype=C.c_int
bridge.bridge_glide_eligible.argtypes=[C.c_int];bridge.bridge_glide_eligible.restype=None
bridge.bridge_motion_delta.argtypes=[];bridge.bridge_motion_delta.restype=C.c_float
libc=C.CDLL(None);libc.mmap.argtypes=[C.c_void_p,C.c_size_t,C.c_int,C.c_int,C.c_int,C.c_long];libc.mmap.restype=C.c_void_p

libc.munmap.argtypes=[C.c_void_p,C.c_size_t];libc.munmap.restype=C.c_int
allocation_sizes={}
def allocate(n):
    addr=libc.mmap(None,n,7,0x22,-1,0)
    if addr in [None,C.c_void_p(-1).value]:raise OSError('mmap failed')
    allocation_sizes[int(addr)]=n
    return int(addr)
def put(p,data):C.memmove(p,data,len(data))
def r32(p):return C.c_uint.from_address(p).value
def r64(p):return C.c_uint64.from_address(p).value
def w32(p,v):C.c_uint.from_address(p).value=v
def w64(p,v):C.c_uint64.from_address(p).value=v

class Host:
    def __del__(self):
        for address in getattr(self,'buffers',[])+[getattr(self,'game',0),getattr(self,'image',0)]:
            size=allocation_sizes.pop(address,0)
            if size:libc.munmap(address,size)
    def __init__(self,slot=98,encoded_fields=False,stamp=1721645006,remove=0,conflict=0,magic=False,hand_magic=1,fail_alloc=0,fail_protect=0,air=False,air_dodge=1,control_mode=0,guard=False,jump=False,test_page=1,profile_override=0):
        self.game=allocate(0x3000000);bridge.bridge_reset(self.game);bridge.bridge_range(self.game,0x3000000,0x40);bridge.bridge_modes(remove,conflict)
        bridge.bridge_test_options(test_page,profile_override)
        w32(self.game+60,0x80);w32(self.game+0x80,0x4550);w32(self.game+0x88,stamp);put(self.game+0x233fbdc,struct.pack('<f',1.))
        self.buffers=[]
        self.actor=self.buffer(bytes(0x800));w32(self.actor+0x374,1);w64(self.game+0x2537e48,self.actor)
        self.save=self.game+0x2de9360;put(self.save+4,b'\x64\x05\x0a');put(self.save+0x44,b'\x81\x82\x00')
        self.native_table=bytes((i*7)%256 for i in range(65*12));self.original_table=self.buffer(self.native_table);w64(self.game+0x2d36d48,self.original_table)
        put(self.game+0x394770,(ROOT/'fixtures/native_event_at.bin').read_bytes())
        put(self.game+0x38adc0,b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeDecode'))+b'\xff\xe0')
        self.all_records=json.loads((ROOT/'curve_validation.json').read_text())['motions']
        self.activate_bank(slot==60,encoded_fields)
        # Native pointer-to-handle helper uses the ABI of the existing reference.
        put(self.game+0x38ad90,b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeHandle'))+b'\xff\xe0')
        bridge.bridge_magic_modes(hand_magic,fail_alloc,fail_protect)
        if magic:
            self.matrix_prefix=bytes.fromhex('48895c24084889742410574883ec20')
            self.point_prefix=bytes.fromhex('405355574881ec800000000f29742460')
            call=lambda n:b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(n))+b'\xff\xd0'
            put(self.game+0x29ea00,self.matrix_prefix+call(b'NativeMatrix')+bytes.fromhex('4883c4205f488b5c2408488b742410c3'))
            put(self.game+0x29eb20,self.point_prefix+call(b'NativePoint')+bytes.fromhex('0f287424604881c4800000005f5d5bc3'))
        bridge.bridge_air_modes(air_dodge,control_mode)
        self.dir=self.buffer(bytes(16))
        if air:
            self.glide_work=self.buffer(bytes(0x200));w32(self.actor+0x148,bridge.bridge_encode(self.glide_work));w32(self.glide_work+0x104,1)
            self.control_prefix=bytes.fromhex('48895c2418574883ec40488b0557e82a00')
            self.queue_prefix=bytes.fromhex('48895c2408574883ec20488bf9')
            call=lambda n:b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(n))+b'\xff\xd0'
            put(self.game+0x2a6220,self.control_prefix+call(b'NativeControl')+bytes.fromhex('4883c4405f488b5c2418c3'))
            put(self.game+0x29f980,self.queue_prefix+call(b'NativeQueue')+bytes.fromhex('4883c4205f488b5c2408c3'))
            put(self.game+0x2b26c0,(ROOT/'fixtures/native_glide_constructor.bin').read_bytes())
            self.glide_common_prefix=bytes.fromhex('40534883ec20488bd98b8948010000')
            put(self.game+0x2b2d30,self.glide_common_prefix+bytes.fromhex('4889d9')+call(b'NativeGlideCommon')+bytes.fromhex('4883c4205bc3'))
            super_constructor=bytearray((ROOT/'fixtures/native_glide_constructor.bin').read_bytes())
            struct.pack_into('<i',super_constructor,10,0x2b2d30-(0x2b2750+14));struct.pack_into('<i',super_constructor,25,0x38adc0-(0x2b2750+29));super_constructor[0x1d:0x24]=bytes.fromhex('83880401000001')
            put(self.game+0x2b2750,bytes(super_constructor))
            put(self.game+0x29fa30,self.queue_prefix+call(b'NativeAppend')+bytes.fromhex('4883c4205f488b5c2408c3'))
            self.move_prefix=bytes.fromhex('48895c2410574883ec40f70100100000')
            put(self.game+0x2af6a0,self.move_prefix+call(b'NativeMove')+bytes.fromhex('4883c4405f488b5c2410c3'))
            self.state_prefix=bytes.fromhex('48895c2410574883ec2048634170')
            put(self.game+0x2b1960,self.state_prefix+call(b'NativeSetState')+bytes.fromhex('4883c4205f488b5c2410c3'))
            put(self.game+0x297870,bytes.fromhex('f601047518f6818800000020750ff68144040000017506b801000000c333c0c3'))
        if guard:
            call=lambda n:b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(n))+b'\xff\xd0'
            put(self.game+0x2a3980,bytes.fromhex('48895c240848896c24104889742418')+bytes.fromhex('574883ec20')+call(b'NativeGuardRow')+bytes.fromhex('4883c4205f488b5c2408488b6c2410488b742418c3'))
            put(self.game+0x29f0a0,bytes.fromhex('405557488d6c24e84881ec18010000')+call(b'NativeMotionAdvance')+bytes.fromhex('4881c4180100005f5dc3'))
            put(self.game+0x2b4640,bytes.fromhex('4c8bdc49895b20574881eca0000000')+call(b'NativeGuardAngle')+bytes.fromhex('4881c4a00000005f488b5c2420c3'))
            put(self.game+0x2b47a0,bytes.fromhex('48896c241048897424185741564157')+bytes.fromhex('4883ec20')+call(b'NativeGuardPool')+bytes.fromhex('4883c420415f415e5f488b6c2410488b742418c3'))
            put(self.game+0x2b3270,bytes.fromhex('48895c2408574883ec20488bf9')+call(b'NativeGuardCreate')+bytes.fromhex('4883c4205f488b5c2408c3'))
            put(self.game+0x2b3560,bytes.fromhex('4883ec2883b9b400000000')+call(b'NativeGuardFree')+bytes.fromhex('4883c428c3'))
            # Preserve native RIP-relative anchor; the following ABI mock returns the mask.
            put(self.game+0x2b3760,bytes.fromhex('8b15aa3fb00233c9')+b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeGuardMask'))+b'\xff\xe0')
        if jump:
            assert air
            put(self.game+0x2afda0,(ROOT/'fixtures/native_jump_launch.bin').read_bytes())
            put(self.game+0x2af530,(ROOT/'fixtures/native_jump_curve.bin').read_bytes())
            for rva,raw in json.loads((ROOT/'fixtures/native_jump_constants.json').read_text()).items():put(self.game+int(rva,16),bytes.fromhex(raw))
            put(self.game+0x38503e,bytes.fromhex('f30f51c0c3')) # sqrtf SSE stub
            put(self.game+0x3850f2,b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeSinf'))+b'\xff\xe0')
            put(self.game+0x386ad0,bytes.fromhex('0f10020f1101c3')) # exact native vector copy
            put(self.game+0x2af630,b'\xc3') # queue/animation handoff is outside this arc sample
            self.jump_stats=self.buffer(bytes(0xe4));w32(self.actor+0x6c,bridge.bridge_encode(self.jump_stats))
        self.load_pe()
    def activate_bank(self,olympus,encoded_fields=False):
        self.slot=60 if olympus else 98
        self.records=[r for r in self.all_records if not olympus or r['olympus_slot']!=0xffffffff]
        self.record_by_slot={r['normal_slot']:r for r in self.records}
        raw={r['normal_slot']:(ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes() for r in self.records}
        packed=bytearray();offsets={}
        for record in self.records:
            key=record['normal_slot'];packed.extend(bytes((-len(packed))%16));offsets[key]=len(packed);packed.extend(raw[key])
        glide_raw={slot:(ROOT/f'fixtures/native_glide_s{slot:03}.bin').read_bytes() for slot in range(75,79)}
        glide_offsets={}
        for slot,data in glide_raw.items():
            packed.extend(bytes((-len(packed))%16));glide_offsets[slot]=len(packed);packed.extend(data)
        control=(ROOT/'fixtures/control_native_s105.bin').read_bytes();packed.extend(bytes((-len(packed))%16));control_offset=len(packed);packed.extend(control)
        region=self.buffer(bytes(packed));self.unmapped=region+control_offset;self.unmapped_original=control
        self.array=self.buffer(bytes(128*4));self.motions={};self.runtime_originals={}
        for record in self.records:
            key=record['normal_slot'];motion=region+offsets[key];data=raw[key]
            if encoded_fields:
                for off in [20,28,36,40,48,56,60,68,76]:
                    value=r32(motion+off)
                    if value and value<len(data):w32(motion+off,bridge.bridge_encode(motion+value))
            if encoded_fields:
                event_at=struct.unpack_from('<I',data,60)[0]
                while struct.unpack_from('<I',data,event_at)[0]!=0xffffffff:
                    offset=struct.unpack_from('<I',data,event_at+8)[0];w32(motion+event_at+8,bridge.bridge_encode(motion+offset));event_at+=12
            self.motions[key]=motion;self.runtime_originals[key]=C.string_at(motion,len(data))
            slot=record['olympus_slot'] if olympus else record['normal_slot'];w32(self.array+slot*4,bridge.bridge_encode(motion))
        self.native_glide_motions={};self.native_glide_originals={}
        for slot,data in glide_raw.items():
            motion=region+glide_offsets[slot]
            if encoded_fields:
                for off in [20,28,36,40,48,56,60,68,76]:
                    value=r32(motion+off)
                    if value and value<len(data):w32(motion+off,bridge.bridge_encode(motion+value))
                at=struct.unpack_from('<I',data,60)[0]
                while struct.unpack_from('<I',data,at)[0]!=0xffffffff:
                    value=struct.unpack_from('<I',data,at+8)[0];w32(motion+at+8,bridge.bridge_encode(motion+value));at+=12
            self.native_glide_motions[slot]=motion;self.native_glide_originals[slot]=C.string_at(motion,len(data))
            w32(self.array+(slot-38 if olympus else slot)*4,bridge.bridge_encode(motion))
        w32(self.array+(67 if olympus else 105)*4,bridge.bridge_encode(self.unmapped))
        self.motion=self.motions[98];self.original_motion=raw[98]
        self.native_reactions={}
        for row in json.loads((ROOT/'fixtures/native_reactions.json').read_text()):
            key=row['normal_slot'];data=(ROOT/f'fixtures/native_reaction_s{key:03}.bin').read_bytes();motion=self.buffer(data)
            if encoded_fields:
                for off in [20,28,36,40,48,56,60,68,76]:
                    value=r32(motion+off)
                    if value and value<len(data):w32(motion+off,bridge.bridge_encode(motion+value))
                at=struct.unpack_from('<I',data,60)[0]
                while struct.unpack_from('<I',data,at)[0]!=0xffffffff:
                    value=struct.unpack_from('<I',data,at+8)[0];w32(motion+at+8,bridge.bridge_encode(motion+value));at+=12
            self.native_reactions[key]=(motion,C.string_at(motion,len(data)))
            w32(self.array+(row['olympus_slot'] if olympus else key)*4,bridge.bridge_encode(motion))
        self.key_offset=struct.unpack_from('<I',raw[98],40)[0];self.runtime_original=self.runtime_originals[98]
        w32(self.actor+0x1d4,bridge.bridge_encode(self.array))
        self.request_original=(ROOT/f"fixtures/requests_{'he' if olympus else 'normal'}_original.bin").read_bytes()
        self.requests=self.buffer(self.request_original)
        self.original_request_handle=bridge.bridge_encode(self.requests)
        w32(self.actor+0x1d8,self.original_request_handle)
    def buffer(self,data):
        p=allocate((len(data)+4095)&~4095);put(p,data);bridge.bridge_range(p,len(data),4);self.buffers.append(p);return p
    def load_pe(self):
        dll=ROOT/'kh1-terra.dll'
        if not dll.exists():dll=ROOT.parent/'dll/kh1-terra.dll'
        data=dll.read_bytes();pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];op=pe+24
        preferred=struct.unpack_from('<Q',data,op+24)[0];size=struct.unpack_from('<I',data,op+56)[0];headers=struct.unpack_from('<I',data,op+60)[0]
        p=allocate(size);self.image=p;bridge.bridge_range(p,size,0x40);put(p,data[:headers])
        sh=op+struct.unpack_from('<H',data,pe+20)[0]
        for i in range(n):
            s=sh+i*40;vs,va,rs,rp=struct.unpack_from('<4I',data,s+8)
            if rs:put(p+va,data[rp:rp+rs])
        directory=op+112
        reloc,size_reloc=struct.unpack_from('<II',data,directory+5*8);assert reloc and size_reloc
        offset=0
        while offset<size_reloc:
            page,span=struct.unpack('<II',C.string_at(p+reloc+offset,8))
            for at in range(8,span,2):
                item=C.c_ushort.from_address(p+reloc+offset+at).value
                if item>>12==10:
                    q=p+page+(item&4095);w64(q,(r64(q)+p-preferred)&0xffffffffffffffff)
                else:assert item>>12==0
            offset+=span
        imp=r32(p+directory+8)
        while r32(p+imp):
            ilt=r32(p+imp);iat=r32(p+imp+16);index=0
            while r64(p+ilt+index*8):
                name_rva=r64(p+ilt+index*8);name=C.string_at(p+name_rva+2);address=bridge.bridge_symbol(name);assert address,name
                w64(p+iat+index*8,address);index+=1
            imp+=20
        export=r32(p+directory);count=r32(p+export+24);functions=r32(p+export+28);names=r32(p+export+32);ordinals=r32(p+export+36)
        self.exports={}
        for i in range(count):
            name=C.string_at(p+r32(p+names+i*4)).decode();ordinal=C.c_ushort.from_address(p+ordinals+i*2).value
            self.exports[name]=p+r32(p+functions+ordinal*4)
        assert set(self.exports)=={'OnInit','OnFrame','DllMain'}
        bridge.bridge_init(self.exports['OnInit'])
    def frame(self):bridge.bridge_call0(self.exports['OnFrame'])
    def native_count(self,id_):
        w64(self.game+0x2868ba0,self.save)
        put(self.game+0x284be0,(ROOT/'fixtures/native_ability_count.bin').read_bytes())
        return bridge.bridge_ability_count(self.game+0x284be0,id_,0)
    def abilities(self):return C.string_at(self.save+0x44,48)
    def equip(self,on,profile=0):
        id_=116+profile;data=bytearray(self.abilities());i=next(i for i,v in enumerate(data) if v&127==id_);data[i]=id_ if on else id_|128;put(self.save+0x44,bytes(data))
    def decode(self,h):return r64(self.game+0x2ee3980+((h&0x7fffffff)>>25)*8)+(h&0x1ffffff)
    def body(self,slot=98):return C.string_at(self.motions[slot],len(self.runtime_originals[slot]))
    def expected(self,slot,on):
        r=self.record_by_slot[slot];folder=ROOT/'fixtures'
        if int(on)>1:
            candidate=ROOT/f'sets/p{int(on)-1}/fixtures'
            if (candidate/f"terra_{r['fixture_stem']}.bin").exists():folder=candidate
        data=bytearray((folder/f"{'terra' if on else 'original'}_{r['fixture_stem']}.bin").read_bytes())
        data[:80]=self.runtime_originals[slot][:80]
        event_at=struct.unpack_from('<I',(ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes(),60)[0]
        while struct.unpack_from('<I',data,event_at)[0]!=0xffffffff:
            data[event_at+8:event_at+12]=self.runtime_originals[slot][event_at+8:event_at+12];event_at+=12
        return bytes(data)
    def assert_all(self,test,on):
        for r in self.records:test.assertEqual(self.body(r['normal_slot']),self.expected(r['normal_slot'],on),r['action'])
        test.assertEqual(r32(self.actor+0x1d8),self.original_request_handle)
        test.assertEqual(C.string_at(self.requests,len(self.request_original)),self.request_original)
    def snapshot(self):return {r['normal_slot']:self.body(r['normal_slot']) for r in self.records}
    def matrix(self,actor=None,code=0x30):
        out=(C.c_float*16)();bridge.bridge_matrix(self.game+0x29ea00,self.actor if actor is None else actor,code,out);return list(out)
    def point(self,actor=None,code=0x30,fraction=.75):
        out=(C.c_float*4)();bridge.bridge_point(self.game+0x29eb20,self.actor if actor is None else actor,code,fraction,out);return list(out)

    def control(self,down=0,pressed=0,state=2,request=6,height=100,tilt=0,x=0,z=0,actor=None):
        a=self.actor if actor is None else actor
        w32(a+0x70,state);w32(a+0x164,request);put(a+0x3d4,struct.pack('<f',height))
        for field in [4,8,16,20]:w32(self.game+0x298ca90+field,(down if field in [4,16] else pressed))
        put(self.dir,struct.pack('<4f',x,0,z,tilt))
        bridge.bridge_control(self.game+0x2a6220,a,self.dir)
    def move(self,dt=1.):
        put(self.game+0x233fbdc,struct.pack('<f',dt));out=self.buffer(bytes(16))
        result=bridge.bridge_move(self.game+0x2af6a0,self.actor,C.cast(out,C.POINTER(C.c_float)))
        return list((C.c_float*4).from_address(out)),result
    def blizzard_body(self,slot):
        data=bytearray((ROOT/f'blizzard/fixtures/terra_s{slot:03}.bin').read_bytes());data[:80]=self.runtime_originals[slot][:80]
        at=struct.unpack_from('<I',(ROOT/f'blizzard/fixtures/terra_s{slot:03}.bin').read_bytes(),60)[0]
        while struct.unpack_from('<I',data,at)[0]!=0xffffffff:
            data[at+8:at+12]=self.runtime_originals[slot][at+8:at+12];at+=12
        return bytes(data)
    def dodge_body(self):
        data=bytearray((ROOT/'dodge/fixtures/terra_s010.bin').read_bytes());data[:80]=self.runtime_originals[10][:80];return bytes(data)
    def event(self,slot,kind,frame,track=0):
        p=bridge.bridge_event(self.game+0x394770,self.motions[slot],(kind<<16)|track,frame)
        return None if not p else r32(p+4)
    def native_glide(self):bridge.bridge_glide(self.game+0x2b26c0,self.actor)
    def queue(self,request,frame=0):
        w32(self.actor+0x178,1);w32(self.actor+0x17c,request);put(self.actor+0x184,struct.pack('<f',frame))
    def clock(self,value):put(self.actor+0x16c,struct.pack('<f',value))
    def arm_air(self,profile=0):
        self.frame();self.equip(True,profile);self.frame();self.control(state=0,request=0,height=0)
        self.control(state=2,request=6)

class RuntimeTests(unittest.TestCase):
    def test_all_eleven_names_zero_ap_native_table_copy_and_default_off(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:2],before[:2])
        self.assertEqual(list(h.abilities()[2:13]),[i|0x80 for i in range(116,127)])
        self.assertEqual(h.abilities()[13:],bytes(35));h.assert_all(self,False)
        for i,name in enumerate(['terra']+[f'terra {j}' for j in range(1,11)]):
            row=table+(115+i)*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
            actual=C.string_at(h.decode(r32(row+4)))
            expected=bytes((ord(c)+0xe4)&255 if c.islower() else (ord(c)+0xf1)&255 if c.isdigit() else 1 for c in name)
            self.assertEqual(actual,expected,name)
    def test_all_eleven_exact_profiles_round_trip_both_banks_with_encoded_pointers(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in range(11):
                h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
                self.assertEqual([b for b in h.abilities() if 116<=b<=126],[116+profile])
            h.equip(False,10);h.frame();h.assert_all(self,False)
    def test_every_profile_can_switch_directly_to_every_other_profile(self):
        h=Host();h.frame()
        for old in range(11):
            h.equip(True,old);h.frame()
            for new in range(11):
                h.equip(True,new);h.frame();self.assertEqual([b for b in h.abilities() if 116<=b<=126],[116+new]);h.assert_all(self,new+1)
    def test_saved_terra_selection_retained_and_new_missing_entries_learned_off(self):
        h=Host();put(h.save+0x44,bytes([1,116|128,126,2,0]));h.frame()
        self.assertEqual([b for b in h.abilities() if 116<=b<=126],[126]);h.assert_all(self,11)
        h.frame();h.assert_all(self,11)
    def test_first_terra_install_reuses_custom_test_ids_without_native_or_ap_changes(self):
        h=Host();put(h.save+0x44,bytes([6,0x97,117,126,65,0]));before=C.string_at(h.save,0x74);h.frame()
        self.assertEqual(h.abilities()[:5],bytes([6,0x97,117|128,126|128,65]))
        self.assertEqual(C.string_at(h.save,0x44),before[:0x44]);h.assert_all(self,False)
        h.equip(True);h.frame();h.assert_all(self,True)
    def test_already_learned_entries_never_duplicate_or_evict_natives(self):
        h=Host();h.frame();before=h.abilities()
        for _ in range(10):h.frame()
        self.assertEqual(h.abilities(),before)
        self.assertEqual(sum(b&127==116 for b in h.abilities()),1)
    def test_full_native_ability_list_is_never_evicted(self):
        h=Host();data=bytes(range(1,49));put(h.save+0x44,data);h.frame()
        self.assertEqual(h.abilities(),data);h.assert_all(self,False)
    def test_incomplete_space_prioritizes_main_and_preserves_each_native_byte(self):
        h=Host();data=bytes(range(1,45))+bytes(4);put(h.save+0x44,data);h.frame()
        self.assertEqual(h.abilities()[:44],data[:44]);self.assertEqual(h.abilities()[44:],bytes([244,245,246,0]))
        self.assertIn('TERRA PAGED TESTS',bridge.bridge_log().decode());h.assert_all(self,False)
    def test_legacy_ten_styles_no_longer_block_main_at_47_occupied_slots(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True)
            native=bytes(v|(128 if v%2 else 0) for v in range(1,38))
            put(h.save+0x44,native+bytes(range(117,127))+b'\0')
            outside=C.string_at(h.save,0x44);neighbor=bytes(range(64));put(h.save+0x74,neighbor)
            h.frame();self.assertEqual(h.abilities()[:37],native)
            self.assertEqual(set(b&127 for b in h.abilities()[37:-1]),set(range(116,126)))
            self.assertTrue(all(b&128 for b in h.abilities()[37:-1]));self.assertEqual(h.abilities()[-1],0)
            self.assertEqual(C.string_at(h.save,0x44),outside);self.assertEqual(C.string_at(h.save+0x74,64),neighbor)
            self.assertIn('TERRA ABILITY INPUT occupied=47\r\n',bridge.bridge_log().decode())
            self.assertIn('TERRA TEST PAGES=2\r\n',bridge.bridge_log().decode())
            h.assert_all(self,False);h.equip(True);h.frame();h.assert_all(self,True)
            self.assertEqual(h.native_count(116),1);self.assertEqual(h.native_count(126),0)
    def test_second_page_reaches_test_ten_and_keeps_main_selection_through_restart(self):
        native=bytes(range(1,38));saved=None
        h=Host();put(h.save+0x44,native+bytes(i|128 for i in range(117,127))+b'\0');h.frame();h.equip(True);h.frame();saved=h.abilities();del h
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True,test_page=2);put(h.save+0x44,saved);h.frame()
            self.assertEqual(h.abilities()[:37],native)
            self.assertEqual(set(b&127 for b in h.abilities() if 116<=b&127<=126),{116,126})
            h.assert_all(self,True);h.equip(True,10);h.frame();h.assert_all(self,11)
            self.assertEqual(h.native_count(126),1);self.assertEqual(h.native_count(116),0)
    def test_every_test_is_reachable_on_capacity_driven_pages(self):
        for other_count in [0,36,37,38,39,40,41,42,43,44,45]:
            native=bytes((i%35+1)|(128 if i%2 else 0) for i in range(other_count))
            capacity=min(11,47-other_count);per_page=capacity-1;pages=(10+per_page-1)//per_page;seen=set()
            for page in range(1,pages+1):
                h=Host(test_page=page);put(h.save+0x44,native+bytes(48-other_count));h.frame()
                self.assertEqual(h.abilities()[:other_count],native);self.assertEqual(h.abilities()[-1],0)
                ids=[b&127 for b in h.abilities() if 116<=b&127<=126];self.assertIn(116,ids)
                expected={116}|set(range(116+(page-1)*per_page+1,116+min(page*per_page,10)+1))
                self.assertEqual(set(ids),expected);seen.update(v-116 for v in ids)
            self.assertEqual(seen,set(range(11)),other_count)
    def test_exact_fit_36_other_entries_uses_47_bytes_and_native_terminator(self):
        h=Host(encoded_fields=True);native=bytes(range(1,37));put(h.save+0x44,native+bytes(12));put(h.save+0x74,bytes([116])*48);h.frame()
        self.assertEqual(h.abilities()[:36],native);self.assertEqual(h.abilities()[47],0)
        for profile in range(11):
            h.equip(True,profile);h.frame();h.assert_all(self,profile+1);self.assertEqual(h.native_count(116+profile),1)
        self.assertEqual(C.string_at(h.save+0x74,48),bytes([116])*48)
    def test_only_duplicate_terra_entries_compact_native_and_foreign_copies_survive(self):
        h=Host();original=bytes([1,1,129,66,115,116,116|128,126|128,65,65,66])+bytes(37);put(h.save+0x44,original);h.frame()
        foreign=lambda data:bytes(b for b in data if b and not 116<=b&127<=126)
        self.assertEqual(foreign(h.abilities()),foreign(original))
        for id_ in range(116,127):self.assertEqual(sum(b&127==id_ for b in h.abilities()),1)
        self.assertEqual([b for b in h.abilities() if 116<=b<=126],[116]);h.assert_all(self,True)
    def test_one_available_slot_adds_main_and_zero_available_preserves_entire_list(self):
        for n in [46,47,48]:
            h=Host();native=bytes((i%35+1)|(128 if i%2 else 0) for i in range(n));put(h.save+0x44,native+bytes(48-n));h.frame()
            self.assertEqual(h.abilities()[:n],native)
            if n==46:
                self.assertEqual(h.abilities()[46:],bytes([244,0]));h.equip(True);h.frame();h.assert_all(self,True)
            else:self.assertEqual(h.abilities(),native+bytes(48-n));h.assert_all(self,False)
    def test_full_list_can_test_main_and_last_profile_using_explicit_config_override(self):
        native=bytes((i%35+1)|128 for i in range(47))+b'\0'
        for bank in [98,60]:
            for profile in [1,11]:
                h=Host(slot=bank,profile_override=profile);put(h.save+0x44,native);h.frame()
                self.assertEqual(h.abilities(),native);h.assert_all(self,profile)
    def test_page_setup_waits_for_idle_without_touching_abilities_or_motions(self):
        h=Host();data=bytes(range(1,38))+bytes(range(117,127))+b'\0';put(h.save+0x44,data);w32(h.actor+0x164,2)
        h.frame();self.assertEqual(h.abilities(),data);h.assert_all(self,False)
        w32(h.actor+0x164,0);h.frame();self.assertNotEqual(h.abilities(),data);self.assertIn(244,h.abilities());h.assert_all(self,False)
    def test_native_reward_can_reduce_test_page_without_losing_a_native_copy(self):
        h=Host();native=bytes(range(1,37));put(h.save+0x44,native+bytes(12));h.frame();h.equip(True);h.frame()
        filled=bytearray(h.abilities());filled[-1]=37|128;put(h.save+0x44,bytes(filled));h.frame()
        self.assertEqual(bytes(b for b in h.abilities() if b and not 116<=b&127<=126),native+bytes([37|128]))
        self.assertEqual(h.abilities()[-1],0);self.assertNotIn(126|128,h.abilities());h.assert_all(self,True)
    def test_bad_page_and_override_values_are_bounded(self):
        native=bytes(range(1,38));data=native+bytes(11)
        for page in [0,-1,100]:
            h=Host(test_page=page,profile_override=12);put(h.save+0x44,data);h.frame()
            self.assertIn(245,h.abilities());self.assertNotIn(254,h.abilities());h.assert_all(self,False)
        h=Host(test_page=10);put(h.save+0x44,data);h.frame();self.assertIn(254,h.abilities());self.assertNotIn(245,h.abilities())
    def test_paged_uninstall_removes_all_terra_ids_and_ignores_override(self):
        h=Host(test_page=2,profile_override=11,remove=1);data=bytes([1,129,115,116,126|128])+bytes(43);put(h.save+0x44,data);h.frame()
        self.assertEqual(h.abilities(),bytes([1,129,115])+bytes(45));h.assert_all(self,False)
    def test_paged_layout_and_diagnostics_do_not_repeat_every_frame(self):
        h=Host();put(h.save+0x44,bytes(range(1,38))+bytes(11));h.frame();original=h.abilities();logged=bridge.bridge_log()
        for _ in range(30):h.frame()
        self.assertEqual(h.abilities(),original);self.assertEqual(bridge.bridge_log(),logged)
    def test_unstable_ability_tail_causes_no_save_or_body_write(self):
        h=Host();data=bytes([1,0,2])+bytes(45);put(h.save+0x44,data);h.frame();self.assertEqual(h.abilities(),data);h.assert_all(self,False)
    def test_all_profile_switches_wait_for_idle_during_combat_cast_jump_and_walk(self):
        h=Host();h.frame();h.equip(True)
        for request in [1,2,4,5,6,0x36,0x3e,0x48,0x83,0xc8,0xc9,0xcc,0xd4,0xdc]:
            w32(h.actor+0x164,request);h.frame();h.assert_all(self,False)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,True)
        h.equip(True,10);w32(h.actor+0x164,0xcb);h.frame();h.assert_all(self,True)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,11)
    def test_unequipping_during_guard_restores_only_after_idle(self):
        h=Host();h.frame();h.equip(True);h.frame();w32(h.actor+0x164,0xd4);h.equip(False);h.frame();h.assert_all(self,True)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,False)
    def test_uninstall_removes_only_custom_116_to_126_and_restores_bodies(self):
        h=Host(remove=1);put(h.save+0x44,bytes([6,116,117|128,126,65,115,0]));h.frame()
        self.assertEqual(h.abilities()[:5],bytes([6,65,115,0,0]));h.assert_all(self,False)
    def test_first_and_last_body_record_corruptions_block_all_initial_writes(self):
        for slot in [0,117]:
            h=Host();h.frame();h.equip(True);p=h.motions[slot];w32(p+r32(p+40)+4,0x7f123456);before=h.snapshot();h.frame()
            self.assertEqual(h.snapshot(),before)
    def test_early_locomotion_and_late_air_schema_mismatch_block_all_writes(self):
        for slot in [4,104]:
            h=Host();h.frame();h.equip(True);w32(h.motions[slot]+44,70);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_unknown_native_motion_pointer_prevents_partial_profile_application(self):
        h=Host();h.frame();h.equip(True);w32(h.array+104*4,0);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_all_native_headers_events_requests_and_helper_hierarchy_stay_original(self):
        h=Host(encoded_fields=True);h.frame()
        arrays=C.string_at(h.array,512);requests=C.string_at(h.requests,len(h.request_original))
        for profile in range(11):
            h.equip(True,profile);h.frame()
            self.assertEqual(C.string_at(h.array,512),arrays);self.assertEqual(C.string_at(h.requests,len(requests)),requests)
            for r in h.records:
                raw=h.body(r['normal_slot']);original=h.runtime_originals[r['normal_slot']];self.assertEqual(raw[:80],original[:80])
                source=(ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes()
                first=struct.unpack_from('<I',source,60)[0];self.assertEqual(raw[first:],original[first:],r['action'])
    def test_native_glide_superglide_and_damage_reaction_records_are_unchanged(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in range(11):
                h.equip(True,profile);h.frame()
                for slot,p in h.native_glide_motions.items():self.assertEqual(C.string_at(p,len(h.native_glide_originals[slot])),h.native_glide_originals[slot])
                for slot,(p,raw) in h.native_reactions.items():self.assertEqual(C.string_at(p,len(raw)),raw)
    def test_native_unmapped_slapshot_is_never_replaced(self):
        h=Host();h.frame();h.equip(True);h.frame();self.assertEqual(C.string_at(h.unmapped,len(h.unmapped_original)),h.unmapped_original)
    def test_original_cast_pointer_is_never_replaced_even_when_foreign(self):
        h=Host();h.frame();p=h.buffer(bytes(1408));handle=bridge.bridge_encode(p);w32(h.actor+0x1d8,handle);h.equip(True);h.frame()
        self.assertEqual(r32(h.actor+0x1d8),handle);self.assertEqual(h.body(98),h.expected(98,1))
    def test_unknown_executable_build_and_conflicting_mods_publish_nothing(self):
        for args in [{'stamp':0},{'conflict':1},{'conflict':2},{'conflict':3}]:
            h=Host(**args);before=h.abilities();table=r64(h.game+0x2d36d48);h.frame()
            self.assertEqual(h.abilities(),before);self.assertEqual(r64(h.game+0x2d36d48),table);h.assert_all(self,False)
    def test_no_stale_writes_after_actor_unload(self):
        h=Host();h.frame();h.equip(True);h.frame();before=h.snapshot();w64(h.game+0x2537e48,0);h.equip(False);h.frame();self.assertEqual(h.snapshot(),before)
    def test_reloaded_record_at_same_address_rebinds_safely(self):
        h=Host();h.frame();h.equip(True);h.frame();put(h.motion,h.runtime_original);h.frame();h.assert_all(self,True)
    def test_bank_change_uses_the_c8_signature_and_restores_on_reentry(self):
        h=Host();h.frame();h.equip(True);h.frame();h.activate_bank(True,True);h.frame();h.assert_all(self,True)
        h.equip(False);h.frame();h.assert_all(self,False);h.activate_bank(False,True);h.frame();h.assert_all(self,False)
    def test_noncontiguous_native_part_pointers_remain_supported(self):
        h=Host(encoded_fields=True);h.frame();m=h.motions[98];source=(ROOT/'fixtures/original_s098.bin').read_bytes()
        offset=struct.unpack_from('<I',source,40)[0];end=struct.unpack_from('<I',source,48)[0]
        # Use the original descriptor spans to preserve all native body keys.
        n=max(struct.unpack_from('<H',source,struct.unpack_from('<I',source,p)[0]+i*6+4)[0]+source[struct.unpack_from('<I',source,p)[0]+i*6+3] for p,c in [(28,24),(36,32)] for i in range(struct.unpack_from('<I',source,c)[0]))*16
        data=C.string_at(m+offset,n);external=h.buffer(data);w32(m+40,bridge.bridge_encode(external));h.equip(True);h.frame()
        self.assertNotEqual(C.string_at(external,n),data);self.assertEqual(r32(m+40),bridge.bridge_encode(external))
    def test_cached_scalar_and_non_sentinel_data_changes_are_not_overwritten(self):
        for mutation in ['scalar','body']:
            h=Host();h.frame();h.equip(True);h.frame();p=h.motions[98]
            if mutation=='scalar':w32(p+24,999)
            else:C.c_ubyte.from_address(p+r32(p+40)+5).value^=1
            before=h.snapshot();h.equip(False);h.frame();self.assertEqual(h.snapshot(),before)
    def test_frame_cache_has_bounded_memory_queries(self):
        h=Host(encoded_fields=True);h.frame();h.equip(True);h.frame();before=bridge.bridge_queries()
        for _ in range(50):h.frame()
        self.assertLessEqual(bridge.bridge_queries()-before,7*50)
    def test_temporary_residency_loss_readmits_identical_bodies_without_midaction_writes(self):
        h=Host();h.frame();h.equip(True);h.frame();w32(h.actor+0x374,0);h.frame();w32(h.actor+0x374,1);w32(h.actor+0x164,2);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
        self.assertIn('BINDING RECOVERED',bridge.bridge_log().decode())

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_terra_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
