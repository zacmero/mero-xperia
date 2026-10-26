/* ARM Linux EABI syscalls: no libc, Android framework, or root required. */
static const char message[] = "Hello from the Xperia ARMv6!\n";

__attribute__((noreturn)) void _start(void)
{
    register long r0 __asm__("r0") = 1; /* stdout */
    register const char *r1 __asm__("r1") = message;
    register unsigned long r2 __asm__("r2") = sizeof(message) - 1;
    register long r7 __asm__("r7") = 4; /* write */
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r1), "r"(r2), "r"(r7) : "memory");

    /* Return failure if write did not produce the complete greeting. */
    r0 = r0 == sizeof(message) - 1 ? 0 : 1;
    r7 = 1; /* exit */
    __asm__ volatile("svc 0" : : "r"(r0), "r"(r7) : "memory");
    __builtin_unreachable();
}
