/* Standalone Panacea ability gate for eleven Terra FK motion profiles.
 * Native capacities and event/input/movement controllers remain unchanged.
 * Scope: Steam Global build identified by the user's existing v52 reference.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef __UINTPTR_TYPE__ uptr;
typedef __SIZE_TYPE__ usize;
typedef unsigned short w16;
#define ABI __attribute__((ms_abi))
#define HIDDEN __attribute__((visibility("hidden")))
#define EXPORT __attribute__((visibility("default")))
#define NULL ((void*)0)

extern uptr (ABI *kGetModuleHandleA)(const char*) HIDDEN;
extern u32 (ABI *kGetModuleFileNameW)(uptr,w16*,u32) HIDDEN;
extern usize (ABI *kVirtualQuery)(const void*,void*,usize) HIDDEN;
extern uptr (ABI *kCreateFileW)(const w16*,u32,u32,void*,u32,u32,uptr) HIDDEN;
extern int (ABI *kWriteFile)(uptr,const void*,u32,u32*,void*) HIDDEN;
extern int (ABI *kCloseHandle)(uptr) HIDDEN;
extern u32 (ABI *kGetPrivateProfileIntW)(const w16*,const w16*,int,const w16*) HIDDEN;
extern void* (ABI *kVirtualAlloc)(void*,usize,u32,u32) HIDDEN;
extern int (ABI *kVirtualFree)(void*,usize,u32) HIDDEN;
extern int (ABI *kVirtualProtect)(void*,usize,u32,u32*) HIDDEN;
extern int (ABI *kFlushInstructionCache)(uptr,const void*,usize) HIDDEN;

#include "terra_data.h"
#define TERRA_ID 116u
#define TERRA_OFF (TERRA_ID|0x80u)
#define TERRA_ABILITIES 11u
#define ABILITY_SLOTS 48u
#define TABLE_ROWS 127u
#define TABLE_BYTES (TABLE_ROWS*12u)
#define STEAM_STAMP 1721645006u
#define SORA_RVA 0x2537e48u
#define BANK_RVA 0x2ee3980u
#define TABLE_RVA 0x2d36d48u
#define HANDLE_RVA 0x38ad90u
#define SAVE_PTR_RVA 0x2868ba0u
#define SAVE_RVA 0x2de9360u

static uptr base,log_handle;
static int checked,ready,remove_mode,conflict_reported,full_reported;
static u32 requested_page=1,profile_override,reported_layout=0xffffffffu;
static u8 table[TABLE_BYTES] __attribute__((aligned(16)));
static u8 encoded_name[TERRA_ABILITIES][16],encoded_help[TERRA_ABILITIES][128];
static u32 name_handle[TERRA_ABILITIES],help_handle[TERRA_ABILITIES];
static uptr choice_save;
static u32 previous_equipped_mask;
static const char *profile_names[TERRA_ABILITIES]={"terra","terra 1","terra 2","terra 3","terra 4","terra 5","terra 6","terra 7","terra 8","terra 9","terra 10"};
static const char *profile_help[TERRA_ABILITIES]={"Terra Ground 300 411 332 Air 305 306 353","Terra Ground 045 217 218 Air 332 357 361","Terra Ground 362 363 350 Air 370 371 372","Terra Ground 373 315 316 Air 317 318 391","Terra Ground 390 427 392 Air 393 428 399","Terra Ground 411 352 353 Air 351 304 308","Terra Ground 500 501 503 Air 510 511 512","Terra Ground 513 514 507 Air 508 517 518","Terra Ground 519 550 650 Air 557 405 616","Terra Ground 618 619 613 Air 602 603 604","Terra Ground 605 606 617 Air 614 615 620"};
static int table_reported;
static w16 log_path[1024],ini_path[1024];
/* A real DIR64 relocation keeps the PE image independently relocatable. */
static void *volatile relocation_anchor __attribute__((used))=&table[0];
typedef struct {uptr motion,parts[TERRA_PART_COUNT];u32 handle,slot,contiguous;} Binding;
static Binding cached[TERRA_MOTION_COUNT];
static uptr cache_actor,cache_array,reported_wait_array,cache_low,cache_high;
static u32 cache_array_bytes,cache_count;
static int cache_choice=-1,pending_reported,last_choice=-1;
static int action_choice,slide_active;
static u32 action_variant_mask;
static void actions_install(void);
static void actions_prepare(uptr actor,int choice);
static void actions_tick(uptr actor);
static void actions_forget(void);
static u32 frame_serial,admission_due,admission_scans,rebind_notes,suspend_notes;
static int admission_waiting_idle;
static uptr admission_actor,admission_array;static int admission_choice=-1;
static u32 last_action=0xffffffffu,action_logs;

