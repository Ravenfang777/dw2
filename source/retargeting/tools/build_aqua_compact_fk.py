"""Fit full Aqua FK poses into each original KH1 motion's existing capacity.

All motion headers, lengths, bone/helper counts and allocations stay original.
Body flags, constants, body channel descriptors and body-owned key records are
reused. The eleven helper slots, hierarchy and travel tracks survive. Unused helper
channels are neutralized and their key capacity is reused for the FK body.
"""
from pathlib import Path
import json,math,struct,sys,warnings
import numpy as np
from scipy.spatial.transform import Rotation,Slerp
from bbs_source_inspector import read_pam,read_pmo_skeleton
from aqua_retarget_math import Retarget,MAPPING,rotation
from kh1_motion_source import read_model,read_mset,parse_motion,pose,helper_pose,u32,matrices

ROOT=Path(__file__).resolve().parents[1]
PLAN=[('ground first',0xc8,'300'),('ground second',0xc9,'301'),
      ('ground alternate',0xca,'302'),('ground finisher',0xcb,'304'),
      ('air first',0xcc,'305'),('air second',0xcd,'306'),
      ('air finisher',0xce,'309'),('Guard / Barrier pose',0xd4,'400'),
      ('Dodge Roll / Cartwheel pose',0xdc,'009')]
ROLES={1:0,33:3,2:77,3:78,4:147,5:151,14:92,15:93,16:94,17:95,
       24:197,25:198,26:199,27:200,47:17,48:18,49:19,50:23,
       41:43,42:44,43:45,44:49}

def continuous_eulers(matrices_):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        angles=Rotation.from_matrix(matrices_).as_euler('xyz')
    result=[]
    for xyz in angles:
        if result:
            alternatives=np.array([xyz,[xyz[0]+math.pi,math.pi-xyz[1],xyz[2]+math.pi]])
            alternatives+=np.round((result[-1]-alternatives)/(2*math.pi))*(2*math.pi)
            xyz=alternatives[np.argmin(np.sum((alternatives-result[-1])**2,axis=1))]
        result.append(xyz)
    return np.array(result)

def fit(times,values,knots):
    result=np.empty(len(times));incoming=np.zeros(len(knots));outgoing=np.zeros(len(knots))
    for index,(a,b) in enumerate(zip(knots,knots[1:])):
        gap=times[b]-times[a];t=(times[a:b+1]-times[a])/gap
        base=(2*t**3-3*t*t+1)*values[a]+(-2*t**3+3*t*t)*values[b]
        basis=np.column_stack([gap*(t**3-2*t*t+t),gap*(t**3-t*t)])
        slopes=np.linalg.lstsq(basis,values[a:b+1]-base,rcond=None)[0] if b-a>1 else np.repeat((values[b]-values[a])/gap,2)
        result[a:b+1]=base+basis@slopes
        outgoing[index]=slopes[0];incoming[index+1]=slopes[1]
    incoming[0]=outgoing[0];outgoing[-1]=incoming[-1]
    return result,incoming,outgoing

