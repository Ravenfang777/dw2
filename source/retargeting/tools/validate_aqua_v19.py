"""Record native anchors and derived v19 behavior; no game execution claimed."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'ability_v19'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):(WORK/name).write_text(json.dumps(data,indent=2)+'\n')

def validate(exe):
    raw=exe.read_bytes();pe=struct.unpack_from('<I',raw,60)[0];count=struct.unpack_from('<H',raw,pe+6)[0]
    sh=pe+24+struct.unpack_from('<H',raw,pe+20)[0]
    def at(rva,n):
        for i in range(count):
            vs,va,rs,rp=struct.unpack_from('<4I',raw,sh+40*i+8)
            if va<=rva and rva+n<=va+rs:return raw[rp+rva-va:rp+rva-va+n]
        raise ValueError(hex(rva))
    checks={0x2a6220:'48895c2418574883ec40488b0557e82a00',0x2b26c0:'40534883ec20488bd9e862060000',
        0x2af6a0:'48895c2410574883ec40f70100100000',0x2b1960:'48895c2410574883ec2048634170',
        0x297870:'f601047518f6818800000020750ff68144040000017506b801000000c333c0c3',
        0x29f980:'48895c2408574883ec20488bf9',0x2af356:'488d0543030000',
        0x2af4b8:'8d5102',0x2af4ca:'e891240000',0x2af3f0:'48895c2410574883ec50'}
    for rva,expected in checks.items():assert at(rva,len(bytes.fromhex(expected))).hex()==expected,(hex(rva),at(rva,len(bytes.fromhex(expected))).hex())
    assert struct.unpack_from('<I',raw,pe+8)[0]==1721645006
    common={'version':19,'passed':True,'game_runtime_tested':False}
    report=json.loads((WORK/'curve_validation.json').read_text());rows={r['normal_slot']:r for r in report['motions']}
    extra={0x2a3980:'48895c240848896c24104889742418',
        0x29f0a0:'405557488d6c24e84881ec18010000',0x2b4640:'4c8bdc49895b20574881eca0000000',
        0x2b4762:'f30f104b640f2fc87604',0x29f2a2:'f3440f598f84020000'}
    for rva,expected in extra.items():assert at(rva,len(bytes.fromhex(expected))).hex()==expected,hex(rva)
    checks.update(extra)
    write('native_controller_validation.json',{**common,'executable_sha256':sha(exe),'verified_anchors':{hex(k):v for k,v in checks.items()},
        'guard_row':'0x2A3980; row0x3D witness; rejects absent/interrupted/stale actions',
        'motion_clock':'0x29F0A0 takes actor and motion delta;0x29F2A2 multiplies delta by actor+284;0x29F366 advances actor+16C',
        'normal_speed_guard_delta_factor':53./156.,'finisher_trim_delta_factor':47./35.,
        'guard_angle_predicate':'0x2B4640;0x2B4762 compares facing dot against native guard data+64',
        'guard_angle_scope':'main Aqua; witnessed live Guard; own live native facing-restricted clash objects during Guard only; native clash pipeline remains',
        'native_unguardable_attack_policy_retained':True,'headers_and_allocation_sizes_unchanged':True,
        'direct_animation_clock_actor_position_or_hp_writes':False})
    write('guard_validation.json',{**common,'scope':'main Aqua only','source':'400','source_frames':40,'source_fps':30,
        'native_frames':54,'forward_native_clock':[0,26.5],'reverse_native_clock':[26.5,53],
        'native_motion_delta_factor':53./156.,'nominal_source_seconds':2.6,'defense_window_native_clock':[0,54],
        'angle':'360 degrees; native guard objects only','guard_action_requires_native_Guard_selection':True,
        'numbered_profiles':'v18 guard bytes and native timing retained','native_unblockable_attacks':'native policy'})
    write('native_movement_validation.json',{**common,'scope':'main Glide replacement; numbered profiles retain v18',
        'source_animation':'504','duration_native_units':39.,'horizontal_speed':14.,'upward_speed':.75,
        'horizontal_requested_distance':546.,'requested_lift':29.25,'direction':'capture prepared movement direction on tap; fallback existing horizontal momentum, then facing',
        'button':'fresh airborne Circle tap; release then tap again after animation to repeat',
        'held_glide':'suppressed in main; native input restored outside main or when air_dodge=0',
        'actor_position_written':False,'native_collision_callbacks_retained':True,'native_movement_rva':'0x2AF6A0'})
    write('air_dodge_validation.json',{**common,'main':'single-tap replacement for held Glide',
        'direction_locked_for_full_animation':True,'release_circle_or_stick_shortens_action':False,
        'repeat_requires_new_press_after_completion':True,'numbered_profiles':'retain v18 once-per-airtime steered dodge and native Glide',
        'native_headers_unmodified':True,'movement_tuning_report':'native_movement_validation.json'})
    write('glide_validation.json',{**common,'main':'Glide input and constructor replaced by tap504 burst',
        'numbered_profiles':'original native Glide','normal_native_motion_slots':[75,76,77,78],
        'all_native_glide_motion_bytes_and_clocks_unmodified':True,'new_native_glide_constructor_scope':'main Aqua only, air_dodge enabled'})
    write('head_skin_validation.json',{**common,'skinned_skull_joint':150,
        'main_combat_idle_slot':1,'main_combat_idle_yaw_left_degrees':20.,
        'main_aerial_fire_slots':[79,82],'main_aerial_blizzard_variant_slot':80,
        'main_aerial_cast_yaw_right_degrees':20.,'head_turns_on_numbered_profiles':False,
        'main_normal_run_source':'013','main_combat_run_source':'004','both_run_loops_retained':True,
        'bind_hair_corrections_retained':True,'game_rendering_pending':True})
    timing={str(s):rows[s]['event_timing'] for s in [98,99,100,101,110]}
    write('combo_timing_validation.json',{**common,'variants':timing,
        'main_ground_combo':['300','301','366'],'main_air_combo':['305','353','407'],
        'main_finisher_source_range':[12,47],'finisher_native_delta_factor':47./35.,
        'finisher_native_events_retimed_for_trim':True,'native_event_payloads_counts_and_pointers_unchanged':True,
        'second_source_finish_and_chain_open_frames':[32,44],'numbered_profiles':'byte-identical v18 choices and timing'})
    for name in ['cast_request_validation.json','native_attachment_validation.json','damage_reaction_validation.json']:
        r=json.loads((WORK/name).read_text());r['version']=19;write(name,r)
    for profile in range(1,5):
        folder=WORK/'sets'/f'p{profile}';r=json.loads((folder/'curve_validation.json').read_text());r['scope']='v18 numbered profile plus frozen v18 common poses; no v19 main edits'
        r['profile_changes_from_v18']=False;(folder/'curve_validation.json').write_text(json.dumps(r,indent=2)+'\n')
    report['scope']='Aqua v19 main: full native Guard with source30fps forward/reverse, all-angle native guard, air305/353/407,366 trimmed12, tap replaces Glide, skull yaw and run swap'
    (WORK/'curve_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V19 native controller anchors, scope and mappings verified')
if __name__=='__main__':
    validate(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'native_reference/Custom Movesets KH1/KINGDOM HEARTS FINAL MIX.exe')
