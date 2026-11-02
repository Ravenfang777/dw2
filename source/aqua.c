/* Standalone Panacea ability gate for compact Aqua FK motion tests.
 * Compact motion tables plus two checked native attachment function hooks.
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

#include "aqua_data.h"
#define AQUA_ID 117u
#define AQUA_OFF (AQUA_ID|0x80u)
#define AQUA_ABILITIES 5u
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
static int checked,ready,remove_mode,learned_reported,conflict_reported,full_reported;
static u8 table[TABLE_BYTES] __attribute__((aligned(16)));
static u8 encoded_name[AQUA_ABILITIES][16],encoded_help[AQUA_ABILITIES][128];
static u32 name_handle[AQUA_ABILITIES],help_handle[AQUA_ABILITIES];
static uptr choice_save;
static u32 previous_equipped_mask;
static int slots_reported;
static const char *profile_names[AQUA_ABILITIES]={"aqua","aqua 1","aqua 2","aqua 3","aqua 4"};
static const char *profile_help[AQUA_ABILITIES]={
    "Aqua movement attacks guard dodge magic and reactions",
    "Test 4 Ground 622 623 045 Air 220 221 351",
    "Test 4 Ground 353 399 411 Air 413 710 711",
    "Test 4 Ground 060 022 023 Air 025 026 052",
    "Test 4 Ground 701 700 708 Air 395 051 505"};
static int table_reported;
static w16 log_path[1024],ini_path[1024];
/* A real DIR64 relocation keeps the PE image independently relocatable. */
static void *volatile relocation_anchor __attribute__((used))=&table[0];
typedef struct {uptr motion,parts[AQUA_PART_COUNT];u32 handle,slot,contiguous;} Binding;
static Binding cached[AQUA_MOTION_COUNT];
static uptr cache_actor,cache_array,reported_wait_array,cache_low,cache_high;
static u32 cache_array_bytes,cache_count;
static int air_dodge_active;
static void air_dodge_clear(void);
static int cache_choice=-1,pending_reported,last_choice=-1;
static u32 last_action=0xffffffffu,action_logs;

