/* Main-only native Guard. A unique pool object supplies a wider body-centered
 * capsule; the normal native clash/deflection policy still decides contacts. */
typedef uptr (ABI *GuardRowFn)(uptr,u32);
typedef uptr (ABI *MotionAdvanceFn)(uptr,float);
typedef int (ABI *GuardAngleFn)(uptr,uptr);
typedef int (ABI *GuardPoolFn)(uptr);
static GuardRowFn guard_row_original;
static MotionAdvanceFn guard_motion_original;
static GuardAngleFn guard_angle_original;
static GuardPoolFn guard_pool_original;
static int guard_attempted,guard_ready;
static uptr guard_actor,guard_array,guard_shield;
static u32 guard_notes,guard_shield_notes,guard_owner_handle,guard_data_handle,guard_mask;
static int guard_seen;static u32 guard_wait;
static float guard_elapsed,guard_parry_elapsed,guard_last_clock;
static u8 guard_data[0x70] __attribute__((aligned(16)));
static const u8 guard_row_prefix[15]={0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x6c,0x24,0x10,0x48,0x89,0x74,0x24,0x18};
static const u8 guard_motion_prefix[15]={0x40,0x55,0x57,0x48,0x8d,0x6c,0x24,0xe8,0x48,0x81,0xec,0x18,0x01,0,0};
static const u8 guard_angle_prefix[15]={0x4c,0x8b,0xdc,0x49,0x89,0x5b,0x20,0x57,0x48,0x81,0xec,0xa0,0,0,0};
static const u8 guard_pool_prefix[15]={0x48,0x89,0x6c,0x24,0x10,0x48,0x89,0x74,0x24,0x18,0x57,0x41,0x56,0x41,0x57};
static int guard_pool_slot(uptr p){return p>=base+0x2db4710u&&p<base+0x2db7710u&&(p-base-0x2db4710u)%0xc0u==0;}
static int guard_owns_shield(void){
    return guard_shield&&guard_pool_slot(guard_shield)&&(r32(guard_shield)&0x800u)
        &&r32(guard_shield+0x34)==guard_owner_handle&&r32(guard_shield+0x5c)==guard_data_handle
        &&r32(guard_shield+0x54)==guard_mask;
}
static void guard_retire(void){
    if(guard_owns_shield()){
        typedef void (ABI *FreeFn)(uptr);((FreeFn)(base+0x2b3560u))(guard_shield);
    }
    guard_shield=0;guard_mask=0;
}
static void guard_clear(void){
    guard_retire();guard_actor=guard_array=0;guard_seen=0;guard_wait=0;
    guard_elapsed=guard_parry_elapsed=guard_last_clock=0.f;
}
static int guard_main_scope(uptr actor){
    return actor&&guard_ready&&!magic_conflict&&!remove_mode&&cache_choice==1&&air_requested_choice==1
        &&actor==cache_actor&&actor==r64(base+SORA_RVA)&&memory(actor,0x448,0)
        &&(r32(actor+0x374)&3u)==1u&&decode(r32(actor+0x1d4))==cache_array
        &&!r32(base+0x298c9a0u)&&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
static int guard_live(uptr actor){
    if(actor!=guard_actor||cache_array!=guard_array||!guard_main_scope(actor)||r32(actor+0x70)!=0u
        ||!guard_seen||guard_elapsed>=168.f)return 0;
    u32 request=r32(actor+0x164)&0xffffu;float clock=air_float(actor+0x16c);
    if(!air_finite(clock)||clock<0.f)return 0;
    if(request==0xd4u)return clock<54.f;
    if(request==0x6eu||request==0x6fu)return guard_parry_elapsed<12.f;
    /* Only a completed Guard receives a twelve native-tick release grace.
     * Walking, damage, attacks, magic, scripts and any new queue cancel it. */
    return request==0u&&!r32(actor+0x178)&&guard_last_clock>=52.5f&&guard_elapsed<168.f;
}
static void guard_observe(uptr actor){
    if(!guard_actor||actor!=guard_actor)return;
    if(!guard_main_scope(actor)||guard_array!=cache_array){guard_clear();return;}
    u32 request=r32(actor+0x164)&0xffffu;
    if(guard_seen&&r32(actor+0x178)){
        u32 next=r32(actor+0x17c)&0xffffu;
        if(r32(actor+0x178)!=1u||(next!=0xd4u&&next!=0x6eu&&next!=0x6fu)){guard_clear();return;}
    }
    if(request==0xd4u){
        guard_seen=1;guard_wait=0;guard_last_clock=air_float(actor+0x16c);
        if(!guard_live(actor))guard_clear();return;
    }
    if(!guard_seen){
        if(r32(actor+0x178)!=1u||(r32(actor+0x17c)&0xffffu)!=0xd4u||++guard_wait>16u)guard_clear();
    }else if(!guard_live(actor))guard_clear();
}
static void guard_shield_refresh(void){
    if(!guard_live(guard_actor)){guard_retire();return;}
    if(!guard_owns_shield()){
        guard_shield=0;
        uptr template=0;unsigned free_slots=0;
        for(unsigned i=0;i<64u;i++){
            uptr p=base+0x2db4710u+i*0xc0u;u32 flags=r32(p);
            if(!(flags&0x800u)){free_slots++;continue;}
            u32 cls=flags&0xe0000u;
            if((flags&0x200000u)||decode(r32(p+0x34))!=guard_actor||(cls!=0x80000u&&cls!=0x40000u))continue;
            uptr data=decode(r32(p+0x5c));if(data!=(uptr)guard_data&&memory(data,sizeof(guard_data),0))template=data;
        }
        if(!template||!free_slots)return;
        copy(guard_data,(void*)template,sizeof(guard_data));
        *(u32*)(guard_data+0x10)=0xffffffffu; /* manual world-space capsule */
        air_write_float((uptr)guard_data+0x60,0.f);air_write_float((uptr)guard_data+0x64,-1.01f);
        typedef u32 (ABI *HandleFn)(const void*);typedef u32 (ABI *MaskFn)(void);
        typedef uptr (ABI *CreateFn)(uptr,u32,const void*);
        u32 h=((HandleFn)(base+HANDLE_RVA))(guard_data),owner=((HandleFn)(base+HANDLE_RVA))((void*)guard_actor);
        u32 mask=((MaskFn)(base+0x2b3760u))();
        if(!h||!owner||!mask||decode(h)!=(uptr)guard_data||decode(owner)!=guard_actor)return;
        uptr p=((CreateFn)(base+0x2b3270u))(guard_actor,mask,guard_data);
        if(!guard_pool_slot(p)||decode(r32(p+0x34))!=guard_actor||r32(p+0x5c)!=h)return;
        guard_shield=p;guard_data_handle=h;guard_owner_handle=owner;guard_mask=mask;
        *(u32*)p=(r32(p)&0xffe1fdf0u)|0x8000cu;
        *(u32*)(p+0x68)=100u;*(u32*)(p+0x2c)=0u;*(u32*)(p+0x30)=r32(p+0x30)&~0x1fu;
        air_write_float(p+0x50,10.f);
        if(guard_shield_notes++<12u)log_text("AQUA GUARD SHIELD: wider body capsule radius50, full-angle native deflection, release/parry grace12 ticks");
    }
    if(!guard_owns_shield())return;
    float x=air_float(guard_actor+0x10),y=air_float(guard_actor+0x14),z=air_float(guard_actor+0x18);
    if(!air_finite(x)||!air_finite(y)||!air_finite(z)){guard_clear();return;}
    /* Native KH1 Y increases downward. Cover the torso and head, with a
     * fifty-unit radius reaching around both shoulders and behind Sora. */
    float lower[4]={x,y-35.f,z,1.f},upper[4]={x,y-85.f,z,1.f};
    copy((void*)(guard_shield+0x10),lower,16);copy((void*)(guard_shield+0x70),lower,16);
    copy((void*)(guard_shield+0x40),upper,16);copy((void*)(guard_shield+0x80),upper,16);
    air_write_float(guard_shield+0x0c,50.f);air_write_float(guard_shield+0x3c,50.f);
    *(u32*)guard_shield=(r32(guard_shield)|0x200u)&~0x200000u; /* native rearm, no automatic bone transform */
}
static uptr ABI guard_row(uptr actor,u32 row){
    int watch=guard_main_scope(actor)&&row==0x3du;
    if(actor==guard_actor&&row==0x3du)guard_clear();
    uptr result=guard_row_original(actor,row);
    if(watch&&guard_main_scope(actor)&&((r32(actor+0x164)&0xffffu)==0xd4u
        ||(r32(actor+0x178)==1u&&(r32(actor+0x17c)&0xffffu)==0xd4u))){
        guard_actor=actor;guard_array=cache_array;guard_seen=(r32(actor+0x164)&0xffffu)==0xd4u;guard_wait=0;
        if(guard_notes++<24u)log_text("AQUA MAIN GUARD: row3D witnessed; source30fps forward/reverse; body shield plus12 native-tick grace");
    }
    else if(actor==guard_actor)guard_observe(actor);
    return result;
}
static uptr ABI guard_motion(uptr actor,float delta){
    guard_observe(actor);
    if(guard_main_scope(actor)&&air_finite(delta)&&delta>=0.f&&delta<=4.f){
        u32 request=r32(actor+0x164)&0xffffu;
        if(guard_actor==actor){
            guard_elapsed+=delta;
            if(request==0x6eu||request==0x6fu)guard_parry_elapsed+=delta;
        }
        if((guard_live(actor)&&request==0xd4u)||(guard_actor==actor&&!guard_seen&&r32(actor+0x178)==1u&&(r32(actor+0x17c)&0xffffu)==0xd4u))delta*=53.f/156.f;
        else if(air_dodge_active&&!air_pending&&air_actor==actor&&request==6u&&r32(actor+0x70)==2u){
            float clock=air_float(actor+0x16c);delta*=air_rate;
            /* Keep the final pose until the collision callback has supplied
             * its last bounded displacement, independent of callback order. */
            if(air_rate>1.f&&air_finite(clock)&&air_elapsed<air_duration()&&clock+delta>=39.f){
                float room=38.999f-clock;delta=room>0.f?room:0.f;
            }
        }
        else if(request==0xc9u||request==0xcau){
            float clock=air_float(actor+0x16c),rate=request==0xc9u?1.f:1.4f;
            float finish=request==0xc9u?24.f:33.6f;
            if(air_finite(clock)&&clock>=0.f){
                if(clock>=finish)delta*=rate*2.f;
                else if(clock+delta*rate>finish)delta=(finish-clock)+(delta-(finish-clock)/rate)*rate*2.f;
                else delta*=rate;
            }
        }
        else if(request==0xcbu)delta*=47.f/32.f;
    }
    return guard_motion_original(actor,delta);
}
static int ABI guard_pool(uptr work){
    if(guard_actor){guard_observe(guard_actor);guard_shield_refresh();}
    return guard_pool_original(work);
}
static int ABI guard_angle(uptr first,uptr second){
    /* Unrelated global clash pairs cost no VirtualQuery or actor validation. */
    if(guard_actor&&guard_pool_slot(first)&&(r32(first)&0x200800u)==0x800u
        &&decode(r32(first+0x34))==guard_actor
        &&(((r32(first)&0xe0000u)-0x20000u)&0xfff9ffffu)==0u
        &&guard_live(guard_actor))return 1;
    return guard_angle_original(first,second);
}
static void guard_install(void){
    if(guard_attempted||remove_mode)return;guard_attempted=1;
    uptr addresses[4]={base+0x2a3980u,base+0x29f0a0u,base+0x2b4640u,base+0x2b47a0u};
    const u8*prefixes[4]={guard_row_prefix,guard_motion_prefix,guard_angle_prefix,guard_pool_prefix};
    static const u8 create_prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
    static const u8 free_prefix[11]={0x48,0x83,0xec,0x28,0x83,0xb9,0xb4,0,0,0,0};
    static const u8 mask_prefix[8]={0x8b,0x15,0xaa,0x3f,0xb0,0x02,0x33,0xc9};
    for(unsigned i=0;i<4;i++)if(!memory(addresses[i],15,0)||!equal((void*)addresses[i],prefixes[i],15)){
        log_text("AQUA GUARD CONTROLLER UNAVAILABLE: native row/motion/angle/pool anchors did not match");return;
    }
    if(!memory(base+0x2db4710u,0x3004,1)||!memory(base+0x2b3270u,13,0)||!equal((void*)(base+0x2b3270u),create_prefix,13)
        ||!memory(base+0x2b3560u,11,0)||!equal((void*)(base+0x2b3560u),free_prefix,11)
        ||!memory(base+0x2b3760u,8,0)||!equal((void*)(base+0x2b3760u),mask_prefix,8)){
        log_text("AQUA GUARD CONTROLLER UNAVAILABLE: native shield allocator anchors did not match");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    for(unsigned i=0;i<4;i++){copy(page+i*64,prefixes[i],15);magic_jump(page+i*64+15,addresses[i]+15);}
    u32 old_page,old[4],unused;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,256);
    unsigned protected=0;
    for(;protected<4;protected++)if(!kVirtualProtect((void*)addresses[protected],15,0x40u,old+protected))break;
    if(protected<4){
        while(protected){protected--;kVirtualProtect((void*)addresses[protected],15,old[protected],&unused);}
        kVirtualFree(page,0,0x8000u);return;
    }
    guard_row_original=(GuardRowFn)(uptr)page;guard_motion_original=(MotionAdvanceFn)(uptr)(page+64);
    guard_angle_original=(GuardAngleFn)(uptr)(page+128);guard_pool_original=(GuardPoolFn)(uptr)(page+192);
    uptr callbacks[4]={(uptr)guard_row,(uptr)guard_motion,(uptr)guard_angle,(uptr)guard_pool};
    for(unsigned i=0;i<4;i++){
        u8 code[15];code[14]=0x90;magic_jump(code,callbacks[i]);copy((void*)addresses[i],code,15);
        kFlushInstructionCache((uptr)-1,(void*)addresses[i],15);kVirtualProtect((void*)addresses[i],15,old[i],&unused);
    }
    guard_ready=motion_rate_ready=1;log_text("AQUA MAIN GUARD READY: native pool body shield, all angles, bounded parry/release grace, source30fps motion rate");
}
