"""Execute the built PE's real OnInit/OnFrame with a controlled Win64 mock host.

This checks the DLL's actual calling convention, relocations, imports, ability
entry, curve admission and reversible gate. It is not a Windows/game test.
"""
from pathlib import Path
import ctypes as C,json,struct,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parent
subprocess.run(['gcc','-std=c11','-O2','-shared','-fPIC','test_bridge.c','-o','test_bridge.so'],cwd=ROOT,check=True)
bridge=C.CDLL(str(ROOT/'test_bridge.so'))
for name,args,ret in [('bridge_reset',[C.c_size_t],None),('bridge_range',[C.c_size_t,C.c_size_t,C.c_uint],None),('bridge_modes',[C.c_int,C.c_int],None),('bridge_log',[],C.c_char_p),('bridge_encode',[C.c_size_t],C.c_uint),('bridge_symbol',[C.c_char_p],C.c_size_t),('bridge_call0',[C.c_size_t],None),('bridge_init',[C.c_size_t],None)]:
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
    def __init__(self,slot=98,encoded_fields=False,stamp=1721645006,remove=0,conflict=0):
        self.game=allocate(0x3000000);bridge.bridge_reset(self.game);bridge.bridge_range(self.game,0x3000000,0x40);bridge.bridge_modes(remove,conflict)
        w32(self.game+60,0x80);w32(self.game+0x80,0x4550);w32(self.game+0x88,stamp)
        self.buffers=[]
        self.actor=self.buffer(bytes(0x800));w32(self.actor+0x374,1);w64(self.game+0x2537e48,self.actor)
        self.save=self.game+0x2de9360;put(self.save+4,b'\x64\x05\x0a');put(self.save+0x44,b'\x81\x82\x00')
        self.native_table=bytes((i*7)%256 for i in range(65*12));self.original_table=self.buffer(self.native_table);w64(self.game+0x2d36d48,self.original_table)
        self.original_motion=(ROOT/'fixtures/original_C8.bin').read_bytes()
        self.motion=self.buffer(self.original_motion);self.key_offset=r32(self.motion+40)
        if encoded_fields:
            for off in [20,28,36,40,48,56,60,68,76]:
                value=r32(self.motion+off)
                if value and value<len(self.original_motion):w32(self.motion+off,bridge.bridge_encode(self.motion+value))
        self.runtime_original=C.string_at(self.motion,len(self.original_motion))
        self.array=self.buffer(bytes(128*4));w32(self.array+slot*4,bridge.bridge_encode(self.motion));w32(self.actor+0x1d4,bridge.bridge_encode(self.array));self.slot=slot
        # Native pointer-to-handle helper uses the ABI of the existing reference.
        put(self.game+0x38ad90,b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeHandle'))+b'\xff\xe0')
        self.load_pe()
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
    def equip(self,on):
        data=bytearray(self.abilities());i=next(i for i,v in enumerate(data) if v&127==117);data[i]=117 if on else 245;put(self.save+0x44,bytes(data))
    def decode(self,h):return r64(self.game+0x2ee3980+((h&0x7fffffff)>>25)*8)+(h&0x1ffffff)
    def body(self):return C.string_at(self.motion,len(self.original_motion))

class RuntimeTests(unittest.TestCase):
    def test_actual_pe_registers_lowercase_aqua_unequipped_and_preserves_native_table(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:3],b'\x81\x82\xf5');self.assertEqual(h.abilities()[3:],before[3:])
        row=table+116*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
        self.assertEqual(C.string_at(h.decode(r32(row+4)),5),b'\x45\x55\x59\x45\x00')
        self.assertEqual(h.body(),h.runtime_original)
    def test_normal_gate_on_matches_tested_v4_and_off_restores_every_motion_byte(self):
        h=Host();h.frame();h.equip(True);h.frame()
        probe=(ROOT/'fixtures/v4_C8.bin').read_bytes()
        self.assertEqual(h.body(),probe)
        h.equip(False);h.frame();self.assertEqual(h.body(),h.runtime_original)
    def test_olympus_slot_and_encoded_runtime_pointers_use_the_same_verified_gate(self):
        h=Host(slot=60,encoded_fields=True);h.frame();h.equip(True);h.frame()
        self.assertNotEqual(h.body(),h.runtime_original)
        self.assertIn('AQUA bank physical slot=0x3C',bridge.bridge_log().decode())
        h.equip(False);h.frame();self.assertEqual(h.body(),h.runtime_original)
    def test_full_ability_list_does_not_evict_or_write_any_native_entry(self):
        h=Host();put(h.save+0x44,bytes(range(1,49)));before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);self.assertEqual(h.body(),h.runtime_original)
    def test_foreign_curve_change_rejects_all_motion_writes(self):
        h=Host();h.frame();h.equip(True);w32(h.motion+h.key_offset+950*16+4,0x7f123456);before=h.body();h.frame();self.assertEqual(h.body(),before)
    def test_switch_waits_for_current_first_attack_to_finish(self):
        h=Host();h.frame();h.equip(True);w32(h.actor+0x164,0xc8);h.frame();self.assertEqual(h.body(),h.runtime_original)
        w32(h.actor+0x164,0);h.frame();self.assertNotEqual(h.body(),h.runtime_original)
    def test_uninstall_removes_only_aqua(self):
        h=Host(remove=1);put(h.save+0x44,b'\x81\x75\x82\x00');h.frame();self.assertEqual(h.abilities()[:4],b'\x81\x82\x00\x00');self.assertEqual(h.body(),h.runtime_original)
    def test_unknown_build_disables_before_ability_or_curve_writes(self):
        h=Host(stamp=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);self.assertEqual(h.body(),h.runtime_original);self.assertEqual(r64(h.game+0x2d36d48),h.original_table)
    def test_old_styles_dll_suspends_standalone_controller(self):
        h=Host(conflict=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);self.assertEqual(h.body(),h.runtime_original)
    def test_reloaded_record_at_same_addresses_is_readmitted_and_patched(self):
        h=Host();h.frame();h.equip(True);h.frame();self.assertNotEqual(h.body(),h.runtime_original)
        put(h.motion,h.runtime_original);h.frame();self.assertNotEqual(h.body(),h.runtime_original)
        h.equip(False);h.frame();self.assertEqual(h.body(),h.runtime_original)
    def test_changed_motion_schema_causes_no_partial_writes(self):
        h=Host();h.frame();h.equip(True);w32(h.motion+44,70);before=h.body();h.frame();self.assertEqual(h.body(),before)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
