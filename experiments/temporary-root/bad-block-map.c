/* Read-only MTD bad-block inventory for the verified U20a partitions. */
typedef unsigned int u32;
typedef unsigned long long u64;
struct info { unsigned char type; unsigned char pad[3]; u32 flags, size, erasesize, writesize, oobsize; u64 padding; };
static long sc(long n,long a,long b,long c) {
    register long r0 __asm__("r0")=a,r1 __asm__("r1")=b,r2 __asm__("r2")=c,r7 __asm__("r7")=n;
    __asm__ volatile("svc 0":"+r"(r0):"r"(r1),"r"(r2),"r"(r7):"memory","cc"); return r0;
}
static unsigned length(const char*s){unsigned n=0;while(s[n])++n;return n;}
static void say(const char*s){sc(4,1,(long)s,length(s));}
static void out(long fd,const char*s){sc(4,fd,(long)s,length(s));}
static void num(long fd,u32 n){char b[16];unsigned i=0;do{b[i++]='0'+(n%10);n/=10;}while(n);while(i){char c=b[--i];sc(4,fd,(long)&c,1);}}
__attribute__((noreturn)) static void done(int c){sc(1,c,0,0);__builtin_unreachable();}
__attribute__((used,noreturn)) static void entry(void){
    const char *path="/sqlite_stmt_journals/mero-temp-root-20261026/bad-blocks.txt";
    long output=sc(5,(long)path,577,0644);
    if(output<0){say("output open failed\n");done(1);}
    const u32 expected[4]={216006656U,52428800U,262144U,222035968U};
    for(u32 index=0;index<4;++index){
        char dev[]="/dev/mtd/mtd0ro";dev[12]=(char)('0'+index);
        long fd=sc(5,(long)dev,0,0);
        if(fd<0){say("device open failed\n");done(2);}
        struct info info={0};
        if(sc(54,fd,0x80204d01,(long)&info)<0||info.size!=expected[index]
           ||info.erasesize!=131072||info.writesize!=2048||info.oobsize!=64){
            say("unexpected geometry\n");done(3);
        }
        u32 blocks=info.size/info.erasesize,bad=0;
        for(u32 block=0;block<blocks;++block){
            u64 start=(u64)block*info.erasesize;
            long result=sc(54,fd,0x40084d0b,(long)&start);
            if(result<0){say("MEMGETBADBLOCK unsupported or failed\n");done(4);}
            if(result>0){
                out(output,"bad mtd");num(output,index);out(output," block=");num(output,block);out(output,"\n");++bad;
            }
        }
        out(output,"summary mtd");num(output,index);out(output," blocks=");num(output,blocks);
        out(output," bad=");num(output,bad);out(output,"\n");
        sc(6,fd,0,0);
    }
    sc(6,output,0,0);say("bad-block inventory saved\n");done(0);
}
__attribute__((naked,noreturn)) void _start(void){__asm__ volatile("b entry");}
