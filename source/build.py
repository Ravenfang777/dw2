"""Build a small Windows x64 Panacea DLL with GCC and GNU ld's PE backend.

No MinGW runtime or game executable is embedded. Kernel32 imports are standard
COFF import descriptors, emitted explicitly so the build has no SDK dependency.
"""
from pathlib import Path
import struct,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent
IMPORTS=['GetModuleHandleA','GetModuleFileNameW','VirtualQuery','CreateFileW','WriteFile','CloseHandle','GetPrivateProfileIntW','VirtualAlloc','VirtualFree','VirtualProtect','FlushInstructionCache']

def elf_to_coff(source,target):
    """Translate ELF RELA semantics to AMD64 COFF, including implicit addends.

    objcopy alone preserves numeric relocation IDs across these formats;
    ELF PC32 (2) and COFF ADDR32 (2) have different meanings.
    """
    b=source.read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
    shoff=struct.unpack_from('<Q',b,40)[0];ents,n,strings_idx=struct.unpack_from('<HHH',b,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*ents) for i in range(n)]
    string_sec=sections[strings_idx];section_names=b[string_sec[4]:string_sec[4]+string_sec[5]]
    z=lambda data,at:data[at:data.index(0,at)].decode()
    names=[z(section_names,s[0]) for s in sections]
    selected=[i for i,s in enumerate(sections) if s[2]&2 and s[5] and s[1] in [1,8]]
    section_map={old:i+1 for i,old in enumerate(selected)}
    symbol_sec=next(s for s in sections if s[1]==2);strings=sections[symbol_sec[6]]
    strings=b[strings[4]:strings[4]+strings[5]]
    elf_symbols=[struct.unpack_from('<IBBHQQ',b,at) for at in range(symbol_sec[4],symbol_sec[4]+symbol_sec[5],24)]
    symbols=[];symbol_map={}
    for i,(name,info,other,section,value,size) in enumerate(elf_symbols):
        if i==0 or (section not in section_map and section!=0):continue
        label=z(strings,name) if name else names[section]
        symbol_map[i]=len(symbols)
        symbols.append((label,value,section_map.get(section,0),0x20 if info&15==2 else 0,2 if info>>4 else 3))
    strings=bytearray(b'\0\0\0\0')
    def coff_name(name,section=False):
        encoded=name.encode()
        if len(encoded)<=8:return encoded.ljust(8,b'\0')
        at=len(strings);strings.extend(encoded+b'\0')
        return (('/'+str(at)).encode().ljust(8,b'\0') if section else struct.pack('<II',0,at))
    data={i:bytearray(b[sections[i][4]:sections[i][4]+sections[i][5]]) if sections[i][1]!=8 else bytearray() for i in selected}
    relocs={i:[] for i in selected}
    for s in sections:
        if s[1]!=4 or s[7] not in section_map:continue
        dest=s[7]
        for at in range(s[4],s[4]+s[5],24):
            offset,info,addend=struct.unpack_from('<QQq',b,at);symbol=info>>32;kind=info&0xffffffff
            if kind in [2,4]:coff_kind=4;struct.pack_into('<i',data[dest],offset,addend+4)
            elif kind==1:coff_kind=1;struct.pack_into('<Q',data[dest],offset,addend&0xffffffffffffffff)
            elif kind in [10,11]:coff_kind=2;struct.pack_into('<I',data[dest],offset,addend&0xffffffff)
            else:raise ValueError(('Unsupported ELF relocation',kind))
            relocs[dest].append((offset,symbol_map[symbol],coff_kind))
    offset=20+40*len(selected);headers=[];chunks=[]
    for i in selected:
        s=sections[i];name=names[i]
        if name.startswith('.rodata'):name='.rdata$'+str(i)
        elif name.startswith('.data'):name='.data$'+str(i)
        raw=offset if data[i] else 0;chunks.append(bytes(data[i]));offset+=len(data[i])
        reloc_at=offset if relocs[i] else 0
        encoded_relocs=b''.join(struct.pack('<IIH',*r) for r in relocs[i]);chunks.append(encoded_relocs);offset+=len(encoded_relocs)
        align=(max(1,s[8]).bit_length())<<20
        flags=(0x60000020 if s[2]&4 else (0xc0000080 if s[1]==8 else 0x40000040|(0x80000000 if s[2]&1 else 0)))|align
        headers.append(struct.pack('<8sIIIIIIHHI',coff_name(name,True),0,0,s[5],raw,reloc_at,0,len(relocs[i]),0,flags))
    sym_at=offset;sym_bytes=bytearray()
    for name,value,section,kind,storage in symbols:sym_bytes.extend(struct.pack('<8sIhHBB',coff_name(name),value,section,kind,storage,0))
    struct.pack_into('<I',strings,0,len(strings))
    target.write_bytes(struct.pack('<HHIIIHH',0x8664,len(selected),0,sym_at,len(symbols),0,0)+b''.join(headers)+b''.join(chunks)+sym_bytes+strings)

