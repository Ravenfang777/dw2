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
        self.all_records=json.loads((ROOT/'curve_validation.json').read_text())['motions']
        self.activate_bank(slot==60,encoded_fields)
        # Native pointer-to-handle helper uses the ABI of the existing reference.
        put(self.game+0x38ad90,b'\x48\xb8'+struct.pack('<Q',bridge.bridge_symbol(b'NativeHandle'))+b'\xff\xe0')
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
    def body(self,slot=98):return C.string_at(self.motions[slot],len(self.runtime_originals[slot]))
    def expected(self,slot,on):
        r=self.record_by_slot[slot];data=bytearray((ROOT/f"fixtures/{'aqua' if on else 'original'}_{r['fixture_stem']}.bin").read_bytes())
        data[:80]=self.runtime_originals[slot][:80];return bytes(data)
    def assert_all(self,test,on):
        for r in self.records:test.assertEqual(self.body(r['normal_slot']),self.expected(r['normal_slot'],on),r['action'])
    def snapshot(self):return {r['normal_slot']:self.body(r['normal_slot']) for r in self.records}

class RuntimeTests(unittest.TestCase):
    def test_actual_pe_registers_lowercase_zero_ap_aqua_unequipped_and_preserves_native_table(self):
        h=Host();before=h.abilities();h.frame();table=r64(h.game+0x2d36d48)
        self.assertEqual(C.string_at(table,65*12),h.native_table)
        self.assertEqual(h.abilities()[:3],b'\x81\x82\xf5');self.assertEqual(h.abilities()[3:],before[3:])
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
        h=Host();h.frame();h.equip(True);h.frame();old=(h.records,h.record_by_slot,h.motions,h.runtime_originals,h.array);old_bytes=h.snapshot()
        h.activate_bank(True,True);h.frame();h.assert_all(self,True);h.equip(False);h.frame();h.assert_all(self,False)
        for slot,data in old_bytes.items():self.assertEqual(C.string_at(old[2][slot],len(data)),data)
        h.records,h.record_by_slot,h.motions,h.runtime_originals,h.array=old
        w32(h.actor+0x1d4,bridge.bridge_encode(h.array));h.frame();h.assert_all(self,False)
    def test_invalid_table_pointer_cannot_patch_any_other_valid_record(self):
        h=Host();h.frame();h.equip(True);w32(h.motions[79]+40,0);before=h.snapshot();h.frame();self.assertEqual(h.snapshot(),before)
    def test_saved_equipped_aqua_is_respected_without_duplicate_grant(self):
        h=Host();put(h.save+0x44,b'\x81\x75\x82\x00');before=h.abilities();h.frame();self.assertEqual(h.abilities(),before);h.assert_all(self,True)
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

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
    (ROOT/'runtime_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executed_actual_pe_dll':True,'win64_abi_and_imports_mocked':True,'windows_or_game_executed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