def compact(model,native,animation,calibration):
    times=np.linspace(0,native.frames-1,(native.frames-1)*8+1)
    cache=ROOT/'ability_v6/sampling_cache'/f'{animation.name}_{native.frames}_v1.npz'
    if cache.exists():
        cached=np.load(cache);values=cached['values'];expected=cached['expected']
    else:
        locals_=[];expected=[]
        for f in times:
            t=float(f)/(native.frames-1);edge=float(np.clip(min(t,1-t)/.12,0,1));w=edge*edge*(3-2*edge)
            original=pose(model,native,float(f));travel=helper_pose(native,float(f))[-1,:3,3]
            donor_local,donor=calibration.sample(animation,t*(animation.frame_count-1),not 305<=int(animation.name)<=309)
            # Blend semantic source rotations toward the native start/end pose.
            # All duplicate/corrective target joints retain one coherent source
            # role; independent IK parents cannot introduce a second torso turn.
            source_pose=calibration.source_bind.copy()
            for source_i,target_i in ROLES.items():
                wanted=rotation(donor[target_i])@calibration.target_rotation[target_i].T@calibration.source_rotation[source_i]
                native_r=rotation(original[target_i])@calibration.target_rotation[target_i].T@calibration.source_rotation[source_i]
                source_pose[source_i,:3,:3]=Slerp([0,1],Rotation.from_matrix(np.array([native_r,wanted])))(w).as_matrix()
            local,body=calibration.from_world(source_pose)
            root=donor_local[0,6:9].copy()+travel
            local[0,6:9]=original[0,:3,3]*(1-w)+root*w
            # from_world already calculated local joint rotations/lengths. Root
            # translation is adjusted separately to retain native actor travel.
            transform=matrices(local);world=np.empty_like(body)
            for i,parent in enumerate(model.parents):world[i]=transform[i] if parent<0 else world[parent]@transform[i]
            locals_.append(local);expected.append(world)
        values=np.array(locals_);expected=np.array(expected)
        for bone in range(len(model.parents)):
            values[:,bone,3:6]=continuous_eulers(Rotation.from_euler('xyz',values[:,bone,3:6]).as_matrix())
        cache.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(cache,values=values,expected=expected)
    dynamic=[tuple(x) for x in np.argwhere(np.ptp(values,axis=0)>1e-5)]
    static=[(int(b),int(a),float(values[0,b,a])) for b,a in np.argwhere(np.max(np.abs(values-model.local),axis=0)>1e-5) if (b,a) not in dynamic]
    # The FK body no longer refers to limb helpers. Retain the travel helper
    # and every ancestor exactly; neutralize only unused helper channels and
    # reuse their key space, with all original counts/allocations unchanged.
    body_keys={k for c in native.channels for k in range(c.first,c.first+len(c.keys))}
    helper_keys={k for c in native.helper_channels for k in range(c.first,c.first+len(c.keys))}
    assert not body_keys&helper_keys
    root_ancestors=set();parent=len(native.helper_local)-1
    while parent>=0:root_ancestors.add(parent);parent=native.helper_parents[parent]
    protected={k for c in native.helper_channels if c.bone in root_ancestors for k in range(c.first,c.first+len(c.keys))}
    total_keys=max(body_keys|helper_keys)+1
    pool=sorted(set(range(total_keys))-protected);constant_count=len(native.constants)
    constants=static[:constant_count];static_curves=static[constant_count:]
    required_channels=len(dynamic)+len(static_curves)
    if required_channels>len(native.channels):raise ValueError(('Native channel capacity',required_channels,len(native.channels)))
    knots=[[0,len(times)-1] for _ in dynamic]
    # A small margin allows each curve to fit inside a contiguous body-key
    # run; the original helper keys split that capacity into separate ranges.
    budget=len(pool)-len(static_curves)-1-8
    tolerances=[.0075 if 3<=a<=5 else .20 for b,a in dynamic]
    def error(index):
        b,a=dynamic[index];v=values[:,b,a]
        e=np.abs(fit(times,v,knots[index])[0]-v)/tolerances[index]
        e[knots[index]]=0;at=int(np.argmax(e));return float(e[at]),at
    errors=[error(i) for i in range(len(dynamic))]
    used=sum(map(len,knots))
    while used<budget:
        best=max(range(len(errors)),key=lambda i:errors[i][0])
        if errors[best][0]<=1:break
        if len(knots[best])>=255:raise ValueError('Curve exceeds 255 native keys')
        knots[best]=sorted(knots[best]+[errors[best][1]]);used+=1;errors[best]=error(best)
    raw=bytearray(native.raw);key_at=u32(raw,40);constant_at=u32(raw,56);channel_at=u32(raw,28);flag_at=u32(raw,20)
    raw[flag_at:flag_at+len(model.parents)*4]=bytes(len(model.parents)*4)
    while len(constants)<constant_count:constants.append((0,0,1.))
    for i,(b,a,v) in enumerate(sorted(constants)):
        struct.pack_into('<HHf',raw,constant_at+i*8,b,a+1,v)
    runs=[]
    for k in pool:
        if runs and runs[-1][0]+runs[-1][1]==k:runs[-1][1]+=1
        else:runs.append([k,1])
    cursor=0;channels=[]
    def write_keys(entries):
        nonlocal cursor
        size=len(entries);choices=[i for i,r in enumerate(runs) if r[1]>=size]
        if not choices:raise ValueError(('Contiguous native key capacity',size,runs))
        run=runs[min(choices,key=lambda i:runs[i][1])]
        selection=list(range(run[0],run[0]+size));run[0]+=size;run[1]-=size
        for k,(tick,v,incoming,outgoing) in zip(selection,entries):struct.pack_into('<Ifff',raw,key_at+k*16,(round(tick)<<8)|2,float(v),float(incoming),float(outgoing))
        cursor+=len(entries);return selection[0]
    for index in sorted(range(len(dynamic)),key=lambda i:-len(knots[i])):
        b,a=dynamic[index]
        _,incoming,outgoing=fit(times,values[:,b,a],knots[index])
        entries=[(times[k]*256,values[k,b,a],incoming[j]/256,outgoing[j]/256) for j,k in enumerate(knots[index])]
        first=write_keys(entries);channels.append((b,a+1,len(entries),first))
    for b,a,v in static_curves:channels.append((b,a+1,1,write_keys([(0,v,0.,0.)])))
    one=write_keys([(0,1.,0.,0.)])
    while len(channels)<len(native.channels):channels.append((0,1,1,one))
    for i,(b,kind,n,first) in enumerate(sorted(channels)):struct.pack_into('<HBBH',raw,channel_at+i*6,b,kind,n,first)
    helper_channel_at=u32(raw,36)
    for i,c in enumerate(native.helper_channels):
        if c.bone not in root_ancestors:struct.pack_into('<HBBH',raw,helper_channel_at+i*6,0,1,1,one)
    result=parse_motion(bytes(raw))
    assert len(raw)==len(native.raw) and raw[:80]==native.raw[:80]
    assert result.helper_parents==native.helper_parents and np.array_equal(result.helper_local,native.helper_local)
    assert all(np.array_equal(a.keys,b.keys) for a,b in zip(result.helper_channels,native.helper_channels) if b.bone in root_ancestors)
    allowed=set(range(flag_at,flag_at+len(model.parents)*4))|set(range(constant_at,constant_at+constant_count*8))|set(range(channel_at,channel_at+len(native.channels)*6))
    allowed.update(range(helper_channel_at,helper_channel_at+len(native.helper_channels)*6))
    allowed.update(j for k in pool for j in range(key_at+k*16,key_at+k*16+16))
    changed={i for i,(a,b) in enumerate(zip(native.raw,raw)) if a!=b};assert changed<=allowed
    worst_position=0.;worst_basis=0.;root_error=0.;length_error=0.;step=0.;previous=None;samples=0
    for index in range(0,len(times),2):
        f=float(times[index]);actual=pose(model,result,f)
        worst_position=max(worst_position,float(np.max(np.linalg.norm(actual[:,:3,3]-expected[index,:,:3,3],axis=1))))
        worst_basis=max(worst_basis,float(np.max(np.abs(actual[:,:3,:3]-expected[index,:,:3,:3]))))
        root_error=max(root_error,float(np.max(np.abs(helper_pose(result,f)[-1]-helper_pose(native,f)[-1]))))
        for b,parent in enumerate(model.parents):
            if parent>=0:length_error=max(length_error,abs(float(np.linalg.norm(actual[b,:3,3]-actual[parent,:3,3])-np.linalg.norm(expected[index,b,:3,3]-expected[index,parent,:3,3]))))
        if previous is not None:step=max(step,float(np.max(np.linalg.norm(actual[:,:3,3]-previous[:,:3,3],axis=1))))
        assert np.isfinite(actual).all() and np.max(np.abs(actual[:,:3,3]))<2000
        previous=actual;samples+=1
    if worst_position>5 or worst_basis>.12 or length_error>.01 or root_error>1e-7:
        print('Fit diagnostic',animation.name,'dynamic',len(dynamic),'static',len(static_curves),'keys',cursor,'normalized',max(e[0] for e in errors),
              'worst curves',sorted([(round(e[0],2),dynamic[i],len(knots[i])) for i,e in enumerate(errors)],reverse=True)[:8],flush=True)
        raise AssertionError(('Fit exceeds bounds',worst_position,worst_basis,length_error,root_error))
    return result,{'changed_bytes':len(changed),'dynamic_body_curves':len(dynamic),'static_body_curves':len(static_curves),
                   'original_body_channel_capacity':len(native.channels),'body_keys_used':cursor,'reusable_key_capacity':len(pool),
                   'max_normalized_curve_error':max(e[0] for e in errors),'max_pose_position_error':worst_position,
                   'max_pose_basis_error':worst_basis,'max_segment_length_error':length_error,
                   'max_quarter_frame_bone_step':step,'root_helper_error':root_error,'validated_pose_samples':samples}