static u32 r32(uptr p){return *(volatile u32*)p;}
static u64 r64(uptr p){return *(volatile u64*)p;}
static u8 r8(uptr p){return *(volatile u8*)p;}
static void copy(void *dst,const void *src,usize n){u8*d=dst;const u8*s=src;for(usize i=0;i<n;i++)d[i]=s[i];}
static int equal(const void*a,const void*b,usize n){const u8*x=a,*y=b;while(n>=8){if(*(const u64*)x!=*(const u64*)y)return 0;x+=8;y+=8;n-=8;}while(n--){if(*x++!=*y++)return 0;}return 1;}
static usize length(const char*s){usize n=0;while(s[n])n++;return n;}
static void zeros(void*p,usize n){u8*d=p;for(usize i=0;i<n;i++)d[i]=0;}

typedef struct {uptr base,allocation;u32 allocation_protect;u16 partition,pad;usize size;u32 state,protect,type,pad2;} MemInfo;
static int memory(uptr p,usize n,int writing){
    if(p<0x10000u||!n||p+n<p)return 0;
    uptr stop=p+n;
    while(p<stop){MemInfo m;zeros(&m,sizeof(m));
        if(kVirtualQuery((const void*)p,&m,sizeof(m))!=sizeof(m)||m.state!=0x1000u||!m.protect||(m.protect&0x101u))return 0;
        if(writing&&!(m.protect&0xccu))return 0;
        uptr end=m.base+m.size;if(end<=p)return 0;p=end<stop?end:stop;
    }return 1;
}
static void log_text(const char*s){if(!log_handle||log_handle==(uptr)-1)return;u32 done=0;kWriteFile(log_handle,s,(u32)length(s),&done,NULL);kWriteFile(log_handle,"\r\n",2,&done,NULL);}
static void log_number(const char*label,uptr value){
    char out[160];usize n=0;while(label[n]&&n<120){out[n]=label[n];n++;}
    out[n++]='0';out[n++]='x';int begun=0;
    for(int shift=60;shift>=0;shift-=4){unsigned v=(unsigned)((value>>shift)&15);if(v||begun||shift==0){out[n++]="0123456789ABCDEF"[v];begun=1;}}
    out[n]=0;log_text(out);
}
static void log_count(const char*label,u32 value){
    char out[160],digits[10];usize n=0;unsigned count=0;
    while(label[n]&&n<120){out[n]=label[n];n++;}
    do{digits[count++]=(char)('0'+value%10u);value/=10u;}while(value);
    while(count)out[n++]=digits[--count];out[n]=0;log_text(out);
}
static void path_for(w16*out,const char*name){
    u32 n=kGetModuleFileNameW(0,out,1000);if(!n||n>=1000){out[0]=0;return;}
    while(n&&out[n-1]!='\\'&&out[n-1]!='/')n--;
    for(usize i=0;name[i]&&n<1023;i++)out[n++]=(u8)name[i];out[n]=0;
}
static void encode(const char*text,u8*out,usize cap){
    usize n=0;for(;text[n]&&n+1<cap;n++){u8 c=(u8)text[n];
        if(c>='A'&&c<='Z')out[n]=(u8)(c+0xea);
        else if(c>='a'&&c<='z')out[n]=(u8)(c+0xe4);
        else if(c>='0'&&c<='9')out[n]=(u8)(c+0xf1);
        else out[n]=1; /* The supplied helper maps a space to 01. */
    }out[n]=0;
}
static void clear_binding(void){cache_actor=cache_array=cache_low=cache_high=0;cache_array_bytes=cache_count=0;cache_choice=-1;pending_reported=0;zeros(cached,sizeof(cached));}
static uptr decode(u32 h){
    if(!h)return 0;
    if(!(h&0x80000000u))return (uptr)h;
    unsigned i=(h&0x7fffffffu)>>25;
    uptr address=base+BANK_RVA+(uptr)i*8;
    if(i>=64)return 0; /* The fixed game-image bank table was admitted once. */
    uptr bank=(uptr)r64(address);return bank?bank+(h&0x1ffffffu):0;
}
static uptr relative_or_handle(uptr motion,u32 value,unsigned raw_bytes){
    if(value&&value<raw_bytes)return motion+value;
    return decode(value);
}
/* Event key streams have a descriptor indirection. Keep every live encoded
 * descriptor pointer untouched and verify their shape/contiguous key layout. */
