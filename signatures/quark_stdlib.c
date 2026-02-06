#define dont_inline_me_bro() \
    puts(""); puts(""); puts(""); puts(""); puts(""); puts(""); \
    puts(""); puts(""); puts(""); puts(""); puts(""); puts(""); \
    puts(""); puts(""); puts(""); puts(""); puts(""); puts(""); \
    puts(""); puts(""); puts(""); puts(""); puts(""); puts(""); \
    puts(""); puts(""); puts("");


uint8_t _u8 = (uint8_t)__undefined;
uint16_t _u16 = (uint16_t)__undefined;
uint32_t _u32 = (uint32_t)__undefined;
uint64_t _u64 = (uint64_t)__undefined;
int8_t _i8 = (int8_t)__undefined;
int16_t _i16 = (int16_t)__undefined;
int32_t _i32 = (int32_t)__undefined;
int64_t _i64 = (int64_t)__undefined;
void* _ptr = (void*)__undefined;
    
void use_pls(...)
{
    void* foo;
    __syscall(0, __next_arg(foo, 4));
}

void builtin_group()
{
    puts("abs8");
    use_pls(abs(_i8));
    puts("abs16");
    use_pls(abs(_i16));
    puts("abs32");
    use_pls(abs(_i32));
    puts("__breakpoint");
    if (_u8 == 1)
        __breakpoint();
    puts("__byteswap16");
    use_pls(__byteswap(_u16));
    puts("__byteswap32");
    use_pls(__byteswap(_u32));
    puts("__byteswap64");
    use_pls(__byteswap(_u64));
    puts("__next_arg");
    use_pls(__next_arg(_ptr, 4));
    puts("__prev_arg");
    use_pls(__prev_arg(_ptr, 4));
    puts("__syscall");
    if (_u32 == 1)
        use_pls(__syscall(0));
    puts("__syscall2");
    if (_u32 == 1)
        use_pls(__syscall2(_u32, 0));
    dont_inline_me_bro();
}

void vprintf_group(int a, ...)
{
    FILE* f = fdopen(0);
    va_list va;
    va_start(va, a);
    puts("vprintf");
    vprintf("a", va);
    puts("vfprintf");
    vfprintf(f, "b", va);
    dont_inline_me_bro();
}

void file_group()
{
    char stuff[0x10];
    puts("chdir");
    chdir("/");
    puts("close");
    close(0);
    puts("dup");
    dup(0);
    puts("dup2");
    dup2(0, 1);
    puts("fchdir");
    fchdir(0);
    puts("fcntl");
    fcntl(0, 0, 0);
    puts("fdopen");
    FILE* f = fdopen(0);
    puts("fgetc");
    fgetc(f);
    puts("fgets");
    fgets(stuff, 0x10, f);
    puts("fprintf");
    fprintf(f, "a");
    puts("fputc");
    fputc(0, f);
    puts("fputs");
    fputs("aa", f);
    puts("fstat");
    struct stat buf;
    fstat(0, &buf);
    puts("ftruncate");
    ftruncate(0, 0);
    puts("getcwd");
    getcwd(stuff, 0x10);
    puts("getdents");
    struct dirent ents[0x10];
    getdents(0, ents, 0x10);
#ifdef SYS_getdirentries
    puts("getdirentries");
    ssize_t basep;
    getdirentries(0, ents, 0x10, &basep);
#endif
    puts("link");
    link("a", "b");
    puts("lseek");
    lseek(0, 0, 0);
    puts("lstat");
    lstat("a", &buf);
    puts("mkdir");
    mkdir("a", 0);
    puts("open");
    open("a", 0, 0);
    puts("pipe");
    int fds[2];
    pipe(fds);
    puts("printf");
    printf("a %s %s", "b", "c");
    puts("puts");
    puts("a");
    puts("read");
    read(0, stuff, 0x10);
    puts("readlink");
    readlink("a", stuff, 0x10);
    puts("rename");
    rename("a", "b");
    puts("rmdir");
    rmdir("a");
    puts("select");
    fd_set fdset;
    FD_ZERO(&fdset);
    struct timeval timeout;
    select(0, &fdset, &fdset, &fdset, &timeout);
    puts("sendfile");
    size_t offset;
    sendfile(0, 1, &offset, 0);
    puts("stat");
    stat("a", &buf);
    puts("symlink");
    symlink("a", "b");
    puts("truncate");
    truncate("a", 0);
    puts("unlink");
    unlink("a");
    puts("vprintf group");
    vprintf_group(1);
    puts("write");
    write(0, stuff, 0x10);
    dont_inline_me_bro();
}

