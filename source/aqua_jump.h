/* Adjust only a native normal/High Jump launch that this actor just completed.
 * KH1 creates its own arc first; retain its launch height, collision and gravity. */
typedef float (ABI *JumpLaunchFn)(uptr,uptr);
static JumpLaunchFn jump_original;
static int jump_attempted,jump_ready;
static u32 jump_notes;
#define AQUA_JUMP_HEIGHT_FACTOR 1.25f
#define AQUA_JUMP_TIME_FACTOR 1.118033988749895f
static const u8 jump_prefix[18]={0x48,0x89,0x74,0x24,0x10,0x57,0x48,0x83,0xec,0x30,0xf3,0x0f,0x10,0x81,0xb0,0x03,0,0};
static int jump_scope(uptr actor){
    return jump_ready&&main_aqua_air()&&movement_scope(actor)&&!air_dodge_active;
}
static float ABI jump_launch(uptr actor,uptr out){
    int watch=jump_scope(actor)&&r32(actor+0x70)==1u
        &&((r32(actor+0x164)&0xffffu)==4u||(r32(actor+0x164)&0xffffu)==9u);
    float result=jump_original(actor,out);
    if(watch&&jump_scope(actor)&&r32(actor+0x70)==2u&&air_float(actor+0x3b0)==0.f
        &&((r32(actor+0x164)&0xffffu)==4u||(r32(actor+0x164)&0xffffu)==9u)
        &&memory(actor+0x3b8,8,1)){
        float duration=air_float(actor+0x3b8),height=air_float(actor+0x3bc);
        if(air_finite(duration)&&duration>0.f&&duration<1000.f&&air_finite(height)&&height<0.f&&height>-10000.f){
            air_write_float(actor+0x3b8,duration*AQUA_JUMP_TIME_FACTOR);
            air_write_float(actor+0x3bc,height*AQUA_JUMP_HEIGHT_FACTOR);
            if(jump_notes++<12u)log_text("AQUA MAIN JUMP: native launch height1.25, native arc time sqrt1.25; normal and High Jump supported");
        }
    }
    return result;
}
static void jump_install(void){
    if(jump_attempted||remove_mode)return;jump_attempted=1;
    uptr a=base+0x2afda0u;
    if(!memory(a,18,0)||!equal((void*)a,jump_prefix,18)){
        log_text("AQUA JUMP BOOST UNAVAILABLE: native launch anchor did not match");return;
    }
    u8*page=kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page)return;
    copy(page,jump_prefix,18);magic_jump(page+18,a+18);
    u32 old_page,old,unused;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,32);
    if(!kVirtualProtect((void*)a,18,0x40u,&old)){kVirtualFree(page,0,0x8000u);return;}
    jump_original=(JumpLaunchFn)(uptr)page;
    u8 code[18];for(unsigned i=0;i<18;i++)code[i]=0x90;magic_jump(code,(uptr)jump_launch);copy((void*)a,code,18);
    kFlushInstructionCache((uptr)-1,(void*)a,18);kVirtualProtect((void*)a,18,old,&unused);
    jump_ready=1;log_text("AQUA JUMP READY: main normal/High Jump native launch height+25 percent; numbered/native jumps retained");
}
