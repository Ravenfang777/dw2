/* Neutral airborne logical Jump/Circle: one 504 pose per airtime.
 * The normal fall record is temporarily given a second fitted body pose.
 * Native state, gravity, velocity, collision and defensive flags stay native.
 * One admitted control-entry hook consumes only Jump bits during that pose.
 */
typedef void (ABI *AirControlFn)(uptr,uptr);
static AirControlFn air_original;
static int air_attempted,air_ready,air_disabled,air_armed,air_used,air_pending,air_requested_choice;
static uptr air_actor,air_array;
static float air_last_clock;
static u32 air_wait,air_notes;
static const u8 air_prefix[17]={0x48,0x89,0x5c,0x24,0x18,0x57,0x48,0x83,0xec,0x40,0x48,0x8b,0x05,0x57,0xe8,0x2a,0};
static const u8 air_can_bytes[32]={0xf6,0x01,0x04,0x75,0x18,0xf6,0x81,0x88,0,0,0,0x20,0x75,0x0f,0xf6,0x81,0x44,0x04,0,0,0x01,0x75,0x06,0xb8,0x01,0,0,0,0xc3,0x33,0xc0,0xc3};
static const u8 air_queue_prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
static float air_float(uptr p){float x;u32 bits=r32(p);copy(&x,&bits,4);return x;}
static int air_finite(float x){u32 b;copy(&b,&x,4);return (b&0x7f800000u)!=0x7f800000u;}
static void air_dodge_clear(void){air_dodge_active=air_armed=air_used=air_pending=0;air_actor=air_array=0;air_wait=0;air_last_clock=0;}
static int air_scope(uptr actor){
    return air_ready&&!air_disabled&&!magic_conflict&&!remove_mode&&air_requested_choice>0&&cache_choice>0&&actor==cache_actor
        &&r64(base+SORA_RVA)==actor&&memory(actor,0x448,0)&&(r32(actor+0x374)&3u)==1u
        &&decode(r32(actor+0x1d4))==cache_array&&!r32(base+0x298c9a0u)
        &&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
static int air_pose(int special){
    if(!cache_actor||cache_choice<1||cache_choice>5||r64(base+SORA_RVA)!=cache_actor
        ||!memory(cache_actor,0x378,0)||(r32(cache_actor+0x374)&3u)!=1u
        ||decode(r32(cache_actor+0x1d4))!=cache_array)return 0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot==10){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<AQUA_PART_COUNT;j++)if(again.parts[j]!=b->parts[j]||!d->parts[j].dodge)return 0;
        for(unsigned j=0;j<AQUA_PART_COUNT;j++){
            const AquaPart*p=d->parts+j;copy((void*)b->parts[j],special?p->dodge:part_data(p,cache_choice),p->size);
        }
        return 1;
    }return 0;
}
static void air_end(void){
    if(!air_dodge_active)return;
    if(!air_pose(0))log_text("AQUA AIR DODGE END: changed/unloaded record retained without stale writes");
    air_dodge_active=air_pending=0;air_wait=0;
}
static void air_tick(uptr actor,int choice){
    if(!air_dodge_active)return;
    if(actor!=air_actor||choice<1||!air_scope(actor)){air_end();return;}
    u32 state=r32(actor+0x70),request=r32(actor+0x164)&0xfffu;
    float height=air_float(actor+0x3d4);
    if((state!=1u&&state!=2u)||!air_finite(height)||height<=1.f){air_end();return;}
    if(request!=6u){
        if(air_pending&&r32(actor+0x178)&&(r32(actor+0x17c)&0xfffu)==6u&&++air_wait<=8u)return;
        air_end();return;
    }
    float clock=air_float(actor+0x16c);
    if(!air_finite(clock)||clock<0||clock>=39.f||(!air_pending&&clock+.5f<air_last_clock)){air_end();return;}
    air_pending=0;air_last_clock=clock;
}
static int air_free_request(u32 request){return request==4u||request==5u||request==6u||request==9u||request==10u||request==11u;}
static void ABI air_control(uptr actor,uptr dir){
    int mask=0;
    if(air_scope(actor)&&memory(base+0x298ca90u,0x18,1)&&memory(dir,16,0)){
        uptr pad=base+0x298ca90u;u32 down=r32(pad+4)&6u,press=r32(pad+8)&6u;
        if(air_actor!=actor||air_array!=cache_array){air_actor=actor;air_array=cache_array;air_armed=!down;air_used=0;}
        u32 state=r32(actor+0x70);float height=air_float(actor+0x3d4);
        if(state==0u&&air_finite(height)&&height<=1.f){air_end();air_used=0;air_armed=!down;}
        else if(!down)air_armed=1;
        air_tick(actor,cache_choice);
        float x=air_float(dir),z=air_float(dir+8),tilt=air_float(dir+12);
        u32 request=r32(actor+0x164)&0xfffu;
        int free_request=air_free_request(request);
        if(!air_dodge_active&&!air_used&&air_armed&&down&&press&&(state==1u||state==2u)
            &&air_finite(height)&&height>1.f&&air_finite(x)&&air_finite(z)&&air_finite(tilt)
            &&tilt>=0&&tilt<=.15f&&x*x+z*z<=.0225f&&free_request
            &&!(r32(pad+4)&0x00140000u)&&!(r32(base+0x2d53a40u)&0xffu)
            &&(!r32(actor+0x178)||air_free_request(r32(actor+0x17c)&0xfffu))){
            typedef int (ABI *CanFn)(uptr);typedef void (ABI *QueueFn)(uptr,u32,float);
            if(((CanFn)(base+0x297870u))(actor)&&fast_binding(actor,cache_array,cache_choice)
                &&memory(actor+0x16c,4,1)&&air_pose(1)){
                if(request==6u){*(volatile u32*)(actor+0x16c)=0;air_pending=0;}
                else{((QueueFn)(base+0x29f980u))(actor,6u,0.f);air_pending=1;}
                air_dodge_active=air_used=1;air_armed=0;air_wait=0;air_last_clock=0;
                if(air_notes++<32)log_text("AQUA AIR DODGE 504: fresh neutral airborne Jump/Circle; one per airtime; native fall physics");
            }
        }
        mask=air_dodge_active;
        if(mask){
            static const u32 fields[4]={4,8,16,20};u32 saved[4];
            for(unsigned i=0;i<4;i++){saved[i]=r32(pad+fields[i])&6u;*(volatile u32*)(pad+fields[i])=r32(pad+fields[i])&~6u;}
            air_original(actor,dir);
            for(unsigned i=0;i<4;i++)*(volatile u32*)(pad+fields[i])=(r32(pad+fields[i])&~6u)|saved[i];
            air_tick(actor,cache_choice);return;
        }
    }else if(actor==air_actor)air_end();
    air_original(actor,dir);
}
static void air_install(void){
    if(air_attempted||air_disabled||remove_mode)return;air_attempted=1;
    uptr a=base+0x2a6220u;
    if(!memory(a,17,0)||!equal((void*)a,air_prefix,17)
        ||!memory(base+0x297870u,32,0)||!equal((void*)(base+0x297870u),air_can_bytes,32)
        ||!memory(base+0x29f980u,13,0)||!equal((void*)(base+0x29f980u),air_queue_prefix,13)
        ||!memory(base+0x298ca90u,0x18,1)||!memory(base+0x554a88u,8,0)){
        log_text("AQUA AIR DODGE UNAVAILABLE: native control/input admission failed; other Aqua poses remain available");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    copy(page,air_prefix,10);
    /* Relocate the one RIP-relative cookie load in the 17-byte stolen span. */
    page[10]=0x48;page[11]=0xb8;uptr cookie=base+0x554a88u;copy(page+12,&cookie,8);
    page[20]=0x48;page[21]=0x8b;page[22]=0;magic_jump(page+23,a+17);
    u32 old_page=0,old_code=0,unused=0;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,64);
    if(!kVirtualProtect((void*)a,17,0x40u,&old_code)){kVirtualFree(page,0,0x8000u);return;}
    air_original=(AirControlFn)(uptr)page;u8 patch[17];for(unsigned i=0;i<17;i++)patch[i]=0x90;
    magic_jump(patch,(uptr)air_control);copy((void*)a,patch,17);
    kFlushInstructionCache((uptr)-1,(void*)a,17);kVirtualProtect((void*)a,17,old_code,&unused);
    air_ready=1;log_text("AQUA AIR DODGE READY: neutral airborne Jump/Circle uses 504; original control trampoline admitted");
}
