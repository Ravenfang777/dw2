/* Linux-only test host: executes the actual PE DLL with Win64 ABI mocks. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <sys/mman.h>
#define ABI __attribute__((ms_abi))
typedef struct {uintptr_t base,allocation;uint32_t allocation_protect;uint16_t partition,pad;size_t size;uint32_t state,protect,type,pad2;} MemInfo;
static struct {uintptr_t start;size_t size;uint32_t protect;} ranges[128];
static unsigned nranges,queries;
static uintptr_t game_base;
static int remove_mode,conflict;
static int hand_magic=1,alloc_failure,protect_failure;
static unsigned matrix_code,point_code;static float point_fraction;
static char output[131072];static size_t used;
void bridge_reset(uintptr_t game){game_base=game;nranges=queries=0;remove_mode=conflict=0;hand_magic=1;alloc_failure=protect_failure=0;matrix_code=point_code=0;used=0;output[0]=0;}
void bridge_magic_modes(int enabled,int noalloc,int noprotect){hand_magic=enabled;alloc_failure=noalloc;protect_failure=noprotect;}
void bridge_range(uintptr_t start,size_t size,uint32_t protect){ranges[nranges].start=start;ranges[nranges].size=size;ranges[nranges].protect=protect;nranges++;}
void bridge_modes(int remove,int other){remove_mode=remove;conflict=other;}
const char* bridge_log(void){return output;}
unsigned bridge_queries(void){return queries;}
static uintptr_t ABI get_module(const char*name){if(!name)return game_base;return conflict&&strcmp(name,"kh1-dual-wield.dll")==0?1:0;}
static uint32_t ABI file_name(uintptr_t module,uint16_t*out,uint32_t count){(void)module;const char*s="C:\\mock\\KINGDOM HEARTS FINAL MIX.exe";uint32_t i=0;for(;s[i]&&i+1<count;i++)out[i]=(unsigned char)s[i];out[i]=0;return i;}
static size_t ABI query(const void*p,MemInfo*out,size_t size){queries++;uintptr_t a=(uintptr_t)p;if(size!=sizeof(*out))return 0;for(unsigned i=0;i<nranges;i++)if(a>=ranges[i].start&&a<ranges[i].start+ranges[i].size){memset(out,0,sizeof(*out));out->base=out->allocation=ranges[i].start;out->size=ranges[i].size;out->state=0x1000;out->protect=ranges[i].protect;return sizeof(*out);}return 0;}
static uintptr_t ABI create_file(const uint16_t*path,uint32_t a,uint32_t b,void*c,uint32_t d,uint32_t e,uintptr_t f){(void)path;(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 7;}
static int ABI write_file(uintptr_t f,const void*data,uint32_t n,uint32_t*done,void*overlap){(void)f;(void)overlap;if(used+n>=sizeof(output))return 0;memcpy(output+used,data,n);used+=n;output[used]=0;if(done)*done=n;return 1;}
static int ABI close_file(uintptr_t f){(void)f;return 1;}
static uint32_t ABI profile(const uint16_t*a,const uint16_t*b,int c,const uint16_t*d){(void)a;(void)c;(void)d;return b[0]=='h'?(uint32_t)hand_magic:(uint32_t)remove_mode;}
static void* ABI valloc(void*p,size_t n,uint32_t kind,uint32_t protect){(void)p;(void)kind;(void)protect;if(alloc_failure)return 0;void*q=mmap(0,n,PROT_READ|PROT_WRITE|PROT_EXEC,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);if(q==MAP_FAILED)return 0;bridge_range((uintptr_t)q,n,0x40);return q;}
static int ABI vfree(void*p,size_t n,uint32_t kind){(void)n;(void)kind;return munmap(p,4096)==0;}
static int ABI vprotect(void*p,size_t n,uint32_t protect,uint32_t*old){(void)p;(void)n;(void)protect;if(protect_failure)return 0;*old=0x20;return 1;}
static int ABI flush(uintptr_t process,const void*p,size_t n){(void)process;(void)p;(void)n;return 1;}
static void ABI native_matrix(uintptr_t actor,uint32_t code,float*out){(void)actor;matrix_code=code;memset(out,0,16*sizeof(float));out[0]=out[5]=out[10]=out[15]=1;out[12]=code==0x2065?11:100;out[13]=code==0x2065?22:200;out[14]=code==0x2065?33:300;}
static void ABI native_point(uintptr_t actor,uint32_t code,float fraction,float*out){(void)actor;point_code=code;point_fraction=fraction;out[0]=100;out[1]=200;out[2]=300;out[3]=1;}
void bridge_matrix(uintptr_t f,uintptr_t actor,uint32_t code,float*out){((void(ABI*)(uintptr_t,uint32_t,float*))f)(actor,code,out);}
void bridge_point(uintptr_t f,uintptr_t actor,uint32_t code,float fraction,float*out){((void(ABI*)(uintptr_t,uint32_t,float,float*))f)(actor,code,fraction,out);}
unsigned bridge_matrix_code(void){return matrix_code;}
unsigned bridge_point_code(void){return point_code;}
float bridge_point_fraction(void){return point_fraction;}
static uint32_t ABI handle(const void*p){uintptr_t addr=(uintptr_t)p,aligned=addr&~(uintptr_t)0x1ffffff;uintptr_t*t=(uintptr_t*)(game_base+0x2ee3980);for(unsigned i=1;i<64;i++)if(t[i]==aligned)return 0x80000000u|(i<<25)|(uint32_t)(addr-aligned);for(unsigned i=1;i<64;i++)if(!t[i]){t[i]=aligned;return 0x80000000u|(i<<25)|(uint32_t)(addr-aligned);}return 0;}
uint32_t bridge_encode(uintptr_t p){return handle((void*)p);}
uintptr_t bridge_symbol(const char*n){
    if(!strcmp(n,"GetModuleHandleA"))return (uintptr_t)get_module;
    if(!strcmp(n,"GetModuleFileNameW"))return (uintptr_t)file_name;
    if(!strcmp(n,"VirtualQuery"))return (uintptr_t)query;
    if(!strcmp(n,"CreateFileW"))return (uintptr_t)create_file;
    if(!strcmp(n,"WriteFile"))return (uintptr_t)write_file;
    if(!strcmp(n,"CloseHandle"))return (uintptr_t)close_file;
    if(!strcmp(n,"GetPrivateProfileIntW"))return (uintptr_t)profile;
    if(!strcmp(n,"NativeHandle"))return (uintptr_t)handle;
    if(!strcmp(n,"VirtualAlloc"))return (uintptr_t)valloc;
    if(!strcmp(n,"VirtualFree"))return (uintptr_t)vfree;
    if(!strcmp(n,"VirtualProtect"))return (uintptr_t)vprotect;
    if(!strcmp(n,"FlushInstructionCache"))return (uintptr_t)flush;
    if(!strcmp(n,"NativeMatrix"))return (uintptr_t)native_matrix;
    if(!strcmp(n,"NativePoint"))return (uintptr_t)native_point;
    return 0;
}
void bridge_call0(uintptr_t f){((void(ABI*)(void))f)();}
void bridge_init(uintptr_t f){((void(ABI*)(const uint16_t*))f)(0);}