void file_security_group()
{
#ifdef SYS_chflags
    puts("chflags");
    chflags("a", 0);
#endif
    puts("chmod");
    chmod("a", 0);
    puts("chown");
    chown("a", 0, 0);
#ifdef SYS_chflags
    puts("fchflags");
    fchflags(0, 0);
#endif
    puts("fchmod");
    fchmod(0, 0);
    puts("fchown");
    fchown(0, 0, 0);
#ifdef SYS_chflags
    puts("lchflags");
    lchflags("a", 0);
#endif
    puts("lchown");
    lchown("a", 0, 0);
    
    dont_inline_me_bro();
}

void hash_group()
{
    char data[0x10];
    puts("crc32");
    crc32(data, 0x10);
    
    dont_inline_me_bro();
}

void helper_group()
{
    puts("bash");
    if (_u8)
        bash();
    puts("create_tcp4_connection");
    if (_u8)
        create_tcp4_connection(0, 0);
    void* ip;
    puts("create_tcp6_connection");
    if (_u8)
        create_tcp6_connection(ip, 0);
    puts("create_udp4_connection");
    if (_u8)
        create_udp4_connection(0, 0);
    puts("create_udp6_connection");
    if (_u8)
        create_udp6_connection(ip, 0);
    puts("interactive_bash");
    if (_u8)
        interactive_bash();
    puts("interactive_sh");
    if (_u8)
        interactive_sh();
    puts("recv_all");
    char buffer[0x10];
    if (_u8)
        recv_all(0, buffer, 0x10, 0);
    puts("redirect_io");
    if (_u8)
        redirect_io(0);
    puts("send_all");
    if (_u8)
        send_all(0, buffer, 0x10, 0);
    puts("send_string");
    if (_u8)
        send_string(0, "a");
    puts("sh");
    if (_u8)
        sh();
    dont_inline_me_bro();
}

void memory_group()
{
    puts("alloca");
    alloca(0x10);
    puts("free");
    free(_ptr);
    puts("malloc");
    malloc(0x10);
    puts("memcpy");
    memcpy(_ptr, _ptr, 0x10);
    puts("memmove");
    memmove(_ptr, _ptr, 0x10);
    puts("memset");
    memset(_ptr, 0, 0x10);
    puts("mmap");
    mmap(NULL, 0, 0, 0, 0, 0);
    puts("munmap");
    munmap(_ptr, 0);
    puts("mprotect");
    mprotect(_ptr, 0, 0);
#ifdef SYS_shm_open
    puts("shm_open");
    shm_open("a", 0, 0);
#endif
#ifdef SYS_shm_unlink
    puts("shm_unlink");
    shm_unlink("a");
#endif
    dont_inline_me_bro();
}

void process_group()
{
    puts("execl");
    execl("a", "b", "c");
    const char* foo;
    puts("execve");
    execve("a", &foo, &foo);
    puts("exit");
    if (_u8)
        exit(1);
    puts("fork");
    fork();
    puts("getpgid");
    getpgid(0);
    puts("getpgrp");
    getpgrp();
    puts("getpid");
    getpid();
    puts("getppid");
    getppid();
    puts("kill");
    kill(0, 0);
    puts("setpgid");
    setpgid(0, 0);
    puts("setsid");
    setsid();
    puts("sigaction");
    struct sigaction sig;
    sigaction(0, &sig, &sig);
    puts("signal");
    void (*sigfn)(int);
    signal(0, sigfn);
#ifdef SYS_sysctl
    puts("sysctl");
    size_t sz;
    sysctl(&_i32, 0, _ptr, &sz, _ptr, sz);
#endif
    puts("system");
    system("a");
    puts("tgkill");
    tgkill(0, 0, 0);
    puts("wait");
    wait(&_i32);
    puts("waitpid");
    waitpid(0, &_i32, 0);
    dont_inline_me_bro();
}