static u32 r32(uptr p){return *(volatile u32*)p;}
static u64 r64(uptr p){return *(volatile u64*)p;}
static u8 r8(uptr p){return *(volatile u8*)p;}
static void copy(void *dst,const void *src,usize n){u8*d=dst;const u8*s=src;for(usize i=0;i<n;i++)d[i]=s[i];}
static int equal(const void*a,const void*b,usize n){const u8*x=a,*y=b;for(usize i=0;i<n;i++)if(x[i]!=y[i])return 0;return 1;}
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
static void clear_binding(void){air_dodge_clear();cache_actor=cache_array=cache_low=cache_high=0;cache_array_bytes=cache_count=0;cache_choice=-1;pending_reported=0;zeros(cached,sizeof(cached));}
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
static uptr save_block(void){
    uptr p=(uptr)r64(base+SAVE_PTR_RVA);
    if(p<0x10000u)p=base+SAVE_RVA;
    if(!memory(p,0x74,1)||!r8(p+4)||!r8(p+5)||!r8(p+6))return 0;
    return p;
}
static int own_id(u8 value){u32 id=value&0x7fu;return id>=AQUA_ID&&id<AQUA_ID+AQUA_ABILITIES;}
static const u8 *part_data(const AquaPart *part,int choice){return choice>0?part->after[choice-1]:part->before;}
static int part_known(uptr p,const AquaPart *part){
    if(equal((void*)p,part->before,part->size))return 1;
    for(unsigned i=0;i<AQUA_PROFILE_COUNT;i++)if(equal((void*)p,part->after[i],part->size))return 1;
    if(part->dodge&&equal((void*)p,part->dodge,part->size))return 1;
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
        for(unsigned i=0;i<AQUA_ABILITIES;i++){
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
    for(unsigned i=0;i<AQUA_ABILITIES;i++){
        u8 *record=table+(AQUA_ID+i-1)*12;copy(record,snapshot+64*12,12);record[0]=0;
        u32 order=(u16)snapshot[64*12+2]|((u32)snapshot[64*12+3]<<8);order+=1+i;if(order>65535)order=65535;
        record[2]=(u8)order;record[3]=(u8)(order>>8);copy(record+4,name_handle+i,4);copy(record+8,help_handle+i,4);
    }
    if(r64(base+TABLE_RVA)!=current||!equal(snapshot,(void*)current,sizeof(snapshot)))return 0;
    *(volatile u64*)(base+TABLE_RVA)=(u64)(uptr)table;
    if(!table_reported){log_text("AQUA ABILITY TABLE READY: aqua and aqua 1..4 ids117..121 AP=0; original 65 records copied unchanged");table_reported=1;}
    return 1;
}
static int choice_and_learn(uptr save){
    u8 before[ABILITY_SLOTS],list[ABILITY_SLOTS];copy(before,(void*)(save+0x44),sizeof(before));copy(list,before,sizeof(list));
    unsigned end=0;while(end<ABILITY_SLOTS&&list[end])end++;
    for(unsigned i=end;i<ABILITY_SLOTS;i++)if(list[i])return -1;
    u32 present=0,enabled=0;
    for(unsigned i=0;i<end;i++)if(own_id(list[i])){u32 bit=1u<<((list[i]&0x7fu)-AQUA_ID);present|=bit;if(!(list[i]&0x80u))enabled|=bit;}
    unsigned missing=0;for(unsigned i=0;i<AQUA_ABILITIES;i++)if(!(present&(1u<<i)))missing++;
    if(missing&&end+missing<ABILITY_SLOTS){
        for(unsigned i=0;i<AQUA_ABILITIES;i++)if(!(present&(1u<<i)))list[end++]=(u8)(AQUA_OFF+i);
        if(!learned_reported){log_text("AQUA ABILITIES LEARNED: missing aqua entries added UNEQUIPPED; native abilities and AP untouched");learned_reported=1;}
        slots_reported=0;
    }else if(missing&&!slots_reported){log_text("AQUA ABILITY SLOTS FULL: five entries need free tail slots; native entries retained");slots_reported=1;}
    if(choice_save!=save){choice_save=save;previous_equipped_mask=0;}
    u32 newly_enabled=enabled&~previous_equipped_mask;int chosen=-1;
    for(unsigned i=0;i<AQUA_ABILITIES;i++)if((newly_enabled?newly_enabled:enabled)&(1u<<i))chosen=(int)i;
    if(chosen>=0){
        for(unsigned i=0;i<end;i++)if(own_id(list[i])&&(list[i]&0x7fu)!=AQUA_ID+(u32)chosen)list[i]|=0x80u;
        if(enabled!=(1u<<chosen))log_text("AQUA EXCLUSIVE SELECTION: other Aqua entries unequipped");
    }
    if(!equal(before,(void*)(save+0x44),sizeof(before)))return -1;
    if(!equal(before,list,sizeof(before)))copy((void*)(save+0x44),list,sizeof(list));
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
        copy((void*)(save+0x44),after,sizeof(after));log_text("AQUA ABILITIES REMOVED: only ids117..121 removed; save now to retain uninstall");
    }
}
static int valid_motion(uptr motion,const AquaMotion *d,Binding *out,int *failure){
    *failure=1;if(!memory(motion,80,0))return 0;
    *failure=2;for(unsigned i=0;i<7;i++)if(r32(motion+aqua_scalar_fields[i])!=d->scalars[i])return 0;
    out->contiguous=1;
    for(unsigned i=0;i<AQUA_PART_COUNT;i++){
        const AquaPart *part=d->parts+i;uptr p=relative_or_handle(motion,r32(motion+part->field),d->raw_bytes);
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
#include "aqua_cast_requests.h"
static int fast_binding(uptr actor,uptr array,int choice){
    if(!cast_cached(actor,array,choice))return 0;
    if(cache_actor!=actor||cache_array!=array||cache_choice!=choice||!cache_array_bytes||!memory(array,cache_array_bytes,0))return 0;
    int group=cache_high>cache_low&&cache_high-cache_low<0x1000000u&&memory(cache_low,cache_high-cache_low,0);
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++){
        Binding *b=cached+i;const AquaMotion *d=aqua_motions+i;
        if(!b->motion)continue;
        if(r32(array+b->slot*4u)!=b->handle)return 0;
        if(!group&&!memory(b->motion,b->contiguous?d->raw_bytes:80,0))return 0;
        for(unsigned k=0;k<7;k++)if(r32(b->motion+aqua_scalar_fields[k])!=d->scalars[k])return 0;
        for(unsigned j=0;j<AQUA_PART_COUNT;j++){
            const AquaPart *part=d->parts+j;uptr p=relative_or_handle(b->motion,r32(b->motion+part->field),d->raw_bytes);
            const u8 *expected=air_dodge_active&&d->normal_slot==10&&part->dodge?part->dodge:part_data(part,choice);
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
    Binding found[AQUA_MOTION_COUNT];zeros(found,sizeof(found));
    unsigned failed=AQUA_ANCHOR_INDEX;int failure=0,bank=-1;
    /* The common idle/walk prefix is identical in both banks. Identify the
       bank with the independently tested C8 record, never with that prefix. */
    const AquaMotion *anchor=aqua_motions+AQUA_ANCHOR_INDEX;
    for(int attempt=0;attempt<2;attempt++){
        u32 slot=attempt?anchor->normal_slot:anchor->olympus_slot;
        Binding candidate;zeros(&candidate,sizeof(candidate));found[failed].slot=slot;failure=1;
        if(!memory(array+slot*4u,4,0))continue;
        if(valid_motion(decode(r32(array+slot*4u)),anchor,&candidate,&failure)){bank=attempt;break;}
    }
    if(bank>=0)for(unsigned i=0;i<AQUA_MOTION_COUNT;i++){
        const AquaMotion *d=aqua_motions+i;u32 slot=bank?d->normal_slot:d->olympus_slot;
        if(slot==0xffffffffu)continue;
        found[i].slot=slot;failed=i;failure=1;
        if(!memory(array+slot*4u,4,0)){bank=-1;break;}
        found[i].handle=r32(array+slot*4u);
        if(!valid_motion(decode(found[i].handle),d,found+i,&failure)){bank=-1;break;}
    }
    if(bank<0){
        if(reported_wait_array!=array){reported_wait_array=array;
            log_text("AQUA WAITING: all mapped motion records must verify before any body writes");
            log_number("AQUA rejected request=",aqua_motions[failed].request);
            log_number("AQUA admission stage=",(uptr)failure);
            log_number("AQUA candidate physical slot=",found[failed].slot);
        }clear_binding();return;
    }
    CastBinding cast_found;
    if(!cast_admit(actor,array,bank,choice,&cast_found)){
        if(reported_wait_array!=array){reported_wait_array=array;log_text("AQUA WAITING: original ground/air cast request table must verify before any body writes");}
        clear_binding();return;
    }
    if(test_action(r32(actor+0x164)&0xfffu)){
        if(!pending_reported){log_text("AQUA SWITCH PENDING: finish the current action and stand idle before switching");pending_reported=1;}return;
    }
    if((uptr)r64(base+SORA_RVA)!=actor||r32(actor+0x1d4)!=encoded_array)return;
    /* Recheck every destination after admission; failure prevents every write. */
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++){
        if(!found[i].motion)continue;
        Binding again;int reason;
        if(r32(array+found[i].slot*4u)!=found[i].handle||!valid_motion(found[i].motion,aqua_motions+i,&again,&reason))return;
        for(unsigned j=0;j<AQUA_PART_COUNT;j++)if(again.parts[j]!=found[i].parts[j])return;
    }
    CastBinding cast_again;
    if(r32(actor+0x1d8)!=cast_found.current||!cast_admit(actor,array,bank,choice,&cast_again)
        ||cast_again.original!=cast_found.original||cast_again.next!=cast_found.next)return;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(found[i].motion)for(unsigned j=0;j<AQUA_PART_COUNT;j++){
        const AquaPart *part=aqua_motions[i].parts+j;const u8 *desired=part_data(part,choice);
        if(!equal((void*)found[i].parts[j],desired,part->size))copy((void*)found[i].parts[j],desired,part->size);
    }
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++)if(found[i].motion)for(unsigned j=0;j<AQUA_PART_COUNT;j++){
        const AquaPart *part=aqua_motions[i].parts+j;
        if(!equal((void*)found[i].parts[j],part_data(part,choice),part->size)){clear_binding();return;}
    }
    cache_low=(uptr)-1;cache_high=0;cache_array_bytes=cache_count=0;
    for(unsigned i=0;i<AQUA_MOTION_COUNT;i++){
        if(!found[i].motion)continue;cache_count++;
        if(found[i].motion<cache_low)cache_low=found[i].motion;
        if(found[i].motion+80>cache_high)cache_high=found[i].motion+80;
        if((found[i].slot+1)*4u>cache_array_bytes)cache_array_bytes=(found[i].slot+1)*4u;
        for(unsigned j=0;j<AQUA_PART_COUNT;j++){
            uptr p=found[i].parts[j],end=p+aqua_motions[i].parts[j].size;
            if(p<cache_low)cache_low=p;if(end>cache_high)cache_high=end;
        }
    }
    cast_publish(actor,array,&cast_found);
    copy(cached,found,sizeof(cached));cache_actor=actor;cache_array=array;cache_choice=choice;pending_reported=0;reported_wait_array=0;
    log_text(choice?"AQUA MOTIONS ENABLED: Aqua common body records applied; eleven helper slots and native travel retained":"AQUA MOTIONS DISABLED: all mapped original Sora records restored");
    log_text(bank?"AQUA BANK: normal Sora":"AQUA BANK: Olympus");
    log_number("AQUA verified motion count=",cache_count);
    log_number("AQUA active profile 0 native 1 aqua 2..5 tests=",(uptr)choice);
}

#include "aqua_magic.h"
#include "aqua_air_dodge.h"

EXPORT void ABI OnInit(const w16 *mod_path){
    (void)mod_path;
    path_for(log_path,"kh1-aqua.log");path_for(ini_path,"kh1-aqua.ini");
    log_handle=kCreateFileW(log_path,0x40000000u,3,NULL,2,0x80,0);
    static const w16 section[]={'a','q','u','a',0},key[]={'r','e','m','o','v','e','_', 'a','q','u','a',0};
    remove_mode=(int)kGetPrivateProfileIntW(section,key,0,ini_path);
    static const w16 magic_key[]={'h','a','n','d','_','m','a','g','i','c',0};
    magic_disabled=!kGetPrivateProfileIntW(section,magic_key,1,ini_path);
    static const w16 air_key[]={'a','i','r','_','d','o','d','g','e',0};
    air_disabled=!kGetPrivateProfileIntW(section,air_key,1,ini_path);
    log_text("KH1FM AQUA ANIMATION TEST v12 Test 4 loaded by Panacea; aqua and aqua 1..4; finisher411, air407/352/353, airborne dodge504, fall506 and LEFT-hand magic");
    log_text("On disk: original Sora/Olympus MSETs. All mapped records must verify before body writes. Native defensive behavior is unchanged.");
    if(remove_mode)log_text("AQUA UNINSTALL MODE: ids117..121 will be removed from the loaded ability list");
}
EXPORT void ABI OnFrame(void){
    if(!checked){
        base=kGetModuleHandleA(NULL);if(!memory(base,0x100,0))return;
        u32 pe=r32(base+60);if(pe>0x1000||!memory(base+pe,0x108,0))return;
        checked=1;
        if(r32(base+pe)!=0x4550u||r32(base+pe+8)!=STEAM_STAMP){log_number("AQUA DISABLED unsupported executable timestamp=",r32(base+pe+8));return;}
        if(!memory(base+SORA_RVA,8,0)||!memory(base+TABLE_RVA,8,1)||!memory(base+SAVE_PTR_RVA,8,0)||!memory(base+BANK_RVA,64*8,0)){log_text("AQUA DISABLED: verified global memory ranges unavailable");return;}
        ready=1;log_text("AQUA Steam Global build admitted");
    }
    if(!ready)return;
    if(kGetModuleHandleA("kh1-dual-wield.dll")){
        magic_conflict=1;
        if(!conflict_reported){log_text("AQUA SUSPENDED: disable Nine Styles / Dual Wield for this standalone ability test");conflict_reported=1;}
        return;
    }
    magic_conflict=0;magic_install();air_install();
    uptr actor=(uptr)r64(base+SORA_RVA);
    if(!memory(actor,0x378,0)||(r32(actor+0x374)&3u)!=1u){clear_binding();return;}
    uptr save=save_block();if(!save){clear_binding();return;}
    int choice=0;
    if(remove_mode){remove_ability(save);choice=0;}
    else {if(!ensure_table())return;choice=choice_and_learn(save);if(choice<0){if(!full_reported){log_text("AQUA WAITING: ability list full or not stable; no native entry overwritten");full_reported=1;}return;}full_reported=0;}
    if(choice!=last_choice){log_text(choice?profile_names[choice-1]:"AQUA UNEQUIPPED");last_choice=choice;}
    air_requested_choice=choice;
    air_tick(actor,choice);
    motion_gate(actor,choice);
    u32 action=r32(actor+0x164)&0xfffu;
    if(choice&&action!=last_action&&action_logs<192){
        log_number("AQUA native action request=",action);action_logs++;
    }
    last_action=action;
}
EXPORT int ABI DllMain(uptr module,u32 reason,void *reserved){(void)module;(void)reason;(void)reserved;return 1;}
