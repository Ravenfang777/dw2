/* Main Terra only: native spell recovery variants and a finite Square tap
 * replacing Superglide. Ordinary Glide and every numbered profile stay native.
 * Movement is supplied to native fall physics BEFORE collision, never XYZ.
 */
typedef void (ABI *SlideControlFn)(uptr,uptr);
typedef float (ABI *SlideMoveFn)(uptr,uptr);
typedef int (ABI *SlideGlideFn)(uptr);
static SlideControlFn slide_control_original;
static SlideMoveFn slide_move_original;
static SlideGlideFn slide_glide_original;
static int actions_attempted,actions_ready,slide_armed=1,slide_pending;
static uptr actions_actor,actions_array,slide_actor,slide_array;
static unsigned slide_wait,slide_notes,slide_rejections,cast_notes;
static u32 cast_family;
static float slide_elapsed,slide_clock,slide_vx,slide_vz;
#define SLIDE_DURATION 39.f
#define SLIDE_SPEED 16.f /* Native Superglide horizontal speed limit. */
static const u8 slide_control_prefix[17]={0x48,0x89,0x5c,0x24,0x18,0x57,0x48,0x83,0xec,0x40,0x48,0x8b,0x05,0x57,0xe8,0x2a,0};
static const u8 slide_glide_prefix[15]={0x40,0x53,0x48,0x83,0xec,0x20,0x48,0x8b,0xd9,0x8b,0x89,0x48,0x01,0,0};
static const u8 slide_move_prefix[16]={0x48,0x89,0x5c,0x24,0x10,0x57,0x48,0x83,0xec,0x40,0xf7,0x01,0,0x10,0,0};
static const u8 slide_state_prefix[14]={0x48,0x89,0x5c,0x24,0x10,0x57,0x48,0x83,0xec,0x20,0x48,0x63,0x41,0x70};
static const u8 slide_can_bytes[32]={0xf6,0x01,0x04,0x75,0x18,0xf6,0x81,0x88,0,0,0,0x20,0x75,0x0f,0xf6,0x81,0x44,0x04,0,0,0x01,0x75,0x06,0xb8,0x01,0,0,0,0xc3,0x33,0xc0,0xc3};
static const u8 slide_queue_prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
static float slide_float(uptr p){float f;u32 bits=r32(p);copy(&f,&bits,4);return f;}
static void slide_put_float(uptr p,float f){copy((void*)p,&f,4);}
static int slide_finite(float f){u32 bits;copy(&bits,&f,4);return (bits&0x7f800000u)!=0x7f800000u;}
static float slide_sqrt(float f){float result;__asm__("sqrtss %1,%0":"=x"(result):"x"(f));return result;}
static u32 variant_slot(u32 bit){return bit==1u?10u:bit==2u?57u:82u;}
static int actions_binding(uptr actor){
    return cache_choice==1&&actor==cache_actor&&actor==r64(base+SORA_RVA)
        &&memory(actor,0x448,0)&&(r32(actor+0x374)&3u)==1u
        &&decode(r32(actor+0x1d4))==cache_array;
}
static int actions_scope(uptr actor){
    return !remove_mode&&action_choice==1&&actions_binding(actor)
        &&!r32(base+0x298c9a0u)&&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
static int main_super_scope(uptr actor){
    return actions_ready&&!remove_mode&&action_choice==1&&actor==r64(base+SORA_RVA)
        &&memory(actor,0x448,0)&&(r32(actor+0x374)&3u)==1u
        &&!r32(base+0x298c9a0u)&&!(r32(base+0x2867364u)&0x00012000u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&!(r32(actor)&0x01000000u);
}
static int variant_binding(u32 bit,Binding **binding,const TerraMotion **motion){
    if(!actions_binding(cache_actor))return 0;
    for(unsigned i=0;i<TERRA_MOTION_COUNT;i++)if(terra_motions[i].normal_slot==variant_slot(bit)){
        const TerraMotion*d=terra_motions+i;Binding*b=cached+i,again;int reason;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&reason))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(again.parts[j]!=b->parts[j]||!d->parts[j].variant)return 0;
        *binding=b;*motion=d;return 1;
    }return 0;
}
static int variant_write(u32 bit,int on){
    Binding*b;const TerraMotion*d;if(!variant_binding(bit,&b,&d))return 0;
    for(unsigned j=0;j<d->part_count;j++){
        const TerraPart*p=d->parts+j;const u8*desired=on?p->variant:part_data(p,1);
        if(!equal((void*)b->parts[j],desired,p->size))copy((void*)b->parts[j],desired,p->size);
    }
    action_variant_mask=on?action_variant_mask|bit:action_variant_mask&~bit;return 1;
}
static void actions_forget(void){
    action_choice=0;slide_active=slide_pending=0;cast_family=0;slide_armed=1;
    /* Keep known body variants marked until safe readmission can restore them. */
}
static void slide_arc_reset(uptr actor){
    if(!actions_binding(actor)||!memory(actor+0x3b0,0x28,1)||r32(actor+0x70)!=2u||(r32(actor+0x164)&0xffffu)!=6u)return;
    float y=slide_float(actor+0x14);if(!slide_finite(y))return;
    slide_put_float(actor+0x3b0,0.f);slide_put_float(actor+0x3b4,y);
    slide_put_float(actor+0x3b8,0.f);slide_put_float(actor+0x3bc,0.f);*(volatile u32*)(actor+0x3d0)=0;
}
static void slide_end(int finished){
    if(!slide_active)return;
    if(finished&&actions_scope(slide_actor)&&r32(slide_actor+0x70)==2u&&(r32(slide_actor+0x164)&0xffffu)==6u&&memory(slide_actor+0x3c0,16,1)){
        /* Native Superglide's release halves horizontal travel velocity. */
        slide_put_float(slide_actor+0x3c0,slide_float(slide_actor+0x3c0)*.5f);
        slide_put_float(slide_actor+0x3c8,slide_float(slide_actor+0x3c8)*.5f);
        slide_put_float(slide_actor+0x3cc,slide_float(slide_actor+0x3cc)*.5f);
        slide_arc_reset(slide_actor);
    }
    if(!variant_write(1u,0)&&slide_notes<24u)log_text("TERRA SLIDE END: changed/unloaded body retained without stale writes");
    slide_active=slide_pending=0;slide_wait=0;slide_elapsed=slide_clock=slide_vx=slide_vz=0.f;
}
static void actions_prepare(uptr actor,int choice){
    action_choice=choice;uptr array=decode(r32(actor+0x1d4));
    if(actor!=actions_actor||array!=actions_array){
        actions_actor=actor;actions_array=array;slide_active=slide_pending=0;slide_armed=1;
        action_variant_mask=cast_family=0;slide_actor=slide_array=0;slide_elapsed=slide_clock=0.f;
    }
    if(choice!=1){
        slide_end(0);cast_family=0;
        for(u32 bit=2u;bit<=4u;bit<<=1u)if(action_variant_mask&bit)variant_write(bit,0);
    }
}
static int slide_free_request(u32 request){return request==4u||request==5u||request==6u||request==9u||request==10u||request==11u;}
static void slide_tick(uptr actor){
    if(!slide_active)return;
    if(actor!=slide_actor||cache_array!=slide_array||!actions_scope(actor)){slide_end(0);return;}
    Binding*b;const TerraMotion*d;if(!variant_binding(1u,&b,&d)){slide_end(0);return;}
    u32 state=r32(actor+0x70),request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178);
    float height=slide_float(actor+0x3d4);
    if((state!=1u&&state!=2u)||!slide_finite(height)||height<=1.f){slide_end(0);return;}
    if(count){
        if(count!=1u||(r32(actor+0x17c)&0xffffffffu)!=6u){slide_end(0);return;}
        if(slide_pending&&++slide_wait<=16u)return;
        slide_end(0);return;
    }
    if(request!=6u){slide_end(0);return;}
    float clock=slide_float(actor+0x16c);
    if(!slide_finite(clock)||clock<0.f||(!slide_pending&&clock+.5f<slide_clock)){slide_end(0);return;}
    if(clock>=SLIDE_DURATION){slide_end(1);return;}
    slide_pending=0;slide_clock=clock;
}
static u32 cast_release_family(u32 request){
    if(request==0x36u||request==0x37u||request==0x3au)return 1u;
    if(request==0x83u||request==0x84u||request==0x87u)return 2u;
    if((request>=0x38u&&request<=0x3cu)||(request>=0x85u&&request<=0x89u))return 3u;
    return 0u;
}
static int cast_request(u32 request){return (request>=0x36u&&request<=0x3du)||(request>=0x83u&&request<=0x8au);}
static void cast_tick(uptr actor){
    /* Both callers have already admitted the live actor. Idle/non-magic frames
       need no additional VirtualQuery or full motion comparison. */
    if(cache_choice!=1||actor!=cache_actor||actor!=r64(base+SORA_RVA))return;
    u32 current=r32(actor+0x164)&0xffffu,queued=r32(actor+0x178)?r32(actor+0x17c)&0xffffu:0u;
    if(!cast_request(current)&&!cast_request(queued)&&!(action_variant_mask&6u)){cast_family=0;return;}
    if(!actions_binding(actor))return;
    u32 wanted=0;
    if(actions_scope(actor)){
        u32 request=r32(actor+0x164)&0xffffu,live=request,family=cast_release_family(live),count=r32(actor+0x178);
        if(family)cast_family=family;
        if(count&&count<=5u){u32 queued=r32(actor+0x17c);if(!(queued&0x40000000u)&&cast_request(queued&0xffffu))request=queued&0xffffu;}
        family=cast_release_family(request);if(family)cast_family=family;
        if(request==0x3du&&cast_family==1u)wanted=2u;
        if(request==0x8au&&cast_family==2u)wanted=4u;
        if(!cast_request(live)&&!cast_request(request))cast_family=0;
    }else cast_family=0;
    for(u32 bit=2u;bit<=4u;bit<<=1u)if((wanted^action_variant_mask)&bit){
        if(variant_write(bit,(wanted&bit)!=0)&&(wanted&bit)&&cast_notes++<24u)
            log_text("TERRA MAIN CAST RECOVERY: Fire/Blizzard/Gravity315 ground or316 air; native events retained");
    }
}
static void actions_tick(uptr actor){
    slide_tick(actor);
    /* A failed stale-record restore is retried only after full readmission. */
    if(!slide_active&&(action_variant_mask&1u))variant_write(1u,0);
    cast_tick(actor);
}
static void slide_start(uptr actor,uptr dir){
    float x=slide_float(dir),z=slide_float(dir+8),tilt=slide_float(dir+12),magnitude=slide_sqrt(x*x+z*z);
    if(tilt<=.15f||magnitude<=.15f){x=slide_float(actor+0x30);z=slide_float(actor+0x38);magnitude=slide_sqrt(x*x+z*z);}
    if(!slide_finite(magnitude)||magnitude<=.0001f){x=0.f;z=1.f;magnitude=1.f;}
    slide_vx=x/magnitude*SLIDE_SPEED;slide_vz=z/magnitude*SLIDE_SPEED;
    typedef u32 (ABI *StateFn)(uptr,u32);((StateFn)(base+0x2b1960u))(actor,2u);
    typedef void (ABI *QueueFn)(uptr,u32,float);((QueueFn)(base+0x29f980u))(actor,6u,0.f);
    slide_actor=actor;slide_array=cache_array;slide_active=slide_pending=1;slide_armed=0;slide_wait=0;slide_elapsed=slide_clock=0.f;
    slide_arc_reset(actor);
    if(slide_notes++<24u)log_text("TERRA SUPERGLIDE TAP: slide009, locked stick/facing direction, speed16 duration39; release does not shorten; native collision; ordinary Glide retained");
}
static void ABI slide_control(uptr actor,uptr dir){
    uptr pad=base+0x298ca90u;
    int local=actor==r64(base+SORA_RVA)&&memory(actor,0x448,0)&&memory(pad,0x18,1);
    if(local&&cache_choice<0&&main_super_scope(actor))motion_gate(actor,action_choice);
    if(local){actions_tick(actor);if(!(r32(pad+4)&0x10u))slide_armed=1;}
    if(actions_ready&&actions_scope(actor)&&memory(dir,16,0)&&memory(pad,0x18,1)){
        u32 press=r32(pad+8),request=r32(actor+0x164)&0xffffu,state=r32(actor+0x70),count=r32(actor+0x178);
        if((press&0x10u)&&!slide_active){
            u32 reason=0;float x=slide_float(dir),z=slide_float(dir+8),tilt=slide_float(dir+12),height=slide_float(actor+0x3d4);
            if(!slide_armed)reason|=1u;
            if(state!=1u&&state!=2u)reason|=2u;
            if(!slide_finite(height)||height<=50.f)reason|=4u;
            if(!(r32(base+0x2d5ec10u)&0x100u))reason|=8u;
            if(!slide_free_request(request))reason|=16u;
            if(!slide_finite(x)||!slide_finite(z)||!slide_finite(tilt)||tilt<0.f||x*x+z*z>4.f)reason|=32u;
            if(r32(pad+4)&0x00140000u)reason|=64u;
            u32 command=r32(base+0x2d53a40u);if((command&0xffu)&&!(command&0x01000000u))reason|=128u;
            if(count&&(count!=1u||!slide_free_request(r32(actor+0x17c)&0xffffu)||(r32(actor+0x17c)&0x40000000u)))reason|=256u;
            uptr work=decode(r32(actor+0x148));
            if(!memory(work+0x100,4,0)||!slide_finite(slide_float(work+0x100))||slide_float(work+0x100)>0.f)reason|=512u;
            typedef int (ABI *CanFn)(uptr);
            if(!reason&&!((CanFn)(base+0x297870u))(actor))reason|=1024u;
            if(!reason&&(!memory(actor+0x160,0x2c,1)||!memory(actor+0x3b0,0x28,1)||!variant_write(1u,1)))reason|=2048u;
            if(!reason)slide_start(actor,dir);
            else if(slide_rejections++<20u)log_number("TERRA SUPERGLIDE TAP rejection mask=",reason);
        }
    }
    u32 mask=0;
    if(local&&main_super_scope(actor)){
        if(slide_active)mask=0x16u;
        else if((r32(actor+0x70)==1u||r32(actor+0x70)==2u)&&slide_free_request(r32(actor+0x164)&0xffffu)&&(r32(base+0x2d5ec10u)&0x100u)&&!(r32(pad+4)&0x00140000u))mask=0x10u;
    }
    if(mask){
        static const u32 fields[4]={4,8,16,20};u32 saved[4];
        for(unsigned i=0;i<4;i++){saved[i]=r32(pad+fields[i])&mask;*(volatile u32*)(pad+fields[i])=r32(pad+fields[i])&~mask;}
        slide_control_original(actor,dir);
        for(unsigned i=0;i<4;i++)*(volatile u32*)(pad+fields[i])=(r32(pad+fields[i])&~mask)|saved[i];
    }else slide_control_original(actor,dir);
    if(local)actions_tick(actor);
}
static float ABI slide_move(uptr actor,uptr out){
    if(!slide_active||actor!=slide_actor||!actions_scope(actor))return slide_move_original(actor,out);
    slide_tick(actor);
    if(!slide_active||slide_pending||r32(actor+0x70)!=2u||!memory(out,16,1))return slide_move_original(actor,out);
    float dt=slide_float(base+0x233fbdcu);
    if(!slide_finite(dt)||dt<0.f||dt>4.f){slide_end(0);return slide_move_original(actor,out);}
    if(dt==0.f){zeros((void*)out,16);return slide_float(actor+0x124);}
    float remaining=SLIDE_DURATION-slide_elapsed;if(dt>remaining)dt=remaining;
    if(dt<=0.f){slide_end(1);return slide_move_original(actor,out);}
    float move[4]={slide_vx*dt,0.f,slide_vz*dt,SLIDE_SPEED*dt};copy((void*)out,move,16);
    float velocity[4]={slide_vx,0.f,slide_vz,SLIDE_SPEED};copy((void*)(actor+0x3c0),velocity,16);
    slide_arc_reset(actor);slide_elapsed+=dt;if(slide_elapsed>=SLIDE_DURATION)slide_end(1);
    return slide_float(actor+0x124);
}
static int ABI slide_glide(uptr actor){
    uptr caller=(uptr)__builtin_return_address(0);
    if(main_super_scope(actor)&&caller==base+0x2b275eu)return 0;
    if(slide_active&&actor==slide_actor&&actions_scope(actor)&&caller==base+0x2b26ceu)return 0;
    return slide_glide_original(actor);
}
static void slide_jump(u8*out,uptr target){out[0]=0xff;out[1]=0x25;out[2]=out[3]=out[4]=out[5]=0;copy(out+6,&target,8);}
static void actions_install(void){
    if(actions_attempted||remove_mode)return;actions_attempted=1;
    uptr a=base+0x2a6220u,g=base+0x2b2d30u,m=base+0x2af6a0u;
    static const u8 normal_ctor[14]={0x40,0x53,0x48,0x83,0xec,0x20,0x48,0x8b,0xd9,0xe8,0x62,0x06,0,0};
    static const u8 super_ctor[14]={0x40,0x53,0x48,0x83,0xec,0x20,0x48,0x8b,0xd9,0xe8,0xd2,0x05,0,0};
    if(!memory(a,17,0)||!equal((void*)a,slide_control_prefix,17)||!memory(g,15,0)||!equal((void*)g,slide_glide_prefix,15)
        ||!memory(m,16,0)||!equal((void*)m,slide_move_prefix,16)
        ||!memory(base+0x2b26c0u,14,0)||!equal((void*)(base+0x2b26c0u),normal_ctor,14)
        ||!memory(base+0x2b2750u,14,0)||!equal((void*)(base+0x2b2750u),super_ctor,14)
        ||!memory(base+0x2b1960u,14,0)||!equal((void*)(base+0x2b1960u),slide_state_prefix,14)
        ||!memory(base+0x297870u,32,0)||!equal((void*)(base+0x297870u),slide_can_bytes,32)
        ||!memory(base+0x29f980u,13,0)||!equal((void*)(base+0x29f980u),slide_queue_prefix,13)
        ||!memory(base+0x233fbdcu,4,0)||!memory(base+0x554a88u,8,0)||!memory(base+0x298ca90u,0x18,1)){
        log_text("TERRA TAP SLIDE UNAVAILABLE: native hook admission failed; combo/cast poses remain usable");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    copy(page,slide_control_prefix,10);page[10]=0x48;page[11]=0xb8;uptr cookie=base+0x554a88u;copy(page+12,&cookie,8);
    page[20]=0x48;page[21]=0x8b;page[22]=0;slide_jump(page+23,a+17);
    copy(page+128,slide_glide_prefix,15);slide_jump(page+143,g+15);
    copy(page+256,slide_move_prefix,16);slide_jump(page+272,m+16);
    u32 old_page=0,old_code=0,old_glide=0,old_move=0,unused=0;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,320);
    if(!kVirtualProtect((void*)a,17,0x40u,&old_code)){kVirtualFree(page,0,0x8000u);return;}
    if(!kVirtualProtect((void*)g,15,0x40u,&old_glide)){kVirtualProtect((void*)a,17,old_code,&unused);kVirtualFree(page,0,0x8000u);return;}
    if(!kVirtualProtect((void*)m,16,0x40u,&old_move)){
        kVirtualProtect((void*)g,15,old_glide,&unused);kVirtualProtect((void*)a,17,old_code,&unused);kVirtualFree(page,0,0x8000u);return;
    }
    slide_control_original=(SlideControlFn)(uptr)page;slide_glide_original=(SlideGlideFn)(uptr)(page+128);slide_move_original=(SlideMoveFn)(uptr)(page+256);
    u8 patch[17];for(unsigned i=0;i<17;i++)patch[i]=0x90;
    slide_jump(patch,(uptr)slide_move);copy((void*)m,patch,16);kFlushInstructionCache((uptr)-1,(void*)m,16);kVirtualProtect((void*)m,16,old_move,&unused);
    slide_jump(patch,(uptr)slide_glide);copy((void*)g,patch,15);kFlushInstructionCache((uptr)-1,(void*)g,15);kVirtualProtect((void*)g,15,old_glide,&unused);
    slide_jump(patch,(uptr)slide_control);copy((void*)a,patch,17);kFlushInstructionCache((uptr)-1,(void*)a,17);kVirtualProtect((void*)a,17,old_code,&unused);
    actions_ready=1;log_text("TERRA TAP SUPERGLIDE READY: main only, fresh Square with native Superglide equipped; finite009 slide; ordinary Glide and numbered profiles retained");
}