void process_security_group()
{
    puts("getegid");
    getegid();
    puts("geteuid");
    geteuid();
    puts("getgid");
    getgid();
    puts("getgroups");
    gid_t groups[0x10];
    getgroups(0x10, groups);
    puts("getuid");
    getuid();
    puts("setegid");
    setegid(0);
    puts("seteuid");
    seteuid(0);
    puts("setgid");
    setgid(0);
    puts("setregid");
    setregid(0, 0);
    puts("setreuid");
    setreuid(0, 0);
    puts("setuid");
    setuid(0);
    dont_inline_me_bro();
}

void rc4_group()
{
    rc4_state_t state;
    puts("rc4_crypt");
    rc4_crypt(&state, _ptr, 0);
    puts("rc4_init");
    rc4_init(&state, _ptr, 0);
    puts("rc4_output");
    rc4_output(&state);
    dont_inline_me_bro();
}

void socket_group()
{
    puts("accept");
    struct sockaddr addr;
    socklen_t addrlen;
    accept(0, &addr, &addrlen);
    puts("accept4");
    accept4(0, &addr, &addrlen, 0);
    puts("bind");
    bind(0, &addr, addrlen);
    puts("connect");
    connect(0, &addr, addrlen);
    puts("getpeername");
    getpeername(0, &addr, &addrlen);
    puts("getsockname");
    getsockname(0, &addr, &addrlen);
    puts("getsockopt");
    getsockopt(0, 0, 0, _ptr, &addrlen);
    puts("listen");
    listen(0, 0);
    puts("recv");
    recv(0, _ptr, 0, 0);
    puts("recvfrom");
    recvfrom(0, _ptr, 0, 0, &addr, &addrlen);
    puts("send");
    send(0, _ptr, 0, 0);
    puts("sendto");
    sendto(0, _ptr, 0, 0, &addr, addrlen);
    puts("setsockopt");
    setsockopt(0, 0, 0, _ptr, 0);
    puts("shutdown");
    shutdown(0, 0);
    puts("closesocket");
    closesocket(0);
    puts("socket");
    socket(0, 0, 0);
    puts("socketpair");
    int fds[2];
    socketpair(0, 0, 0, fds);
    dont_inline_me_bro();
}

void vsprintf_group(int a, ...)
{
    char str[0x10];
    va_list va;
    va_start(va, a);
    puts("vsprintf");
    vsprintf(str, "a", va);
    puts("vsnprintf");
    vsnprintf(str, 0x10, "b", va);
    dont_inline_me_bro();
}

void string_group()
{
    char str[0x10];
    puts("atoi");
    atoi("0");
    puts("snprintf");
    snprintf(str, 0x10, "a %s", "b");
    puts("sprintf");
    sprintf(str, "a %s", "b");
    puts("strcat");
    strcat(str, str);
    puts("strchr");
    strchr(str, 'a');
    puts("strstr");
    strstr(str, str);
    puts("strcmp");
    strcmp(str, str);
    puts("strncmp");
    strncmp(str, str, 0x10);
    puts("strcpy");
    strcpy(str, str);
    puts("strdup");
    strdup(str);
    puts("strlen");
    strlen(str);
    puts("strncpy");
    strncpy(str, str, 0x10);
    puts("strrchr");
    strrchr(str, 'a');
    puts("vsprintf group");
    vsprintf_group(0);
    dont_inline_me_bro();
}

void time_group()
{
    puts("alarm");
    alarm(0);
    puts("getitimer");
    struct itimerval val;
    getitimer(0, &val);
    puts("gettimeofday");
    struct timeval t;
    struct timezone tz;
    gettimeofday(&t, &tz);
    puts("nanosleep");
    struct timespec amount;
    nanosleep(&amount, &amount);
    puts("setitimer");
    setitimer(0, &val, &val);
    puts("time");
    time_t ti;
    time(&ti);
    dont_inline_me_bro();
}

// LOL
void quark_exec(void* buf, ...) __noreturn;

void vm_group()
{
    puts("quark_exec");
    if (_u8)
        quark_exec(_ptr);
    dont_inline_me_bro();
}

void main()
{
    builtin_group();
    file_group();
    file_security_group();
    hash_group();
    helper_group();
    memory_group();
    process_group();
    process_group();
    process_security_group();
    rc4_group();
    socket_group();
    string_group();
    time_group();
    vm_group();
}