static uptr motion_part(uptr motion,const TerraMotion*d,const TerraPart*p,int group){
    if(p->field!=60u)return relative_or_handle(motion,r32(motion+p->field),d->raw_bytes);
    if(!d->event_count||!d->event_schema)return 0;
    uptr descriptors=relative_or_handle(motion,r32(motion+60),d->raw_bytes);
    usize bytes=d->event_count*12u+4u;
    if(!(group&&descriptors>=cache_low&&descriptors+bytes<=cache_high)&&!memory(descriptors,bytes,0))return 0;
    uptr first=0;
    for(unsigned i=0;i<d->event_count;i++){
        const u32*s=d->event_schema+i*3u;uptr at=descriptors+i*12u;
        if(r32(at)!=s[0]||r32(at+4)!=s[1])return 0;
        uptr keys=relative_or_handle(motion,r32(at+8),d->raw_bytes);
        if(!i)first=keys;
        if(keys!=first+s[2]-d->event_schema[2])return 0;
    }
    return r32(descriptors+d->event_count*12u)==0xffffffffu?first:0;
}
static uptr save_block(void){
    uptr p=(uptr)r64(base+SAVE_PTR_RVA);
    if(p<0x10000u)p=base+SAVE_RVA;
    if(!memory(p,0x74,1)||!r8(p+4)||!r8(p+5)||!r8(p+6))return 0;
    return p;
}
static int own_id(u8 value){u32 id=value&0x7fu;return id>=TERRA_ID&&id<TERRA_ID+TERRA_ABILITIES;}
static const u8 *part_data(const TerraPart *part,int choice){return choice>0?part->after[choice-1]:part->before;}
static int part_known(uptr p,const TerraPart *part){
    if(equal((void*)p,part->before,part->size))return 1;
    for(unsigned i=0;i<TERRA_PROFILE_COUNT;i++)if(equal((void*)p,part->after[i],part->size))return 1;
    if(part->variant&&equal((void*)p,part->variant,part->size))return 1;
    return 0;
}
static int ensure_table(void){
    uptr current=(uptr)r64(base+TABLE_RVA);
    if(current==(uptr)table)return 1;
    if(!memory(current,65*12,0)||!memory(base+TABLE_RVA,8,1))return 0;
    if(!name_handle[0]||!help_handle[0]){
        if(!memory(base+HANDLE_RVA,16,0))return 0;
        typedef u32 (ABI *HandleFn)(const void*);
        HandleFn handle=(HandleFn)(base+HANDLE_RVA);
        for(unsigned i=0;i<TERRA_ABILITIES;i++){
            encode(profile_names[i],encoded_name[i],sizeof(encoded_name[i]));
            encode(profile_help[i],encoded_help[i],sizeof(encoded_help[i]));
            name_handle[i]=handle(encoded_name[i]);help_handle[i]=handle(encoded_help[i]);
            if(!name_handle[i]||!help_handle[i]||decode(name_handle[i])!=(uptr)encoded_name[i]||decode(help_handle[i])!=(uptr)encoded_help[i]){
                zeros(name_handle,sizeof(name_handle));zeros(help_handle,sizeof(help_handle));return 0;
            }
        }
    }
    u8 snapshot[65*12];copy(snapshot,(void*)current,sizeof(snapshot));
    zeros(table,sizeof(table));copy(table,snapshot,sizeof(snapshot));
    for(unsigned i=0;i<TERRA_ABILITIES;i++){
        u8 *record=table+(TERRA_ID+i-1)*12;copy(record,snapshot+64*12,12);record[0]=0;
        u32 order=(u16)snapshot[64*12+2]|((u32)snapshot[64*12+3]<<8);order+=1+i;if(order>65535)order=65535;
        record[2]=(u8)order;record[3]=(u8)(order>>8);copy(record+4,name_handle+i,4);copy(record+8,help_handle+i,4);
    }
    if(r64(base+TABLE_RVA)!=current||!equal(snapshot,(void*)current,sizeof(snapshot)))return 0;
    *(volatile u64*)(base+TABLE_RVA)=(u64)(uptr)table;
    if(!table_reported){log_text("TERRA ABILITY TABLE READY: terra plus terra 1..10 ids116..126 AP=0; original65 native records copied unchanged");table_reported=1;}
    return 1;
}
/* Native readers scan to a zero terminator, so keep one of the 48 bytes zero.
 * All eleven profiles remain available. If the save cannot hold eleven real
 * entries, retain the main entry and page only our numbered tests via the INI.
 * Never remove, deduplicate or toggle a non-Terra byte (native copies stack).
 */