def build(output):
    output.mkdir(parents=True,exist_ok=True);fixtures=output/'fixtures';fixtures.mkdir(exist_ok=True)
    p=ROOT/'sora_source/Custom Movesets KH1';model=read_model((p/'xa_ex_0010.mdls').read_bytes())
    assets=p if (p/'xa_ex_0010.mset').exists() else ROOT.parents[1]/'assets'
    data=(assets/'xa_ex_0010.mset').read_bytes();bank=read_mset(data)
    he=(assets/'xa_ex_0010_he.mset').read_bytes();heb=read_mset(he)
    source=read_pmo_skeleton((ROOT/'core_source/p02ex00.pmo').read_bytes())
    animations={a.name:a for a in read_pam((ROOT/'core_source/p02ex_001.pam').read_bytes(),54)}
    calibration=Retarget(source,model,pose(model,bank['motions'][1],0));records=[]
    for action,request,clip in PLAN:
        slot=u32(data,bank['sections'][1]+request*4)&4095;heslot=u32(he,heb['sections'][1]+request*4)&4095
        native=bank['motions'][slot];assert native.raw==heb['motions'][heslot].raw
        result,metrics=compact(model,native,animations[clip],calibration)
        (fixtures/f'original_{request:02X}.bin').write_bytes(native.raw);(fixtures/f'aqua_{request:02X}.bin').write_bytes(result.raw)
        records.append({'action':action,'request':request,'donor':clip,'normal_slot':slot,'olympus_slot':heslot,
                        'native_frames':native.frames,'motion_bytes':len(native.raw),**metrics})
        print(action,'keys',metrics['body_keys_used'],'/',metrics['reusable_key_capacity'],'position error',round(metrics['max_pose_position_error'],3),flush=True)
    report={'passed':True,'game_runtime_tested':False,'scope':'Compact FK body motion test in original native allocation',
            'file_growth':0,'headers_counts_helper_hierarchy_and_travel_tracks_unchanged':True,
            'native_action_logic_events_hitboxes_and_defense_windows_unchanged':True,
            'normal_and_olympus_records_identical':True,'motions':records}
    (output/'curve_validation.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':build(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'ability_v6')
