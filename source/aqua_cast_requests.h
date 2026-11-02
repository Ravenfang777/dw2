/* Actor-local original-sized request tables. Numbered profiles retain v13's
 * Thunder split. Main Aqua additionally routes Stop/Aero to Gravity's family.
 * Only body assignments and lookup pointers change; native spell logic stays.
 */
typedef struct {u32 current,original,next;int bank,choice;} CastBinding;
static uptr cast_actor[2],cast_array[2];
static u32 cast_original[2],cast_after_handle[2][2];
static int cast_bank=-1;
static const u8*cast_data(const AquaRequestTable*d,int choice){return choice==1?d->main_after:d->after;}

static int cast_admit(uptr actor,uptr array,int bank,int choice,CastBinding*out){
    const AquaRequestTable*d=aqua_requests+bank;
    u32 current=r32(actor+0x1d8),original=current;uptr p=decode(current);
    if(p==(uptr)d->after||p==(uptr)d->main_after){
        if(cast_actor[bank]!=actor||cast_array[bank]!=array||!cast_original[bank])return 0;
        original=cast_original[bank];p=decode(original);
    }
    if(!memory(p,d->bytes,0)||!equal((void*)p,d->before,d->bytes)||!memory(actor+0x1d8,4,1))return 0;
    unsigned kind=choice==1;u32 after=cast_after_handle[bank][kind];
    if(choice&&!after){
        typedef u32 (ABI *CastHandleFn)(const void*);
        if(!memory(base+HANDLE_RVA,16,0))return 0;
        const u8*desired=cast_data(d,choice);
        after=((CastHandleFn)(base+HANDLE_RVA))(desired);
        if(!after||decode(after)!=(uptr)desired)return 0;
        cast_after_handle[bank][kind]=after;
    }
    out->current=current;out->original=original;out->next=choice?after:original;out->bank=bank;out->choice=choice;
    return 1;
}
static int cast_cached(uptr actor,uptr array,int choice){
    if(cast_bank<0||cast_bank>1||cast_actor[cast_bank]!=actor||cast_array[cast_bank]!=array)return 0;
    const AquaRequestTable*d=aqua_requests+cast_bank;
    u32 wanted=choice?cast_after_handle[cast_bank][choice==1]:cast_original[cast_bank];
    if(!wanted||r32(actor+0x1d8)!=wanted)return 0;
    if(choice)return decode(wanted)==(uptr)cast_data(d,choice);
    uptr p=decode(wanted);return memory(p,d->bytes,0)&&equal((void*)p,d->before,d->bytes);
}
static void cast_publish(uptr actor,uptr array,const CastBinding*b){
    if(b->next!=b->current){
        *(volatile u32*)(actor+0x1d8)=b->next;
        log_text(b->next==b->original?"AQUA CAST REQUESTS RESTORED: original actor lookup":
            b->choice==1?"AQUA MAIN CAST REQUESTS: Stop/Aero use Gravity ground317 air390; Thunder split retained":
            "AQUA TEST CAST REQUESTS: numbered profiles retain v13 spell routing and poses");
    }
    cast_actor[b->bank]=actor;cast_array[b->bank]=array;cast_original[b->bank]=b->original;cast_bank=b->bank;
}

/* Native Blizzard keeps its own logical spell id. Main Aqua borrows both
 * Fire pose phases, inserting only the visual recovery before its existing
 * terminal request. MP, element, projectile and target scripts remain native. */
static int cast_append_ready,cast_followup_notes;
static void cast_followup(uptr actor){
    if(remove_mode||cache_choice!=1||cache_actor!=actor||r64(base+SORA_RVA)!=actor||!memory(actor,0x448,0)
        ||(r32(actor+0x374)&3u)!=1u||decode(r32(actor+0x1d4))!=cache_array
        ||r32(base+0x298c9a0u)||r32(actor+0x440)||(r32(actor+0x444)&1u)
        ||!cast_cached(actor,cache_array,1))return;
    u32 count=r32(actor+0x178),current=r32(actor+0x164)&0xffffu;
    if(!count||count>2u)return;
    u32 first=r32(actor+0x17c)&0xffffu;
    u32 spell=count==2u?first:current;
    if(spell!=0x37u&&spell!=0x84u)return;
    uptr tail=actor+0x17c+(count-1u)*16u;
    if(!(r32(tail)&0x40000000u)||!memory(actor+0x178,(count+1u)*16u+4u,1))return;
    static const u8 prefix[13]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xf9};
    if(!cast_append_ready)cast_append_ready=memory(base+0x29fa30u,13,0)&&equal((void*)(base+0x29fa30u),prefix,13)?1:-1;
    if(cast_append_ready<0)return;
    u8 terminal[16];copy(terminal,(void*)tail,16);
    typedef uptr (ABI *AppendFn)(uptr,u32,float);
    ((AppendFn)(base+0x29fa30u))(actor,spell==0x37u?0x3du:0x8au,0.f);
    if(r32(actor+0x178)!=count+1u)return;
    copy((void*)tail,(void*)(tail+16),16);copy((void*)(tail+16),terminal,16);
    if(cast_followup_notes++<16)log_text("AQUA BLIZZARD: native spell retained; Fire-style release and recovery queued before original terminal");
}
