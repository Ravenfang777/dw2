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
for name,args,ret in [('bridge_air_modes',[C.c_int,C.c_uint],None),('bridge_control',[C.c_size_t,C.c_size_t,C.c_size_t],None),('bridge_control_calls',[],C.c_uint),('bridge_control_word',[C.c_uint],C.c_uint)]:
    f=getattr(bridge,name);f.argtypes=args;f.restype=ret
libc=C.CDLL(None);libc.mmap.argtypes=[C.c_void_p,C.c_size_t,C.c_int,C.c_int,C.c_int,C.c_long];libc.mmap.restype=C.c_void_p

def allocate(n):
    addr=libc.mmap(None,n,7,0x22,-1,0)
    if addr in [None,C.c_void_p(-1).value]:raise OSError('mmap failed')
    return int(addr)
def put(p,data):C.memmove(p,data,len(data))
def r32(p):return C.c_uint.from_address(p).value
def r64(p):return C.c_uint64.from_address(p).value
def w32(p,v):C.c_uint.from_address(p).value=v
def w64(p,v):C.c_uint64.from_address(p).value=v

class Host:
    def __init__(self,slot=98,encoded_fields=False,stamp=1721645006,remove=0,conflict=0,magic=False,hand_magic=1,fail_alloc=0,fail_protect=0,air=False,air_dodge=1,control_mode=0):
        self.game=allocate(0x3000000);bridge.bridge_reset(self.game);bridge.bridge_range(self.game,0x3000000,0x40);bridge.bridge_modes(remove,conflict)
        w32(self.game+60,0x80);w32(self.game+0x80,0x4550);w32(self.game+0x88,stamp)
        self.buffers=[]
        self.actor=self.buffer(bytes(0x800));w32(self.actor+0x374,1);w64(self.game+0x2537e48,self.actor)
        self.save=self.game+0x2de9360;put(self.save+4,b'\x64\x05\x0a');put(self.save+0x44,b'\x81\x82\x00')
        self.native_table=bytes((i*7)%256 for i in range(65*12));self.original_table=self.buffer(self.native_table);w64(self.game+0x2d36d48,self.original_table)
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
            self.control_prefix=bytes.fromhex('48895c2418574883ec40488b0557e82a00')
            self.queue_prefix=bytes.fromhex('48895c2408574883ec20488bf9')
            call=lambda n:b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(n))+b'\xff\xd0'
            put(self.game+0x2a6220,self.control_prefix+call(b'NativeControl')+bytes.fromhex('4883c4405f488b5c2418c3'))
            put(self.game+0x29f980,self.queue_prefix+call(b'NativeQueue')+bytes.fromhex('4883c4205f488b5c2408c3'))
            put(self.game+0x297870,bytes.fromhex('f601047518f6818800000020750ff68144040000017506b801000000c333c0c3'))
        self.load_pe()
    def activate_bank(self,olympus,encoded_fields=False):
        self.slot=60 if olympus else 98
        self.records=[r for r in self.all_records if not olympus or r['olympus_slot']!=0xffffffff]
        self.record_by_slot={r['normal_slot']:r for r in self.records}
        raw={r['normal_slot']:(ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes() for r in self.records}
        packed=bytearray();offsets={}
        for record in self.records:
            key=record['normal_slot'];packed.extend(bytes((-len(packed))%16));offsets[key]=len(packed);packed.extend(raw[key])
        control=(ROOT/'fixtures/control_native_s105.bin').read_bytes();packed.extend(bytes((-len(packed))%16));control_offset=len(packed);packed.extend(control)
        region=self.buffer(bytes(packed));self.unmapped=region+control_offset;self.unmapped_original=control
        self.array=self.buffer(bytes(128*4));self.motions={};self.runtime_originals={}
        for record in self.records:
            key=record['normal_slot'];motion=region+offsets[key];data=raw[key]
            if encoded_fields:
                for off in [20,28,36,40,48,56,60,68,76]:
                    value=r32(motion+off)
                    if value and value<len(data):w32(motion+off,bridge.bridge_encode(motion+value))
            self.motions[key]=motion;self.runtime_originals[key]=C.string_at(motion,len(data))
            slot=record['olympus_slot'] if olympus else record['normal_slot'];w32(self.array+slot*4,bridge.bridge_encode(motion))
        w32(self.array+(67 if olympus else 105)*4,bridge.bridge_encode(self.unmapped))
        self.motion=self.motions[98];self.original_motion=raw[98]
        self.key_offset=struct.unpack_from('<I',raw[98],40)[0];self.runtime_original=self.runtime_originals[98]
        w32(self.actor+0x1d4,bridge.bridge_encode(self.array))
        self.request_original=(ROOT/f"fixtures/requests_{'he' if olympus else 'normal'}_original.bin").read_bytes()
        self.requests=self.buffer(self.request_original)
        self.original_request_handle=bridge.bridge_encode(self.requests)
        w32(self.actor+0x1d8,self.original_request_handle)
    def buffer(self,data):
        p=allocate((len(data)+4095)&~4095);put(p,data);bridge.bridge_range(p,len(data),4);self.buffers.append(p);return p
    def load_pe(self):
        data=(ROOT/'kh1-aqua.dll').read_bytes();pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];op=pe+24
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
        if int(on)>1 and 98<=slot<=104:folder=ROOT/f'sets/p{int(on)-1}/fixtures'
        data=bytearray((folder/f"{'aqua' if on else 'original'}_{r['fixture_stem']}.bin").read_bytes())
        data[:80]=self.runtime_originals[slot][:80];return bytes(data)
    def assert_all(self,test,on):
        for r in self.records:test.assertEqual(self.body(r['normal_slot']),self.expected(r['normal_slot'],on),r['action'])
        active=self.decode(r32(self.actor+0x1d8))
        wanted=(ROOT/f"fixtures/requests_{'he' if self.slot==60 else 'normal'}_{'aqua' if on else 'original'}.bin").read_bytes()
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
    def dodge_body(self):
        data=bytearray((ROOT/'dodge/fixtures/aqua_s010.bin').read_bytes());data[:80]=self.runtime_originals[10][:80];return bytes(data)
    def arm_air(self,profile=0):
        self.frame();self.equip(True,profile);self.frame();self.control(state=0,request=0,height=0)
        self.control(state=2,request=6)

