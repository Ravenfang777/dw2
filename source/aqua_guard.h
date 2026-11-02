/* Main-only Guard row witness, native actor-motion rate and facing cone.
 * No hurt/damage interception, actor position or animation-clock writes.
 */
typedef uptr (ABI *GuardRowFn)(uptr,u32);
typedef uptr (ABI *MotionAdvanceFn)(uptr,float);
typedef int (ABI *GuardAngleFn)(uptr,uptr);
static GuardRowFn guard_row_original;
static MotionAdvanceFn guard_motion_original;
static GuardAngleFn guard_angle_original;
static int guard_attempted,guard_ready;
static uptr guard_actor,guard_array;
static u32 guard_notes;
static int guard_seen;static u32 guard_wait;
static const u8 guard_row_prefix[15]={0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x6c,0x24,0x10,0x48,0x89,0x74,0x24,0x18};
static const u8 guard_motion_prefix[15]={0x40,0x55,0x57,0x48,0x8d,0x6c,0x24,0xe8,0x48,0x81,0xec,0x18,0x01,0,0};
static const u8 guard_angle_prefix[15]={0x4c,0x8b,0xdc,0x49,0x89,0x5b,0x20,0x57,0x48,0x81,0xec,0xa0,0,0,0};
static void guard_clear(void){guard_actor=guard_array=0;guard_seen=0;guard_wait=0;}
static int guard_main_scope(uptr actor){
    return guard_ready&&!magic_conflict&&!remove_mode&&cache_choice==1&&air_requested_choice==1
        &&actor==cache_actor&&actor==r64(base+SORA_RVA)&&memory(actor,0x448,0)
        &&(r32(actor+0x374)&3u)==1u&&decode(r32(actor+0x1d4))==cache_array
        &&!r32(base+0x298c9a0u)&&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
static int guard_live(uptr actor){
    if(actor!=guard_actor||cache_array!=guard_array||!guard_main_scope(actor)||r32(actor+0x70)!=0u
        ||(r32(actor+0x164)&0xffffu)!=0xd4u)return 0;
    float clock=air_float(actor+0x16c);
    return air_finite(clock)&&clock>=0.f&&clock<54.f;
}
static void guard_observe(uptr actor){
    if(!guard_actor||actor!=guard_actor)return;
    if(!guard_main_scope(actor)||guard_array!=cache_array){guard_clear();return;}
    if((r32(actor+0x164)&0xffffu)==0xd4u){guard_seen=1;guard_wait=0;return;}
    if(guard_seen||r32(actor+0x178)!=1u||(r32(actor+0x17c)&0xffffu)!=0xd4u||++guard_wait>16u)guard_clear();
}
static uptr ABI guard_row(uptr actor,u32 row){
    int watch=guard_main_scope(actor)&&row==0x3du;
    if(actor==guard_actor)guard_clear();
    uptr result=guard_row_original(actor,row);
    if(watch&&guard_main_scope(actor)&&((r32(actor+0x164)&0xffffu)==0xd4u
        ||(r32(actor+0x178)==1u&&(r32(actor+0x17c)&0xffffu)==0xd4u))){
        guard_actor=actor;guard_array=cache_array;guard_seen=(r32(actor+0x164)&0xffffu)==0xd4u;guard_wait=0;
        if(guard_notes++<24u)log_text("AQUA MAIN GUARD: native row3D witnessed; full400 forward/reverse at source30fps; all-angle native guard contacts");
    }
    return result;
}
static uptr ABI guard_motion(uptr actor,float delta){
    guard_observe(actor);
    if(guard_main_scope(actor)&&air_finite(delta)&&delta>=0.f&&delta<=4.f){
        if(guard_live(actor)||(guard_actor==actor&&!guard_seen&&r32(actor+0x178)==1u&&(r32(actor+0x17c)&0xffffu)==0xd4u))delta*=53.f/156.f;
        else if((r32(actor+0x164)&0xffffu)==0xcbu)delta*=47.f/35.f;
    }
    return guard_motion_original(actor,delta);
}
static int ABI guard_angle(uptr first,uptr second){
    if(guard_live(guard_actor)&&memory(first,0x68,0)&&memory(second,0x68,0)
        &&(r32(first)&0x200800u)==0x800u
        /* Match exactly the native facing-check eligibility at2B4675..4686.
         * Guard can supply more than one native clash class; scope by the
         * witnessed Guard and direct actor ownership, not one guessed class. */
        &&(((r32(first)&0x000e0000u)-0x00020000u)&0xfff9ffffu)==0u
        &&decode(r32(first+0x34))==guard_actor)return 1;
    return guard_angle_original(first,second);
}
static void guard_install(void){
    if(guard_attempted||remove_mode)return;guard_attempted=1;
    uptr addresses[3]={base+0x2a3980u,base+0x29f0a0u,base+0x2b4640u};
    const u8*prefixes[3]={guard_row_prefix,guard_motion_prefix,guard_angle_prefix};
    for(unsigned i=0;i<3;i++)if(!memory(addresses[i],15,0)||!equal((void*)addresses[i],prefixes[i],15)){
        log_text("AQUA GUARD CONTROLLER UNAVAILABLE: native row/motion/angle anchors did not match");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    for(unsigned i=0;i<3;i++){copy(page+i*64,prefixes[i],15);magic_jump(page+i*64+15,addresses[i]+15);}
    u32 old_page,old[3],unused;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,192);
    unsigned protected=0;
    for(;protected<3;protected++)if(!kVirtualProtect((void*)addresses[protected],15,0x40u,old+protected))break;
    if(protected<3){
        while(protected){protected--;kVirtualProtect((void*)addresses[protected],15,old[protected],&unused);}
        kVirtualFree(page,0,0x8000u);return;
    }
    guard_row_original=(GuardRowFn)(uptr)page;guard_motion_original=(MotionAdvanceFn)(uptr)(page+64);guard_angle_original=(GuardAngleFn)(uptr)(page+128);
    uptr callbacks[3]={(uptr)guard_row,(uptr)guard_motion,(uptr)guard_angle};
    for(unsigned i=0;i<3;i++){
        u8 code[15];code[14]=0x90;magic_jump(code,callbacks[i]);copy((void*)addresses[i],code,15);
        kFlushInstructionCache((uptr)-1,(void*)addresses[i],15);kVirtualProtect((void*)addresses[i],15,old[i],&unused);
    }
    guard_ready=1;log_text("AQUA MAIN GUARD READY: witnessed row3D, full native defense timeline, scoped direction check, native motion delta scaling");
}
