#include "posix.c"
#include "linux.c"

typedef void* va_list;

void sys_exit(int32_t status) __syscall(1) __noreturn;
void sys_exit_group(int32_t status) __syscall(252) __noreturn;