class RuntimeTests(unittest.TestCase):
    def test_air_control_hook_executes_relocated_cookie_trampoline_and_preserves_ground_input(self):
        h=Host(air=True);h.frame();before=h.snapshot()
        h.control(down=6,pressed=6,state=0,request=0,height=0)
        self.assertEqual(bridge.bridge_control_calls(),1)
        self.assertEqual([bridge.bridge_control_word(i) for i in range(4)],[6]*4)
        self.assertEqual(h.snapshot(),before)
        self.assertIn('AIR DODGE READY',bridge.bridge_log().decode())
    def test_neutral_air_circle_plays_504_masks_only_jump_and_preserves_velocity_and_native_flags(self):
        h=Host(air=True,control_mode=1);h.arm_air()
        put(h.actor+0x3b0,struct.pack('<3f',-4,2,3));velocity=C.string_at(h.actor+0x3b0,12);flags=C.string_at(h.actor,4)
        put(h.actor+0x16c,struct.pack('<f',18));h.control(down=6|0x80,pressed=6|0x100)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x16c),0)
        self.assertEqual([bridge.bridge_control_word(i)&6 for i in range(4)],[0]*4)
        self.assertEqual(r32(h.game+0x298ca94),6|0x80)
        self.assertEqual(r32(h.game+0x298ca98),6|0x100|0x40000000)
        self.assertEqual(C.string_at(h.actor+0x3b0,12),velocity);self.assertEqual(C.string_at(h.actor,4),flags)
        for slot in h.motions:
            if slot!=10:self.assertEqual(h.body(slot),h.expected(slot,1))
    def test_aerial_dodge_rising_start_queues_native_fall_without_changing_native_air_state(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6,state=1,request=5)
        self.assertEqual(h.body(10),h.dodge_body());self.assertEqual(r32(h.actor+0x164),6)
        self.assertEqual(r32(h.actor+0x70),1);self.assertEqual(r32(h.actor+0x178),0)
    def test_aerial_dodge_does_not_trigger_from_held_takeoff_or_directional_air_circle(self):
        h=Host(air=True);h.frame();h.equip(True);h.frame()
        h.control(down=6,pressed=6,state=0,request=4,height=0)
        h.control(down=6,pressed=0,state=1,request=5)
        self.assertEqual(h.body(10),h.expected(10,1))
        h.control();h.control(down=6,pressed=6,tilt=.8,x=.8)
        self.assertEqual(h.body(10),h.expected(10,1));self.assertEqual(bridge.bridge_control_word(0)&6,6)
        h.control();h.control(down=6,pressed=6);self.assertEqual(h.body(10),h.dodge_body())
    def test_aerial_dodge_finishes_into_506_and_requires_a_landing_before_repeating(self):
        h=Host(air=True);h.arm_air();h.control(down=6,pressed=6)
        put(h.actor+0x16c,struct.pack('<f',39));h.frame();h.assert_all(self,1)
        h.control();h.control(down=6,pressed=6);h.assert_all(self,1)
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
        for reason in ['off','other','event','menu','script','scriptflag','actionflag','cast','attack','reaction','shortcut','command','queued','queued_ledge','nan','moving','near_ground']:
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
            elif reason=='command':w32(h.game+0x2d53a40,2)
            elif reason in ['queued','queued_ledge']:w32(h.actor+0x178,1);w32(h.actor+0x17c,0xc8 if reason=='queued' else 0xd)
            elif reason=='nan':kwargs['tilt']=float('nan')
            elif reason=='moving':kwargs.update(tilt=.5,x=.5)
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
        for reason in ['control','can','queue','alloc','protect','disabled','remove']:
            h=Host(air=True,fail_alloc=reason=='alloc',fail_protect=reason=='protect',air_dodge=reason!='disabled',remove=reason=='remove')
            if reason in ['control','can','queue']:
                address=h.game+{'control':0x2a6220,'can':0x297870,'queue':0x29f980}[reason]
                C.c_ubyte.from_address(address).value^=1
            before=C.string_at(h.game+0x2a6220,17);h.frame()
            self.assertEqual(C.string_at(h.game+0x2a6220,17),before,reason)
    def test_ground_and_air_fire_thunder_cure_resolve_to_requested_distinct_records(self):
        for bank in [98,60]:
            h=Host(slot=bank,encoded_fields=True);h.frame()
            for profile in range(5):
                h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
                p=h.decode(r32(h.actor+0x1d8))
                targets=[54,55,56,79,80,81] if bank==98 else [17,18,19,41,42,43]
                self.assertEqual([r32(p+q*4)&0xfff for q in [0x36,0x38,0x39,0x83,0x85,0x86]],targets)
                self.assertEqual([i//4 for i in range(0,len(h.request_original),4)
                                  if C.string_at(p+i,4)!=h.request_original[i:i+4]],[0x38,0x85])
            h.equip(False,4);h.frame();h.assert_all(self,False)
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
        w32(h.actor+0x1d8,h.original_request_handle);h.frame();h.assert_all(self,False)
    def test_request_restore_waits_for_cast_completion_and_rejects_changed_original(self):
        h=Host();h.frame();h.equip(True);h.frame();pointer=r32(h.actor+0x1d8)
        w32(h.actor+0x164,0x38);h.equip(False);h.frame();self.assertEqual(r32(h.actor+0x1d8),pointer)
        w32(h.actor+0x164,0);w32(h.requests+0x39*4,0x1002);before=h.snapshot();h.frame()
        self.assertEqual(h.snapshot(),before);self.assertEqual(r32(h.actor+0x1d8),pointer)
        put(h.requests,h.request_original);h.frame();h.assert_all(self,False)
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
    def test_left_palm_magic_applies_in_all_five_profiles_with_distinct_right_hand_mock(self):
        h=Host(magic=True);h.frame()
        for profile in range(5):
            w32(h.actor+0x164,0);h.equip(True,profile);h.frame();h.assert_all(self,profile+1)
            for action in [0x36,0x83]:
                w32(h.actor+0x164,action);self.assertEqual(h.point(),[-11,22,33,1]);self.assertEqual(h.matrix()[12:],[-11,22,33,1])
                self.assertEqual(bridge.bridge_matrix_code(),0x20ce)

    def test_actual_pe_registers_lowercase_zero_ap_aqua_unequipped_and_preserves_native_table(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:7],b'\x81\x82\xf5\xf6\xf7\xf8\xf9');self.assertEqual(h.abilities()[7:],before[7:])
        row=table+116*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
        self.assertEqual(C.string_at(h.decode(r32(row+4)),5),b'\x45\x55\x59\x45\x00');h.assert_all(self,False)
    def test_normal_all_47_exact_on_and_off_including_idle_and_normal_only_ledge_recovery(self):
        h=Host();self.assertEqual(len(h.records),47);h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        self.assertIn('AQUA BANK: normal Sora',bridge.bridge_log().decode())
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_olympus_46_exact_on_and_off_with_encoded_pointers_and_common_idle_prefix(self):
        h=Host(slot=60,encoded_fields=True);self.assertEqual(len(h.records),46);h.frame();h.equip(True);h.frame();h.assert_all(self,True)
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

    def test_hand_magic_executes_actual_entry_detours_and_both_native_trampolines(self):
        h=Host(magic=True);h.frame();self.assertIn('AQUA HAND MAGIC READY',bridge.bridge_log().decode())
        self.assertEqual(h.point(),[100,200,300,1]);self.assertEqual(h.matrix()[12:],[100,200,300,1])
        h.equip(True);h.frame()
        for action in list(range(0x36,0x3e))+list(range(0x83,0x8b)):
            w32(h.actor+0x164,action)
            self.assertEqual(h.point(),[-11,22,33,1]);self.assertEqual(h.matrix()[12:],[-11,22,33,1]);self.assertEqual(bridge.bridge_matrix_code(),0x20ce)
        self.assertIn('AQUA HAND MAGIC ORIGIN',bridge.bridge_log().decode());self.assertIn('AQUA HAND MAGIC MATRIX',bridge.bridge_log().decode())
    def test_hand_magic_excludes_other_actors_attachments_actions_events_and_unloaded_banks(self):
        h=Host(magic=True);h.frame();h.equip(True);h.frame();w32(h.actor+0x164,0x36)
        companion=h.buffer(bytes(0x800));w32(companion+0x164,0x36);w32(companion+0x374,1)
        self.assertEqual(h.point(actor=companion),[100,200,300,1]);self.assertEqual(h.matrix(actor=companion)[12:],[100,200,300,1])
        for code in [0,0x31,0x2030,0x4065,0x8003]:
            self.assertEqual(h.point(code=code),[100,200,300,1]);self.assertEqual(bridge.bridge_point_code(),code);self.assertAlmostEqual(bridge.bridge_point_fraction(),.75)
        for action in [0,1,6,0x3e,0x71,0x72,0xc8,0xd4,0xdc]:
            w32(h.actor+0x164,action);self.assertEqual(h.point(),[100,200,300,1])
        w32(h.actor+0x164,0x36)
        for address in [h.actor+0x440,h.actor+0x444,h.game+0x298c9a0]:
            w32(address,1);self.assertEqual(h.point(),[100,200,300,1]);self.assertEqual(h.matrix()[12:],[100,200,300,1]);w32(address,0)
        old=r32(h.actor+0x1d4);w32(h.actor+0x1d4,0);self.assertEqual(h.point(),[100,200,300,1]);w32(h.actor+0x1d4,old)
        w32(h.actor+0x374,0);self.assertEqual(h.point(),[100,200,300,1])
    def test_hand_magic_returns_to_native_on_ability_off_and_reenables_on_new_bank(self):
        h=Host(magic=True);h.frame();h.equip(True);h.frame();w32(h.actor+0x164,0x36);self.assertEqual(h.point(),[-11,22,33,1])
        h.equip(False);w32(h.actor+0x164,0);h.frame();w32(h.actor+0x164,0x36);self.assertEqual(h.point(),[100,200,300,1]);h.assert_all(self,False)
        w32(h.actor+0x164,0);h.activate_bank(True,True);h.equip(True);h.frame();w32(h.actor+0x164,0x83);self.assertEqual(h.point(),[-11,22,33,1]);h.assert_all(self,True)
    def test_magic_hooks_admit_both_exact_prologues_before_any_code_write(self):
        for offset in [0x29ea00,0x29eb20]:
            h=Host(magic=True);C.c_ubyte.from_address(h.game+offset+8).value^=1
            before_a=C.string_at(h.game+0x29ea00,32);before_b=C.string_at(h.game+0x29eb20,32)
            h.frame();self.assertEqual(C.string_at(h.game+0x29ea00,32),before_a);self.assertEqual(C.string_at(h.game+0x29eb20,32),before_b)
            self.assertIn('attachment function bytes differ',bridge.bridge_log().decode());h.equip(True);h.frame();h.assert_all(self,True)
    def test_magic_allocation_protection_and_user_disable_fail_without_partial_hook_writes(self):
        for kwargs in [dict(fail_alloc=1),dict(fail_protect=1),dict(hand_magic=0)]:
            h=Host(magic=True,**kwargs);before_a=C.string_at(h.game+0x29ea00,32);before_b=C.string_at(h.game+0x29eb20,32)
            h.frame();self.assertEqual(C.string_at(h.game+0x29ea00,32),before_a);self.assertEqual(C.string_at(h.game+0x29eb20,32),before_b)
            h.equip(True);h.frame();h.assert_all(self,True)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
