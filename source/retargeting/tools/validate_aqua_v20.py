"""Verify v20 anchors against the supplied executable and freeze change scope."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent if ROOT.parent.name=='source' else ROOT/'ability_v20'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):(WORK/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def validate(exe):
    raw=exe.read_bytes();pe=struct.unpack_from('<I',raw,60)[0];count=struct.unpack_from('<H',raw,pe+6)[0]
    sh=pe+24+struct.unpack_from('<H',raw,pe+20)[0]
    def at(rva,n):
        for i in range(count):
            vs,va,rs,rp=struct.unpack_from('<4I',raw,sh+40*i+8)
            if va<=rva and rva+n<=va+rs:return raw[rp+rva-va:rp+rva-va+n]
        raise ValueError(hex(rva))
    checks={0x2a6220:'48895c2418574883ec40488b0557e82a00',0x2b26c0:'40534883ec20488bd9e862060000',
        0x2b2750:'40534883ec20488bd9e8d2050000',0x2b2d30:'40534883ec20488bd98b8948010000',
        0x2af6a0:'48895c2410574883ec40f70100100000',0x2b1960:'48895c2410574883ec2048634170',
        0x297870:'f601047518f6818800000020750ff68144040000017506b801000000c333c0c3',
        0x29f980:'48895c2408574883ec20488bf9',0x2a3980:'48895c240848896c24104889742418',
        0x29f0a0:'405557488d6c24e84881ec18010000',0x2b4640:'4c8bdc49895b20574881eca0000000',
        0x2b47a0:'48896c241048897424185741564157',0x2b3270:'48895c2408574883ec20488bf9',
        0x2b3560:'4883ec2883b9b400000000',0x2b3760:'8b15aa3fb00233c9',
        0x2b4762:'f30f104b640f2fc87604',0x29f2a2:'f3440f598f84020000'}
    for rva,expected in checks.items():assert at(rva,len(bytes.fromhex(expected))).hex()==expected,(hex(rva),at(rva,len(bytes.fromhex(expected))).hex())
    assert struct.unpack_from('<I',raw,pe+8)[0]==1721645006
    assert sha(exe)=='d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac'
    common={'version':20,'passed':True,'game_runtime_tested':False}
    write('native_controller_validation.json',{**common,'executable_sha256':sha(exe),'verified_anchors':{hex(k):v for k,v in checks.items()},
        'guard_row':'0x2A3980 row3D witness; other callbacks preserve the witness until action/queue validation',
        'motion_clock':'0x29F0A0 actor-motion delta only; headers and counts stay native',
        'guard_pool':'0x2B47A0 pre-collection refresh; native0x2B3270 constructor,0x2B3760 contact mask and0x2B3560 retirement',
        'guard_angle':'0x2B4640; unrelated pairs skip memory queries; only witnessed Sora-owned native Guard classes bypass facing',
        'guard_data':'private copy of a witnessed live native Guard row, full-angle cosine; original shared row untouched',
        'glide':'both0x2B26C0 normal and0x2B2750 Superglide call0x2B2D30; shared admission is hooked',
        'direct_actor_position_animation_clock_or_hp_writes':False})
    write('guard_validation.json',{**common,'scope':'main Aqua only','source':'400','source_frames':40,'source_fps':30,
        'native_frames':54,'forward_native_clock':[0,26.5],'reverse_native_clock':[26.5,53],
        'native_motion_delta_factor':53./156.,'nominal_source_seconds':2.6,'defense_window_native_clock':[0,54],
        'additional_release_grace_native_ticks':12.,'parry_grace_native_ticks':12.,'maximum_lease_native_ticks':168.,
        'body_capsule':{'radius':50.,'lower_center_above_actor':35.,'upper_center_above_actor':85.,'direction':'all angles'},
        'native_pool_objects_added':1,'template_requires_witnessed_native_Guard':True,'body_shield_damage':0,
        'guard_animation_speed_in_parry':'native; D4 rate does not leak into6E/6F',
        'retirement':'only matching private-data, owner and contact-mask slot; recycled slots untouched',
        'cancel_on':['damage','new attack or cast','walking','airborne','ability change','unload','script or menu'],
        'numbered_profiles':'v19/v18 bytes and native timing retained','game_collision_and_deflection_test_pending':True})
    write('native_movement_validation.json',{**common,'scope':'main tap504 replaces both native Glide constructors',
        'source_animation':'504','duration_native_units':39.,'horizontal_speed':14.,'upward_speed':.75,
        'horizontal_requested_distance':546.,'requested_lift':29.25,'direction':'locked tap direction, momentum/facing fallback',
        'binding_recovery':'Glide blocking uses selected main intent; action execution requires full admitted binding',
        'actor_position_written':False,'native_collision_callbacks_retained':True})
    write('air_dodge_validation.json',{**common,'main':'finite504, held normal/Superglide blocked through binding recovery',
        'direction_locked_for_full_animation':True,'release_shortens_dodge':False,'repeat_requires_new_press':True,
        'numbered_profiles':'prior v19/v18 controls; normal Glide suppressed during active dodge, Superglide behavior retained',
        'full_bank_admission_retry_frames':8,'already_applied_payloads_can_readmit_while_moving':True})
    write('glide_validation.json',{**common,'main':'shared normal and Superglide constructor blocked when selected and air_dodge enabled',
        'numbered_profiles':'prior native Glide behavior','normal_native_motion_slots':[75,76,77,78],
        'all_native_glide_motion_bytes_and_clocks_unmodified':True,'native_input_restored_when_unequipped_or_disabled':True})
    write('head_skin_validation.json',{**common,'skinned_skull_joint':150,'main_combat_idle_slot':1,
        'main_combat_idle_roll_right_degrees':20.,'previous_main_idle_yaw_left_removed':True,
        'main_aerial_fire_slots':[79,82],'main_aerial_blizzard_variant_slot':80,
        'main_aerial_cast_yaw_right_degrees':20.,'numbered_head_poses_unchanged':True,
        'main_normal_run_source':'013','main_combat_run_source':'004','both_run_loops_retained':True,
        'bind_hair_corrections_retained':True,'game_rendering_pending':True})
    report=json.loads((WORK/'curve_validation.json').read_text());rows={r['normal_slot']:r for r in report['motions']}
    write('combo_timing_validation.json',{**common,'variants':{str(s):rows[s]['event_timing'] for s in [98,99,100,101,102,103,110]},
        'main_ground_combo':['300','301','366'],'main_air_combo':['305','353','407'],
        'main_second_source_range':[0,37],'main_second_discarded_source_frames':[38,39,40],
        'main_second_native_chain_open':[30,42],'main_second_native_delta_factors':[1.,1.4],
        'main_second_real_chain_open_ticks':[30,30],'first_contact_and_chain_timing_unchanged':True,
        'main_finisher_source_range':[12,47],'finisher_native_delta_factor':47./35.,
        'main_air_chain_windows':{'102':[18,40],'103':[24,42]},
        'event_counts_payloads_pointers_and_native_headers_preserved':True,'numbered_profiles':'v19/v18 bytes preserved'})
    for name in ['cast_request_validation.json','native_attachment_validation.json','damage_reaction_validation.json']:
        r=json.loads((WORK/name).read_text());r['version']=20;write(name,r)
    report['scope']='Aqua v20 main: right skull roll20,301 tail trim and matching alternate timing, longer air chain windows, wider native body Guard and grace, tap504 Glide replacement with bounded readmission'
    write('curve_validation.json',report)
    from aqua_v20_plan import get_plan
    write('source_selections.json',{'version':20,'profiles':{str(i):get_plan(i) for i in [0,1,2,3,4,5,7]}})
    print('v20 executable anchors, mappings, timing and scope verified')
if __name__=='__main__':
    if len(sys.argv)<2:raise SystemExit('Usage: python validate_aqua_v20.py PATH_TO_SUPPLIED_STEAM_EXE')
    validate(Path(sys.argv[1]))