static int choice_and_learn(uptr save,uptr actor){
    u8 before[ABILITY_SLOTS],list[ABILITY_SLOTS];copy(before,(void*)(save+0x44),sizeof(before));copy(list,before,sizeof(list));
    unsigned end=0;while(end<ABILITY_SLOTS&&list[end])end++;
    for(unsigned i=end;i<ABILITY_SLOTS;i++)if(list[i])return -1;
    u32 present=0,enabled=0;unsigned others=0,natives=0;
    for(unsigned i=0;i<end;i++){
        if(own_id(list[i])){u32 bit=1u<<((list[i]&0x7fu)-TERRA_ID);present|=bit;if(!(list[i]&0x80u))enabled|=bit;}
        else {others++;if((list[i]&0x7fu)>=1u&&(list[i]&0x7fu)<=65u)natives++;}
    }
    unsigned capacity=others<ABILITY_SLOTS-1u?ABILITY_SLOTS-1u-others:0u;
    if(capacity>TERRA_ABILITIES)capacity=TERRA_ABILITIES;
    unsigned per_page=capacity>1u?capacity-1u:0u;
    unsigned pages=per_page?(10u+per_page-1u)/per_page:1u;
    unsigned page=requested_page>pages?pages:requested_page;
    unsigned first=per_page?(page-1u)*per_page+1u:0u;
    unsigned last=per_page?first+per_page-1u:0u;if(last>10u)last=10u;
    u32 wanted=capacity?1u:0u;
    if(per_page)for(unsigned i=first;i<=last;i++)wanted|=1u<<i;
    int first_setup=!(present&1u);
    if(first_setup)enabled=0;
    /* Stable compaction of only our IDs; native/foreign bytes keep their
       order, multiplicity and equipped state, including legitimate copies. */
    unsigned count=0;u32 retained=0;
    for(unsigned i=0;i<end;i++){
        u8 value=before[i];
        if(own_id(value)){
            u32 index=(value&0x7fu)-TERRA_ID,bit=1u<<index;
            if(!(wanted&bit)||(retained&bit))continue;
            retained|=bit;value=(u8)((TERRA_ID+index)|((enabled&bit)?0u:0x80u));
        }
        list[count++]=value;
    }
    for(unsigned i=0;i<TERRA_ABILITIES;i++)if((wanted&~retained)&(1u<<i))list[count++]=(u8)(TERRA_OFF+i);
    for(unsigned i=count;i<ABILITY_SLOTS;i++)list[i]=0;
    /* Page installation happens at idle, before a menu can select the new
       records. Native body switching has its separate full-record admission. */
    if(!equal(before,list,sizeof(list))&&(r32(actor+0x164)&0xfffu)!=0)return -1;
    enabled&=wanted;
    int new_save=choice_save!=save;
    if(new_save){choice_save=save;previous_equipped_mask=0;}
    u32 newly_enabled=enabled&~previous_equipped_mask;int chosen=-1;
    for(unsigned i=0;i<TERRA_ABILITIES;i++)if((newly_enabled?newly_enabled:enabled)&(1u<<i))chosen=(int)i;
    if(chosen>=0){
        for(unsigned i=0;i<count;i++)if(own_id(list[i])&&(list[i]&0x7fu)!=TERRA_ID+(u32)chosen)list[i]|=0x80u;
        if(enabled!=(1u<<chosen))log_text("TERRA EXCLUSIVE SELECTION: other Terra entries unequipped");
    }
    if(!equal(before,(void*)(save+0x44),sizeof(before)))return -1;
    if(!equal(before,list,sizeof(before))){
        copy((void*)(save+0x44),list,sizeof(list));
        if(first_setup&&capacity)log_text("TERRA FIRST SETUP: reused custom test entries116..126 start UNEQUIPPED; native abilities/AP untouched");
        log_text("TERRA ABILITY PAGE INSTALLED: main prioritized; visible numbered tests added UNEQUIPPED; only custom ids116..126 compacted");
    }
    u32 layout=others|(capacity<<6)|(page<<10)|(pages<<14)|(first<<18)|(last<<22);
    if(new_save||layout!=reported_layout){
        reported_layout=layout;
        log_count("TERRA ABILITY INPUT occupied=",end);
        log_number("TERRA ABILITY INPUT existing Terra mask=",present);
        log_count("TERRA ABILITY INPUT native entries=",natives);
        log_count("TERRA ABILITY INPUT other mod entries=",others-natives);
        log_count("TERRA ABILITY OUTPUT Terra entries=",count-others);
        log_count("TERRA TEST PAGE=",page);log_count("TERRA TEST PAGES=",pages);
        if(per_page){log_count("TERRA FIRST VISIBLE TEST=",first);log_count("TERRA LAST VISIBLE TEST=",last);}
        if(pages>1u)log_text("TERRA PAGED TESTS: set test_page=1..page count in kh1-terra.ini beside the game EXE, then restart; main is available on every page");
        if(!capacity)log_text("TERRA ABILITY SLOTS FULL: native/foreign entries retained; profile_override=1 enables main without a new ability, 2..11 select tests");
        else if(!per_page)log_text("TERRA MAIN ONLY: main ability available; no numbered-test slots free; profile_override=2..11 selects any test without another entry");
    }
    previous_equipped_mask=chosen<0?0:1u<<chosen;
    return chosen+1;
}
static void remove_ability(uptr save){
    u8 before[ABILITY_SLOTS],after[ABILITY_SLOTS];copy(before,(void*)(save+0x44),sizeof(before));copy(after,before,sizeof(after));
    unsigned end=0;while(end<ABILITY_SLOTS&&before[end])end++;
    unsigned n=0;for(unsigned i=0;i<end;i++)if(!own_id(before[i]))after[n++]=before[i];
    for(unsigned i=n;i<end;i++)after[i]=0;
    for(unsigned i=end;i<ABILITY_SLOTS;i++)if(own_id(after[i]))after[i]=0;
    if(!equal(before,after,sizeof(before))&&equal(before,(void*)(save+0x44),sizeof(before))){
        copy((void*)(save+0x44),after,sizeof(after));log_text("TERRA ABILITIES REMOVED: only ids116..126 removed; save now to retain uninstall");
    }
}
static int valid_motion(uptr motion,const TerraMotion *d,Binding *out,int *failure){
    *failure=1;if(!memory(motion,80,0))return 0;
    *failure=2;for(unsigned i=0;i<7;i++)if(r32(motion+terra_scalar_fields[i])!=d->scalars[i])return 0;
    out->contiguous=1;
    for(unsigned i=0;i<d->part_count;i++){
        const TerraPart *part=d->parts+i;uptr p=motion_part(motion,d,part,0);
        *failure=(int)(0x10u+part->field);
        if(!memory(p,part->size,1)||!part_known(p,part))return 0;
        out->parts[i]=p;
        if(p<motion||p+part->size<motion||p+part->size>motion+d->raw_bytes)out->contiguous=0;
    }
    out->motion=motion;*failure=0;return 1;
}
/* New data is published only at idle. Locomotion may be sampled from it
   afterwards; an active attack, jump, cast or reaction completes first. */
