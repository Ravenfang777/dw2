/* Steam Global attachment functions, decoded from the user's executable.
 * 29EA00(actor, code, matrix): code 0x2000|n copies world matrix n.
 * 29EB20(actor, code, fraction, point): code 0x30 is the weapon attachment.
 * Redirect that attachment only in Aqua's native cast requests. No effect,
 * projectile, MP, damage, target, weapon-model or actor-state tables are edited.
 */
extern void* (ABI *kVirtualAlloc)(void*,usize,u32,u32) HIDDEN;
extern int (ABI *kVirtualFree)(void*,usize,u32) HIDDEN;
extern int (ABI *kVirtualProtect)(void*,usize,u32,u32*) HIDDEN;
extern int (ABI *kFlushInstructionCache)(uptr,const void*,usize) HIDDEN;

typedef void (ABI *MatrixFn)(uptr,u32,float*);
typedef void (ABI *PointFn)(uptr,u32,float,float*);
static MatrixFn magic_matrix_original;
static PointFn magic_point_original;
static int magic_attempted,magic_ready,magic_disabled,magic_conflict;
static u32 magic_matrix_notes,magic_point_notes;
static const u8 matrix_prefix[15]={0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x74,0x24,0x10,0x57,0x48,0x83,0xec,0x20};
static const u8 point_prefix[16]={0x40,0x53,0x55,0x57,0x48,0x81,0xec,0x80,0,0,0,0x0f,0x29,0x74,0x24,0x60};

static int magic_scope(uptr actor,u32 code){
    if(!magic_ready||magic_disabled||magic_conflict||code!=0x30u||cache_choice<1||actor!=cache_actor||!actor)return 0;
    if(r64(base+SORA_RVA)!=actor||!memory(actor,0x448,0)||(r32(actor+0x374)&3u)!=1u)return 0;
    if(decode(r32(actor+0x1d4))!=cache_array||r32(base+0x298c9a0u)||r32(actor+0x440)||(r32(actor+0x444)&1u))return 0;
    u32 action=r32(actor+0x164)&0xfffu;
    return (action>=0x36u&&action<=0x3du)||(action>=0x83u&&action<=0x8au);
}
static int magic_matrix_valid(const float*m){
    for(unsigned i=0;i<16;i++){u32 bits;copy(&bits,m+i,4);if((bits&0x7f800000u)==0x7f800000u)return 0;}
    return 1;
}
static void ABI magic_matrix(uptr actor,u32 code,float*out){
    if(magic_scope(actor,code)){
        magic_matrix_original(actor,0x20ceu,out); /* direct Sora LEFT palm 206 */
        if(magic_matrix_valid(out)){
            if(magic_matrix_notes++<16)log_number("AQUA HAND MAGIC MATRIX: native request=",r32(actor+0x164)&0xfffu);
            return;
        }
    }
    magic_matrix_original(actor,code,out);
}
static void ABI magic_point(uptr actor,u32 code,float fraction,float*out){
    if(magic_scope(actor,code)){
        float hand[16] __attribute__((aligned(16)));
        magic_matrix_original(actor,0x20ceu,hand);
        if(magic_matrix_valid(hand)){
            copy(out,hand+12,16);
            if(magic_point_notes++<16)log_number("AQUA HAND MAGIC ORIGIN: native request=",r32(actor+0x164)&0xfffu);
            return;
        }
    }
    magic_point_original(actor,code,fraction,out);
}
static void magic_jump(u8*out,uptr target){
    static const u8 op[6]={0xff,0x25,0,0,0,0};copy(out,op,6);copy(out+6,&target,8);
}
static void magic_install(void){
    if(magic_attempted||magic_disabled||remove_mode)return;magic_attempted=1;
    uptr a=base+0x29ea00u,b=base+0x29eb20u;
    if(!memory(a,sizeof(matrix_prefix),0)||!memory(b,sizeof(point_prefix),0)||!memory(base+0x298c9a0u,4,0)
        ||!equal((void*)a,matrix_prefix,sizeof(matrix_prefix))||!equal((void*)b,point_prefix,sizeof(point_prefix))){
        log_text("AQUA HAND MAGIC UNAVAILABLE: attachment function bytes differ; native spell attachments retained");return;
    }
    u8*page=(u8*)kVirtualAlloc(NULL,4096,0x3000u,4u);if(!page){log_text("AQUA HAND MAGIC UNAVAILABLE: trampoline allocation failed");return;}
    copy(page,matrix_prefix,sizeof(matrix_prefix));magic_jump(page+sizeof(matrix_prefix),a+sizeof(matrix_prefix));
    copy(page+64,point_prefix,sizeof(point_prefix));magic_jump(page+64+sizeof(point_prefix),b+sizeof(point_prefix));
    u32 old_page=0,old_code=0,unused=0;
    if(!kVirtualProtect(page,4096,0x20u,&old_page)){kVirtualFree(page,0,0x8000u);return;}
    kFlushInstructionCache((uptr)-1,page,128);
    /* The two entries share one code page: protect and restore the span once. */
    usize code_span=b+sizeof(point_prefix)-a;
    if(!kVirtualProtect((void*)a,code_span,0x40u,&old_code)){kVirtualFree(page,0,0x8000u);return;}
    /* Both stolen spans contain whole instructions with no RIP-relative data,
       calls or branches. The exact 15/16-byte spans are admitted as one pair. */
    magic_matrix_original=(MatrixFn)(uptr)page;magic_point_original=(PointFn)(uptr)(page+64);
    u8 aa[15],bb[16];for(unsigned i=0;i<sizeof(aa);i++)aa[i]=0x90;for(unsigned i=0;i<sizeof(bb);i++)bb[i]=0x90;
    magic_jump(aa,(uptr)magic_matrix);magic_jump(bb,(uptr)magic_point);
    copy((void*)a,aa,sizeof(aa));copy((void*)b,bb,sizeof(bb));
    kFlushInstructionCache((uptr)-1,(void*)a,sizeof(aa));kFlushInstructionCache((uptr)-1,(void*)b,sizeof(bb));
    kVirtualProtect((void*)a,code_span,old_code,&unused);
    magic_ready=1;
    log_text("AQUA HAND MAGIC READY: weapon attachment 0x30 -> LEFT palm 206; native position and effect matrix; all five Aqua profiles");
}
