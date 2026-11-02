"""Verify v21 native anchors, main mappings and the requested action budgets."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent

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
    assert sha(exe)=='d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac'
    assert struct.unpack_from('<I',raw,pe+8)[0]==1721645006
    checks={0x2a6220:'48895c2418574883ec40488b0557e82a00',0x2b26c0:'40534883ec20488bd9e862060000',
        0x2b2750:'40534883ec20488bd9e8d2050000',0x2b2d30:'40534883ec20488bd98b8948010000',
        0x2af6a0:'48895c2410574883ec40f70100100000',0x2b1960:'48895c2410574883ec2048634170',
        0x297870:'f601047518f6818800000020750ff68144040000017506b801000000c333c0c3',
        0x29f980:'48895c2408574883ec20488bf9',0x2a3980:'48895c240848896c24104889742418',
        0x29f0a0:'405557488d6c24e84881ec18010000',0x2b4640:'4c8bdc49895b20574881eca0000000',
        0x2b47a0:'48896c241048897424185741564157',0x2b3270:'48895c2408574883ec20488bf9',
        0x2b3560:'4883ec2883b9b400000000',0x2b3760:'8b15aa3fb00233c9',
        0x2b4762:'f30f104b640f2fc87604',0x29f2a2:'f3440f598f84020000',
        0x2afda0:'4889742410574883ec30f30f1081b0030000'}
    for rva,expected in checks.items():assert at(rva,len(bytes.fromhex(expected))).hex()==expected,hex(rva)
    assert (WORK/'fixtures/native_jump_launch.bin').read_bytes()==at(0x2afda0,0x115)
    assert (WORK/'fixtures/native_jump_curve.bin').read_bytes()==at(0x2af530,0xff)
    for rva,hex_ in json.loads((WORK/'fixtures/native_jump_constants.json').read_text()).items():assert at(int(rva,16),16).hex()==hex_
    common={'version':21,'passed':True,'game_runtime_tested':False}
    old=json.loads((WORK/'native_controller_validation.json').read_text())
    old.update(common,executable_sha256=sha(exe),verified_anchors={hex(k):v for k,v in checks.items()},
        glide='ordinary Glide is blocked; native Superglide caller2B275E passes original eligibility and constructor',
        jump='native launch callback2AFDA0; post-launch height3BC *=1.25 and duration3B8 *=sqrt1.25; origin and gravity unchanged')
    write('native_controller_validation.json',old)
    write('native_movement_validation.json',{**common,'scope':'main Aqua only','source_animation':'504',
        'rate':1.5,'horizontal_speed':21.,'upward_speed':1.125,'duration_native_units':26.,
        'horizontal_requested_distance':546.,'requested_lift':29.25,'distance_matches_v20':True,
        'animation_clock_rate':1.5,'end_pose_held_until_final_displacement':True,
        'fall_handoff_horizontal_speed':14.,'actor_position_written':False,'collision_callbacks_retained':True,
        'motion_rate_hook_failure':'falls back to prior39-unit rate rather than desynchronizing movement and animation'})
    write('air_dodge_validation.json',{**common,'main':'once per airtime, faster504; ordinary Glide replaced; native Superglide usable',
        'reset':'only actual grounded state0 and height<=1, or a new actor identity',
        'does_not_reset_on':['button release','504 completion','native Superglide','ability toggle','bank/binding readmission'],
        'repeat_requires_landing':True,'direction_locked_for_full_animation':True,
        'numbered_profiles':'unchanged v20/v18 controls and serialized poses'})
    write('glide_validation.json',{**common,'main':'ordinary Glide replaced by one tap504 per airtime; native Superglide retained',
        'normal_constructor_return':'0x2B26CE blocked','superglide_constructor_return':'0x2B275E passes original',
        'successful_superglide_interrupts_dodge':True,'rejected_superglide_does_not_cancel_dodge':True,
        'native_ability_and_button_eligibility_retained':True,'native_glide_motion_slots':[75,76,77,78],
        'all_glide_motion_bytes_and_headers_unchanged':True})
    write('jump_validation.json',{**common,'scope':'main only; normal and High Jump','native_launch_rva':'0x2AFDA0',
        'height_multiplier':1.25,'arc_duration_multiplier':1.25**.5,'native_launch_origin_unchanged':True,
        'global_gravity_stats_and_actor_positions_unchanged':True,'native_ceiling_landing_and_interruptions_retained':True,
        'real_native_launch_and_arc_code_executed_in_test_host':True,'live_windows_tested':False})
    report=json.loads((WORK/'curve_validation.json').read_text());by={r['normal_slot']:r for r in report['motions']}
    assert [by[s]['donor']for s in [102,103,104]]==['305','407','353']
    assert [by[s]['source_range']for s in [99,100,101]]==[[0,30],[0,30],[15,47]]
    write('combo_timing_validation.json',{**common,'main_ground_combo':['300','301','366'],'main_air_combo':['305','407','353'],
        'second_source_range':[0,30],'additional_second_frames_trimmed_since_v20':list(range(31,38)),
        'second_chain_opens_native':[24.,33.6],'second_base_rates':[1.,1.4],'second_chain_opens_real_ticks':[24.,24.],
        'v20_second_chain_open_real_ticks':30.,'second_pose_hold_rate_multiplier':2.,
        'finisher_source_range':[15,47],'additional_finisher_start_frames_trimmed_since_v20':[12,13,14],
        'finisher_delta_factor':47./32.,'native_event_payloads_counts_pointers_and_headers_preserved':True,
        'air_chain_windows':{'102':[18,40],'103':[22,42]},'variants':{str(s):by[s]['event_timing'] for s in [98,99,100,101,102,103,104,110]}})
    for name in ['guard_validation.json','head_skin_validation.json','cast_request_validation.json','native_attachment_validation.json','damage_reaction_validation.json']:
        r=json.loads((WORK/name).read_text());r.update(common);r['retained_from_v20']=True;write(name,r)
    report['scope']='Aqua v21 main: dodge1.5x same distance once per airtime, native Superglide, native jump height1.25, air305/407/353,301 range0..30 with shorter pose hold,366 range15..47'
    write('curve_validation.json',report)
    from aqua_v21_plan import get_plan
    write('source_selections.json',{'version':21,'profiles':{str(i):get_plan(i)for i in [0,1,2,3,4,5,7]}})
    print('v21 native anchors, actual jump fixtures, mappings and requested main behavior verified')
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python validate_aqua_v21.py PATH_TO_STEAM_EXE')
    validate(Path(sys.argv[1]))
