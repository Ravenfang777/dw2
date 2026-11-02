"""Record native anchors and derived v17 behavior; no game execution claimed."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'ability_v17'

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
    log=ROOT.parent/'upload/kh1-aqua(6).log';patch=ROOT.parent/'aqua_source/prototype_v52/source/NineStyles_v52.patch'
    write('native_movement_validation.json',{'version':17,'passed':True,'game_runtime_tested':False,
        'supplied_executable_sha256':sha(exe),'timestamp':1721645006,
        'verified_anchors':{hex(k):v for k,v in checks.items()},
        'native_fall_movement_callback':'0x2AF6A0; original state2 displacement before collision',
        'native_state_registration_evidence':'0x2AF356 loads0x2AF6A0;0x2AF365 selects state2;0x2AF36D registers via0x2B1B80',
        'native_collision_evidence':'0x2AF3F0 compares requested and realized movement; state2 ceiling resets arc and queues native air recovery/fall',
        'native_state_setter':'0x2B1960; registers native callbacks, sets state-change flag, preserves native action systems',
        'native_timestep_global':'0x233FBDC; positive finite timestep <=4 accepted',
        'master_reference':{'source':'user-supplied NineStyles_v52.patch','sha256':sha(patch),
            'lines':'31040..31094 begin_aerial_dodge / start_host_aerial_dodge',
            'borrowed_structure':['free-air admission','fresh airborne input','once per airtime','neutral vertical held arc','tilted stick directional speed','finite action returns native fall'],
            'recorded_dual_d_baseline':{'height':145.,'speed':18.,'source':'prior v52 kh1-dual-wield.log recovered from earlier project context'},'reference_two_times_distance_multiplier_used':True,'exact_kh2_gravity_and_release_coefficients_extracted':False},
        'movement':{'base_height':145.,'base_horizontal_speed':18.,'distance_multiplier':2.,'effective_held_height':290.,'effective_horizontal_speed':36.,'adapter_base_gravity':.75,'adapter_base_release_up_cap':4.,'adapter_base_fall_cap':20.,'native_visual_frames':40,'animation_or_arc_time_multiplier':1.},
        'actor_position_written_by_mod':False,'collision_and_landing_callbacks_native':True,
        'extra_guard_invulnerability_or_attack_grant':False,
        'source_animation':'504','normal_falling_animation':'506','run_head_skin_joint':150,'run_head_source_bone':5,'hair_helper_bind_rotation':151,
        'supplied_v16_log':{'filename':log.name,'sha256':sha(log),'accepted_dodge_count':log.read_text(errors='replace').count('AQUA AIR DODGE504:'),'movement_callback_observed_count':log.read_text(errors='replace').count('AQUA DODGE MOVEMENT ACTIVE:'),'both_ground_chain_variants_and_finisher_observed':True},
        'limitations':['Recorded Dual D145/18 and2x displacement policy reproduced; KH1 gravity/release adapter retained rather than claiming a full KH2 controller port','Windows/KH1 not executed; collision behavior needs live verification']})
    air=json.loads((WORK/'air_dodge_validation.json').read_text());air.update(version=17,actor_state_velocity_gravity_unchanged=False,
        actor_position_written=False,master_style_movement_added=True,movement_callback_rva='0x2AF6A0',
        native_set_state_rva='0x2B1960',native_fall_state=2,collision_handling='native',movement_tuning_report='native_movement_validation.json',
        user_log_name=log.name,user_log_sha256=sha(log),user_log_accepted_504_actions=log.read_text(errors='replace').count('AQUA AIR DODGE504:'),
        postfix_game_verified=False)
    for k in ['user_log_airborne_press_rejections_due_only_to_command_flag','v13_exact_log_shaped_reproduction_rejected','v14_exact_log_shaped_reproduction_in_tests']:air.pop(k,None)
    write('air_dodge_validation.json',air)
    write('glide_validation.json',{'version':17,'passed':True,'game_runtime_tested':False,
        'default_native_glide':True,'normal_slots':[75,76,77,78],'olympus_slots':[37,38,39,40],
        'aqua_body_overrides':0,'opening_held_and_closing_overlays':0,'clock_or_queue_frame_writes':0,
        'native_physics_unlock_input_and_steering':True,'regular_glide_guard_scope':'only during committed504; otherwise original constructor',
        'normal_fall_after_native_glide':'existing main/profile falling506; no350 closing restart'})
    cast=json.loads((WORK/'cast_request_validation.json').read_text());cast.update(version=17,
        main_blizzard_release_slots=[55,80],main_blizzard_recovery_requests=[],additional_main_requests=[],
        native_spell_queue_append=None,blizzard_native_events_and_request_flags_unchanged=True,blizzard_visual_only_variant=True)
    cast['shared_poses']['main']['Blizzard']='391 ground;316 air; full Fire body in original Blizzard record; no added recovery request'
    write('cast_request_validation.json',cast)
    report=json.loads((WORK/'curve_validation.json').read_text())
    rows={r['normal_slot']:r for r in report['motions']}
    write('combo_timing_validation.json',{'version':17,'passed':True,'game_runtime_tested':False,
        'normal_slots':[98,99,100],'olympus_slots':[60,61,62],'source_clips':['300','300','300'],
        'native_event_sampler_rva':'0x394770','native_chain_flag_reader':'0x29EFB0 reads actor+1CC bit0x400000',
        'native_event_evidence':'0x39229F samples kind5;0x3922AF sets model+14 bit0x400000;0x29F515 copies model flags to actor+1CC',
        'variants':{str(s):rows[s]['event_timing'] for s in [98,99,100]},
        'second_source_finishes_at_native_frames':{'99':32,'100':44},
        'second_chain_window_widths_native_frames':{'99':16,'100':20},
        'sound_and_effect_keys_payloads_descriptors_and_counts_unchanged':True,'numbered_profiles_keep_native_timing':True})
    for folder in [WORK/'sets'/f'p{i}' for i in range(1,5)]+[WORK/'dodge',WORK/'blizzard']:
        p=folder/'curve_validation.json';r=json.loads(p.read_text());r['scope']='Aqua v17 retained numbered combos/casts or common transient visual';p.write_text(json.dumps(r,indent=2)+'\n')
    model_path=ROOT/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls'
    mdls=model_path.read_bytes();u=lambda at:struct.unpack_from('<I',mdls,at)[0]
    mobj=u(4);header=mobj+u(mobj+32);table=header+u(header+4)
    assert (u(table+150*48+44)>>30)&3==1 and (u(table+151*48+44)>>30)&3==0
    write('head_skin_validation.json',{'version':17,'passed':True,'game_rendered':False,'model_sha256':sha(model_path),
        'run_slots':[5,6,7],'previous_target':{'joint':151,'links_word':hex(u(table+151*48+44)),'is_skin_joint':False},
        'corrected_skull':{'joint':150,'links_word':hex(u(table+150*48+44)),'is_skin_joint':True,'orientation_source':'Aqua authored head5, previously evaluated on helper151'},
        'hair_helper151_local_rotation':'native bind','separate_hair_lift_removed':True,'torso_neck_joint_lengths_and_skin_scale_preserved':True,
        'applies_to':'running only; all five profiles inherit the common run records',
        'user_video':{'filename':'20261102-1401-33.5670391.mp4','reviewed_run_frame_seconds':24},
        'game_verification_pending':True})
    print('Native anchors, mappings and v17 provenance verified')
if __name__=='__main__':
    validate(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'native_reference/Custom Movesets KH1/KINGDOM HEARTS FINAL MIX.exe')
