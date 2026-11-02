/* Full Fire-body variants in the original Blizzard motion slots. Spell IDs,
 * event descriptors/keys, release scripts and native queue are never changed. */
static u32 blizzard_notes;
static int blizzard_pose(unsigned bit,int on){
    unsigned slot=bit==1u?55u:80u;
    if(!cache_actor||cache_choice!=1||r64(base+SORA_RVA)!=cache_actor
        ||!memory(cache_actor,0x378,0)||(r32(cache_actor+0x374)&3u)!=1u
        ||decode(r32(cache_actor+0x1d4))!=cache_array)return 0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(aqua_motions[i].normal_slot==slot){
        const AquaMotion*d=aqua_motions+i;Binding*b=cached+i,again;int failure;
        if(!b->motion||!memory(cache_array+b->slot*4u,4,0)||r32(cache_array+b->slot*4u)!=b->handle
            ||!valid_motion(b->motion,d,&again,&failure))return 0;
        for(unsigned j=0;j<d->part_count;j++)if(!d->parts[j].blizzard||again.parts[j]!=b->parts[j])return 0;
        for(unsigned j=0;j<d->part_count;j++){
            const AquaPart*p=d->parts+j;copy((void*)b->parts[j],on?p->blizzard:part_data(p,1),p->size);
        }
        return 1;
    }
    return 0;
}
static void blizzard_tick(uptr actor,int choice){
    if(actor!=cache_actor||!memory(actor,0x448,0)||r64(base+SORA_RVA)!=actor
        ||(r32(actor+0x374)&3u)!=1u||decode(r32(actor+0x1d4))!=cache_array)return;
    u32 wanted=0;
    if(choice==1&&cache_choice==1&&!remove_mode&&!magic_conflict&&!r32(base+0x298c9a0u)
        &&!r32(actor+0x440)&&!(r32(actor+0x444)&1u)&&cast_cached(actor,cache_array,1)){
        u32 request=r32(actor+0x164)&0xffffu,count=r32(actor+0x178);
        if(count&&count<=5u){
            u32 next=r32(actor+0x17c),logical=next&0xffffu;
            if(!(next&0x40000000u)&&((logical>=0x36u&&logical<=0x3fu)||(logical>=0x83u&&logical<=0x8au)))request=logical;
        }
        wanted=request==0x37u?1u:request==0x84u?2u:0u;
    }
    for(unsigned bit=1u;bit<=2u;bit<<=1u)if((wanted^blizzard_active)&bit){
        if(blizzard_pose(bit,(wanted&bit)!=0)){
            blizzard_active=(blizzard_active&~bit)|(wanted&bit);
            if((wanted&bit)&&blizzard_notes++<24u)log_text("AQUA BLIZZARD VISUAL: Fire body only; original Blizzard request, events and queue preserved");
        }
    }
}
