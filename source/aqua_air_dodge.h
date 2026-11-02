/* Checked native control for Aqua's airborne Circle. Glide remains native.
 * Master-style lift and directional travel enter the native fall displacement
 * callback BEFORE KH1 collision. No actor-position writes or defense grants.
 */
typedef void (ABI *AirControlFn)(uptr,uptr);
typedef void (ABI *AirQueueFn)(uptr,u32,float);
static AirControlFn air_original;
static int air_attempted,air_ready,air_disabled,air_armed,air_used,air_pending,air_requested_choice;
static int air_control_seen;
static uptr air_actor,air_array;
/* The recorded Dual D snapshot supplies height145/speed18. Its2x policy
 * scales each displacement (including lift), never animation/arc time. The
 * existing KH1 gravity/release adaptation remains an explicit host parameter. */
#define AIR_BASE_HEIGHT 145.f
#define AIR_BASE_SPEED 18.f
#define AIR_DISTANCE 2.f
#define AIR_GRAVITY .75f
#define AIR_RELEASE_UP 4.f
#define AIR_MAX_FALL 20.f
static float air_last_clock,air_elapsed,air_vx,air_vz,air_vy;
static int air_released;
static u32 air_move_notes;
typedef float (ABI *AirMoveFn)(uptr,uptr);
static AirMoveFn air_move_original;
static const u8 air_move_prefix[16]={0x48,0x89,0x5c,0x24,0x10,0x57,0x48,0x83,0xec,0x40,0xf7,0x01,0,0x10,0,0};
static const u8 air_state_prefix[14]={0x48,0x89,0x5c,0x24,0x10,0x57,0x48,0x83,0xec,0x20,0x48,0x63,0x41,0x70};
static u32 air_wait,air_notes,air_input_notes;
static const u8 air_prefix[17]={0x48,0x89,0x5c,0x24,0x18,0x57,0x48,0x83,0xec,0x40,0x48,0x8b,0x05,0x57,0xe8,0x2a,0};
static const u8 air_can_bytes[32]={0xf6,0x01,0x04,0x75,0x18,0xf6,0x81,0x88,0,0,0,0x20,0x75,0x0f,0xf6,0x81,0x44,0x04,0,0,0x01,0x75,0x06,0xb8,0x01,0,0,0,0xc3,0x33,0xc0,0xc3};
static const u8 air_queue_prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
static float air_float(uptr p){float x;u32 bits=r32(p);copy(&x,&bits,4);return x;}
static int air_finite(float x){u32 b;copy(&b,&x,4);return (b&0x7f800000u)!=0x7f800000u;}
static void air_write_float(uptr p,float x){copy((void*)p,&x,4);}
static void air_dodge_clear(void){
    air_dodge_active=air_armed=air_used=air_pending=0;
    air_actor=air_array=0;air_wait=0;air_last_clock=air_elapsed=air_vx=air_vz=air_vy=0;air_released=0;
}
static int movement_scope(uptr actor){
    return air_ready&&!magic_conflict&&!remove_mode&&air_requested_choice>0&&cache_choice>0&&actor==cache_actor
        &&r64(base+SORA_RVA)==actor&&memory(actor,0x448,0)&&(r32(actor+0x374)&3u)==1u
        &&decode(r32(actor+0x1d4))==cache_array&&!r32(base+0x298c9a0u)
        &&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
/* mode0 = selected fall506, mode1 = dodge504. No Glide overlay exists. */
static int air_pose(int mode){
    if(!cache_actor||cache_choice<1||cache_choice>5||r64(base+SORA_RVA)!=cache_actor
        ||!memory(cache_actor,0x378,0)||(r32(cache_actor+0x374)&3u)!=1u
        ||decode(r32(cache_actor+0x1d4))!=cache_array)return 0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot==10){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(again.parts[j]!=b->parts[j]||!d->parts[j].dodge)return 0;
        for(unsigned j=0;j<d->part_count;j++){
            const AquaPart*p=d->parts+j;const u8*desired=mode==1?p->dodge:part_data(p,cache_choice);
            copy((void*)b->parts[j],desired,p->size);
        }
        return 1;
    }return 0;
}
static void air_arc_reset(uptr actor){
    if(actor!=cache_actor||r64(base+SORA_RVA)!=actor||!memory(actor,0x3d8,1)
        ||(r32(actor+0x374)&3u)!=1u||decode(r32(actor+0x1d4))!=cache_array
        ||r32(actor+0x70)!=2u||(r32(actor+0x164)&0xffffu)!=6u)return;
    float y=air_float(actor+0x14);if(!air_finite(y))return;
    air_write_float(actor+0x3b0,0.f);air_write_float(actor+0x3b4,y);
    air_write_float(actor+0x3b8,0.f);air_write_float(actor+0x3bc,0.f);
    *(volatile u32*)(actor+0x3d0)=0;
}
static float air_sqrt(float x){float r;__asm__("sqrtss %1,%0":"=x"(r):"x"(x));return r;}
static void air_motion_start(uptr actor,float x,float z,float tilt){
    float magnitude=air_sqrt(x*x+z*z);
    air_vx=air_vz=0.f;
    if(tilt>.15f&&magnitude>.15f){air_vx=x/magnitude*AIR_BASE_SPEED;air_vz=z/magnitude*AIR_BASE_SPEED;}
    air_vy=air_sqrt(2.f*AIR_BASE_HEIGHT*AIR_GRAVITY);air_elapsed=0.f;air_released=0;
    typedef u32 (ABI *StateFn)(uptr,u32);
    ((StateFn)(base+0x2b1960u))(actor,2u);
    air_arc_reset(actor);
    if(air_notes<32u)log_text("AQUA DUAL D2X MOVEMENT: baseline height145 speed18; all lift/directional displacement2x;504 timing unchanged; native collision");
}
static void air_end(void){
    if(!air_dodge_active)return;
    if(air_dodge_active)air_arc_reset(air_actor);
    if(!air_pose(0))log_text("AQUA AIR ACTION END: changed/unloaded record retained without stale writes");
    air_dodge_active=air_pending=0;air_wait=0;air_elapsed=air_vx=air_vz=air_vy=0.f;
}
static void air_tick(uptr actor,int choice){
    if(!air_dodge_active)return;
    if(actor!=air_actor||choice<1||!movement_scope(actor)||(air_dodge_active&&air_disabled)){air_end();return;}
    u32 state=r32(actor+0x70),request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178);
    float height=air_float(actor+0x3d4);
    if((state!=1u&&state!=2u)||!air_finite(height)||height<=1.f){air_end();return;}
    if(count){
        /* Native commits after control; an already active fall still needs this
         * queued restart. Do not mistake its old clock for the new action. */
        if(count!=1u||(r32(actor+0x17c)&0xffffu)!=6u){air_end();return;}
        if(air_pending&&++air_wait<=16u)return;
        air_end();return;
    }
    if(request!=6u){air_end();return;}
    float clock=air_float(actor+0x16c);
    if(!air_finite(clock)||clock<0||clock>=39.f||(!air_pending&&clock+.5f<air_last_clock)){air_end();return;}
    if(air_pending&&air_notes<32u)log_text("AQUA AIR ACTION: queued native fall restart committed");
    air_pending=0;air_last_clock=clock;
}
static int air_free_request(u32 request){return request==4u||request==5u||request==6u||request==9u||request==10u||request==11u;}
static void air_start(uptr actor){
    ((AirQueueFn)(base+0x29f980u))(actor,6u,0.f);
    air_actor=actor;air_array=cache_array;air_dodge_active=1;
    air_pending=1;air_wait=0;air_last_clock=0;
}
static void air_input_log(uptr actor,u32 reasons){
    if(air_input_notes++>=24u)return;
    log_number("AQUA AIR INPUT rejection mask (0 means accepted)=",reasons);
    log_number("AQUA AIR INPUT native state=",r32(actor+0x70));
    log_number("AQUA AIR INPUT native request=",r32(actor+0x164));
    log_number("AQUA AIR INPUT native queued count=",r32(actor+0x178));
    if(r32(actor+0x178))log_number("AQUA AIR INPUT first queued request=",r32(actor+0x17c));
    log_number("AQUA AIR INPUT held=",r32(base+0x298ca94u));
    log_number("AQUA AIR INPUT pressed=",r32(base+0x298ca98u));
    log_number("AQUA AIR INPUT command=",r32(base+0x2d53a40u));
    log_number("AQUA AIR INPUT active profile=",(uptr)cache_choice);
}
static void ABI air_control(uptr actor,uptr dir){
    uptr pad=base+0x298ca90u;
    int local=actor==r64(base+SORA_RVA)&&memory(actor,0x448,0)&&memory(pad,0x18,1);
    if(local&&!air_control_seen){
        air_control_seen=1;log_text("AQUA CONTROL OBSERVED: native Sora input callback reached v17");
        log_number("AQUA CONTROL actor=",actor);
    }
    if(movement_scope(actor)&&memory(pad,0x18,1)&&memory(dir,16,0)){
        u32 down=r32(pad+4)&6u,press=r32(pad+8)&6u;
        if(air_actor!=actor||air_array!=cache_array){air_actor=actor;air_array=cache_array;air_armed=!down;air_used=0;}
        u32 state=r32(actor+0x70);float height=air_float(actor+0x3d4);
        if(state==0u&&air_finite(height)&&height<=1.f){air_end();air_used=0;air_armed=!down;}
        else if(!down)air_armed=1;
        air_tick(actor,cache_choice);
        if(press&&!air_disabled){
            float x=air_float(dir),z=air_float(dir+8),tilt=air_float(dir+12);
            u32 request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178),reasons=0;
            if(air_used||air_dodge_active)reasons|=2u;
            if(!air_armed)reasons|=4u;
            if(state!=1u&&state!=2u)reasons|=8u;
            if(!air_finite(height)||height<=1.f)reasons|=16u;
            if(!air_finite(x)||!air_finite(z)||!air_finite(tilt)||tilt<0||x*x+z*z>4.f)reasons|=32u;
            if(!air_free_request(request))reasons|=64u;
            if(r32(pad+4)&0x00140000u)reasons|=128u;
            /* Native control0x2A629A treats bit24 as Jump/landing handling;
             * it skips command dispatch when this bit is SET. Otherwise,
             * 0x2A62F8 dispatches only a NONZERO low command byte. The user's
             * normal airborne Jump value0x03000000 therefore permits dodge. */
            u32 command=r32(base+0x2d53a40u);
            if((command&0xffu)&&!(command&0x01000000u))reasons|=256u;
            if(count&&(count!=1u||!air_free_request(r32(actor+0x17c)&0xffffu)))reasons|=512u;
            if(!reasons){
                typedef int (ABI *CanFn)(uptr);
                if(!((CanFn)(base+0x297870u))(actor))reasons|=1024u;
                else if(!memory(actor+0x160,0x2c,1)||!memory(actor+0x3b0,0x28,1)||!air_pose(1))reasons|=2048u;
                else{
                    air_motion_start(actor,x,z,tilt);air_start(actor);air_used=1;air_armed=0;
                    if(air_notes++<32u)log_text("AQUA AIR DODGE504: fresh airborne Circle; queued native restart even when already falling");
                }
            }
            air_input_log(actor,reasons);
        }
        if(air_dodge_active){
            static const u32 fields[4]={4,8,16,20};u32 saved[4];
            for(unsigned i=0;i<4;i++){saved[i]=r32(pad+fields[i])&6u;*(volatile u32*)(pad+fields[i])=r32(pad+fields[i])&~6u;}
            air_original(actor,dir);blizzard_tick(actor,air_requested_choice);
            for(unsigned i=0;i<4;i++)*(volatile u32*)(pad+fields[i])=(r32(pad+fields[i])&~6u)|saved[i];
            air_tick(actor,cache_choice);return;
        }
    }else{
        if(local&&air_requested_choice>0&&(r32(pad+8)&6u))air_input_log(actor,1u);
        if(actor==air_actor)air_end();
    }
    air_original(actor,dir);blizzard_tick(actor,air_requested_choice);
    if(local){air_tick(actor,cache_choice);}
}
static float ABI air_move(uptr actor,uptr out){
    if(!air_dodge_active||actor!=air_actor||!movement_scope(actor))return air_move_original(actor,out);
    air_tick(actor,cache_choice);
    if(!air_dodge_active||air_pending||r32(actor+0x70)!=2u||!memory(out,16,1))return air_move_original(actor,out);
    if(air_elapsed==0.f&&air_move_notes++<24u)log_text("AQUA DODGE MOVEMENT ACTIVE: native state2 displacement supplied before collision");
    float dt=air_float(base+0x233fbdcu);
    if(!air_finite(dt)||dt<=0.f||dt>4.f){air_end();return air_move_original(actor,out);}
    if(!(r32(base+0x298ca94u)&6u)&&!air_released){
        air_released=1;if(air_vy>AIR_RELEASE_UP)air_vy=AIR_RELEASE_UP;
    }
    /* The native ceiling contact bit clips a rising request. KH1 retains all
     * wall/floor tests and can interrupt this action through its own queue. */
    if((r32(actor+0x2d0)&8u)&&air_vy>0.f)air_vy=0.f;
    float dy=-(air_vy*dt-.5f*AIR_GRAVITY*dt*dt)*AIR_DISTANCE;
    air_vy-=AIR_GRAVITY*dt;if(air_vy< -AIR_MAX_FALL)air_vy= -AIR_MAX_FALL;
    float move[4]={air_vx*dt*AIR_DISTANCE,dy,air_vz*dt*AIR_DISTANCE,air_sqrt(air_vx*air_vx+air_vz*air_vz)*dt*AIR_DISTANCE};
    copy((void*)out,move,16);
    float velocity[4]={air_vx*AIR_DISTANCE,dy/dt,air_vz*AIR_DISTANCE,move[3]/dt};copy((void*)(actor+0x3c0),velocity,16);
    air_arc_reset(actor);air_elapsed+=dt;
    if(air_elapsed>=39.f)air_end();
    return air_float(actor+0x124);
}
typedef void (ABI *GlideFn)(uptr);
static GlideFn regular_glide_original;
static u32 glide_block_notes;
static const u8 regular_glide_prefix[14]={0x40,0x53,0x48,0x83,0xec,0x20,0x48,0x8b,0xd9,0xe8,0x62,0x06,0,0};
static void ABI regular_glide(uptr actor){
    if(air_dodge_active&&air_actor==actor&&movement_scope(actor)){
        if(glide_block_notes++<16u)log_text("AQUA DODGE504: deferred native Glide constructor suppressed while dodge owns the fall pose");
        return;
    }
    regular_glide_original(actor);
}
static void air_install(void){
    if(air_attempted||remove_mode)return;air_attempted=1;
    uptr a=base+0x2a6220u,g=base+0x2b26c0u,m=base+0x2af6a0u;
    if(!memory(m,16,0)||!equal((void*)m,air_move_prefix,16)
        ||!memory(base+0x2b1960u,14,0)||!equal((void*)(base+0x2b1960u),air_state_prefix,14)
        ||!memory(base+0x233fbdcu,4,0)
        ||!memory(a,17,0)||!equal((void*)a,air_prefix,17)
        ||!memory(g,0x24,0)||!equal((void*)g,regular_glide_prefix,14)
        ||r32(g+0x1d)!=0x0104a083u||r32(g+0x20)!=0xfe000001u
        ||!memory(base+0x297870u,32,0)||!equal((void*)(base+0x297870u),air_can_bytes,32)
        ||!memory(base+0x29f980u,13,0)||!equal((void*)(base+0x29f980u),air_queue_prefix,13)
        ||!memory(base+0x298ca90u,0x18,1)||!memory(base+0x554a88u,8,0)){
        log_text("AQUA AIR ACTIONS UNAVAILABLE: native control/input admission failed; other Aqua poses remain available");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    copy(page,air_prefix,10);
    /* Relocate the one RIP-relative cookie load in the 17-byte stolen span. */
    page[10]=0x48;page[11]=0xb8;uptr cookie=base+0x554a88u;copy(page+12,&cookie,8);
    page[20]=0x48;page[21]=0x8b;page[22]=0;magic_jump(page+23,a+17);
    copy(page+128,regular_glide_prefix,9);
    page[137]=0x48;page[138]=0xb8;uptr common=base+0x2b2d30u;copy(page+139,&common,8);
    page[147]=0xff;page[148]=0xd0;magic_jump(page+149,g+14);
    copy(page+256,air_move_prefix,16);magic_jump(page+272,m+16);
    u32 old_page=0,old_code=0,old_glide=0,old_move=0,unused=0;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,320);
    if(!kVirtualProtect((void*)a,17,0x40u,&old_code)){kVirtualFree(page,0,0x8000u);return;}
    if(!kVirtualProtect((void*)g,14,0x40u,&old_glide)){
        kVirtualProtect((void*)a,17,old_code,&unused);kVirtualFree(page,0,0x8000u);return;
    }
    if(!kVirtualProtect((void*)m,16,0x40u,&old_move)){
        kVirtualProtect((void*)g,14,old_glide,&unused);kVirtualProtect((void*)a,17,old_code,&unused);
        kVirtualFree(page,0,0x8000u);return;
    }
    air_move_original=(AirMoveFn)(uptr)(page+256);
    u8 move_patch[16];for(unsigned i=0;i<16;i++)move_patch[i]=0x90;
    magic_jump(move_patch,(uptr)air_move);copy((void*)m,move_patch,16);
    kFlushInstructionCache((uptr)-1,(void*)m,16);kVirtualProtect((void*)m,16,old_move,&unused);
    regular_glide_original=(GlideFn)(uptr)(page+128);
    u8 glide_patch[14];magic_jump(glide_patch,(uptr)regular_glide);copy((void*)g,glide_patch,14);
    kFlushInstructionCache((uptr)-1,(void*)g,14);kVirtualProtect((void*)g,14,old_glide,&unused);
    air_original=(AirControlFn)(uptr)page;u8 patch[17];for(unsigned i=0;i<17;i++)patch[i]=0x90;
    magic_jump(patch,(uptr)air_control);copy((void*)a,patch,17);
    kFlushInstructionCache((uptr)-1,(void*)a,17);kVirtualProtect((void*)a,17,old_code,&unused);
    air_ready=1;log_text("AQUA AIR DODGE READY: v17 Dual D baseline145/18 at2x travel with unchanged504 timing; default native Glide outside dodge");
}
