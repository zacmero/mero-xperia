/* Read-only MTD spare-area capture for the verified U20a NAND geometry. */
typedef unsigned int u32;
typedef unsigned long long u64;
struct info { unsigned char type; unsigned char pad[3]; u32 flags, size, erasesize, writesize, oobsize; u64 padding; };
struct oob { u32 start, length; unsigned char *ptr; };
static long sc(long n, long a, long b, long c) {
    register long r0 __asm__("r0")=a, r1 __asm__("r1")=b, r2 __asm__("r2")=c, r7 __asm__("r7")=n;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r1), "r"(r2), "r"(r7) : "memory", "cc");
    return r0;
}
static unsigned length(const char *s) { unsigned n=0; while(s[n]) ++n; return n; }
static void say(const char *s) { sc(4,1,(long)s,length(s)); }
static void number(u32 n) {
    char b[16]; unsigned i=0; do { b[i++]='0'+(n%10); n/=10; } while(n);
    while(i) { char c=b[--i]; sc(4,1,(long)&c,1); }
}
static int parse(const char *s, u32 *value) {
    u32 n=0; if(!*s) return 0;
    while(*s) { if(*s<'0'||*s>'9'||n>400000000U) return 0; n=n*10U+(u32)(*s++-'0'); }
    *value=n; return 1;
}
__attribute__((noreturn)) static void done(int code) { sc(1,code,0,0); __builtin_unreachable(); }
__attribute__((used,noreturn)) static void entry(long *stack) {
    long argc=stack[0]; char **argv=(char **)&stack[1];
    u32 index, first, count;
    if(argc!=4 || !parse(argv[1],&index) || !parse(argv[2],&first) || !parse(argv[3],&count)
       || index>3 || count==0 || count>32768) { say("usage: oob-capture INDEX FIRST_PAGE COUNT\n"); done(1); }
    const u32 expected[4]={216006656U,52428800U,262144U,222035968U};
    char dev[]="/dev/mtd/mtd0ro"; dev[12]=(char)('0'+index);
    long fd=sc(5,(long)dev,0,0);
    if(fd<0) { say("open failed\n"); done(2); }
    struct info info={0};
    if(sc(54,fd,0x80204d01,(long)&info)<0 || info.size!=expected[index]
       || info.erasesize!=131072 || info.writesize!=2048 || info.oobsize!=64) {
        say("unexpected MTD geometry\n"); done(3);
    }
    u32 pages=info.size/info.writesize;
    if(first>=pages || count>pages-first) { say("page range exceeds partition\n"); done(4); }
    const char *out="/sqlite_stmt_journals/mero-temp-root-20261026/oob-chunk";
    long output=sc(5,(long)out,577,0644);
    if(output<0) { say("output open failed\n"); done(5); }
    unsigned char data[64];
    for(u32 i=0;i<count;++i) {
        struct oob request={(first+i)*2048U,64,data};
        if(sc(54,fd,0xc00c4d04,(long)&request)<0 || request.length!=64) {
            say("OOB read failed at page "); number(first+i); say("\n"); done(6);
        }
        if(sc(4,output,(long)data,64)!=64) { say("output write failed\n"); done(7); }
    }
    sc(6,output,0,0); sc(6,fd,0,0);
    say("pages="); number(count); say(" bytes="); number(count*64U); say("\n"); done(0);
}
__attribute__((naked,noreturn)) void _start(void) { __asm__ volatile("mov r0, sp\nb entry"); }
