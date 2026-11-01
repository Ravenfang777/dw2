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
        self.records=json.loads((ROOT/'curve_validation.json').read_text())['motions']
        self.array=self.buffer(bytes(128*4));self.slot=slot;self.motions={};self.runtime_originals={}
        for record in self.records:
            request=record['request'];data=(ROOT/f'fixtures/original_{request:02X}.bin').read_bytes()
            motion=self.buffer(data);self.motions[request]=motion
            if encoded_fields:
                for off in [20,28,36,40,48,56,60,68,76]:
                    value=r32(motion+off)
                    if value and value<len(data):w32(motion+off,bridge.bridge_encode(motion+value))
            self.runtime_originals[request]=C.string_at(motion,len(data))
            physical=record['olympus_slot'] if slot==60 else record['normal_slot']
            w32(self.array+physical*4,bridge.bridge_encode(motion))
        self.motion=self.motions[0xc8];self.original_motion=(ROOT/'fixtures/original_C8.bin').read_bytes()
        self.key_offset=struct.unpack_from('<I',self.original_motion,40)[0]
        self.runtime_original=self.runtime_originals[0xc8]
        w32(self.actor+0x1d4,bridge.bridge_encode(self.array))
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
    def body(self,request=0xc8):return C.string_at(self.motions[request],len(self.runtime_originals[request]))
    def expected(self,request,on):
        data=bytearray((ROOT/f'fixtures/{"aqua" if on else "original"}_{request:02X}.bin').read_bytes())
        data[:80]=self.runtime_originals[request][:80]
        return bytes(data)
    def assert_all(self,test,on):
        for r in self.records:test.assertEqual(self.body(r['request']),self.expected(r['request'],on),hex(r['request']))

class RuntimeTests(unittest.TestCase):
    def test_actual_pe_registers_lowercase_aqua_off_preserving_all_native_abilities_and_bodies(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:3],b'\x81\x82\xf5');self.assertEqual(h.abilities()[3:],before[3:])
        row=table+116*12;self.assertEqual(C.c_ubyte.from_address(row).value,0)
        self.assertEqual(C.string_at(h.decode(r32(row+4)),5),b'\x45\x55\x59\x45\x00')
        h.assert_all(self,False)
    def test_normal_all_nine_on_exactly_match_fixtures_and_off_restores_every_byte(self):
        h=Host();h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        h.equip(False);h.frame();h.assert_all(self,False)
        self.assertIn('AQUA BANK: normal Sora',bridge.bridge_log().decode())
    def test_olympus_all_nine_with_native_encoded_data_pointers_restore_exactly(self):
        h=Host(slot=60,encoded_fields=True);h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        self.assertIn('AQUA BANK: Olympus',bridge.bridge_log().decode())
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_full_list_does_not_evict_or_write_a_native_entry_or_any_body(self):
        h=Host();put(h.save+0x44,bytes(range(1,49)));before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False)
    def test_foreign_change_in_last_record_blocks_writes_to_every_record(self):
        h=Host();h.frame();h.equip(True);p=h.motions[0xdc];offset=r32(p+40);w32(p+offset+4,0x7f123456)
        before={r['request']:h.body(r['request']) for r in h.records};h.frame()
        for request,data in before.items():self.assertEqual(h.body(request),data)
        log=bridge.bridge_log().decode();self.assertIn('AQUA rejected request=0xDC',log);self.assertIn('AQUA admission stage=0x38',log)
    def test_unknown_schema_in_late_record_blocks_earlier_record_writes(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[0xce]+44,70);before={r['request']:h.body(r['request']) for r in h.records};h.frame()
        for request,data in before.items():self.assertEqual(h.body(request),data)
    def test_every_tested_action_defers_a_body_switch_until_finished(self):
        h=Host();h.frame();h.equip(True)
        for action in [0xc8,0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xd4,0xdc]:
            w32(h.actor+0x164,action);h.frame();h.assert_all(self,False)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,True)
    def test_unequip_during_guard_waits_then_restores_all_original_data(self):
        h=Host();h.frame();h.equip(True);h.frame();h.equip(False);w32(h.actor+0x164,0xd4);h.frame();h.assert_all(self,True)
        w32(h.actor+0x164,0);h.frame();h.assert_all(self,False)
    def test_uninstall_removes_only_aqua_and_restores_previously_patched_bodies(self):
        h=Host(remove=1);put(h.save+0x44,b'\x81\x75\x82\x00')
        for r in h.records:put(h.motions[r['request']],h.expected(r['request'],True))
        h.frame();self.assertEqual(h.abilities()[:4],b'\x81\x82\x00\x00');h.assert_all(self,False)
    def test_unknown_build_never_writes_abilities_table_or_bodies(self):
        h=Host(stamp=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False);self.assertEqual(r64(h.game+0x2d36d48),h.original_table)
    def test_legacy_styles_dll_suspends_controller_without_any_changes(self):
        h=Host(conflict=1);before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,False)
    def test_a_single_record_reloaded_at_same_address_is_readmitted_with_others_still_patched(self):
        h=Host();h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        put(h.motions[0xcd],h.runtime_originals[0xcd]);h.frame();h.assert_all(self,True)
        h.equip(False);h.frame();h.assert_all(self,False)
    def test_live_bank_switch_then_unequip_restores_each_bank_when_active(self):
        h=Host();h.frame();h.equip(True);h.frame();h.assert_all(self,True)
        old_motions,old_originals,old_array=h.motions,h.runtime_originals,h.array
        old_bytes={request:h.body(request) for request in old_motions}
        h.motions={};h.runtime_originals={};h.array=h.buffer(bytes(128*4))
        for r in h.records:
            request=r['request'];data=(ROOT/f'fixtures/original_{request:02X}.bin').read_bytes();p=h.buffer(data)
            for off in [20,28,36,40,48,56,60,68,76]:
                value=r32(p+off)
                if value and value<len(data):w32(p+off,bridge.bridge_encode(p+value))
            h.motions[request]=p;h.runtime_originals[request]=C.string_at(p,len(data));w32(h.array+r['olympus_slot']*4,bridge.bridge_encode(p))
        w32(h.actor+0x1d4,bridge.bridge_encode(h.array));h.frame();h.assert_all(self,True)
        h.equip(False);h.frame();h.assert_all(self,False)
        for request,data in old_bytes.items():self.assertEqual(C.string_at(old_motions[request],len(data)),data)
        h.motions,h.runtime_originals,h.array=old_motions,old_originals,old_array
        w32(h.actor+0x1d4,bridge.bridge_encode(old_array));h.frame();h.assert_all(self,False)
    def test_invalid_data_pointer_cannot_cause_writes_to_other_valid_records(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[0xcd]+40,0)
        before={r['request']:h.body(r['request']) for r in h.records};h.frame()
        for request,data in before.items():self.assertEqual(h.body(request),data)
    def test_preexisting_equipped_aqua_is_respected_without_duplicate_grant(self):
        h=Host();put(h.save+0x44,b'\x81\x75\x82\x00');before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,True)
    def test_unloaded_actor_cannot_trigger_stale_curve_writes(self):
        h=Host();h.frame();h.equip(True);h.frame();w64(h.game+0x2537e48,0);h.equip(False);h.frame();h.assert_all(self,True)
        w64(h.game+0x2537e48,h.actor);h.frame();h.assert_all(self,False)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
