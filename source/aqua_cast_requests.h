/* Native Steam dispatch is request=0x36+spell (ground), 0x83+spell
 * (air): Fire=0, Blizzard=1, Thunder=2, Cure=3. Thunder and Cure share
 * one physical record. Give Thunder the existing alternate cast record
 * through an actor-local request-table pointer. No table/count expansion,
 * native code hook, or write to the original request table is needed.
 */
typedef struct {u32 current,original,next;int bank;} CastBinding;
static uptr cast_actor[2],cast_array[2];
static u32 cast_original[2],cast_after_handle[2];
static int cast_bank=-1;

static int cast_admit(uptr actor,uptr array,int bank,int choice,CastBinding*out){
    const AquaRequestTable*d=aqua_requests+bank;
    u32 current=r32(actor+0x1d8),original=current;uptr p=decode(current);
    if(p==(uptr)d->after){
        if(cast_actor[bank]!=actor||cast_array[bank]!=array||!cast_original[bank])return 0;
        original=cast_original[bank];p=decode(original);
    }
    if(!memory(p,d->bytes,0)||!equal((void*)p,d->before,d->bytes)||!memory(actor+0x1d8,4,1))return 0;
    u32 after=cast_after_handle[bank];
    if(choice&&!after){
        typedef u32 (ABI *CastHandleFn)(const void*);
        if(!memory(base+HANDLE_RVA,16,0))return 0;
        after=((CastHandleFn)(base+HANDLE_RVA))(d->after);
        if(!after||decode(after)!=(uptr)d->after)return 0;
        cast_after_handle[bank]=after;
    }
    out->current=current;out->original=original;out->next=choice?after:original;out->bank=bank;
    return 1;
}
static int cast_cached(uptr actor,uptr array,int choice){
    if(cast_bank<0||cast_bank>1||cast_actor[cast_bank]!=actor||cast_array[cast_bank]!=array)return 0;
    const AquaRequestTable*d=aqua_requests+cast_bank;
    u32 wanted=choice?cast_after_handle[cast_bank]:cast_original[cast_bank];
    if(!wanted||r32(actor+0x1d8)!=wanted)return 0;
    if(choice)return decode(wanted)==(uptr)d->after;
    uptr p=decode(wanted);return memory(p,d->bytes,0)&&equal((void*)p,d->before,d->bytes);
}
static void cast_publish(uptr actor,uptr array,const CastBinding*b){
    if(b->next!=b->current){
        *(volatile u32*)(actor+0x1d8)=b->next;
        log_text(b->next==b->original?"AQUA CAST REQUESTS RESTORED: original actor lookup":"AQUA CAST REQUESTS: Thunder uses its own ground/air poses; other request words retained");
    }
    cast_actor[b->bank]=actor;cast_array[b->bank]=array;cast_original[b->bank]=b->original;cast_bank=b->bank;
}
