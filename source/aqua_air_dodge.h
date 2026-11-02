/* Checked native control hook for Aqua's airborne Circle and Glide phases.
 * Only admitted body tables and native animation clocks/queues are changed.
 * Actor state, velocity, gravity, collision and defensive flags remain native.
 */
typedef void (ABI *AirControlFn)(uptr,uptr);
typedef void (ABI *AirQueueFn)(uptr,u32,float);
static AirControlFn air_original;
static int air_attempted,air_ready,air_disabled,air_armed,air_used,air_pending,air_requested_choice;
static int glide_active,air_control_seen;
static uptr air_actor,air_array,glide_actor,glide_array;
static float air_last_clock,glide_progress;
static u32 air_wait,air_notes,air_input_notes,glide_notes;
static const u8 air_prefix[17]={0x48,0x89,0x5c,0x24,0x18,0x57,0x48,0x83,0xec,0x40,0x48,0x8b,0x05,0x57,0xe8,0x2a,0};
static const u8 air_can_bytes[32]={0xf6,0x01,0x04,0x75,0x18,0xf6,0x81,0x88,0,0,0,0x20,0x75,0x0f,0xf6,0x81,0x44,0x04,0,0,0x01,0x75,0x06,0xb8,0x01,0,0,0,0xc3,0x33,0xc0,0xc3};
static const u8 air_queue_prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
static float air_float(uptr p){float x;u32 bits=r32(p);copy(&x,&bits,4);return x;}
static int air_finite(float x){u32 b;copy(&b,&x,4);return (b&0x7f800000u)!=0x7f800000u;}
static void air_write_float(uptr p,float x){copy((void*)p,&x,4);}
static void air_dodge_clear(void){
    air_dodge_active=glide_stop_active=air_armed=air_used=air_pending=glide_active=glide_standard_active=0;
    air_actor=air_array=glide_actor=glide_array=0;air_wait=0;air_last_clock=glide_progress=0;
}
static int movement_scope(uptr actor){
    return air_ready&&!magic_conflict&&!remove_mode&&air_requested_choice>0&&cache_choice>0&&actor==cache_actor
        &&r64(base+SORA_RVA)==actor&&memory(actor,0x448,0)&&(r32(actor+0x374)&3u)==1u
        &&decode(r32(actor+0x1d4))==cache_array&&!r32(base+0x298c9a0u)
        &&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
/* mode0 = selected fall506, mode1 = dodge504, mode2 = Glide stop350. */
static int air_pose(int mode){
    if(!cache_actor||cache_choice<1||cache_choice>5||r64(base+SORA_RVA)!=cache_actor
        ||!memory(cache_actor,0x378,0)||(r32(cache_actor+0x374)&3u)!=1u
        ||decode(r32(cache_actor+0x1d4))!=cache_array)return 0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot==10){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(again.parts[j]!=b->parts[j]||!d->parts[j].dodge||!d->parts[j].glide_stop)return 0;
        for(unsigned j=0;j<d->part_count;j++){
            const AquaPart*p=d->parts+j;const u8*desired=mode==1?p->dodge:mode==2?p->glide_stop:part_data(p,cache_choice);
            copy((void*)b->parts[j],desired,p->size);
        }
        return 1;
    }return 0;
}
static void air_end(void){
    if(!air_dodge_active&&!glide_stop_active)return;
    if(!air_pose(0))log_text("AQUA AIR ACTION END: changed/unloaded record retained without stale writes");
    air_dodge_active=glide_stop_active=air_pending=0;air_wait=0;
}
static void air_tick(uptr actor,int choice){
    if(!air_dodge_active&&!glide_stop_active)return;
    if(actor!=air_actor||choice<1||!movement_scope(actor)||(air_dodge_active&&air_disabled)){air_end();return;}
    u32 state=r32(actor+0x70),request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178);
    float height=air_float(actor+0x3d4);
    if((state!=1u&&state!=2u&&!(glide_stop_active&&state==21u))||!air_finite(height)||height<=1.f){air_end();return;}
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
static int glide_request(u32 request){return (request>=0x71u&&request<=0x74u)||(request>=0x76u&&request<=0x79u);}
static int glide_record_valid(u32 request){
    u32 slot=75u+request-(request<=0x74u?0x71u:0x76u);
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot==slot){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(again.parts[j]!=b->parts[j]
            ||!equal((void*)b->parts[j],glide_standard_active?d->parts[j].before:part_data(d->parts+j,cache_choice),d->parts[j].size))return 0;
        return 1;
    }return 0;
}
static void air_start(uptr actor,int mode){
    ((AirQueueFn)(base+0x29f980u))(actor,6u,0.f);
    air_actor=actor;air_array=cache_array;air_dodge_active=mode==1;glide_stop_active=mode==2;
    air_pending=1;air_wait=0;air_last_clock=0;
}
static int glide_body(int native){
    if(!cache_actor||r64(base+SORA_RVA)!=cache_actor||!memory(cache_actor,0x378,0)
        ||(r32(cache_actor+0x374)&3u)!=1u||decode(r32(cache_actor+0x1d4))!=cache_array)return 0;
    unsigned found=0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot>=75u&&aqua_motions[i].normal_slot<=78u){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(again.parts[j]!=b->parts[j])return 0;
        found++;
    }
    if(found!=4u)return 0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot>=75u&&aqua_motions[i].normal_slot<=78u){
        const AquaMotion*d=aqua_motions+i;
        for(unsigned j=0;j<d->part_count;j++)copy((void*)cached[i].parts[j],native?d->parts[j].before:part_data(d->parts+j,cache_choice),d->parts[j].size);
    }
    glide_standard_active=native;return 1;
}
static void glide_tick(uptr actor,int choice){
    if(choice<1||!movement_scope(actor)){
        glide_active=0;glide_actor=glide_array=0;glide_progress=0;
        if(glide_stop_active)air_end();return;
    }
    u32 state=r32(actor+0x70),request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178);
    float height=air_float(actor+0x3d4);
    if(!air_finite(height)||height<=1.f||count>5u){glide_active=0;glide_progress=0;return;}
    int queued_glide=0,queued_other=0;
    for(unsigned i=0;i<count;i++){
        u32 q=r32(actor+0x17c+i*16u)&0xffffu;
        if(glide_request(q))queued_glide=1;else if(q!=6u)queued_other=1;
    }
    if(state==21u&&(glide_request(request)||queued_glide)&&!queued_other&&!air_dodge_active){
        if(glide_request(request)&&!glide_record_valid(request)){glide_active=0;return;}
        for(unsigned i=0;i<count;i++){
            u32 q=r32(actor+0x17c+i*16u)&0xffffu;
            if(glide_request(q)&&!glide_record_valid(q)){glide_active=0;return;}
        }
        if(glide_stop_active)air_end();
        if(!glide_active||glide_actor!=actor||glide_array!=cache_array){
            glide_actor=actor;glide_array=cache_array;glide_progress=0;glide_active=1;
            if(glide_standard_active&&!glide_body(0)){glide_active=0;return;}
            if(glide_notes++<16u)log_text("AQUA GLIDE350: Aqua opening then original Sora mid-flight");
        }
        if(glide_standard_active)return;
        if(glide_request(request)){
            float clock=air_float(actor+0x16c);
            if(!air_finite(clock)||clock<0||!memory(actor+0x16c,4,1)){glide_active=0;return;}
            if(clock>glide_progress)glide_progress=clock<40.f?clock:40.f;
            if(glide_progress>=40.f){
                if(glide_body(1)&&glide_notes++<16u)log_text("AQUA GLIDE: original Sora flight bodies restored; native clock and steering resume");
                return;
            }
            /* Native direction changes must not replay the Aqua opening. */
            if(clock!=glide_progress)air_write_float(actor+0x16c,glide_progress);
        }
        for(unsigned i=0;i<count;i++)if(glide_request(r32(actor+0x17c+i*16u)&0xffffu)){
            uptr frame=actor+0x184+i*16u;if(memory(frame,4,1))air_write_float(frame,glide_progress);
        }
        return;
    }
    if(!glide_active)return;
    int ending=(state==1u||state==2u||state==21u)&&!queued_other
        &&(request==6u||(count==1u&&(r32(actor+0x17c)&0xffffu)==6u));
    glide_active=0;glide_progress=0;
    if(glide_standard_active&&!glide_body(0))return;
    if(ending&&!air_dodge_active&&memory(actor+0x160,0x2c,1)&&air_pose(2)){
        air_start(actor,2);
        if(glide_notes++<16u)log_text("AQUA GLIDE350: native Glide ended; closing frames20..40 then falling506");
    }
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
        air_control_seen=1;log_text("AQUA CONTROL OBSERVED: native Sora input callback reached v15");
        log_number("AQUA CONTROL actor=",actor);
    }
    if(movement_scope(actor)&&memory(pad,0x18,1)&&memory(dir,16,0)){
        u32 down=r32(pad+4)&6u,press=r32(pad+8)&6u;
        if(air_actor!=actor||air_array!=cache_array){air_actor=actor;air_array=cache_array;air_armed=!down;air_used=0;}
        u32 state=r32(actor+0x70);float height=air_float(actor+0x3d4);
        if(state==0u&&air_finite(height)&&height<=1.f){air_end();air_used=0;air_armed=!down;}
        else if(!down)air_armed=1;
        air_tick(actor,cache_choice);glide_tick(actor,cache_choice);
        if(press&&!air_disabled){
            float x=air_float(dir),z=air_float(dir+8),tilt=air_float(dir+12);
            u32 request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178),reasons=0;
            if(air_used||air_dodge_active)reasons|=2u;
            if(!air_armed)reasons|=4u;
            if(state!=1u&&state!=2u)reasons|=8u;
            if(!air_finite(height)||height<=1.f)reasons|=16u;
            if(!air_finite(x)||!air_finite(z)||!air_finite(tilt)||tilt<0)reasons|=32u;
            if(!air_free_request(request)||glide_active||glide_stop_active)reasons|=64u;
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
                else if(!memory(actor+0x160,0x2c,1)||!air_pose(1))reasons|=2048u;
                else{
                    air_start(actor,1);air_used=1;air_armed=0;
                    if(air_notes++<32u)log_text("AQUA AIR DODGE504: fresh airborne Circle; queued native restart even when already falling");
                }
            }
            air_input_log(actor,reasons);
        }
        if(air_dodge_active){
            static const u32 fields[4]={4,8,16,20};u32 saved[4];
            for(unsigned i=0;i<4;i++){saved[i]=r32(pad+fields[i])&6u;*(volatile u32*)(pad+fields[i])=r32(pad+fields[i])&~6u;}
            air_original(actor,dir);if(movement_scope(actor))cast_followup(actor);
            for(unsigned i=0;i<4;i++)*(volatile u32*)(pad+fields[i])=(r32(pad+fields[i])&~6u)|saved[i];
            air_tick(actor,cache_choice);glide_tick(actor,cache_choice);return;
        }
    }else{
        if(local&&air_requested_choice>0&&(r32(pad+8)&6u))air_input_log(actor,1u);
        if(actor==air_actor)air_end();
    }
    air_original(actor,dir);if(movement_scope(actor))cast_followup(actor);
    if(local){air_tick(actor,cache_choice);glide_tick(actor,cache_choice);}
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
    uptr a=base+0x2a6220u,g=base+0x2b26c0u;
    if(!memory(a,17,0)||!equal((void*)a,air_prefix,17)
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
    u32 old_page=0,old_code=0,old_glide=0,unused=0;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,192);
    if(!kVirtualProtect((void*)a,17,0x40u,&old_code)){kVirtualFree(page,0,0x8000u);return;}
    if(!kVirtualProtect((void*)g,14,0x40u,&old_glide)){
        kVirtualProtect((void*)a,17,old_code,&unused);kVirtualFree(page,0,0x8000u);return;
    }
    regular_glide_original=(GlideFn)(uptr)(page+128);
    u8 glide_patch[14];magic_jump(glide_patch,(uptr)regular_glide);copy((void*)g,glide_patch,14);
    kFlushInstructionCache((uptr)-1,(void*)g,14);kVirtualProtect((void*)g,14,old_glide,&unused);
    air_original=(AirControlFn)(uptr)page;u8 patch[17];for(unsigned i=0;i<17;i++)patch[i]=0x90;
    magic_jump(patch,(uptr)air_control);copy((void*)a,patch,17);
    kFlushInstructionCache((uptr)-1,(void*)a,17);kVirtualProtect((void*)a,17,old_code,&unused);
    air_ready=1;log_text("AQUA AIR DODGE READY: v15 queued504 plus deferred native Glide guard ready; original Sora mid-flight with Aqua opening and closing");
}
