"""Execute the built PE's real OnInit/OnFrame with a controlled Win64 mock host.

This checks the DLL's actual calling convention, relocations, imports, ability
entry, curve admission and reversible gate. It is not a Windows/game test.
"""
from pathlib import Path
import ctypes as C,json,struct,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parent
subprocess.run(['gcc','-std=c11','-O2','-shared','-fPIC','test_bridge.c','-o','test_bridge.so'],cwd=ROOT,check=True)
bridge=C.CDLL(str(ROOT/'test_bridge.so'))
for name,args,ret in [('bridge_reset',[C.c_size_t],None),('bridge_range',[C.c_size_t,C.c_size_t,C.c_uint],None),('bridge_modes',[C.c_int,C.c_int],None),('bridge_log',[],C.c_char_p),('bridge_queries',[],C.c_uint),('bridge_encode',[C.c_size_t],C.c_uint),('bridge_symbol',[C.c_char_p],C.c_size_t),('bridge_call0',[C.c_size_t],None),('bridge_init',[C.c_size_t],None)]:
    f=getattr(bridge,name);f.argtypes=args;f.restype=ret
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
    def __init__(self,slot=98,encoded_fields=False,stamp=1721645006,remove=0,conflict=0,magic=False,hand_magic=1,fail_alloc=0,fail_protect=0,air=False,air_dodge=1,control_mode=0,guard=False):
        self.game=allocate(0x3000000);bridge.bridge_reset(self.game);bridge.bridge_range(self.game,0x3000000,0x40);bridge.bridge_modes(remove,conflict)
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
        dll=ROOT/'kh1-aqua.dll'
        if not dll.exists():dll=ROOT.parent/'dll/kh1-aqua.dll'
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
    def abilities(self):return C.string_at(self.save+0x44,48)
    def equip(self,on,profile=0):
        id_=117+profile;data=bytearray(self.abilities());i=next(i for i,v in enumerate(data) if v&127==id_);data[i]=id_ if on else id_|128;put(self.save+0x44,bytes(data))
    def decode(self,h):return r64(self.game+0x2ee3980+((h&0x7fffffff)>>25)*8)+(h&0x1ffffff)
    def body(self,slot=98):return C.string_at(self.motions[slot],len(self.runtime_originals[slot]))
    def expected(self,slot,on):
        r=self.record_by_slot[slot];folder=ROOT/'fixtures'
        if int(on)>1:
            candidate=ROOT/f'sets/p{int(on)-1}/fixtures'
            if (candidate/f"aqua_{r['fixture_stem']}.bin").exists():folder=candidate
        data=bytearray((folder/f"{'aqua' if on else 'original'}_{r['fixture_stem']}.bin").read_bytes())
        data[:80]=self.runtime_originals[slot][:80]
        event_at=struct.unpack_from('<I',(ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes(),60)[0]
        while struct.unpack_from('<I',data,event_at)[0]!=0xffffffff:
            data[event_at+8:event_at+12]=self.runtime_originals[slot][event_at+8:event_at+12];event_at+=12
        return bytes(data)
    def assert_all(self,test,on):
        for r in self.records:test.assertEqual(self.body(r['normal_slot']),self.expected(r['normal_slot'],on),r['action'])
        active=self.decode(r32(self.actor+0x1d8))
        variant='main' if int(on)==1 else 'aqua' if on else 'original'
        wanted=(ROOT/f"fixtures/requests_{'he' if self.slot==60 else 'normal'}_{variant}.bin").read_bytes()
        test.assertEqual(C.string_at(active,len(wanted)),wanted)
        test.assertEqual(C.string_at(self.requests,len(self.request_original)),self.request_original)
        if not on:test.assertEqual(r32(self.actor+0x1d8),self.original_request_handle)
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
        data=bytearray((ROOT/f'blizzard/fixtures/aqua_s{slot:03}.bin').read_bytes());data[:80]=self.runtime_originals[slot][:80]
        at=struct.unpack_from('<I',(ROOT/f'blizzard/fixtures/aqua_s{slot:03}.bin').read_bytes(),60)[0]
        while struct.unpack_from('<I',data,at)[0]!=0xffffffff:
            data[at+8:at+12]=self.runtime_originals[slot][at+8:at+12];at+=12
        return bytes(data)
    def dodge_body(self):
        data=bytearray((ROOT/'dodge/fixtures/aqua_s010.bin').read_bytes());data[:80]=self.runtime_originals[10][:80];return bytes(data)
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
    def test_main_tap_replaces_glide_commits_direction_and_can_repeat_after_a_new_tap(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,control_mode=4);h.arm_air()
            h.control(down=6,pressed=0);self.assertEqual(r32(h.actor+0x70),2);self.assertEqual(h.body(10),h.expected(10,1))
            h.control(down=0);h.control(down=6,pressed=6,x=-1,tilt=1)
            self.assertEqual(h.move()[0],[-14.,-.75,0.,14.])
            h.control(down=0,x=0,z=1,tilt=1)
            self.assertEqual(h.move()[0],[-14.,-.75,0.,14.])
            h.clock(39.);h.frame();calls=bridge.bridge_queue_calls()
            for _ in range(3):h.control(down=6,pressed=0)
            self.assertEqual(bridge.bridge_queue_calls(),calls);self.assertEqual(h.body(10),h.expected(10,1))
            h.control();h.control(down=6,pressed=6,x=1,tilt=1)
            self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(bridge.bridge_queue_calls(),calls+1)
            h.native_glide();self.assertEqual(bridge.bridge_native_glide_calls(),0)
    def test_main_neutral_tap_uses_existing_horizontal_momentum_then_character_facing(self):
        for momentum,facing,wanted in [((-4.,0.),(0.,1.),(-14.,0.)),((0.,0.),(1.,0.),(14.,0.))]:
            h=Host(air=True);h.arm_air()
            put(h.actor+0x3c0,struct.pack('<f',momentum[0]));put(h.actor+0x3c8,struct.pack('<f',momentum[1]))
            put(h.actor+0x30,struct.pack('<f',facing[0]));put(h.actor+0x38,struct.pack('<f',facing[1]))
            h.control(down=6,pressed=6);out,_=h.move();self.assertEqual((out[0],out[2]),wanted);self.assertEqual(out[1],-.75)
    def test_guard_hook_admission_and_protection_failures_leave_all_native_entries_original(self):
        for mode in ['bad_anchor','protect']:
            h=Host(guard=True,fail_protect=3 if mode=='protect' else 0)
            if mode=='bad_anchor':C.c_ubyte.from_address(h.game+0x2b4640).value^=1
            before={r:C.string_at(h.game+r,15) for r in [0x2a3980,0x29f0a0,0x2b4640]};h.frame()
            for r,data in before.items():self.assertEqual(C.string_at(h.game+r,15),data)
    def test_main_guard_runs_the_complete_forward_reverse_at_thirty_source_fps(self):
        h=Host(guard=True,encoded_fields=True);h.frame();h.equip(True);h.frame()
        self.assertEqual(bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d),0x1234)
        self.assertEqual(bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.),0x5678)
        self.assertAlmostEqual(bridge.bridge_motion_delta(),53./156.,places=6)
        h.clock(40.);bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
        self.assertAlmostEqual(bridge.bridge_motion_delta(),53./156.,places=6)
        self.assertEqual(h.event(110,1,0.),1);self.assertEqual(h.event(110,1,53.9),1);self.assertEqual(h.event(110,1,54.),0)
    def test_main_guard_accepts_front_side_and_rear_angles_only_with_its_own_live_guard_object(self):
        for bank in [98,60]:
            h=Host(guard=True,slot=bank);h.frame();h.equip(True);h.frame();bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d)
            first=h.game+0x2db4710;second=h.buffer(bytes(0xc0));w32(first,0x80800);w32(first+0x34,bridge.bridge_encode(h.actor))
            for native_class in [0x20000,0x40000,0x60000,0x80000]:
                w32(first,native_class|0x800)
                for direction in [1.,0.,-1.]:
                    put(second+0x10,struct.pack('<f',direction));self.assertEqual(bridge.bridge_guard_angle(h.game+0x2b4640,first,second),1)
            put(second+0x10,struct.pack('<f',-1.));w32(first,0xa0800)
            self.assertEqual(bridge.bridge_guard_angle(h.game+0x2b4640,first,second),0)
            w32(first,0x80800);w32(first+0x34,bridge.bridge_encode(h.buffer(bytes(0x800))))
            self.assertEqual(bridge.bridge_guard_angle(h.game+0x2b4640,first,second),0)
    def test_guard_rate_and_all_angle_behavior_end_after_interruption_and_do_not_leak_to_ars(self):
        h=Host(guard=True);h.frame();h.equip(True);h.frame();bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d)
        w32(h.actor+0x164,0x48);h.frame();w32(h.actor+0x164,0xd4);h.clock(0)
        bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.);self.assertEqual(bridge.bridge_motion_delta(),1.)
    def test_guard_and_finisher_motion_rates_are_main_only_and_do_not_write_native_headers(self):
        for profile in range(5):
            h=Host(guard=True);h.frame();h.equip(True,profile);h.frame();bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d)
            bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
            self.assertAlmostEqual(bridge.bridge_motion_delta(),53./156. if profile==0 else 1.,places=6)
            w32(h.actor+0x164,0xcb);h.clock(0.);bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
            self.assertAlmostEqual(bridge.bridge_motion_delta(),47./35. if profile==0 else 1.,places=6)
            for slot in [101,110]:self.assertEqual(h.body(slot)[:80],h.runtime_originals[slot][:80])
    def test_default_glide_preserves_all_four_native_bodies_clocks_and_queues_in_numbered_profiles(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.frame()
            for profile in range(1,5):
                w32(h.actor+0x164,0);w32(h.actor+0x178,0);h.equip(True,profile);h.frame()
                for clock in [0.,12.,40.,55.,90.,119.]:
                    h.clock(clock);h.control(state=21,request=0x71,down=4)
                    self.assertEqual(C.c_float.from_address(h.actor+0x16c).value,clock)
                    for slot,p in h.native_glide_motions.items():self.assertEqual(C.string_at(p,len(h.native_glide_originals[slot])),h.native_glide_originals[slot])
                h.queue(0x73,12.);h.control(state=21,request=0x72,down=4)
                self.assertEqual(C.c_float.from_address(h.actor+0x16c).value,12.)
                count=bridge.bridge_queue_calls();h.control(state=2,request=6)
                self.assertEqual(bridge.bridge_queue_calls(),count)
                self.assertEqual(h.body(10),h.expected(10,profile+1))
    def test_foreign_glide_motion_cannot_be_modified_or_block_other_aqua_animations(self):
        h=Host(air=True);p=h.native_glide_motions[75];C.c_ubyte.from_address(p+84).value^=1
        before=C.string_at(p,len(h.native_glide_originals[75]));h.frame();h.equip(True);h.frame();h.assert_all(self,1)
        h.clock(70);h.control(state=21,request=0x71,down=4)
        self.assertEqual(C.c_float.from_address(h.actor+0x16c).value,70.)
        self.assertEqual(C.string_at(p,len(before)),before)
    def test_dodge_sustains_horizontal_travel_and_small_lift_for_full_504(self):
        for dt in [.5,1.,2.]:
            h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,x=1,tilt=1)
            elapsed=0.;y=0.;x=0.
            while elapsed<38.:
                move,_=h.move(dt);elapsed+=dt;y-=move[1];x+=move[0]
                expected=.75*elapsed
                self.assertAlmostEqual(y,expected,delta=.005)
                self.assertAlmostEqual(x,14.*elapsed,delta=.005)
                put(h.actor+0x14,struct.pack('<f',-y))
            self.assertEqual(h.body(10),h.dodge_body())
            h.clock(39);h.frame();self.assertEqual(h.body(10),h.expected(10,1))
    def test_dodge_moves_in_each_stick_direction_without_diagonal_speed_boost(self):
        import math
        for bank in [98,60]:
          for x,z in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(.7,.7)]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.arm_air(1)
            h.control(down=6,pressed=6,x=x,z=z,tilt=1 if x or z else 0)
            before=C.string_at(h.actor+0x10,16);out,result=h.move()
            self.assertEqual(C.string_at(h.actor+0x10,16),before)
            self.assertAlmostEqual(out[1],-.75,places=5)
            distance=math.hypot(out[0],out[2]);self.assertAlmostEqual(distance,14 if x or z else 0,places=4)
            if x:self.assertGreater(out[0]*x,0)
            if z:self.assertGreater(out[2]*z,0)
            self.assertEqual(r32(h.actor+0x70),2)
    def test_dodge_small_lift_and_native_fall_handoff_without_teleporting(self):
        for step in [.5,1.,2.]:
            h=Host(air=True);h.arm_air();h.control(down=6,pressed=6)
            y=0.;peak=0.;total=0.
            while total<38.:
                out,_=h.move(step);y+=out[1];peak=max(peak,-y);total+=step
                put(h.actor+0x14,struct.pack('<f',y))
            self.assertAlmostEqual(peak,.75*total,places=4)
            h.clock(39);h.frame();self.assertEqual(h.body(10),h.expected(10,1))
            self.assertAlmostEqual(C.c_float.from_address(h.actor+0x3b4).value,y,places=4)
            self.assertEqual(C.c_float.from_address(h.actor+0x3b8).value,0.)
            out,_=h.move();self.assertEqual(out,[1,2,3,4])
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6);h.move()
        w32(h.game+0x298ca94,0);out,_=h.move();self.assertAlmostEqual(out[1],-.75,places=5)
    def test_live_stick_steering_reverses_direction_and_neutral_stops_only_horizontal_travel(self):
        h=Host(air=True);h.arm_air(1);h.control(down=6,pressed=6,x=1,tilt=1)
        self.assertAlmostEqual(h.move()[0][0],14.,places=5)
        # Circle release must neither shorten the action nor freeze its direction.
        for x,z,tilt,want in [(0,1,1,(0,14)),(-1,0,1,(-14,0)),(1,0,.5,(7,0)),(0,0,0,(0,0))]:
            h.control(down=0,pressed=0,x=x,z=z,tilt=tilt)
            out,_=h.move();self.assertAlmostEqual(out[0],want[0],places=5);self.assertAlmostEqual(out[2],want[1],places=5)
            self.assertAlmostEqual(out[1],-.75,places=5);self.assertEqual(h.body(10),h.dodge_body())
    def test_last_dodge_step_cannot_exceed_the_animation_duration(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,x=1,tilt=1)
        for _ in range(19):h.move(2.)
        out,_=h.move(2.);self.assertEqual(out,[14.,-.75,0.,14.])
        self.assertEqual(h.body(10),h.expected(10,1));self.assertEqual(h.move()[0],[1.,2.,3.,4.])
    def test_native_damage_and_knockback_records_pass_through_all_profiles_and_banks(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.frame()
            for profile in range(5):
                w32(h.actor+0x164,0);h.equip(True,profile);h.frame()
                for row in json.loads((ROOT/'fixtures/native_reactions.json').read_text()):
                    motion,data=h.native_reactions[row['normal_slot']];h.control(state=0,request=row['request'],height=0)
                    self.assertEqual(C.string_at(motion,len(data)),data)
                    handle=r32(h.actor+0x1d8)
                    address=r64(h.game+0x2ee3980+((handle&0x7fffffff)>>25)*8)+(handle&0x1ffffff)
                    table=C.string_at(address,1408)
                    self.assertEqual(table[row['request']*4:row['request']*4+4],h.request_original[row['request']*4:row['request']*4+4])
    def test_dodge_ceiling_contact_stops_lift_and_busy_action_returns_native_displacement(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,x=1,tilt=1)
        w32(h.actor+0x2d0,8);out,_=h.move();self.assertGreaterEqual(out[1],0)
        # KH1's post-collision callback may queue a fall or reaction. The mod
        # must stop replacing displacement as soon as the native action changes.
        w32(h.actor+0x164,0x4e);out,_=h.move();self.assertEqual(out,[1,2,3,4])
        self.assertEqual(h.body(10),h.expected(10,1))
    def test_off_disabled_foreign_and_invalid_timestep_never_replace_native_movement(self):
        for reason in ['off','disabled','script','land','nan','long_dt']:
            h=Host(air=True,air_dodge=reason!='disabled');h.arm_air();h.control(down=6,pressed=6)
            if reason=='off':h.equip(False);h.frame()
            elif reason=='script':w32(h.actor+0x440,1)
            elif reason=='land':w32(h.actor+0x70,0)
            out,_=h.move(float('nan') if reason=='nan' else 9 if reason=='long_dt' else 1)
            self.assertEqual(out,[1,2,3,4],reason)
    def test_third_hook_protection_failure_leaves_all_three_entries_intact(self):
        h=Host(air=True,fail_protect=4)
        before={r:C.string_at(h.game+r,n) for r,n in [(0x2a6220,17),(0x2b26c0,14),(0x2af6a0,16)]}
        h.frame()
        for r,data in before.items():self.assertEqual(C.string_at(h.game+r,len(data)),data)
    def test_blizzard_visual_starts_from_new_queue_and_restores_before_next_spell_or_profile(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.arm_air()
            for request,slot in [(0x37,55),(0x84,80)]:
                w32(h.actor+0x164,6);h.queue(0x01000000|request);before=C.string_at(h.actor+0x178,20)
                h.frame();self.assertEqual(h.body(slot),h.blizzard_body(slot))
                self.assertEqual(C.string_at(h.actor+0x178,20),before)
                h.queue(0x38 if request==0x37 else 0x85);h.frame()
                self.assertEqual(h.body(slot),h.expected(slot,1))
                w32(h.actor+0x178,0)
            w32(h.actor+0x164,0x37);h.frame();self.assertEqual(h.body(55),h.blizzard_body(55))
            h.equip(False);h.frame();self.assertEqual(h.body(55),h.expected(55,1))
            w32(h.actor+0x164,0);h.frame();h.assert_all(self,False)
    def test_blizzard_unknown_or_unloaded_motion_is_never_overwritten(self):
        for reason in ['foreign','unloaded']:
            h=Host(air=True);h.arm_air()
            if reason=='foreign':
                at=struct.unpack_from('<I',h.body(55),40)[0];C.c_ubyte.from_address(h.motions[55]+at+21).value^=1
            else:w32(h.actor+0x374,0)
            before=h.snapshot();w32(h.actor+0x164,0x37);h.frame();self.assertEqual(h.snapshot(),before)

    def test_air_control_hook_executes_relocated_cookie_trampoline_and_preserves_ground_input(self):
        h=Host(air=True);h.frame();before=h.snapshot()
        h.control(down=6,pressed=6,state=0,request=0,height=0)
        self.assertEqual(bridge.bridge_control_calls(),1)
        self.assertEqual([bridge.bridge_control_word(i) for i in range(4)],[6]*4)
        self.assertEqual(h.snapshot(),before)
        self.assertIn('AIR DODGE READY',bridge.bridge_log().decode())
    def test_neutral_air_circle_plays_504_masks_only_jump_and_initializes_a_lift(self):
        h=Host(air=True,control_mode=1);h.arm_air(1)
        put(h.actor+0x3b0,struct.pack('<3f',-4,2,3));velocity=C.string_at(h.actor+0x3b0,12);flags=C.string_at(h.actor,4)
        put(h.actor+0x16c,struct.pack('<f',18));h.control(down=6|0x80,pressed=6|0x100)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x16c),0)
        self.assertEqual([bridge.bridge_control_word(i)&6 for i in range(4)],[0]*4)
        self.assertEqual(r32(h.game+0x298ca94),6|0x80)
        self.assertEqual(r32(h.game+0x298ca98),6|0x100|0x40000000)
        self.assertEqual(C.string_at(h.actor,4),flags)
        before=C.string_at(h.actor+0x10,16);out,_=h.move();self.assertLess(out[1],0);self.assertEqual(out[0],0);self.assertEqual(out[2],0)
        self.assertEqual(C.string_at(h.actor+0x10,16),before)
        for slot in h.motions:
            if slot!=10:self.assertEqual(h.body(slot),h.expected(slot,2))
    def test_aerial_dodge_rising_start_enters_native_fall_callbacks_and_queues_504(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,state=1,request=5)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x164),6)
        self.assertEqual(r32(h.actor+0x70),2);self.assertEqual(r32(h.actor+0x178),0)
    def test_aerial_dodge_requires_release_after_held_takeoff_then_accepts_directional_circle(self):
        h=Host(air=True);h.frame();h.equip(True);h.frame()
        h.control(down=6,pressed=6,state=0,request=4,height=0)
        h.control(down=6,pressed=0,state=1,request=5)
        self.assertEqual(h.body(10),h.expected(10,1))
        h.control();h.control(down=6,pressed=6,tilt=.8,x=.8)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(bridge.bridge_control_word(0)&6,0)
    def test_airborne_circle_accepts_all_stick_directions_in_both_banks_without_rewriting_direction(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.frame();h.equip(True);h.frame()
            for x,z,tilt in [(0,0,0),(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(.7,.7,1),(-.7,-.7,1)]:
                h.control(state=0,request=0,height=0);h.control()
                h.control(down=6,pressed=6,x=x,z=z,tilt=tilt)
                self.assertEqual(h.body(10),h.dodge_body(),(bank,x,z))
                self.assertEqual(C.string_at(h.dir,16),struct.pack('<4f',x,0,z,tilt))
                self.assertEqual([bridge.bridge_control_word(i)&6 for i in range(4)],[0]*4)
                self.assertEqual(r32(h.game+0x298ca94)&6,6)
    def test_aerial_dodge_finishes_into_506_and_requires_a_landing_before_repeating(self):
        h=Host(air=True);h.arm_air(1);h.control(down=6,pressed=6)
        put(h.actor+0x16c,struct.pack('<f',39));h.frame();h.assert_all(self,2)
        h.control();h.control(down=6,pressed=6);h.assert_all(self,2)
        h.control(state=0,request=0,height=0);h.control();h.control(down=6,pressed=6)
        self.assertEqual(h.body(10),h.dodge_body())
    def test_air_dodge_restores_on_clock_loop_interruption_and_ability_off_in_both_banks(self):
        for bank in [98,60]:
            for reason in ['loop','attack','cast','land','off']:
                h=Host(slot=bank,air=True,encoded_fields=True);h.arm_air(4);h.control(down=6,pressed=6)
                self.assertEqual(h.body(10),h.dodge_body())
                put(h.actor+0x16c,struct.pack('<f',20));h.frame()
                if reason=='loop':put(h.actor+0x16c,struct.pack('<f',0))
                elif reason=='attack':w32(h.actor+0x164,0xcc)
                elif reason=='cast':w32(h.actor+0x164,0x85)
                elif reason=='land':w32(h.actor+0x70,0);put(h.actor+0x3d4,struct.pack('<f',0))
                else:h.equip(False,4)
                h.frame();self.assertEqual(h.body(10),h.expected(10,5))
                w32(h.actor+0x164,0);h.equip(False,4);h.frame();h.assert_all(self,False)
    def test_aerial_dodge_retains_each_selected_test_combo_and_native_travel(self):
        h=Host(air=True,encoded_fields=True);h.frame()
        for profile in range(5):
            h.equip(True,profile);w32(h.actor+0x164,0);h.frame()
            h.control(state=0,request=0,height=0);h.control();h.control(down=6,pressed=6)
            self.assertEqual(h.body(10),h.dodge_body())
            for slot in range(98,105):self.assertEqual(h.body(slot),h.expected(slot,profile+1))
            h.control(state=0,request=0,height=0);h.assert_all(self,profile+1)
    def test_air_dodge_excludes_unbound_other_actor_events_scripts_busy_commands_and_invalid_stick(self):
        for reason in ['off','other','event','menu','script','scriptflag','actionflag','cast','attack','reaction','shortcut','command','queued','queued_ledge','nan','negative_tilt','near_ground']:
            h=Host(air=True);h.arm_air();kwargs={}
            if reason=='off':h.equip(False);w32(h.actor+0x164,0);h.frame()
            elif reason=='other':kwargs['actor']=h.buffer(bytes(0x800))
            elif reason=='event':w32(h.game+0x298c9a0,1)
            elif reason=='menu':w32(h.game+0x2867364,0x2000)
            elif reason=='script':w32(h.actor+0x440,1)
            elif reason=='scriptflag':w32(h.actor+0x444,1)
            elif reason=='actionflag':w32(h.actor,4)
            elif reason=='cast':kwargs['request']=0x36
            elif reason=='attack':kwargs['request']=0xc8
            elif reason=='reaction':kwargs.update(state=4,request=0x4e)
            elif reason=='shortcut':kwargs['down']=6|0x40000
            elif reason=='command':w32(h.game+0x2d53a40,0x02000002)
            elif reason in ['queued','queued_ledge']:w32(h.actor+0x178,1);w32(h.actor+0x17c,0xc8 if reason=='queued' else 0xd)
            elif reason=='nan':kwargs['tilt']=float('nan')
            elif reason=='negative_tilt':kwargs['tilt']=-.1
            else:kwargs['height']=1
            before=h.body(10);h.control(pressed=6,**({'down':6}|kwargs))
            self.assertEqual(h.body(10),before,reason)
    def test_air_dodge_never_writes_foreign_fall_data_or_unloaded_actor(self):
        h=Host(air=True);h.arm_air();p=h.motions[10];offset=struct.unpack_from('<I',h.body(10),40)[0]
        C.c_ubyte.from_address(p+offset+21).value^=1;before=h.body(10)
        h.control(down=6,pressed=6);self.assertEqual(h.body(10),before)
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6);before=h.snapshot()
        w32(h.actor+0x374,0);h.frame();self.assertEqual(h.snapshot(),before)
    def test_unequipped_air_dodge_does_not_retrigger_while_body_restore_waits_for_idle(self):
        h=Host(air=True);h.arm_air();h.equip(False);h.frame()
        self.assertEqual(h.body(10),h.expected(10,1))
        h.control(down=6,pressed=6);self.assertEqual(h.body(10),h.expected(10,1))
        self.assertEqual(bridge.bridge_control_word(0)&6,6)
    def test_air_hook_admission_and_failure_paths_leave_original_control_bytes(self):
        for reason in ['control','glide','move','state','can','queue','alloc','protect','remove']:
            h=Host(air=True,fail_alloc=reason=='alloc',fail_protect=reason=='protect',air_dodge=reason!='disabled',remove=reason=='remove')
            if reason in ['control','glide','move','state','can','queue']:
                address=h.game+{'control':0x2a6220,'glide':0x2b2d30,'move':0x2af6a0,'state':0x2b1960,'can':0x297870,'queue':0x29f980}[reason]
                C.c_ubyte.from_address(address).value^=1
            before=C.string_at(h.game+0x2a6220,17);h.frame()
            self.assertEqual(C.string_at(h.game+0x2a6220,17),before,reason)
    def test_second_movement_hook_protection_failure_leaves_both_original_entries(self):
        h=Host(air=True,fail_protect=3)
        control=C.string_at(h.game+0x2a6220,17);glide=C.string_at(h.game+0x2b26c0,14)
        h.frame();self.assertEqual(C.string_at(h.game+0x2a6220,17),control)
        self.assertEqual(C.string_at(h.game+0x2b26c0,14),glide)
    def test_falling_dodge_always_queues_a_restart_and_waits_for_a_delayed_native_commit(self):
        h=Host(air=True,control_mode=3);h.arm_air();h.clock(38)
        h.control(down=6,pressed=6)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(bridge.bridge_queue_calls(),1)
        self.assertEqual(r32(h.actor+0x178),1);self.assertEqual(C.c_float.from_address(h.actor+0x16c).value,38)
        for _ in range(3):h.frame();self.assertEqual(h.body(10),h.dodge_body())
        bridge.bridge_commit(h.actor);h.frame()
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x16c),0)
        self.assertIn('restart committed',bridge.bridge_log().decode())
    def test_jump_flags_and_fresh_press_without_held_bit_do_not_block_dodge(self):
        h=Host(air=True);h.arm_air();w32(h.game+0x2d53a40,0x03000000)
        h.control(down=0,pressed=6)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(bridge.bridge_queue_calls(),1)
        self.assertIn('mask (0 means accepted)=0x0',bridge.bridge_log().decode())
    def test_logged_high_jump_press_03000000_runs_dodge_instead_of_glide_in_all_profiles_and_banks(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True,control_mode=4);h.frame()
            for profile in range(5):
                w32(h.actor+0x164,0);h.equip(True,profile);h.frame()
                h.control(state=0,request=0,height=0);h.control()
                h.queue(0xa);h.clock(12);w32(h.game+0x2d53a40,0x03000000)
                h.control(down=6,pressed=6,state=2,request=0xa)
                self.assertEqual(h.body(10),h.dodge_body(),(bank,profile))
                self.assertEqual(r32(h.actor+0x70),2);self.assertEqual(r32(h.actor+0x164),6)
                self.assertEqual([bridge.bridge_control_word(i)&6 for i in range(4)],[0]*4)
                self.assertIn('mask (0 means accepted)=0x0',bridge.bridge_log().decode())
                h.clock(39);h.frame();h.assert_all(self,profile+1)
    def test_deferred_glide_constructor_cannot_replace_a_live_504_after_control_returns(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True,control_mode=5);h.arm_air()
            w32(h.game+0x2d5ec10,0x80);w32(h.game+0x2d53a40,0x03000000)
            h.control(down=6,pressed=6,state=2,request=0xa)
            self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x70),2)
            self.assertEqual(bridge.bridge_native_glide_calls(),0)
            h.clock(18);h.control(state=2,request=6,down=6)
            self.assertEqual(r32(h.actor+0x70),2);self.assertEqual(h.body(10),h.dodge_body())
            self.assertIn('AQUA MAIN GLIDE REPLACED',bridge.bridge_log().decode())
            h.clock(39);h.frame();h.native_glide()
            self.assertEqual(bridge.bridge_native_glide_calls(),0);self.assertEqual(r32(h.actor+0x70),2)
    def test_native_glide_constructor_and_relocated_call_pass_through_when_dodge_is_off(self):
        for enabled in [False,True]:
            h=Host(air=True,air_dodge=int(enabled));h.arm_air(1 if enabled else 0);h.native_glide()
            self.assertEqual(bridge.bridge_native_glide_calls(),1);self.assertEqual(r32(h.actor+0x164),0x71)
            self.assertEqual(r32(h.glide_work+0x104)&1,0)
    def test_native_keyblade_tip_point_and_effect_matrix_are_used_for_every_spell_and_profile(self):
        for bank in [98,60]:
            h=Host(slot=bank,magic=True,hand_magic=1);h.frame()
            before_matrix=C.string_at(h.game+0x29ea00,15);before_point=C.string_at(h.game+0x29eb20,16)
            for profile in range(5):
                w32(h.actor+0x164,0);h.equip(True,profile);h.frame()
                for action in list(range(0x36,0x3e))+list(range(0x83,0x8b)):
                    w32(h.actor+0x164,action)
                    self.assertEqual(h.point(fraction=.25),[100,200,300,1])
                    self.assertEqual(h.matrix()[12:],[100,200,300,1])
                    self.assertEqual(bridge.bridge_matrix_code(),0x30);self.assertEqual(bridge.bridge_point_code(),0x30)
                    self.assertEqual(bridge.bridge_point_fraction(),.25)
            self.assertEqual(C.string_at(h.game+0x29ea00,15),before_matrix)
            self.assertEqual(C.string_at(h.game+0x29eb20,16),before_point)
    def test_ground_hits_and_usable_chain_windows_use_the_actual_native_event_sampler(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame();h.equip(True);h.frame()
            for slot,contact,start,end in [(98,12.,22.,40.),(99,30.*8/37.,30.,48.),(100,42.*8/37.,42.,64.)]:
                self.assertNotEqual((h.event(slot,4,contact-.5) or 0)&0xffff0000,0x160000)
                self.assertEqual(h.event(slot,4,contact)&0xffff0000,0x160000)
                self.assertNotEqual(h.event(slot,5,start-.5),1)
                self.assertEqual(h.event(slot,5,start),1)
                self.assertEqual(h.event(slot,5,end-.5),1)
                self.assertEqual(h.event(slot,5,end),0)
                for step in [.5,1.,2.]:
                    # Native event sampler still offers multiple follow-up checks
                    # when the timestep skips the old v15 one-frame window.
                    self.assertGreaterEqual(sum(h.event(slot,5,f)==1 for f in __import__('numpy').arange(start+.25,end,step)),8)
            h.equip(False);h.frame();h.assert_all(self,False)

    def test_foreign_event_descriptor_or_payload_blocks_every_initial_body_write(self):
        for change in ['descriptor','payload']:
            h=Host(encoded_fields=True);h.frame();h.equip(True)
            original=(ROOT/'fixtures/original_s099.bin').read_bytes();at=struct.unpack_from('<I',original,60)[0]
            if change=='descriptor':w32(h.motions[99]+at+4,99)
            else:
                keys=struct.unpack_from('<I',original,at+8)[0]
                C.c_ubyte.from_address(h.motions[99]+keys+5).value^=1
            before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_blizzard_keeps_original_lookup_events_and_queue_with_only_the_fire_body_changed(self):
        for bank in [98,60]:
            h=Host(slot=bank,air=True,encoded_fields=True);h.arm_air()
            table=h.decode(r32(h.actor+0x1d8))
            self.assertEqual([r32(table+q*4)&0xfff for q in [0x37,0x84]],[55,80] if bank==98 else [18,42])
            for spell,slot,terminal in [(0x37,55,0x40000000),(0x84,80,0x40000075)]:
                w32(h.actor+0x164,spell);h.queue(terminal);queue=C.string_at(h.actor+0x178,36)
                h.frame()
                self.assertEqual(C.string_at(h.actor+0x178,36),queue)
                self.assertEqual(h.body(slot),h.blizzard_body(slot))
                raw=h.runtime_originals[slot];at=struct.unpack_from('<I',raw,60)[0]
                self.assertEqual(h.body(slot)[at:],raw[at:])
                h.frame();self.assertEqual(C.string_at(h.actor+0x178,36),queue)
                w32(h.actor+0x164,0x38 if spell==0x37 else 0x85);w32(h.actor+0x178,0);h.frame()
                self.assertEqual(h.body(slot),h.expected(slot,1))
            w32(h.actor+0x164,0);h.equip(True,1);h.frame()
            w32(h.actor+0x164,0x37);h.frame();self.assertEqual(h.body(55),h.expected(55,2))

    def test_actual_nonzero_native_command_dispatch_remains_excluded(self):
        for command in [1,2,0x02000002]:
            h=Host(air=True);h.arm_air();w32(h.game+0x2d53a40,command)
            h.control(down=6,pressed=6,request=0xa)
            self.assertEqual(h.body(10),h.expected(10,1),hex(command))
            self.assertEqual(bridge.bridge_queue_calls(),0)
            self.assertIn('mask (0 means accepted)=0x100',bridge.bridge_log().decode())
    def test_log_shaped_jump_press_is_retained_until_delayed_native_restart_commits(self):
        h=Host(air=True,control_mode=3);h.arm_air();h.queue(0xa)
        w32(h.game+0x2d53a40,0x03000000);h.clock(23)
        h.control(down=6,pressed=6,state=2,request=0xa)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x17c),6)
        for _ in range(3):h.frame();self.assertEqual(h.body(10),h.dodge_body())
        bridge.bridge_commit(h.actor);h.frame();self.assertEqual(h.body(10),h.dodge_body())
    def test_uncommitted_dodge_times_out_and_restores_fall_instead_of_staying_active(self):
        h=Host(air=True,control_mode=3);h.arm_air();h.control(down=6,pressed=6)
        for _ in range(20):h.frame()
        self.assertEqual(h.body(10),h.expected(10,1))
    def test_native_input_callback_and_blocked_press_are_reported_for_diagnosis(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,request=0xc8)
        log=bridge.bridge_log().decode()
        self.assertIn('CONTROL OBSERVED',log);self.assertIn('rejection mask',log)
        self.assertIn('native request=0xC8',log);self.assertIn('pressed=0x6',log)
    def test_disabling_aerial_dodge_keeps_native_circle_input_and_default_glide(self):
        h=Host(air=True,air_dodge=0);h.arm_air();h.control(down=6,pressed=6)
        self.assertEqual(h.body(10),h.expected(10,1));self.assertEqual(bridge.bridge_control_word(0)&6,6)
        h.clock(55);h.control(state=21,request=0x71,down=4)
        self.assertEqual(C.c_float.from_address(h.actor+0x16c).value,55)
        for slot,p in h.native_glide_motions.items():self.assertEqual(C.string_at(p,len(h.native_glide_originals[slot])),h.native_glide_originals[slot])

    def test_ground_and_air_fire_thunder_cure_resolve_to_requested_distinct_records(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in range(5):
                h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
                p=h.decode(r32(h.actor+0x1d8))
                targets=[54,55,56,79,80,81] if bank==98 else [17,18,19,41,42,43]
                self.assertEqual([r32(p+q*4)&0xfff for q in [0x36,0x38,0x39,0x83,0x85,0x86]],targets)
                self.assertEqual([i//4 for i in range(0,len(h.request_original),4)
                                  if C.string_at(p+i,4)!=h.request_original[i:i+4]],
                                  [0x38,0x3b,0x3c,0x85,0x88,0x89] if profile==0 else [0x38,0x85])
            h.equip(False,4);h.frame();h.assert_all(self,False)
    def test_main_stop_and_aero_resolve_to_gravity_while_numbered_profiles_keep_v13_routes(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in [0,1,2,3,4,0]:
                h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
                p=h.decode(r32(h.actor+0x1d8))
                g,a=(55,80) if bank==98 else (18,42)
                for gravity,stop,aero,wanted in [(0x3a,0x3b,0x3c,g),(0x87,0x88,0x89,a)]:
                    target=r32(p+gravity*4)&0xfff;self.assertEqual(target,wanted)
                    for q in [stop,aero]:
                        self.assertEqual(r32(p+q*4)&0xfff,wanted if profile==0 else wanted+1)
    def test_main_to_numbered_spell_changes_wait_until_idle_and_restore_both_lookup_and_pose(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame();h.equip(True);h.frame()
            before=h.snapshot();pointer=r32(h.actor+0x1d8)
            w32(h.actor+0x164,0x39);h.equip(True,1);h.frame()
            self.assertEqual(h.snapshot(),before);self.assertEqual(r32(h.actor+0x1d8),pointer)
            w32(h.actor+0x164,0);h.frame();h.assert_all(self,2)
            self.assertNotEqual(r32(h.actor+0x1d8),pointer)
            h.equip(True);h.frame();h.assert_all(self,1)
            self.assertEqual(r32(h.actor+0x1d8),pointer)
    def test_unknown_request_descriptor_blocks_all_body_writes_and_lookup_changes(self):
        h=Host();h.frame();h.equip(True)
        w32(h.requests+0x38*4,0x1001);before=h.snapshot();pointer=r32(h.actor+0x1d8)
        h.frame();self.assertEqual(h.snapshot(),before);self.assertEqual(r32(h.actor+0x1d8),pointer)
        self.assertIn('cast request table must verify',bridge.bridge_log().decode())
    def test_foreign_request_pointer_is_retained_and_native_reload_is_readmitted(self):
        h=Host();h.frame();h.equip(True);h.frame()
        foreign=h.buffer(bytes(1408));pointer=bridge.bridge_encode(foreign)
        w32(h.actor+0x1d8,pointer);h.equip(False);before=h.snapshot();h.frame()
        self.assertEqual(h.snapshot(),before);self.assertEqual(r32(h.actor+0x1d8),pointer)
        w32(h.actor+0x1d8,h.original_request_handle);[h.frame() for _ in range(8)];h.assert_all(self,False)
    def test_request_restore_waits_for_cast_completion_and_rejects_changed_original(self):
        h=Host();h.frame();h.equip(True);h.frame();pointer=r32(h.actor+0x1d8)
        w32(h.actor+0x164,0x38);h.equip(False);h.frame();self.assertEqual(r32(h.actor+0x1d8),pointer)
        w32(h.actor+0x164,0);w32(h.requests+0x39*4,0x1002);before=h.snapshot();h.frame()
        self.assertEqual(h.snapshot(),before);self.assertEqual(r32(h.actor+0x1d8),pointer)
        put(h.requests,h.request_original);[h.frame() for _ in range(8)];h.assert_all(self,False)
    def test_all_five_lowercase_names_are_registered_with_zero_ap(self):
        h=Host();h.frame();table=r64(h.game+0x2d36d48)
        expected=[b'\x45\x55\x59\x45\0']+[b'\x45\x55\x59\x45\x01'+bytes([0x21+i])+b'\0' for i in range(1,5)]
        for i,name in enumerate(expected):
            row=table+(116+i)*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
            self.assertEqual(C.string_at(h.decode(r32(row+4)),len(name)),name)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
    def test_exact_profiles_cycle_in_both_banks_and_only_selected_aqua_entry_stays_enabled(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in [0,1,2,3,4,2,0]:
                h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
                own=[v for v in h.abilities() if 117<=(v&127)<=121]
                self.assertEqual(len(own),5);self.assertEqual([v for v in own if not v&128],[117+profile])
                self.assertEqual(h.abilities()[:2],b'\x81\x82')
            h.equip(False,0);h.frame();h.assert_all(self,False)
    def test_switch_between_test_sets_defers_all_motion_writes_until_idle(self):
        h=Host();h.frame();h.equip(True,1);h.frame();h.assert_all(self,2)
        w32(h.actor+0x164,0xc8);h.equip(True,4);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,5)
        w32(h.actor+0x164,0xcc);h.equip(False,4);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,False)
    def test_saved_fourth_test_selection_is_respected_and_missing_entries_granted_off(self):
        h=Host();put(h.save+0x44,b'\x81\x79\x82\0');h.frame();h.assert_all(self,5)
        own=[v for v in h.abilities() if 117<=(v&127)<=121]
        self.assertEqual(sorted(own),sorted([121,245,246,247,248]));self.assertEqual(h.abilities()[:3],b'\x81\x79\x82')
    def test_insufficient_tail_space_never_evicts_native_abilities(self):
        h=Host();saved=bytes([117]+list(range(1,45))+[0,0,0]);put(h.save+0x44,saved);h.frame()
        self.assertEqual(h.abilities(),saved);h.assert_all(self,True)
        self.assertIn('AQUA ABILITY SLOTS FULL',bridge.bridge_log().decode())
    def test_uninstall_removes_all_five_own_ids_and_restores_fourth_test_payload(self):
        h=Host(remove=1);put(h.save+0x44,b'\x81\x75\xf6\x77\xf8\x79\x82\0')
        for r in h.records:put(h.motions[r['normal_slot']],h.expected(r['normal_slot'],5))
        h.frame();self.assertEqual(h.abilities()[:8],b'\x81\x82\0\0\0\0\0\0');h.assert_all(self,False)

    def test_actual_pe_registers_lowercase_zero_ap_aqua_unequipped_and_preserves_native_table(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:7],b'\x81\x82\xf5\xf6\xf7\xf8\xf9');self.assertEqual(h.abilities()[7:],before[7:])
        row=table+116*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
        self.assertEqual(C.string_at(h.decode(r32(row+4)),5),b'\x45\x55\x59\x45\x00');h.assert_all(self,False)
    def test_normal_all_37_exact_on_and_off_including_idle_and_normal_only_ledge_recovery(self):
        h=Host();self.assertEqual(len(h.records),37);h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        self.assertIn('AQUA BANK: normal Sora',bridge.bridge_log().decode())
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_olympus_36_exact_on_and_off_with_encoded_pointers_and_common_idle_prefix(self):
        h=Host(slot=60,encoded_fields=True);self.assertEqual(len(h.records),36);h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        self.assertIn('AQUA BANK: Olympus',bridge.bridge_log().decode())
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_frame_checks_share_memory_ranges_instead_of_querying_every_table(self):
        h=Host(encoded_fields=True);h.frame();h.equip(True);h.frame();before=bridge.bridge_queries()
        for _ in range(20):h.frame()
        calls=bridge.bridge_queries()-before;self.assertLessEqual(calls,6*20);h.assert_all(self,True)
    def test_full_list_never_evicts_any_native_ability_or_patches_bodies(self):
        h=Host();put(h.save+0x44,bytes(range(1,49)));before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False)
    def test_foreign_change_in_last_record_blocks_every_other_write(self):
        h=Host();h.frame();h.equip(True);p=h.motions[117];w32(p+r32(p+40)+4,0x7f123456);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
        log=bridge.bridge_log().decode();self.assertIn('AQUA rejected request=0xDC',log);self.assertIn('AQUA admission stage=0x38',log)
    def test_changed_early_locomotion_schema_blocks_later_attack_writes(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[4]+44,70);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_changed_late_attack_schema_blocks_earlier_idle_and_locomotion_writes(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[104]+44,70);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_switch_waits_for_attacks_casts_jumping_and_walking_to_finish(self):
        h=Host();h.frame();h.equip(True)
        for action in [1,2,4,5,6,0x36,0x3e,0x48,0x83,0xc8,0xc9,0xcc,0xd4,0xdc]:
            w32(h.actor+0x164,action);h.frame();h.assert_all(self,False)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,True)
    def test_unequip_during_guard_waits_until_idle_then_restores_every_record(self):
        h=Host();h.frame();h.equip(True);h.frame();h.equip(False);w32(h.actor+0x164,0xd4);h.frame();h.assert_all(self,True)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,False)
    def test_uninstall_removes_only_aqua_and_restores_all_converted_data(self):
        h=Host(remove=1);put(h.save+0x44,b'\x81\x75\x82\x00')
        for r in h.records:put(h.motions[r['normal_slot']],h.expected(r['normal_slot'],True))
        h.frame();self.assertEqual(h.abilities()[:4],b'\x81\x82\x00\x00');h.assert_all(self,False)
    def test_unknown_game_build_writes_no_abilities_table_or_animations(self):
        h=Host(stamp=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False);self.assertEqual(r64(h.game+0x2d36d48),h.original_table)
    def test_legacy_styles_dll_suspends_controller_without_mutations(self):
        h=Host(conflict=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False)
    def test_single_reloaded_motion_at_same_address_is_readmitted(self):
        h=Host();h.frame();h.equip(True);h.frame();put(h.motions[103],h.runtime_originals[103]);h.frame();h.assert_all(self,True)
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_bank_switch_with_identical_idle_prefix_uses_c8_and_restores_on_reentry(self):
        h=Host();h.frame();h.equip(True);h.frame();old=(h.records,h.record_by_slot,h.motions,h.runtime_originals,h.array,h.slot,h.requests,h.request_original,h.original_request_handle);old_bytes=h.snapshot();old_request=r32(h.actor+0x1d8)
        h.activate_bank(True,True);h.frame();h.assert_all(self,True);h.equip(False);h.frame();h.assert_all(self,False)
        for slot,data in old_bytes.items():self.assertEqual(C.string_at(old[2][slot],len(data)),data)
        h.records,h.record_by_slot,h.motions,h.runtime_originals,h.array,h.slot,h.requests,h.request_original,h.original_request_handle=old
        # Native bank backups restore both pointers, possibly retaining the
        # earlier actor-local Aqua request table. That route must be restorable.
        w32(h.actor+0x1d4,bridge.bridge_encode(h.array));w32(h.actor+0x1d8,old_request)
        h.frame();h.assert_all(self,False)
    def test_invalid_table_pointer_cannot_patch_any_other_valid_record(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[79]+40,0);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_saved_equipped_aqua_is_respected_without_duplicate_grant(self):
        h=Host();put(h.save+0x44,b'\x81\x75\x82\x00');h.frame();self.assertEqual(h.abilities()[:7],b'\x81\x75\x82\xf6\xf7\xf8\xf9');h.assert_all(self,True)
    def test_no_stale_writes_after_actor_unload(self):
        h=Host();h.frame();h.equip(True);h.frame();w64(h.game+0x2537e48,0);h.equip(False);h.frame();h.assert_all(self,True)
        w64(h.game+0x2537e48,h.actor);h.frame();h.assert_all(self,False)
    def test_unmapped_slapshot_record_is_not_replaced(self):
        h=Host();h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        self.assertEqual(C.string_at(h.unmapped,len(h.unmapped_original)),h.unmapped_original)
        h.equip(False);h.frame();self.assertEqual(C.string_at(h.unmapped,len(h.unmapped_original)),h.unmapped_original)
    def test_noncontiguous_native_table_pointers_remain_supported(self):
        h=Host();h.frame();slot=1;p=h.motions[slot];original=h.runtime_originals[slot]
        offset=struct.unpack_from('<I',original,56)[0];size=r32(p+52)*8
        remote=h.buffer(original[offset:offset+size]);w32(p+56,bridge.bridge_encode(remote))
        h.runtime_originals[slot]=C.string_at(p,len(original));h.equip(True);h.frame()
        expected=bytearray(h.expected(slot,True));expected[offset:offset+size]=original[offset:offset+size]
        self.assertEqual(h.body(slot),bytes(expected))
        after=(ROOT/f"fixtures/aqua_{h.record_by_slot[slot]['fixture_stem']}.bin").read_bytes()
        self.assertEqual(C.string_at(remote,size),after[offset:offset+size])
        h.frame();h.equip(False);h.frame();h.assert_all(self,False)
        self.assertEqual(C.string_at(remote,size),original[offset:offset+size])
    def test_cached_scalar_corruption_is_rejected_before_toggle_writes(self):
        h=Host();h.frame();h.equip(True);h.frame();w32(h.motions[0]+24,999);h.equip(False);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_foreign_nonsentinel_key_change_is_rejected_when_restoring(self):
        h=Host();h.frame();h.equip(True);h.frame();p=h.motions[104];offset=struct.unpack_from('<I',h.runtime_originals[104],40)[0]
        w32(p+offset+80,0x7f123456);h.equip(False);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)

    def guard_setup(self,bank=98):
        h=Host(slot=bank,guard=True);h.frame();h.equip(True);h.frame()
        bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d)
        native=h.game+0x2db4710;data=h.buffer(bytes(0x70))
        w32(native,0x80800);w32(native+0x34,bridge.bridge_encode(h.actor));w32(native+0x5c,bridge.bridge_encode(data))
        w32(native+0x54,1);w32(h.game+0x2db7710,1)
        put(h.actor+0x10,struct.pack('<3f',100.,200.,300.))
        self.assertEqual(bridge.bridge_guard_pool(h.game+0x2b47a0),19)
        return h,native,native+0xc0,data
    def test_other_native_row_callbacks_do_not_forget_the_witnessed_guard(self):
        h,native,p,data=self.guard_setup();bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x12)
        w32(h.actor+0x164,0x6e);h.clock(0.);bridge.bridge_guard_pool(h.game+0x2b47a0)
        self.assertTrue(r32(p)&0x800)
        h.queue(0xc8);bridge.bridge_guard_pool(h.game+0x2b47a0);self.assertFalse(r32(p)&0x800)
    def test_numbered_dodge_keeps_v19_superglide_passthrough(self):
        h=Host(air=True);h.arm_air(1);h.control(down=6,pressed=6,x=1,tilt=1)
        bridge.bridge_glide(h.game+0x2b2750,h.actor);self.assertEqual(bridge.bridge_native_glide_calls(),1)
    def test_wider_guard_creates_one_native_body_capsule_covering_front_sides_and_rear(self):
        for bank in [98,60]:
            h,native,p,data=self.guard_setup(bank)
            self.assertEqual(r32(p)&0xe0000,0x80000);self.assertEqual(r32(p+0x2c),0)
            self.assertEqual(r32(p+0x68),100);self.assertEqual(h.decode(r32(p+0x34)),h.actor)
            self.assertNotEqual(h.decode(r32(p+0x5c)),data)
            self.assertEqual(struct.unpack('<f',C.string_at(data+0x64,4))[0],0.)
            self.assertLess(struct.unpack('<f',C.string_at(h.decode(r32(p+0x5c))+0x64,4))[0],-1.)
            a=list(struct.unpack('<4f',C.string_at(p+0x10,16)));b=list(struct.unpack('<4f',C.string_at(p+0x40,16)))
            self.assertEqual(a,[100.,165.,300.,1.]);self.assertEqual(b,[100.,115.,300.,1.])
            self.assertEqual(struct.unpack('<f',C.string_at(p+0xc,4))[0],50.)
            # Capsule geometry reaches equally to the front, rear and either side.
            for dx,dz in [(0,45),(0,-45),(45,0),(-45,0)]:self.assertLessEqual(dx*dx+dz*dz,50.*50.)
            for _ in range(20):bridge.bridge_guard_pool(h.game+0x2b47a0)
            self.assertEqual(sum(bool(r32(native+i*0xc0)&0x800) for i in range(64)),2)
    def test_guard_shield_follows_body_and_rearms_without_new_allocations(self):
        h,native,p,data=self.guard_setup();put(h.actor+0x10,struct.pack('<3f',-50.,100.,-80.))
        w32(p,r32(p)&~0x200);bridge.bridge_guard_pool(h.game+0x2b47a0)
        self.assertEqual(struct.unpack('<4f',C.string_at(p+0x10,16)),(-50.,65.,-80.,1.))
        self.assertEqual(C.string_at(p+0x10,16),C.string_at(p+0x70,16));self.assertTrue(r32(p)&0x200)
    def test_native_parry_6e_and_6f_keep_only_twelve_ticks_of_extra_guard(self):
        for request in [0x6e,0x6f]:
            h,native,p,data=self.guard_setup();w32(h.actor+0x164,request);h.clock(0.)
            for _ in range(11):
                bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
                bridge.bridge_guard_pool(h.game+0x2b47a0);self.assertTrue(r32(p)&0x800)
            bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.);bridge.bridge_guard_pool(h.game+0x2b47a0)
            self.assertFalse(r32(p)&0x800);self.assertTrue(r32(native)&0x800)
    def test_guard_release_grace_is_small_and_cannot_survive_new_actions(self):
        for request in [0,1,2,0x48,0x4c,0xc8,0xcc,0x36]:
            h,native,p,data=self.guard_setup()
            for _ in range(155):bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
            h.frame();w32(h.actor+0x164,request);h.clock(0.)
            bridge.bridge_guard_pool(h.game+0x2b47a0)
            if request==0:
                self.assertTrue(r32(p)&0x800)
                for _ in range(13):bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
                bridge.bridge_guard_pool(h.game+0x2b47a0)
            self.assertFalse(r32(p)&0x800);self.assertTrue(r32(native)&0x800)
    def test_guard_retirement_cannot_free_a_recycled_or_foreign_pool_object(self):
        for changed in ['owner','data','mask']:
            h,native,p,data=self.guard_setup();field={'owner':0x34,'data':0x5c,'mask':0x54}[changed]
            w32(p+field,0x12345678);before=C.string_at(p,0xc0)
            w32(h.actor+0x164,0x48);h.frame();self.assertEqual(C.string_at(p,0xc0),before)
    def test_guard_does_not_allocate_without_a_witness_template_or_free_native_slot(self):
        for reason in ['witness','template','full','mask']:
            h,native,p,data=self.guard_setup();w32(h.actor+0x164,0x48);h.frame()
            if reason!='witness':bridge.bridge_guard_row(h.game+0x2a3980,h.actor,0x3d)
            if reason=='template':w32(native+0x34,bridge.bridge_encode(h.buffer(bytes(0x800))))
            if reason=='full':
                for i in range(1,64):w32(native+i*0xc0,0x800)
            if reason=='mask':w32(h.game+0x2db7710,0x7fffffff)
            before=C.string_at(native,0x3000);bridge.bridge_guard_pool(h.game+0x2b47a0)
            self.assertEqual(C.string_at(native,0x3000),before)
    def test_unrelated_collision_pairs_do_not_query_or_validate_soras_guard(self):
        h,native,p,data=self.guard_setup();other=h.game+0x2db4710+10*0xc0
        w32(other,0x80800);w32(other+0x34,bridge.bridge_encode(h.buffer(bytes(0x800))))
        enemy=h.buffer(bytes(0xc0));q=bridge.bridge_queries()
        for _ in range(1000):bridge.bridge_guard_angle(h.game+0x2b4640,other,enemy)
        self.assertEqual(bridge.bridge_queries()-q,0)
    def test_all_guard_hooks_fail_atomically_when_pool_or_allocator_anchor_is_changed(self):
        for anchor in [0x2b47a0,0x2b3270,0x2b3560,0x2b3760]:
            h=Host(guard=True);C.c_ubyte.from_address(h.game+anchor).value^=1
            before={r:C.string_at(h.game+r,15) for r in [0x2a3980,0x29f0a0,0x2b4640,0x2b47a0]}
            h.frame()
            for r,b in before.items():self.assertEqual(C.string_at(h.game+r,15),b)
        h=Host(guard=True,fail_protect=5);before={r:C.string_at(h.game+r,15) for r in [0x2a3980,0x29f0a0,0x2b4640,0x2b47a0]};h.frame()
        for r,b in before.items():self.assertEqual(C.string_at(h.game+r,15),b)
    def test_moving_main_binding_recovers_after_temporary_residency_or_save_loss(self):
        for bank in [98,60]:
            for reason in ['resident','save']:
                h=Host(slot=bank,air=True);h.arm_air();w32(h.actor+0x164,2);w32(h.actor+0x70,0)
                if reason=='resident':w32(h.actor+0x374,0)
                else:put(h.save+4,b'\0')
                before=h.snapshot();h.frame()
                if reason=='resident':w32(h.actor+0x374,1)
                else:put(h.save+4,b'\x64')
                h.frame();self.assertEqual(h.snapshot(),before)
                self.assertIn('BINDING RECOVERED',bridge.bridge_log().decode());self.assertNotIn('SWITCH PENDING',bridge.bridge_log().decode())
                h.control(state=2,request=6);h.control(down=6,pressed=6,state=2,request=6,tilt=1,x=-1)
                self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(h.move()[0][0],-14.)
    def test_in_progress_504_keeps_locked_motion_through_read_only_binding_recovery(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,x=1,tilt=1);h.clock(10.);h.move()
        w32(h.actor+0x374,0);h.frame();w32(h.actor+0x374,1);h.frame()
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(h.move()[0][:3],[14.,-.75,0.])
        h.clock(39.);h.frame();self.assertEqual(h.body(10),h.expected(10,1))
    def test_main_shared_constructor_blocks_both_glides_even_when_binding_is_unavailable(self):
        for reason in ['normal','resident','corrupt']:
            h=Host(air=True);h.arm_air()
            if reason=='resident':w32(h.actor+0x374,0);h.frame();w32(h.actor+0x374,1)
            elif reason=='corrupt':w32(h.motions[104]+24,999);h.frame()
            for entry in [0x2b26c0,0x2b2750]:bridge.bridge_glide(h.game+entry,h.actor)
            self.assertEqual(bridge.bridge_native_glide_calls(),0)
    def test_numbered_off_and_disabled_shared_glide_paths_pass_both_native_constructors(self):
        for profile,enabled in [(0,0),(1,1),(2,1),(3,1),(4,1)]:
            h=Host(air=True,air_dodge=enabled);h.arm_air(profile)
            for entry in [0x2b26c0,0x2b2750]:bridge.bridge_glide(h.game+entry,h.actor)
            self.assertEqual(bridge.bridge_native_glide_calls(),2)
        h=Host(air=True);h.frame()
        for entry in [0x2b26c0,0x2b2750]:bridge.bridge_glide(h.game+entry,h.actor)
        self.assertEqual(bridge.bridge_native_glide_calls(),2)
    def test_invalid_bank_admission_is_bounded_and_main_does_not_fall_back_to_glide(self):
        h=Host(air=True);h.arm_air();w32(h.motions[104]+24,999);w32(h.actor+0x164,2)
        before=h.snapshot();q=bridge.bridge_queries()
        for _ in range(120):h.frame()
        self.assertEqual(h.snapshot(),before);self.assertLess(bridge.bridge_queries()-q,12000)
        self.assertLess(bridge.bridge_log().decode().count('AQUA WAITING:'),3)
        for entry in [0x2b26c0,0x2b2750]:bridge.bridge_glide(h.game+entry,h.actor)
        self.assertEqual(bridge.bridge_native_glide_calls(),0)
    def test_air_combo_keeps_a_usable_followup_window_to_end_of_each_nonfinisher(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame();h.equip(True);h.frame()
            for slot,start,end in [(102,18.,40.),(103,24.,42.)]:
                self.assertEqual(h.event(slot,5,start),1);self.assertEqual(h.event(slot,5,end-.1),1)
                self.assertEqual(h.event(slot,5,end),0)
                for dt in [.5,1.,2.,4.]:self.assertGreaterEqual(sum(h.event(slot,5,f)==1 for f in __import__('numpy').arange(start+.1,end,dt)),4)
            self.assertEqual([h.record_by_slot[x]['donor'] for x in [102,103,104]],['305','353','407'])
    def test_both_second_ground_variants_have_identical_real_contact_and_chain_timing(self):
        h=Host(guard=True,encoded_fields=True);h.frame();h.equip(True);h.frame()
        hits=[];chains=[]
        for request,slot,finish in [(0xc9,99,30.),(0xca,100,42.)]:
            w32(h.actor+0x164,request);h.clock(0.);bridge.bridge_motion_advance(h.game+0x29f0a0,h.actor,1.)
            rate=bridge.bridge_motion_delta();hits.append((finish*8./37.)/rate);chains.append(finish/rate)
        self.assertAlmostEqual(hits[0],hits[1],places=5);self.assertAlmostEqual(chains[0],chains[1],places=5)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
