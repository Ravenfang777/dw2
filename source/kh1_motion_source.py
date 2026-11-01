"""Bounded KH1 model/motion reader for offline retarget calibration.

Native constraint semantics follow the user's v52 native_mset.rs reference.
All source bytes are supplied separately; this module embeds no game assets.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import struct
import numpy as np
from scipy.spatial.transform import Rotation


def u32(data, at):
    if at < 0 or at+4 > len(data): raise ValueError('Truncated KH1 word')
    return struct.unpack_from('<I', data, at)[0]


def vec(data, at):
    result = np.array(struct.unpack_from('<3f',data,at), dtype=float)
    if not np.isfinite(result).all(): raise ValueError('Non-finite KH1 vector')
    return result


def matrix(local):
    result = np.eye(4)
    result[:3,:3] = Rotation.from_euler('xyz',local[3:6]).as_matrix() @ np.diag(local[:3])
    result[:3,3] = local[6:9]
    return result


def matrices(local):
    result=np.repeat(np.eye(4)[None],len(local),axis=0)
    result[:,:3,:3]=Rotation.from_euler('xyz',local[:,3:6]).as_matrix()*local[:,None,:3]
    result[:,:3,3]=local[:,6:9]
    return result


def normalized(v):
    norm = np.linalg.norm(v)
    if not np.isfinite(norm) or norm < 1e-8: raise ValueError('Degenerate native direction')
    return v/norm


def unscaled(m):
    result = m.copy()
    for i in range(3): result[:3,i] = normalized(result[:3,i])
    return result


@dataclass
class Model:
    parents: list[int]
    local: np.ndarray
    bind: np.ndarray


def read_model(data):
    mobj = u32(data,4)
    header = mobj+u32(data,mobj+32)
    count = u32(data,header)
    table = header+u32(data,header+4)
    if not 0 < count <= 1024 or table+count*48 > len(data): raise ValueError('Invalid KH1 bone table')
    parents, locals_, bind = [], [], []
    for index in range(count):
        at = table+48*index
        if u32(data,at+12) != index: raise ValueError('Unexpected KH1 bone index')
        parent = u32(data,at+44)&1023
        if parent == 1023: parent = -1
        if parent < -1 or parent >= index: raise ValueError('Invalid KH1 hierarchy')
        local = np.concatenate([vec(data,at),vec(data,at+16),vec(data,at+32)])
        if np.any(np.abs(local[:3])<1e-6): raise ValueError('Singular KH1 bone')
        parents.append(parent); locals_.append(local)
        m = matrix(local)
        bind.append(m if parent<0 else bind[parent]@m)
    return Model(parents,np.array(locals_),np.array(bind))


@dataclass
class Channel:
    bone: int
    kind: int
    before: int
    after: int
    first: int
    keys: np.ndarray

    def sample(self,frame):
        tick = math.trunc(frame*256)
        a,b = self.keys[0],self.keys[-1]
        if len(self.keys)==1: return float(a[1])
        first,last = a[0],b[0]
        if tick <= first:
            if self.before==0: return float(a[1])
            if self.before==1:
                nxt=self.keys[1]
                slope=(nxt[1]-a[1])/(nxt[0]-first) if int(a[4])==1 and nxt[0]!=first else a[2]
                return float(a[1]+(tick-first)*slope)
            if self.before==2 and tick<first: tick=first+(tick-first)%(last-first)
        if tick >= last:
            if self.after==0: return float(b[1])
            if self.after==1:
                prev=self.keys[-2]
                slope=(b[1]-prev[1])/(last-prev[0]) if int(b[4])==1 and last!=prev[0] else b[3]
                return float(b[1]+(tick-last)*slope)
            if self.after==2 and tick>last: tick=last-(last-tick)%(last-first)
        lo,hi=0,len(self.keys)-1
        while hi-lo>=2:
            mid=(lo+hi)//2
            if self.keys[mid,0]==tick: return float(self.keys[mid,1])
            if self.keys[mid,0]<tick:lo=mid
            else:hi=mid
        a,b=self.keys[hi-1],self.keys[hi]
        if int(a[4])==0:return float(a[1])
        gap=b[0]-a[0]
        if gap<=0:raise ValueError('Degenerate native key interval')
        t=(tick-a[0])/gap
        if int(a[4])==1:return float(a[1]+(b[1]-a[1])*t)
        return float((2*t**3-3*t*t+1)*a[1]+(-2*t**3+3*t*t)*b[1]
                     +gap*((t**3-2*t*t+t)*a[3]+(t**3-t*t)*b[2]))


def parse_channels(data,count_at,offset_at,key_at,bone_count):
    count,offset,key_offset=u32(data,count_at),u32(data,offset_at),u32(data,key_at)
    if count>4096 or offset+count*6>len(data):raise ValueError('Invalid native channel table')
    result=[]
    for i in range(count):
        bone,packed,n,first=struct.unpack_from('<HBBH',data,offset+i*6)
        kind=packed&15
        if bone>=bone_count or not 1<=kind<=9 or not n or key_offset+(first+n)*16>len(data):
            raise ValueError('Invalid native key references')
        keys=[]
        for k in range(first,first+n):
            head,value,out_,in_=struct.unpack_from('<ifff',data,key_offset+k*16)
            keys.append([head>>8,value,out_,in_,head&255])
        keys=np.array(keys)
        if not np.isfinite(keys).all() or np.any(np.diff(keys[:,0])<0):raise ValueError('Invalid native keys')
        result.append(Channel(bone,kind,(packed>>4)&3,packed>>6,first,keys))
    return result


@dataclass
class Motion:
    raw: bytes
    frames: int
    fps: float
    flags: np.ndarray
    constants: list
    channels: list[Channel]
    helper_local: np.ndarray
    helper_parents: list[int]
    helper_channels: list[Channel]


def parse_motion(data):
    if len(data)<80:raise ValueError('Truncated native motion')
    frames=u32(data,4);fps=struct.unpack_from('<f',data,8)[0];bones=u32(data,16)
    if not 0<frames<=36000 or not 1<=fps<=240 or not 0<bones<=1024:raise ValueError('Bad native duration/rig')
    flags_at=u32(data,20)
    if flags_at+bones*4>len(data):raise ValueError('Invalid native flags')
    flags=np.array(struct.unpack_from('<'+'I'*bones,data,flags_at),dtype=np.uint32)
    n,at=u32(data,44),u32(data,48)
    if not 0<n<=1024 or at+n*40>len(data):raise ValueError('Bad native helper table')
    helpers,parents=[],[]
    for i in range(n):
        p=at+i*40
        parent=struct.unpack_from('<i',data,p+12)[0]
        if parent>=i or parent < -1:raise ValueError('Bad helper parent')
        helpers.append(np.concatenate([vec(data,p),vec(data,p+16),vec(data,p+28)]));parents.append(parent)
    constants=[];n,at=u32(data,52),u32(data,56)
    if n>16384 or at+n*8>len(data):raise ValueError('Bad constant table')
    for i in range(n):
        bone,kind,value=struct.unpack_from('<HHf',data,at+i*8)
        if bone>=bones or not 1<=kind<=9 or not math.isfinite(value):raise ValueError('Bad native constant')
        constants.append((bone,kind,value))
    channels=parse_channels(data,24,28,40,bones)
    helper_channels=parse_channels(data,32,36,40,len(helpers))
    return Motion(data,frames,fps,flags,constants,channels,np.array(helpers),parents,helper_channels)


def read_mset(data):
    count=u32(data,0)
    if not 0<count<=64:raise ValueError('Bad MSET section count')
    sections=[u32(data,4+i*4) for i in range(count)]
    for start in sections:
        if start>=len(data):continue
        end=min([v for v in sections if start<v<=len(data)]+[len(data)])
        at=start
        for _ in range(1024):
            if at+8>end:break
            next_=at+8+u32(data,at+4)
            if next_<=at or next_>end:break
            if data[at:at+4]==b'MMTN':
                bank=data[at:next_];offsets=[]
                for i in range(4096):
                    off=u32(bank,64+i*4)
                    if off==0xffffffff:break
                    offsets.append(None if off==0 else 64+off)
                else:raise ValueError('Unterminated native bank')
                table_end=64+4*(len(offsets)+1)
                motions=[]
                for off in offsets:
                    if off is None:motions.append(None);continue
                    if off<table_end or off>=len(bank):raise ValueError('Bad native motion offset')
                    stop=min([v for v in offsets if v is not None and v>off]+[len(bank)])
                    motions.append(parse_motion(bank[off:stop]))
                return {'start':at,'end':next_,'bank':bank,'motions':motions,'offsets':offsets,'sections':sections}
            at=next_
    raise ValueError('No bounded MMTN chunk')


def apply(channels,local,frame):
    for channel in channels:
        value=channel.sample(frame)
        if 4<=channel.kind<=6 and abs(value)>math.pi:value=(value+math.pi)%(2*math.pi)-math.pi
        local[channel.bone,channel.kind-1]=value


def limb(goal,start,a,b,arm,rolls,pole):
    delta=goal-start;x=normalized(delta)
    if pole is not None:
        z=normalized(np.cross(x,normalized(pole-start)));y=normalized(np.cross(z,x))
    else:
        y=normalized(np.array([-x[1],x[0],0.]));z=normalized(np.cross(x,y))
    basis=np.eye(4);basis[:3,:3]=np.stack([x,y,z],axis=1)
    rx=np.eye(4);rx[:3,:3]=Rotation.from_euler('x',rolls[0]).as_matrix();basis=basis@rx
    if b==0:basis[:3,3]=start;return basis,None
    c=np.clip((delta@delta-a*a-b*b)/(2*a*b),-1.,1.);s=math.sqrt(max(0.,1-c*c))*(-1 if arm else 1)
    mid=np.eye(4);mid[:2,:2]=[[c,-s],[s,c]];mid[0,3]=a
    rx[:3,:3]=Rotation.from_euler('x',rolls[1]).as_matrix();mid=mid@rx
    alignment=normalized(np.array([a+c*b,-s*b,0.]));turn=np.eye(4)
    turn[:2,:2]=[[alignment[0],-alignment[1]],[alignment[1],alignment[0]]]
    first=basis@turn;first[:3,3]=start
    return first,mid


def helper_pose(motion,frame):
    helper_local=motion.helper_local.copy();apply(motion.helper_channels,helper_local,frame)
    transforms=matrices(helper_local)
    helpers=np.repeat(np.eye(4)[None],len(helper_local),axis=0)
    for i in range(1,len(helpers)):
        helpers[i]=helpers[motion.helper_parents[i]]@transforms[i]
    if not np.isfinite(helpers).all():raise ValueError('Non-finite native helper pose')
    return helpers


def pose(model,motion,frame):
    local=model.local.copy()
    for bone,kind,value in motion.constants:local[bone,kind-1]=value
    rt_local=local.copy();rt_local[:,:3]=1.
    static_rt=matrices(rt_local)
    apply(motion.channels,local,frame)
    rt_local=local.copy();rt_local[:,:3]=1.
    animated_rt=matrices(rt_local)
    helpers=helper_pose(motion,frame)
    bones=np.repeat(np.eye(4)[None],len(local),axis=0);orientation=bones.copy();accum=local[:,:3].copy()
    def helper(index):
        if not 0<index<=len(helpers):raise ValueError('Invalid helper reference')
        return helpers[index-1]
    rtarget=lambda f:((f&0x7fc)|((f>>16)&0x800))>>2
    ptarget=lambda f:((f&0xff800)|((f>>8)&0x100000))>>11
    i=0
    while i<len(local):
        f=int(motion.flags[i])
        if f&(1<<26):i+=1;continue
        parent=model.parents[i];parent_m=np.eye(4) if parent<0 else bones[parent]
        parent_r=np.eye(4) if parent<0 else orientation[parent]
        accum[i]=local[i,:3] if parent<0 else accum[parent]*local[i,:3]
        mode=(f>>21)&3;r=rtarget(f);t=ptarget(f)
        if mode or f&3==1:inv=np.linalg.inv(parent_m)
        if mode:
            end=i+(1 if mode==1 else 2)
            goal=(inv@helper(ptarget(int(motion.flags[end]))))[:3,3]
            pole=(inv@helper(r))[:3,3] if f&3==3 else None
            a=model.local[i+1,6]*local[i,0]
            b=0 if mode==1 else model.local[end,6]*local[i,0]*local[i+1,0]
            first,second=limb(goal,local[i,6:9],a,b,mode==3,[local[i,3],local[i+1,3]],pole)
            scaled=first.copy();scaled[:3,:3]*=local[i,:3]
            bones[i]=parent_m@scaled;bones[i,:3,3]=(parent_m@np.r_[local[i,6:9],1])[:3]
            orientation[i]=unscaled(bones[i]);orientation[i,:3,3]=0
            bones[i+1,:3,3]=(bones[i]@np.r_[model.local[i+1,6:9],1])[:3]
            if second is not None:
                second=np.diag(np.r_[1/local[i,:3],1])@second
                accum[i+1]=local[i,:3]*local[i+1,:3];second[:3,:3]*=accum[i+1]
                bones[i+1]=bones[i]@second
                bones[i+1,:3,3]=(bones[i]@np.r_[model.local[i+1,6:9],1])[:3]
                orientation[i+1]=unscaled(bones[i+1]);orientation[i+1,:3,3]=0
                bones[end,:3,3]=(bones[i+1]@np.r_[model.local[end,6:9],1])[:3]
                i+=1
            i+=1;continue
        if f&(1<<23):position=bones[i,:3,3].copy()
        elif t:position=helper(t)[:3,3].copy()
        else:position=(parent_m@np.r_[local[i,6:9],1])[:3]
        if f&3==0:
            rt=static_rt[i].copy() if f&(1<<25) and not f&(1<<24) else animated_rt[i]
            current=rt if f&(1<<24) else parent_r@rt
        elif f&3==1:
            goal=(inv@helper(r))[:3,3]
            start=local[i,6:9] if not (f&(1<<23) or t) else (inv@np.r_[position,1])[:3]
            x=normalized(goal-start);z=normalized(np.cross(x,[0.,1.,0.]));y=normalized(np.cross(z,x))
            rt=np.eye(4);rt[:3,:3]=np.stack([x,y,z],axis=1)
            rx=np.eye(4);rx[:3,:3]=Rotation.from_euler('x',local[i,3]).as_matrix();rt=rt@rx
            current=parent_r@rt
        elif f&3==2:current=unscaled(helper(r))
        else:raise ValueError('Unsupported native pole mode')
        bones[i]=current;bones[i,:3,:3]*=accum[i];bones[i,:3,3]=position
        orientation[i]=current.copy();orientation[i,:3,3]=0
        i+=1
    if not np.isfinite(bones).all():raise ValueError('Non-finite native pose')
    return bones