def import_object(path):
    names=[('.idata$2',bytearray(20),[]),('.idata$4',bytearray((len(IMPORTS)+1)*8),[]),('.idata$5',bytearray((len(IMPORTS)+1)*8),[]),('.idata$6',bytearray(b'KERNEL32.dll\0'),[])]
    symbols=[]
    def sym(name,section,value=0,storage=2):
        symbols.append((name,value,section,storage));return len(symbols)-1
    ilt=sym('aqua_ilt',2);iat=sym('aqua_iat',3);dll=sym('aqua_kernel32_name',4)
    names[0][2].extend([(0,ilt,3),(12,dll,3),(16,iat,3)])
    for i,name in enumerate(IMPORTS):
        if len(names[3][1])%2:names[3][1].append(0)
        hint=sym('aqua_hint_'+name,4,len(names[3][1]),3)
        names[3][1].extend(b'\0\0'+name.encode()+b'\0')
        sym('k'+name,3,i*8)
        names[1][2].append((i*8,hint,3));names[2][2].append((i*8,hint,3))
    offset=20+40*len(names);headers=[];chunks=[]
    for name,data,relocs in names:
        raw=offset;chunks.append(bytes(data));offset+=len(data)
        reloc_at=offset if relocs else 0
        reloc_data=b''.join(struct.pack('<IIH',*r) for r in relocs);chunks.append(reloc_data);offset+=len(reloc_data)
        headers.append(struct.pack('<8sIIIIIIHHI',name.encode(),0,0,len(data),raw,reloc_at,0,len(relocs),0,0xc0300040))
    sym_at=offset;strings=bytearray(b'\0\0\0\0');sym_bytes=bytearray()
    for name,value,section,storage in symbols:
        encoded=name.encode()
        if len(encoded)<=8:field=encoded.ljust(8,b'\0')
        else:field=struct.pack('<II',0,len(strings));strings.extend(encoded+b'\0')
        sym_bytes.extend(struct.pack('<8sIhHBB',field,value,section,0,storage,0))
    struct.pack_into('<I',strings,0,len(strings))
    header=struct.pack('<HHIIIHH',0x8664,len(names),0,sym_at,len(symbols),0,0)
    path.write_bytes(header+b''.join(headers)+b''.join(chunks)+sym_bytes+strings)


def run(argv):
    result=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True)
    if result.stdout:print(result.stdout.strip())
    if result.stderr:print(result.stderr.strip())
    result.check_returncode()


def build():
    import_object(ROOT/'imports.obj')
    (ROOT/'exports.def').write_text('LIBRARY kh1-aqua.dll\nEXPORTS\n  DllMain\n  OnInit\n  OnFrame\n')
    run(['gcc','-std=c11','-O2','-m64','-mabi=ms','-maccumulate-outgoing-args','-mno-red-zone','-fPIC','-fvisibility=hidden','-fno-strict-aliasing','-fno-stack-protector','-fno-builtin','-fno-tree-loop-distribute-patterns','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-ffreestanding','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-c','aqua.c','-o','aqua.elf.o'])
    elf_to_coff(ROOT/'aqua.elf.o',ROOT/'aqua.obj')
    run(['ld','-mi386pep','--dll','--entry','DllMain','--image-base','0x180000000','--dynamicbase','--nxcompat','--enable-reloc-section','--no-insert-timestamp','--subsystem','windows','-o','kh1-aqua.dll','aqua.obj','imports.obj','exports.def'])
    dll=(ROOT/'kh1-aqua.dll').read_bytes()
    print(json.dumps({'dll':str(ROOT/'kh1-aqua.dll'),'bytes':len(dll),'sha256':hashlib.sha256(dll).hexdigest()},indent=2))

if __name__=='__main__':build()
