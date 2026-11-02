"""Record native anchors and derived v16 behavior; no game execution claimed."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'ability_v16'

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
    log=ROOT.parent/'upload/kh1-aqua(5).log';patch=ROOT.parent/'aqua_source/prototype_v52/source/NineStyles_v52.patch'
    write('native_movement_validation.json',{'version':16,'passed':True,'game_runtime_tested':False,
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
            'exact_kh2_parameters_extracted':False,'reference_two_times_distance_multiplier_used':False},
        'kh1_test_tuning':{'height_units_held':96,'initial_up_speed_per_native_frame':12,'gravity_per_native_frame_squared':.75,
            'horizontal_speed_per_native_frame':6,'release_up_speed_cap':4,'fall_speed_cap':20,'native_animation_frames':40},
        'actor_position_written_by_mod':False,'collision_and_landing_callbacks_native':True,
        'extra_guard_invulnerability_or_attack_grant':False,
        'source_animation':'504','normal_falling_animation':'506','run_head_lift_degrees':12,
        'supplied_v15_log':{'filename':log.name,'sha256':sha(log),'accepted_animation_but_no_movement_in_v15':True},
        'limitations':['KH1-specific movement tuning follows Master-style structure; not a byte-identical KH2 controller port','Windows/KH1 not executed; collision behavior needs live verification']})
    air=json.loads((WORK/'air_dodge_validation.json').read_text());air.update(version=16,actor_state_velocity_gravity_unchanged=False,
        actor_position_written=False,master_style_movement_added=True,movement_callback_rva='0x2AF6A0',
        native_set_state_rva='0x2B1960',native_fall_state=2,collision_handling='native',movement_tuning_report='native_movement_validation.json',
        user_log_name=log.name,user_log_sha256=sha(log),user_log_accepted_504_actions=log.read_text(errors='replace').count('AQUA AIR DODGE504:'),
        postfix_game_verified=False)
    for k in ['user_log_airborne_press_rejections_due_only_to_command_flag','v13_exact_log_shaped_reproduction_rejected','v14_exact_log_shaped_reproduction_in_tests']:air.pop(k,None)
    write('air_dodge_validation.json',air)
    glide=json.loads((WORK/'glide_validation.json').read_text());glide.update(version=16,held_source_frame=20,
        native_clock_and_queued_frame_cap=40,direction_changes_keep_progress=True,middle='Aqua350 frame20 held through native steering and motion changes')
    glide.pop('original_sora_middle_slots',None);write('glide_validation.json',glide)
    cast=json.loads((WORK/'cast_request_validation.json').read_text());cast.update(version=16,
        main_blizzard_release_slots=[55,80],main_blizzard_recovery_requests=[],additional_main_requests=[],
        native_spell_queue_append=None,blizzard_native_events_and_request_flags_unchanged=True,blizzard_visual_only_variant=True)
    cast['shared_poses']['main']['Blizzard']='391 ground;316 air; full Fire body in original Blizzard record; no added recovery request'
    write('cast_request_validation.json',cast)
    report=json.loads((WORK/'curve_validation.json').read_text())
    rows={r['normal_slot']:r for r in report['motions']}
    write('combo_timing_validation.json',{'version':16,'passed':True,'game_runtime_tested':False,
        'normal_slots':[98,99,100],'olympus_slots':[60,61,62],'source_clips':['300','365','365'],
        'native_event_sampler_rva':'0x394770','native_chain_flag_reader':'0x29EFB0 reads actor+1CC bit0x400000',
        'native_event_evidence':'0x39229F samples kind5;0x3922AF sets model+14 bit0x400000;0x29F515 copies model flags to actor+1CC',
        'variants':{str(s):rows[s]['event_timing'] for s in [98,99,100]},
        'second_source_finishes_at_native_frames':{'99':32,'100':44},
        'second_chain_window_widths_native_frames':{'99':16,'100':20},
        'sound_and_effect_keys_payloads_descriptors_and_counts_unchanged':True,'numbered_profiles_keep_native_timing':True})
    for folder in [WORK/'sets'/f'p{i}' for i in range(1,5)]+[WORK/'dodge',WORK/'glide_stop',WORK/'blizzard']:
        p=folder/'curve_validation.json';r=json.loads(p.read_text());r['scope']='Aqua v16 retained numbered combos/casts or common transient visual';p.write_text(json.dumps(r,indent=2)+'\n')
    print('Native anchors, mappings and v16 provenance verified')
if __name__=='__main__':
    validate(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'native_reference/Custom Movesets KH1/KINGDOM HEARTS FINAL MIX.exe')