static int test_action(u32 action){return action!=0;}
static const u8 *active_part(const TerraMotion*d,const TerraPart*p,int choice){
    u32 bit=d->normal_slot==10u?1u:d->normal_slot==57u?2u:d->normal_slot==82u?4u:0u;
    return choice==1&&(action_variant_mask&bit)&&p->variant?p->variant:part_data(p,choice);
}
static int fast_binding(uptr actor,uptr array,int choice){
    if(cache_actor!=actor||cache_array!=array||cache_choice!=choice||!cache_array_bytes||!memory(array,cache_array_bytes,0))return 0;
    int group=cache_high>cache_low&&cache_high-cache_low<0x1000000u&&memory(cache_low,cache_high-cache_low,0);
    for(unsigned i=0;i<TERRA_MOTION_COUNT;i++){
        Binding *b=cached+i;const TerraMotion *d=terra_motions+i;
        if(!b->motion)continue;
        if(r32(array+b->slot*4u)!=b->handle)return 0;
        if(!group&&!memory(b->motion,b->contiguous?d->raw_bytes:80,0))return 0;
        for(unsigned k=0;k<7;k++)if(r32(b->motion+terra_scalar_fields[k])!=d->scalars[k])return 0;
        for(unsigned j=0;j<terra_motions[i].part_count;j++){
            const TerraPart *part=d->parts+j;uptr p=motion_part(b->motion,d,part,group);
            const u8 *expected=active_part(d,part,choice);
            if(p!=b->parts[j])return 0;
            if(!group&&!b->contiguous&&!memory(p+part->sentinel,4,0))return 0;
            if(!equal((void*)(p+part->sentinel),expected+part->sentinel,4))return 0;
        }
    }return 1;
}
static void motion_gate(uptr actor,int choice){
    u32 encoded_array=r32(actor+0x1d4);uptr array=decode(encoded_array);
    if(!array){clear_binding();return;}
    if(fast_binding(actor,array,choice))return;
    int same_attempt=admission_actor==actor&&admission_array==array&&admission_choice==choice;
    if(same_attempt&&(int)(frame_serial-admission_due)<0&&!(admission_waiting_idle&&!test_action(r32(actor+0x164)&0xfffu)))return;
    admission_waiting_idle=0;
    admission_actor=actor;admission_array=array;admission_choice=choice;
    admission_due=frame_serial+8u;admission_scans++;
    Binding found[TERRA_MOTION_COUNT];zeros(found,sizeof(found));
    unsigned failed=TERRA_ANCHOR_INDEX;int failure=0,bank=-1;
    /* The common idle/walk prefix is identical in both banks. Identify the
       bank with the independently tested C8 record, never with that prefix. */
    const TerraMotion *anchor=terra_motions+TERRA_ANCHOR_INDEX;
    for(int attempt=0;attempt<2;attempt++){
        u32 slot=attempt?anchor->normal_slot:anchor->olympus_slot;
        Binding candidate;zeros(&candidate,sizeof(candidate));found[failed].slot=slot;failure=1;
        if(!memory(array+slot*4u,4,0))continue;
        if(valid_motion(decode(r32(array+slot*4u)),anchor,&candidate,&failure)){bank=attempt;break;}
    }
    if(bank>=0)for(unsigned i=0;i<TERRA_MOTION_COUNT;i++){
        const TerraMotion *d=terra_motions+i;u32 slot=bank?d->normal_slot:d->olympus_slot;
        if(slot==0xffffffffu)continue;
        found[i].slot=slot;failed=i;failure=1;
        if(!memory(array+slot*4u,4,0)){bank=-1;break;}
        found[i].handle=r32(array+slot*4u);
        if(!valid_motion(decode(found[i].handle),d,found+i,&failure)){bank=-1;break;}
    }
    if(bank<0){
        if(reported_wait_array!=array){reported_wait_array=array;
            log_text("TERRA WAITING: all mapped motion records must verify before any body writes");
            log_number("TERRA rejected request=",terra_motions[failed].request);
            log_number("TERRA admission stage=",(uptr)failure);
            log_number("TERRA candidate physical slot=",found[failed].slot);
        }clear_binding();return;
    }
    int already_applied=1;
    for(unsigned i=0;i<TERRA_MOTION_COUNT&&already_applied;i++)if(found[i].motion)
        for(unsigned j=0;j<terra_motions[i].part_count;j++){
            const TerraPart*p=terra_motions[i].parts+j;
            if(!equal((void*)found[i].parts[j],active_part(terra_motions+i,p,choice),p->size)){already_applied=0;break;}
        }
    if(!already_applied&&test_action(r32(actor+0x164)&0xfffu)){
        admission_waiting_idle=1;
        if(!pending_reported){log_text("TERRA SWITCH PENDING: finish the current action and stand idle before switching");pending_reported=1;}return;
    }
    if((uptr)r64(base+SORA_RVA)!=actor||r32(actor+0x1d4)!=encoded_array)return;
    /* Recheck every destination after admission; failure prevents every write. */
    for(unsigned i=0;i<TERRA_MOTION_COUNT;i++){
        if(!found[i].motion)continue;
        Binding again;int reason;
        if(r32(array+found[i].slot*4u)!=found[i].handle||!valid_motion(found[i].motion,terra_motions+i,&again,&reason))return;
        for(unsigned j=0;j<terra_motions[i].part_count;j++)if(again.parts[j]!=found[i].parts[j])return;
    }
    for(unsigned i=0;!already_applied&&i<TERRA_MOTION_COUNT;i++)if(found[i].motion)for(unsigned j=0;j<terra_motions[i].part_count;j++){
        const TerraPart *part=terra_motions[i].parts+j;const u8 *desired=active_part(terra_motions+i,part,choice);
        if(!equal((void*)found[i].parts[j],desired,part->size))copy((void*)found[i].parts[j],desired,part->size);
    }
    for(unsigned i=0;i<TERRA_MOTION_COUNT;i++)if(found[i].motion)for(unsigned j=0;j<terra_motions[i].part_count;j++){
        const TerraPart *part=terra_motions[i].parts+j;
        if(!equal((void*)found[i].parts[j],active_part(terra_motions+i,part,choice),part->size)){clear_binding();return;}
    }
    cache_low=(uptr)-1;cache_high=0;cache_array_bytes=cache_count=0;
    for(unsigned i=0;i<TERRA_MOTION_COUNT;i++){
        if(!found[i].motion)continue;cache_count++;
        if(found[i].motion<cache_low)cache_low=found[i].motion;
        if(found[i].motion+80>cache_high)cache_high=found[i].motion+80;
        if((found[i].slot+1)*4u>cache_array_bytes)cache_array_bytes=(found[i].slot+1)*4u;
        for(unsigned j=0;j<terra_motions[i].part_count;j++){
            uptr p=found[i].parts[j],end=p+terra_motions[i].parts[j].size;
            if(p<cache_low)cache_low=p;if(end>cache_high)cache_high=end;
        }
    }
    copy(cached,found,sizeof(cached));cache_actor=actor;cache_array=array;cache_choice=choice;pending_reported=0;reported_wait_array=0;
    admission_due=frame_serial;
    if(already_applied){if(rebind_notes++<12u)log_text("TERRA BINDING RECOVERED: all payloads verified; moving actor readmitted without body writes");return;}
    log_text(choice?"TERRA MOTIONS ENABLED: Terra common body records applied; eleven helper slots and native travel retained":"TERRA MOTIONS DISABLED: all mapped original Sora records restored");
    log_text(bank?"TERRA BANK: normal Sora":"TERRA BANK: Olympus");
    log_number("TERRA verified motion count=",cache_count);
    log_number("TERRA active profile 0 native 1 main 2..11 tests=",(uptr)choice);
}

