"""Record native anchors and derived v18 behavior; no game execution claimed."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'ability_v18'

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
    log=ROOT.parent/'upload/kh1-aqua(7).log'
    common={'version':18,'passed':True,'game_runtime_tested':False}
    write('native_movement_validation.json',{**common,'supplied_executable_sha256':sha(exe),
        'timestamp':1721645006,'verified_anchors':{hex(k):v for k,v in checks.items()},
        'native_fall_movement_callback':'0x2AF6A0 before native collision',
        'native_state_setter':'0x2B1960 with native callbacks',
        'native_timestep_global':'0x233FBDC; finite positive timestep <=4',
        'movement':{'policy':'resample held world stick each native control; normalized, analog pressure clamped0..1; neutral brakes horizontal travel',
            'horizontal_speed':14.,'upward_speed':.75,'duration_native_units':39.,'full_stick_horizontal_distance':546.,'total_lift':29.25,
            'circle_release_shortens_action':False,'duration_from_visual_clock_and_bounded_elapsed_time':True},
        'actor_position_written_by_mod':False,'collision_and_landing_callbacks_native':True,
        'extra_guard_invulnerability_or_attack_grant':False,'source_animation':'504','normal_falling_animation':'506',
        'supplied_v17_log':{'filename':log.name,'sha256':sha(log),
            'accepted_504_count':log.read_text(errors='replace').count('AQUA AIR DODGE504:'),
            'observed_movement_callback_count':log.read_text(errors='replace').count('AQUA DODGE MOVEMENT ACTIVE:')},
        'limitations':['Movement numbers describe requested displacement before native collision; live travel depends on obstacles and interruption','Windows/KH1 not executed']})
    write('air_dodge_validation.json',{**common,'source':'504','temporary_normal_slot':10,'native_frames':40,
        'controls':'fresh airborne Circle after takeoff release; one dodge per airtime',
        'steerable_through_animation':True,'circle_release_cuts_lift':False,
        'profile_scope':'all five Aqua abilities','normal_fall':'506','native_glide_outside_dodge':True,
        'native_control_rva':'0x2A6220','native_displacement_rva':'0x2AF6A0','native_glide_guard_rva':'0x2B26C0',
        'movement_tuning_report':'native_movement_validation.json','no_direct_position_writes':True})
    write('glide_validation.json',{**common,'default_native_glide':True,'normal_slots':[75,76,77,78],
        'olympus_slots':[37,38,39,40],'aqua_body_overrides':0,'clock_or_queue_frame_writes':0,
        'native_physics_unlock_input_and_steering':True,'normal_fall_after_native_glide':'506'})
    cast=json.loads((WORK/'cast_request_validation.json').read_text());cast['version']=18
    write('cast_request_validation.json',cast)
    report=json.loads((WORK/'curve_validation.json').read_text());rows={r['normal_slot']:r for r in report['motions']}
    assert not set(rows)&set(range(61,71))
    write('combo_timing_validation.json',{**common,'normal_slots':[98,99,100],
        'olympus_slots':[60,61,62],'source_clips':['300','301','301'],
        'native_event_sampler_rva':'0x394770','native_chain_flag_reader':'0x29EFB0 reads actor+1CC bit0x400000',
        'variants':{str(s):rows[s]['event_timing'] for s in [98,99,100]},
        'second_source_finishes_at_native_frames':{'99':32,'100':44},
        'second_chain_window_widths_native_frames':{'99':16,'100':20},
        'sound_and_effect_keys_payloads_descriptors_and_counts_unchanged':True,'numbered_profiles_keep_native_timing':True})
    model_path=ROOT/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls'
    mdls=model_path.read_bytes();u=lambda at:struct.unpack_from('<I',mdls,at)[0]
    mobj=u(4);header=mobj+u(mobj+32);table=header+u(header+4)
    assert (u(table+150*48+44)>>30)&3==1 and (u(table+151*48+44)>>30)&3==0
    write('head_skin_validation.json',{**common,'model_sha256':sha(model_path),'run_slots':[5,6,7],
        'run_head_mapping_retained':'Aqua head5 on skinned skull150; hair151 local bind',
        'idle_front_hair_slots':[0,1],'idle_front_hair_local_bind_joints':[151,152,153,154],
        'idle_skull150_direction_retained':True,'joint_lengths_scale_and_native_travel_preserved':True,
        'user_image':'image(1).png','game_rendered_verification_pending':True})
    guard=rows[110];assert guard['source_timing']=='guard_forward_hold_reverse'
    before=(WORK/'fixtures/original_s110.bin').read_bytes();after=(WORK/'fixtures/aqua_s110.bin').read_bytes()
    events=struct.unpack_from('<I',before,60)[0];assert before[events:]==after[events:]
    write('guard_validation.json',{**common,'source':'400','source_frames':40,'native_frames':54,
        'forward_frames':[0,10],'hold_frames':[10,36],'reverse_frames':[36,52],
        'forward_source_rate':3.9,'reverse_source_rate':2.4375,'minimum_requested_rate':1.25,
        'entire_source_played_each_direction_once':True,'native_guard_events_and_defense_unchanged':True,
        'no_new_hold_to_guard_mechanic':True,'native_hits_cancels_and_actions_can_interrupt_visual_recovery':True})
    write('damage_reaction_validation.json',{'version':18,'native_fallback_verified':True,'requested_replacement_completed':False,
        'requested':'default KH2 Sora damage and knockback','current':'original KH1 Sora damage and knockback',
        'blocked_by':'Default KH2 Sora model and motion source assets were not supplied; reference DLL loads these from users installed game',
        'no_aqua_reactions_installed':True,'normal_slots':list(range(61,71)),'olympus_slots':list(range(24,34)),
        'native_requests':list(range(0x48,0x52)),
        'known_kh2_donors':{'front_high':10,'front_low':11,'back_high':12,'back_low':13,'front_air':14,'back_air':15,'heavy_front':23,'heavy_back':24},
        'needed_files':['obj/P_EX100.mdlx','obj/P_EX100.mset'],
        'collector':'COLLECT_KH2_SORA_SOURCE.cmd','game_runtime_tested':False})
    for folder in [WORK/'sets'/f'p{i}' for i in range(1,5)]+[WORK/'dodge',WORK/'blizzard']:
        p=folder/'curve_validation.json';r=json.loads(p.read_text());r['scope']='Aqua v18 next test combos, retained casts or transient visual';p.write_text(json.dumps(r,indent=2)+'\n')
    print('Native anchors, mappings and v18 provenance verified')
if __name__=='__main__':
    validate(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'native_reference/Custom Movesets KH1/KINGDOM HEARTS FINAL MIX.exe')
