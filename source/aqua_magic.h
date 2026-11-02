/* V17 uses native keyblade-tip spell origins and effect matrices. No palm
 * attachment detours are installed, including with an older hand_magic INI.
 * These memory APIs and the absolute jump writer serve the movement hooks. */
extern void* (ABI *kVirtualAlloc)(void*,usize,u32,u32) HIDDEN;
extern int (ABI *kVirtualFree)(void*,usize,u32) HIDDEN;
extern int (ABI *kVirtualProtect)(void*,usize,u32,u32*) HIDDEN;
extern int (ABI *kFlushInstructionCache)(uptr,const void*,usize) HIDDEN;
static int magic_disabled=1,magic_conflict;
static void magic_install(void){}
static void magic_jump(u8*out,uptr target){
    static const u8 op[6]={0xff,0x25,0,0,0,0};copy(out,op,6);copy(out+6,&target,8);
}