#include "terra_actions.h"

EXPORT void ABI OnInit(const w16 *mod_path){
    (void)mod_path;
    path_for(log_path,"kh1-terra.log");path_for(ini_path,"kh1-terra.ini");
    log_handle=kCreateFileW(log_path,0x40000000u,3,NULL,2,0x80,0);
    static const w16 section[]={'t','e','r','r','a',0},key[]={'r','e','m','o','v','e','_','t','e','r','r','a',0};
    static const w16 page_key[]={'t','e','s','t','_','p','a','g','e',0},override_key[]={'p','r','o','f','i','l','e','_','o','v','e','r','r','i','d','e',0};
    remove_mode=(int)kGetPrivateProfileIntW(section,key,0,ini_path);
    requested_page=kGetPrivateProfileIntW(section,page_key,1,ini_path);if(requested_page<1u||requested_page>10u)requested_page=1u;
    profile_override=kGetPrivateProfileIntW(section,override_key,0,ini_path);if(profile_override>TERRA_ABILITIES)profile_override=0u;
    log_text("KH1FM TERRA ANIMATION TEST v3 loaded: main ground300/411/332 air305/306/353; ground Fire/Blizzard/Gravity315 air316; main tap Superglide uses slide009; ten numbered tests retained");
    log_text("TERRA NATIVE LOGIC: original Sora/Olympus MSETs on disk; original combo/contact/Guard/spell events and keyblade-tip magic retained; ordinary Glide and damage reactions unchanged; main-only finite Superglide replacement");
    if(remove_mode)log_text("TERRA UNINSTALL MODE: only custom ids116..126 removed from loaded ability list");
    else if(profile_override){log_number("TERRA CONFIG PROFILE OVERRIDE=",profile_override);log_text("TERRA CONFIG: override replaces the ability gate for this run; set profile_override=0 to return to ability selection");}
}
EXPORT void ABI OnFrame(void){
    if(!checked){
        base=kGetModuleHandleA(NULL);if(!memory(base,0x100,0))return;
        u32 pe=r32(base+60);if(pe>0x1000||!memory(base+pe,0x108,0))return;
        checked=1;
        if(r32(base+pe)!=0x4550u||r32(base+pe+8)!=STEAM_STAMP){log_number("TERRA DISABLED unsupported executable timestamp=",r32(base+pe+8));return;}
        if(!memory(base+SORA_RVA,8,0)||!memory(base+TABLE_RVA,8,1)||!memory(base+SAVE_PTR_RVA,8,0)||!memory(base+BANK_RVA,64*8,0)){log_text("TERRA DISABLED: verified global memory ranges unavailable");return;}
        ready=1;log_text("TERRA Steam Global build admitted");
    }
    if(!ready)return;
    frame_serial++;
    if(kGetModuleHandleA("kh1-dual-wield.dll")||kGetModuleHandleA("kh1-aqua.dll")||kGetModuleHandleA("kh1-kh2.dll")){
        actions_forget();
        if(!conflict_reported){log_text("TERRA SUSPENDED: disable Dual Wield/Nine Styles, standalone Aqua and the full KH2 Combat DLL for this separate test");conflict_reported=1;}
        return;
    }
    actions_install();
    uptr actor=(uptr)r64(base+SORA_RVA);
    if(!memory(actor,0x378,0)||actor!=cache_actor){
        if(cache_actor&&actor!=cache_actor){if(suspend_notes++<12u)log_text("TERRA BINDING RESET: actor identity changed");clear_binding();}
        if(!memory(actor,0x378,0)){actions_forget();clear_binding();return;}
    }
    if((r32(actor+0x374)&3u)!=1u){actions_forget();cache_choice=-1;return;}
    uptr save=save_block();if(!save){actions_forget();cache_choice=-1;return;}
    int choice=0;
    if(remove_mode){remove_ability(save);choice=0;}
    else {if(!ensure_table()){actions_forget();return;}choice=choice_and_learn(save,actor);if(choice<0){actions_forget();if(!full_reported){log_text("TERRA WAITING: stand idle for stable ability setup; existing entries retained");full_reported=1;}return;}full_reported=0;if(profile_override)choice=(int)profile_override;}
    actions_prepare(actor,choice);
    if(choice!=last_choice){log_text(choice?profile_names[choice-1]:"TERRA UNEQUIPPED");last_choice=choice;}
    motion_gate(actor,choice);
    actions_tick(actor);
    u32 action=r32(actor+0x164)&0xfffu;
    if(choice&&action!=last_action&&action_logs<192){log_number("TERRA native action request=",action);action_logs++;}
    last_action=action;
}
EXPORT int ABI DllMain(uptr module,u32 reason,void *reserved){(void)module;(void)reason;(void)reserved;return 1;}
