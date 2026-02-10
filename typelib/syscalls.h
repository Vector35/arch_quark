
typedef void* va_list;

//------------------------------------------------------------------------------
// Forward Declarations of Structures
//------------------------------------------------------------------------------

struct __kernel_fd_set;
struct __kernel_fsid_t;
struct __kernel_old_timeval;
struct __sysctl_args;
struct __timespec64;
struct __user_cap_data_struct;
struct __user_cap_header_struct;
struct arch_spinlock_t;
struct atomic64_t;
struct atomic_t;
struct bio_vec;
struct callback_head;
struct clone_args;
struct cpu_set_t;
struct epoll_event;
struct file_handle;
struct fp_emul_space;
struct fpchip_state;
struct fpregset_t;
struct getcpu_cache;
struct hlist_head;
struct hlist_head_t;
struct hlist_node;
struct hlist_node_t;
struct in_addr;
struct io_context;
struct io_cq;
struct io_cqring_offsets;
struct io_event;
struct io_sqring_offsets;
struct io_uring_params;
struct iocb;
struct iov_iter;
struct iovec;
struct ipc_perm;
struct itimerspec;
struct itimerval;
struct kernel_sigset_t;
struct kernel_sym;
struct kexec_segment;
struct kiocb;
struct kvec;
struct l_timespec;
struct linux_dirent;
struct linux_dirent64;
struct list_head;
struct list_head_t;
struct mcontext_t;
struct mmsghdr;
struct mq_attr;
struct msg;
struct msghdr;
struct msqid_ds;
struct new_utsname;
struct nfsctl_arg;
struct nfsctl_client;
struct nfsctl_export;
struct nfsctl_fdparm;
struct nfsctl_fsparm;
struct nfsctl_svc;
struct old_linux_dirent;
struct perf_event_attr;
struct pollfd;
struct qspinlock;
struct raw_spinlock;
struct raw_spinlock_t;
struct revectored_struct;
struct rlimit;
struct robust_list;
struct robust_list_head;
struct rseq;
struct rusage;
struct sched_attr;
struct sched_param;
struct sembuf;
struct shmid_ds;
struct sigaction;
struct sigevent;
struct sigevent_t;
struct siginfo;
struct siginfo_t;
struct sockaddr;
struct spinlock;
struct spinlock_t;
struct stack_t;
struct stat;
struct stat64;
struct statfs;
struct statfs64;
struct statx;
struct statx_timestamp;
struct strbuf;
struct sysinfo;
struct timeb;
struct timespec;
struct timeval;
struct timex;
struct timezone;
struct tms;
struct user_desc;
struct user_msghdr;
struct ustat;
struct utimbuf;
struct vm86_regs;
struct vm86_struct;
struct vm86plus_info_struct;
struct vm86plus_struct;
struct work_struct;
struct xarray;
union __sifields;
union bpf_attr;
union nfsctl_res;
union sigval;
union sigval_t;
//------------------------------------------------------------------------------
// Type Definitions
//------------------------------------------------------------------------------

// "__ptrace_request"
enum __ptrace_request : uint32_t
{
	PTRACE_TRACEME = 0x0,
	PTRACE_PEEKTEXT = 0x1,
	PTRACE_PEEKDATA = 0x2,
	PTRACE_PEEKUSER = 0x3,
	PTRACE_POKETEXT = 0x4,
	PTRACE_POKEDATA = 0x5,
	PTRACE_POKEUSER = 0x6,
	PTRACE_CONT = 0x7,
	PTRACE_KILL = 0x8,
	PTRACE_SINGLESTEP = 0x9,
	PTRACE_GETREGS = 0xc,
	PTRACE_SETREGS = 0xd,
	PTRACE_GETFPREGS = 0xe,
	PTRACE_SETFPREGS = 0xf,
	PTRACE_ATTACH = 0x10,
	PTRACE_DETACH = 0x11,
	PTRACE_GETVRREGS = 0x12,
	PTRACE_SETVRREGS = 0x13,
	PTRACE_GETEVRREGS = 0x14,
	PTRACE_SETEVRREGS = 0x15,
	PTRACE_GETREGS64 = 0x16,
	PTRACE_SETREGS64 = 0x17,
	PTRACE_SYSCALL = 0x18,
	PTRACE_GET_DEBUGREG = 0x19,
	PTRACE_SET_DEBUGREG = 0x1a,
	PTRACE_GETVSRREGS = 0x1b,
	PTRACE_SETVSRREGS = 0x1c,
	PTRACE_SINGLEBLOCK = 0x100,
	PTRACE_SETOPTIONS = 0x4200,
	PTRACE_GETEVENTMSG = 0x4201,
	PTRACE_GETSIGINFO = 0x4202,
	PTRACE_SETSIGINFO = 0x4203,
	PTRACE_GETREGSET = 0x4204,
	PTRACE_SETREGSET = 0x4205,
	PTRACE_SEIZE = 0x4206,
	PTRACE_INTERRUPT = 0x4207,
	PTRACE_LISTEN = 0x4208,
	PTRACE_PEEKSIGINFO = 0x4209,
	PTRACE_GETSIGMASK = 0x420a,
	PTRACE_SETSIGMASK = 0x420b,
	PTRACE_SECCOMP_GET_FILTER = 0x420c,
	PTRACE_SECCOMP_GET_METADATA = 0x420d,
	PTRACE_GET_SYSCALL_INFO = 0x420e
};

// "e_dyn_tag"
enum e_dyn_tag : uint32_t
{
	DT_NULL = 0x0,
	DT_NEEDED = 0x1,
	DT_PLTRELSZ = 0x2,
	DT_PLTGOT = 0x3,
	DT_HASH = 0x4,
	DT_STRTAB = 0x5,
	DT_SYMTAB = 0x6,
	DT_RELA = 0x7,
	DT_RELASZ = 0x8,
	DT_RELAENT = 0x9,
	DT_STRSZ = 0xa,
	DT_SYMENT = 0xb,
	DT_INIT = 0xc,
	DT_FINI = 0xd,
	DT_SONAME = 0xe,
	DT_RPATH = 0xf,
	DT_SYMBOLIC = 0x10,
	DT_REL = 0x11,
	DT_RELSZ = 0x12,
	DT_RELENT = 0x13,
	DT_PLTREL = 0x14,
	DT_DEBUG = 0x15,
	DT_TEXTREL = 0x16,
	DT_JMPREL = 0x17,
	DT_BIND_NOW = 0x18,
	DT_INIT_ARRAY = 0x19,
	DT_FINI_ARRAY = 0x1a,
	DT_INIT_ARRAYSZ = 0x1b,
	DT_FINI_ARRAYSZ = 0x1c,
	DT_RUNPATH = 0x1d,
	DT_FLAGS = 0x1e,
	DT_ENCODING = 0x1f,
	DT_PREINIT_ARRAY = 0x20,
	DT_PREINIT_ARRAYSZ = 0x21,
	DT_LOOS = 0x6000000d,
	DT_SUNW_RTLDINF = 0x6000000e,
	DT_HIOS = 0x6ffff000,
	DT_VALRNGLO = 0x6ffffd00,
	DT_CHECKSUM = 0x6ffffdf8,
	DT_PLTPADSZ = 0x6ffffdf9,
	DT_MOVEENT = 0x6ffffdfa,
	DT_MOVESZ = 0x6ffffdfb,
	DT_FEATURE_1 = 0x6ffffdfc,
	DT_POSFLAG_1 = 0x6ffffdfd,
	DT_SYMINSZ = 0x6ffffdfe,
	DT_SYMINENT = 0x6ffffdff,
	DT_VALRNGHI = 0x6ffffdff,
	DT_ADDRRNGLO = 0x6ffffe00,
	DT_GNU_HASH = 0x6ffffef5,
	DT_CONFIG = 0x6ffffefa,
	DT_DEPAUDIT = 0x6ffffefb,
	DT_AUDIT = 0x6ffffefc,
	DT_PLTPAD = 0x6ffffefd,
	DT_MOVETAB = 0x6ffffefe,
	DT_SYMINFO = 0x6ffffeff,
	DT_ADDRRNGHI = 0x6ffffeff,
	DT_RELACOUNT = 0x6ffffff9,
	DT_RELCOUNT = 0x6ffffffa,
	DT_FLAGS_1 = 0x6ffffffb,
	DT_VERDEF = 0x6ffffffc,
	DT_VERDEFNUM = 0x6ffffffd,
	DT_VERNEED = 0x6ffffffe,
	DT_VERNEEDNUM = 0x6fffffff,
	DT_VERSYM = 0x6ffffff0,
	DT_MIPS_RLD_VERSION = 0x70000001,
	DT_MIPS_TIME_STAMP = 0x70000002,
	DT_MIPS_ICHECKSUM = 0x70000003,
	DT_MIPS_IVERSION = 0x70000004,
	DT_MIPS_FLAGS = 0x70000005,
	DT_MIPS_BASE_ADDRESS = 0x70000006,
	DT_MIPS_CONFLICT = 0x70000008,
	DT_MIPS_LIBLIST = 0x70000009,
	DT_MIPS_LOCAL_GOTNO = 0x7000000a,
	DT_MIPS_CONFLICTNO = 0x7000000b,
	DT_MIPS_LIBLISTNO = 0x70000010,
	DT_MIPS_SYMTABNO = 0x70000011,
	DT_MIPS_UNREFEXTNO = 0x70000012,
	DT_MIPS_GOTSYM = 0x70000013,
	DT_MIPS_HIPAGENO = 0x70000014,
	DT_MIPS_RLD_MAP = 0x70000016,
	DT_MIPS_RLD_MAP_REL = 0x70000035
};

// "idtype_t"
enum idtype_t : uint32_t
{
	P_ALL = 0x0,
	P_PID = 0x1,
	P_PGID = 0x2
};

// "__ino64_t"
typedef uint64_t __ino64_t;

// "__syscall_ulong_t"
typedef uint32_t __syscall_ulong_t;

// "__sysctl_args"
struct __sysctl_args
{
	int32_t* name;
	int32_t nlen;
	void* oldval;
	uint32_t* oldlenp;
	void* newval;
	uint32_t newlen;
	uint32_t __unused[0x4];
};

// "__uint16_t"
typedef uint16_t __uint16_t;

// "__uint32_t"
typedef uint32_t __uint32_t;

// "__uint64_t"
typedef uint64_t __uint64_t;

// "bio_vec"
struct bio_vec
{
	uint32_t bv_len;
	uint32_t bv_offset;
};

// "blkcnt64_t"
typedef int64_t blkcnt64_t;

// "caddr_t"
typedef char* caddr_t;

// "cap_user_data_t"
typedef struct __user_cap_data_struct* cap_user_data_t;

// "cap_user_header_t"
typedef struct __user_cap_header_struct* cap_user_header_t;

// "clockid_t"
typedef int32_t clockid_t;

// "getcpu_cache"
struct getcpu_cache
{
	uint32_t blob[0x20];
};

// "hlist_head"
struct hlist_head
{
	struct hlist_head* next;
	struct hlist_head* prev;
};

// "hlist_node"
struct hlist_node
{
	struct hlist_node* next;
	struct hlist_node** pprev;
};

// "hlist_node_t"
struct hlist_node_t
{
	struct hlist_node* next;
	struct hlist_node** pprev;
};

// "id_t"
typedef uint32_t id_t;

// "io_context_t"
typedef struct io_context* io_context_t;

// "iovec"
struct iovec
{
	void* iov_base;
	uint32_t iov_len;
};

// "kernel_sym"
struct kernel_sym
{
	int32_t value_offset;
	int32_t name_offset;
	int32_t namespace_offset;
};

// "kexec_segment"
struct kexec_segment
{
	void* kbuf;
	uint32_t bufsz;
	uint32_t mem;
	uint32_t memsz;
};

// "key_serial_t"
typedef int32_t key_serial_t;

// "key_t"
typedef int32_t key_t;

// "kvec"
struct kvec
{
	void* iov_base;
	uint32_t iov_len;
};

// "l_int"
typedef int32_t l_int;

// "linux_dirent"
struct linux_dirent
{
	uint32_t d_ino;
	uint32_t d_off;
	uint16_t d_reclen;
	char d_name[0x1];
};

// "list_head"
struct list_head
{
	struct list_head* next;
	struct list_head* prev;
};

// "mqd_t"
typedef int32_t mqd_t;

// "new_utsname"
struct new_utsname
{
	char sysname[0x41];
	char nodename[0x41];
	char release[0x41];
	char version[0x41];
	char machine[0x41];
	char domainname[0x41];
};

// "nfds_t"
typedef uint32_t nfds_t;

// "nfsctl_res"
union nfsctl_res
{
	uint32_t cr_debug;
};

// "off64_t"
typedef int64_t off64_t;

// "old_linux_dirent"
struct old_linux_dirent
{
	uint32_t d_ino;
	uint32_t d_offset;
	uint16_t d_namlen;
	char d_name[0x1];
};

// "pid_t"
typedef int32_t pid_t;

// "pollfd"
struct pollfd
{
	int32_t fd;
	int16_t events;
	int16_t revents;
};

// "sched_param"
struct sched_param
{
	int32_t sched_priority;
};

// "sembuf"
struct sembuf
{
	uint16_t sem_num;
	int16_t sem_op;
	int16_t sem_flg;
};

// "sighandler_t"
typedef void (* sighandler_t)(int32_t);

// "siginfo"
struct siginfo
{
	int32_t _si_pad[0xc];
};

// "siginfo_t"
struct siginfo_t
{
	int32_t _si_pad[0xc];
};

// "sigval"
union sigval
{
	int32_t sival_int;
	void* sival_ptr;
};

// "size_t"
typedef uint32_t size_t;

// "socklen_t"
typedef uint32_t socklen_t;

// "stack_t"
struct stack_t
{
	void* ss_sp;
	int32_t ss_flags;
	uint32_t ss_size;
};

// "stat64"
struct stat64
{
	uint64_t st_dev;
	uint8_t __pad0[0x4];
	uint32_t __st_ino;
	uint32_t st_mode;
	uint32_t st_nlink;
	uint32_t st_uid;
	uint32_t st_gid;
	uint64_t st_rdev;
	uint8_t __pad3[0x4];
	int64_t st_size;
	uint32_t st_blksize;
	int64_t st_blocks;
	uint32_t st_atime;
	uint32_t st_atime_nsec;
	uint32_t st_mtime;
	uint32_t st_mtime_nsec;
	uint32_t st_ctime;
	uint32_t st_ctime_nsec;
	uint64_t st_ino;
};

// "strbuf"
struct strbuf
{
	int32_t maxlen;
	int32_t len;
	char* buf;
};

// "timezone"
struct timezone
{
	int32_t tz_minuteswest;
	int32_t tz_dsttime;
};

// "u32"
typedef uint32_t u32;

// "u64"
typedef uint64_t u64;

// "user_desc"
struct user_desc
{
	uint32_t entry_number;
	uint32_t base_addr;
	uint32_t limit;
	uint32_t seg_32bit;
	uint32_t contents;
	uint32_t read_exec_only;
	uint32_t limit_in_pages;
	uint32_t seg_not_present;
	uint32_t useable;
};

// "va_list"
typedef void* va_list;

// "__blkcnt_t"
typedef int32_t __blkcnt_t;

// "__kernel_ipc_pid_t"
typedef int32_t __kernel_ipc_pid_t;

// "vm86plus_info_struct"
struct vm86plus_info_struct
{
	uint32_t force_return_for_pic;
	uint32_t vm86dbg_active;
	uint32_t vm86dbg_TFpendig;
	uint32_t unused;
	uint32_t is_vm86pus;
	uint8_t vm86dbg_intxxtab[0x20];
};

// "dev_t"
typedef uint64_t dev_t;

// "__cpu_mask"
typedef uint32_t __cpu_mask;

// "__kernel_gid_t"
typedef uint32_t __kernel_gid_t;

// "fp_emul_space"
struct fp_emul_space
{
	char fp_emul[0xf6];
	char fp_epad[0x2];
};

// "__kernel_long_t"
typedef int32_t __kernel_long_t;

// "uid_t"
typedef uint32_t uid_t;

// "__kernel_uid32_t"
typedef uint32_t __kernel_uid32_t;

// "blksize_t"
typedef int32_t blksize_t;

// "__s32"
typedef int32_t __s32;

// "__syscall_slong_t"
typedef int32_t __syscall_slong_t;

// "__kernel_daddr_t"
typedef int32_t __kernel_daddr_t;

// "off_t"
typedef int32_t off_t;

// "list_head_t"
struct list_head_t
{
	struct list_head* next;
	struct list_head* prev;
};

// "__kernel_fd_set"
struct __kernel_fd_set
{
	uint32_t fds_bits[0x20];
};

// "gregset_t"
typedef uint32_t gregset_t[0x13];

// "__u32"
typedef uint32_t __u32;

// "__kernel_fsid_t"
struct __kernel_fsid_t
{
	int32_t val[0x2];
};

// "__kernel_timer_t"
typedef int32_t __kernel_timer_t;

// "__u64"
typedef uint64_t __u64;

// "iov_iter"
struct iov_iter
{
	uint32_t type;
	uint32_t iov_offset;
	uint32_t count;
	struct bio_vec* bvec;
	uint32_t head;
	uint32_t start_head;
};

// "u8"
typedef uint8_t u8;

// "sa_family_t"
typedef uint16_t sa_family_t;

// "fpchip_state"
struct fpchip_state
{
	int32_t state[0x1b];
	int32_t status;
};

// "__nlink_t"
typedef uint32_t __nlink_t;

// "s64"
typedef int64_t s64;

// "__kernel_uid_t"
typedef uint32_t __kernel_uid_t;

// "revectored_struct"
struct revectored_struct
{
	uint32_t __map[0x8];
};

// "nfsctl_svc"
struct nfsctl_svc
{
	uint16_t svc_port;
	int32_t svc_nthreads;
};

// "callback_head"
struct callback_head
{
	struct callback_head* next;
	void (* func)(struct callback_head* head);
};

// "robust_list"
struct robust_list
{
	struct robust_list* next;
};

// "__kernel_pid_t"
typedef int32_t __kernel_pid_t;

// "__kernel_key_t"
typedef int32_t __kernel_key_t;

// "__s64"
typedef int64_t __s64;

// "sigval_t"
union sigval_t
{
	int32_t sival_int;
	void* sival_ptr;
};

// "__kernel_size_t"
typedef uint32_t __kernel_size_t;

// "__s16"
typedef int16_t __s16;

// "gid_t"
typedef uint32_t gid_t;

// "__u16"
typedef uint16_t __u16;

// "l_long"
typedef int32_t l_long;

// "__kernel_old_dev_t"
typedef uint16_t __kernel_old_dev_t;

// "__kernel_mode_t"
typedef uint32_t __kernel_mode_t;

// "kernel_sigset_t"
struct kernel_sigset_t
{
	uint32_t __val[0x20];
};

// "l_ulong"
typedef uint32_t l_ulong;

// "hlist_head_t"
struct hlist_head_t
{
	struct hlist_head* next;
	struct hlist_head* prev;
};

// "mode_t"
typedef uint32_t mode_t;

// "__time_t"
typedef int32_t __time_t;

// "__suseconds_t"
typedef int32_t __suseconds_t;

// "__kernel_loff_t"
typedef int64_t __kernel_loff_t;

// "__kernel_ulong_t"
typedef uint32_t __kernel_ulong_t;

// "__ino_t"
typedef uint32_t __ino_t;

// "__kernel_rwf_t"
typedef int32_t __kernel_rwf_t;

// "atomic_t"
struct atomic_t
{
	int32_t counter;
};

// "gfp_t"
typedef uint32_t gfp_t;

// "work_func_t"
typedef void (* work_func_t)(struct work_struct* work);

// "vm86_regs"
struct vm86_regs
{
	int32_t ebx;
	int32_t ecx;
	int32_t edx;
	int32_t esi;
	int32_t edi;
	int32_t ebp;
	int32_t eax;
	int32_t __null_ds;
	int32_t __null_es;
	int32_t __null_fs;
	int32_t __null_gs;
	int32_t orig_eax;
	int32_t eip;
	uint16_t cs;
	uint16_t __csh;
	int32_t eflags;
	int32_t esp;
	uint16_t ss;
	uint16_t __ssh;
	uint16_t es;
	uint16_t __esh;
	uint16_t ds;
	uint16_t __dsh;
	uint16_t fs;
	uint16_t __fsh;
	uint16_t gs;
	uint16_t __gsh;
};

// "arch_spinlock_t"
struct arch_spinlock_t
{
	u8 reserved[0x2];
	u8 pending;
	u8 locked;
};

// "raw_spinlock"
struct raw_spinlock
{
	struct arch_spinlock_t raw_lock;
};

// "atomic64_t"
struct atomic64_t
{
	s64 counter;
};

// "__be32"
typedef __u32 __be32;

// "spinlock_t"
struct spinlock_t
{
	struct raw_spinlock rlock;
};

// "atomic_long_t"
typedef struct atomic64_t atomic_long_t;

// "__kernel_time_t"
typedef __kernel_long_t __kernel_time_t;

// "sockaddr"
struct sockaddr
{
	sa_family_t sa_family;
	char sa_data[0xe];
};

// "__kernel_ino_t"
typedef __kernel_ulong_t __kernel_ino_t;

// "in_addr"
struct in_addr
{
	__be32 s_addr;
};

// "__kernel_old_time_t"
typedef __kernel_long_t __kernel_old_time_t;

// "ipc_perm"
struct ipc_perm
{
	__kernel_key_t key;
	__kernel_uid_t uid;
	__kernel_gid_t gid;
	__kernel_uid_t cuid;
	__kernel_gid_t cgid;
	__kernel_mode_t mode;
	uint16_t seq;
};

// "time_t"
typedef __time_t time_t;

// "timeval"
struct timeval
{
	__time_t tv_sec;
	__suseconds_t tv_usec;
};

// "__kernel_clock_t"
typedef __kernel_long_t __kernel_clock_t;

// "u16"
typedef __u16 u16;

// "loff_t"
typedef __kernel_loff_t loff_t;

// "xarray"
struct xarray
{
	struct spinlock_t xa_lock;
	gfp_t xa_flags;
	void* xa_head;
};

// "work_struct"
struct work_struct
{
	atomic_long_t data;
	struct list_head_t entry;
	work_func_t func;
};

// "timespec"
struct timespec
{
	__kernel_time_t tv_sec;
	__syscall_slong_t tv_nsec;
};

// "nfsctl_fsparm"
struct nfsctl_fsparm
{
	struct sockaddr gd_addr;
	char gd_path[0x401];
	int32_t gd_maxlen;
};

// "nfsctl_fdparm"
struct nfsctl_fdparm
{
	struct sockaddr gd_addr;
	char gd_path[0x401];
	int32_t gd_version;
};

// "nfsctl_export"
struct nfsctl_export
{
	char ex_client[0x401];
	char ex_path[0x401];
	__kernel_old_dev_t ex_dev;
	__kernel_ino_t ex_ino;
	int32_t ex_flags;
	__kernel_uid_t ex_anon_uid;
	__kernel_gid_t ex_anon_gid;
};

// "nfsctl_client"
struct nfsctl_client
{
	char cl_ident[0x401];
	int32_t cl_naddr;
	struct in_addr cl_addrlist[0x10];
	int32_t cl_fhkeytype;
	int32_t cl_fhkeylen;
	uint8_t cl_fhkey[0x20];
};

// "l_time_t"
typedef l_long l_time_t;

// "time64_t"
typedef __s64 time64_t;

struct io_sqring_offsets
{
	__u32 head;
	__u32 tail;
	__u32 ring_mask;
	__u32 ring_entries;
	__u32 flags;
	__u32 dropped;
	__u32 array;
	__u32 resv1;
	__u64 resv2;
};

// "io_cqring_offsets"
struct io_cqring_offsets
{
	__u32 head;
	__u32 tail;
	__u32 ring_mask;
	__u32 ring_entries;
	__u32 overflow;
	__u32 cqes;
	__u32 flags;
	__u32 resv1;
	__u64 resv2;
};

// "statx_timestamp"
struct statx_timestamp
{
	__s64 tv_sec;
	__u32 tv_nsec;
};

// "fpregset_t"
struct fpregset_t
{
	union
	{
		struct fpchip_state fpchip_state;
		struct fp_emul_space fp_emul_space;
		int32_t f_fpregs[0x3e];
	} fp_reg_set;
	int32_t f_wregs[0x21];
};

// "__kernel_old_timeval"
struct __kernel_old_timeval
{
	__kernel_long_t tv_sec;
	__kernel_long_t tv_usec;
};

// "user_msghdr"
struct user_msghdr
{
	void* msg_name;
	int32_t msg_namelen;
	struct iovec* msg_iov;
	__kernel_size_t msg_iovlen;
	void* msg_control;
	__kernel_size_t msg_controllen;
	uint32_t msg_flags;
};

// "statfs64"
struct statfs64
{
	__kernel_long_t f_type;
	__kernel_long_t f_bsize;
	__u64 f_blocks;
	__u64 f_bfree;
	__u64 f_bavail;
	__u64 f_files;
	__u64 f_ffree;
	struct __kernel_fsid_t f_fsid;
	__kernel_long_t f_namelen;
	__kernel_long_t f_frsize;
	__kernel_long_t f_flags;
	__kernel_long_t f_spare[0x4];
};

// "file_handle"
struct file_handle
{
	__u32 handle_bytes;
	int32_t handle_type;
	uint8_t f_handle[0x0];
};

// "sysinfo"
struct sysinfo
{
	__kernel_long_t uptime;
	__kernel_ulong_t loads[0x3];
	__kernel_ulong_t totalram;
	__kernel_ulong_t freeram;
	__kernel_ulong_t sharedram;
	__kernel_ulong_t bufferram;
	__kernel_ulong_t totalswap;
	__kernel_ulong_t freeswap;
	__u16 procs;
	__u16 pad;
	__kernel_ulong_t totalhigh;
	__kernel_ulong_t freehigh;
	__u32 mem_unit;
};

// "utimbuf"
struct utimbuf
{
	__kernel_old_time_t actime;
	__kernel_old_time_t modtime;
};

// "msqid_ds"
struct msqid_ds
{
	struct ipc_perm msg_perm;
	struct msg* msg_first;
	struct msg* msg_last;
	__kernel_old_time_t msg_stime;
	__kernel_old_time_t msg_rtime;
	__kernel_old_time_t msg_ctime;
	uint32_t msg_lcbytes;
	uint32_t msg_lqbytes;
	uint16_t msg_cbytes;
	uint16_t msg_qnum;
	uint16_t msg_qbytes;
	__kernel_ipc_pid_t msg_lspid;
	__kernel_ipc_pid_t msg_lrpid;
};

// "ustat"
struct ustat
{
	__kernel_daddr_t f_tfree;
	__kernel_ino_t f_tinode;
	char f_fname[0x6];
	char f_fpack[0x6];
};

// "msg"
struct msg
{
	struct msg* msg_next;
	int32_t msg_type;
	char* msg_spot;
	time_t msg_stime;
	int16_t msg_ts;
};

// "perf_event_attr"
struct perf_event_attr
{
	__u32 type;
	__u32 size;
	__u64 config;
	__u64 sample_freq;
	__u64 sample_type;
	__u64 read_format;
	__u64 disabled;
	__u64 inherit;
	__u64 pinned;
	__u64 exclusive;
	__u64 exclude_user;
	__u64 exclude_kernel;
	__u64 exclude_hv;
	__u64 exclude_idle;
	__u64 mmap;
	__u64 comm;
	__u64 freq;
	__u64 inherit_stat;
	__u64 enable_on_exec;
	__u64 task;
	__u64 watermark;
	__u64 precise_ip;
	__u64 mmap_data;
	__u64 sample_id_all;
	__u64 exclude_host;
	__u64 exclude_guest;
	__u64 exclude_callchain_kernel;
	__u64 exclude_callchain_user;
	__u64 mmap2;
	__u64 comm_exec;
	__u64 use_clockid;
	__u64 context_switch;
	__u64 write_backward;
	__u64 namespaces;
	__u64 ksymbol;
	__u64 bpf_event;
	__u64 aux_output;
	__u64 cgroup;
	__u64 __reserved_1;
	__u32 wakeup_watermark;
	__u32 bp_type;
	__u64 config1;
	__u64 config2;
	__u64 branch_sample_type;
	__u64 sample_regs_user;
	__u32 sample_stack_user;
	__s32 clockid;
	__u64 sample_regs_intr;
	__u32 aux_watermark;
	__u16 sample_max_stack;
	__u16 __reserved_2;
	__u32 aux_sample_size;
	__u32 __reserved_3;
};

// "l_uintptr_t"
typedef l_ulong l_uintptr_t;

// "timex"
struct timex
{
	uint32_t modes;
	__syscall_slong_t offset;
	__syscall_slong_t freq;
	__syscall_slong_t maxerror;
	__syscall_slong_t esterror;
	int32_t status;
	__syscall_slong_t constant;
	__syscall_slong_t precision;
	__syscall_slong_t tolerance;
	struct timeval time;
	__syscall_slong_t tick;
	__syscall_slong_t ppsfreq;
	__syscall_slong_t jitter;
	int32_t shift;
	__syscall_slong_t stabil;
	__syscall_slong_t jitcnt;
	__syscall_slong_t calcnt;
	__syscall_slong_t errcnt;
	__syscall_slong_t stbcnt;
	int32_t tai;
};

// "itimerval"
struct itimerval
{
	struct timeval it_interval;
	struct timeval it_value;
};

// "shmid_ds"
struct shmid_ds
{
	struct ipc_perm shm_perm;
	int32_t shm_segsz;
	__kernel_old_time_t shm_atime;
	__kernel_old_time_t shm_dtime;
	__kernel_old_time_t shm_ctime;
	__kernel_ipc_pid_t shm_cpid;
	__kernel_ipc_pid_t shm_lpid;
	uint16_t shm_nattch;
	uint16_t shm_unused;
	void* shm_unused2;
	void* shm_unused3;
};

// "tms"
struct tms
{
	__kernel_clock_t tms_utime;
	__kernel_clock_t tms_stime;
	__kernel_clock_t tms_cutime;
	__kernel_clock_t tms_cstime;
};

// "sigaction"
struct sigaction
{
	void (* sa_handler)(int32_t);
	void (* sa_sigaction)(int32_t, struct siginfo_t*, void*);
	struct kernel_sigset_t sa_mask;
	int32_t sa_flags;
	void (* sa_restorer)();
};

// "kiocb"
struct kiocb
{
	loff_t ki_pos;
	void (* ki_complete)(struct kiocb* iocb, int32_t ret, int32_t ret2);
	void* private_;
	int32_t ki_flags;
	u16 ki_hint;
	u16 ki_ioprio;
	uint32_t ki_cookie;
};

// "cpu_set_t"
struct cpu_set_t
{
	__cpu_mask __bits[0x20];
};

// "__user_cap_data_struct"
struct __user_cap_data_struct
{
	__u32 effective;
	__u32 permitted;
	__u32 inheritable;
};

// "vm86plus_struct"
struct vm86plus_struct
{
	struct vm86_regs regs;
	uint32_t flags;
	uint32_t screen_bitmap;
	uint32_t cpu_type;
	struct revectored_struct int_revectored;
	struct revectored_struct int21_revectored;
	struct vm86plus_info_struct vm86plus;
};

// "io_cq"
struct io_cq
{
	struct io_context* ioc;
	struct list_head_t q_node;
	struct callback_head __rcu_head;
	uint32_t flags;
};

// "bpf_attr"
union bpf_attr
{
	__u32 map_type;
	__u32 map_fd;
	struct
	{
		__u64 in_batch;
		__u64 out_batch;
		__u64 keys;
		__u64 values;
		__u32 count;
		__u32 map_fd;
		__u64 elem_flags;
		__u64 flags;
	} batch;
	__u32 prog_type;
	__u64 pathname;
	__u32 target_fd;
	struct
	{
		__u32 prog_fd;
		__u32 retval;
		__u32 data_size_in;
		__u32 data_size_out;
		__u64 data_in;
		__u64 data_out;
		__u32 repeat;
		__u32 duration;
		__u32 ctx_size_in;
		__u32 ctx_size_out;
		__u64 ctx_in;
		__u64 ctx_out;
	} test;
	__u32 start_id;
	__u32 prog_id;
	__u32 map_id;
	__u32 btf_id;
	__u32 link_id;
	struct
	{
		__u32 bpf_fd;
		__u32 info_len;
		__u64 info;
	} info;
	struct
	{
		__u32 target_fd;
		__u32 attach_type;
		__u32 query_flags;
		__u32 attach_flags;
		__u64 prog_ids;
		__u32 prog_cnt;
	} query;
	struct
	{
		__u64 name;
		__u32 prog_fd;
	} raw_tracepoint;
	__u64 btf;
	struct
	{
		__u32 pid;
		__u32 fd;
		__u32 flags;
		__u32 buf_len;
		__u64 buf;
		__u32 prog_id;
		__u32 fd_type;
		__u64 probe_offset;
		__u64 probe_addr;
	} task_fd_query;
	struct
	{
		__u32 prog_fd;
		__u32 target_fd;
		__u32 attach_type;
		__u32 flags;
	} link_create;
	struct
	{
		__u32 link_fd;
		__u32 new_prog_fd;
		__u32 flags;
		__u32 old_prog_fd;
	} link_update;
	struct
	{
		__u32 type;
	} enable_stats;
	struct
	{
		__u32 link_fd;
		__u32 flags;
	} iter_create;
	struct {
		__padding char _0[4];
		__u32 key_size;
	};
	struct {
		__padding char _1[4];
		__u32 insn_cnt;
	};
	struct {
		__padding char _2[4];
		__u32 attach_bpf_fd;
	};
	struct {
		__padding char _3[4];
		__u32 next_id;
	};
	struct {
		__padding char _4[8];
		__u32 value_size;
	};
	struct {
		__padding char _5[8];
		__u64 key;
	};
	struct {
		__padding char _6[8];
		__u64 insns;
	};
	struct {
		__padding char _7[8];
		__u32 bpf_fd;
	};
	struct {
		__padding char _8[8];
		__u32 attach_type;
	};
	struct {
		__padding char _9[8];
		__u32 open_flags;
	};
	struct {
		__padding char _10[8];
		__u64 btf_log_buf;
	};
	struct {
		__padding char _11[0xc];
		__u32 max_entries;
	};
	struct {
		__padding char _12[0xc];
		__u32 file_flags;
	};
	struct {
		__padding char _13[0xc];
		__u32 attach_flags;
	};
	struct {
		__padding char _14[0x10];
		__u32 map_flags;
	};
	struct {
		__padding char _15[0x10];
		__u64 value;
	};
	struct {
		__padding char _16[0x10];
		__u64 next_key;
	};
	struct {
		__padding char _17[0x10];
		__u64 license;
	};
	struct {
		__padding char _18[0x10];
		__u32 replace_bpf_fd;
	};
	struct {
		__padding char _19[0x10];
		__u32 btf_size;
	};
	struct {
		__padding char _20[0x14];
		__u32 inner_map_fd;
	};
	struct {
		__padding char _21[0x14];
		__u32 btf_log_size;
	};
	struct {
		__padding char _22[0x18];
		__u32 numa_node;
	};
	struct {
		__padding char _23[0x18];
		__u64 flags;
	};
	struct {
		__padding char _24[0x18];
		__u32 log_level;
	};
	struct {
		__padding char _25[0x18];
		__u32 btf_log_level;
	};
	struct {
		__padding char _26[0x1c];
		char map_name[0x10];
	};
	struct {
		__padding char _27[0x1c];
		__u32 log_size;
	};
	struct {
		__padding char _28[0x20];
		__u64 log_buf;
	};
	struct {
		__padding char _29[0x28];
		__u32 kern_version;
	};
	struct {
		__padding char _30[0x2c];
		__u32 map_ifindex;
	};
	struct {
		__padding char _31[0x2c];
		__u32 prog_flags;
	};
	struct {
		__padding char _32[0x30];
		__u32 btf_fd;
	};
	struct {
		__padding char _33[0x30];
		char prog_name[0x10];
	};
	struct {
		__padding char _34[0x34];
		__u32 btf_key_type_id;
	};
	struct {
		__padding char _35[0x38];
		__u32 btf_value_type_id;
	};
	struct {
		__padding char _36[0x3c];
		__u32 btf_vmlinux_value_type_id;
	};
	struct {
		__padding char _37[0x40];
		__u32 prog_ifindex;
	};
	struct {
		__padding char _38[0x40+4];
		__u32 expected_attach_type;
	};
	struct {
		__padding char _39[0x40+8];
		__u32 prog_btf_fd;
	};
	struct {
		__padding char _40[0x40+0xc];
		__u32 func_info_rec_size;
	};
	struct {
		__padding char _41[0x40+0x10];
		__u64 func_info;
	};
	struct {
		__padding char _42[0x40+0x18];
		__u32 func_info_cnt;
	};
	struct {
		__padding char _43[0x40+0x1c];
		__u32 line_info_rec_size;
	};
	struct {
		__padding char _44[0x40+0x20];
		__u64 line_info;
	};
	struct {
		__padding char _45[0x40+0x28];
		__u32 line_info_cnt;
	};
	struct {
		__padding char _46[0x40+0x2c];
		__u32 attach_btf_id;
	};
	struct {
		__padding char _47[0x40+0x30];
		__u32 attach_prog_fd;
	};
};

// "sched_attr"
struct sched_attr
{
	__u32 size;
	__u32 sched_policy;
	__u64 sched_flags;
	__s32 sched_nice;
	__u32 sched_priority;
	__u64 sched_runtime;
	__u64 sched_deadline;
	__u64 sched_period;
	__u32 sched_util_min;
	__u32 sched_util_max;
};

// "epoll_event"
struct epoll_event
{
	uint32_t events;
	__u64 data;
};

// "__sifields"
union __sifields
{
	struct
	{
		__kernel_pid_t _pid;
		__kernel_uid32_t _uid;
	} _kill;
	struct
	{
		__kernel_timer_t _tid;
		int32_t _overrun;
		union sigval_t _sigval;
		int32_t _sys_private;
	} _timer;
	struct
	{
		__kernel_pid_t _pid;
		__kernel_uid32_t _uid;
		union sigval_t _sigval;
	} _rt;
	struct
	{
		__kernel_pid_t _pid;
		__kernel_uid32_t _uid;
		int32_t _status;
		__kernel_clock_t _utime;
		__kernel_clock_t _stime;
	} _sigchld;
	struct
	{
		void* _addr;
		struct
		{
			char _dummy_pkey[0x4];
			__u32 _pkey;
		} _addr_pkey;
	__padding char _C[4];
	} _sigfault;
	struct
	{
		int32_t _band;
		int32_t _fd;
	} _sigpoll;
	struct
	{
		void* _call_addr;
		int32_t _syscall;
		uint32_t _arch;
	} _sigsys;
};

// "io_context"
struct io_context
{
	atomic_long_t refcount;
	struct atomic_t active_ref;
	struct atomic_t nr_tasks;
	struct spinlock_t lock;
	uint16_t ioprio;
	int32_t nr_batch_requests;
	uint32_t last_waited;
	struct xarray icq_tree;
	struct io_cq* icq_hint;
	struct hlist_head_t icq_list;
	struct work_struct release_work;
};

// "stat"
struct stat
{
	dev_t st_dev;
	int32_t st_pad1[0x3];
	__ino_t st_ino;
	mode_t st_mode;
	__nlink_t st_nlink;
	uid_t st_uid;
	gid_t st_gid;
	dev_t st_rdev;
	uint32_t st_pad2[0x2];
	off_t st_size;
	int32_t st_pad3;
	struct timespec st_atim;
	struct timespec st_mtim;
	struct timespec st_ctim;
	blksize_t st_blksize;
	uint32_t st_pad4;
	__blkcnt_t st_blocks;
	int32_t st_pad5[0xe];
};

// "nfsctl_arg"
struct nfsctl_arg
{
	int32_t ca_version;
	union
	{
		struct nfsctl_svc u_svc;
		struct nfsctl_client u_client;
		struct nfsctl_export u_export;
		struct nfsctl_fdparm u_getfd;
		struct nfsctl_fsparm u_getfs;
		void* u_ptr;
	} u;
};

// "robust_list_head"
struct robust_list_head
{
	struct robust_list list;
	int32_t futex_offset;
	struct robust_list* list_op_pending;
};

// "raw_spinlock_t"
struct raw_spinlock_t
{
	struct arch_spinlock_t raw_lock;
};

// "l_timespec"
struct l_timespec
{
	l_time_t tv_sec;
	l_long tv_nsec;
};

// "rseq"
struct rseq
{
	__u32 cpu_id_start;
	__u32 cpu_id;
	union
	{
		__u64 ptr64;
		struct
		{
			__u32 padding;
			__u32 ptr32;
		} ptr;
	} rseq_cs;
	__u32 flags;
};

// "iocb"
struct iocb
{
	__u64 aio_data;
	__kernel_rwf_t aio_rw_flags;
	__u16 aio_lio_opcode;
	__s16 aio_reqprio;
	__u32 aio_fildes;
	__u64 aio_buf;
	__u64 aio_nbytes;
	__s64 aio_offset;
	__u64 aio_reserved2;
	__u32 aio_flags;
	__u32 aio_resfd;
};

// "__timespec64"
struct __timespec64
{
	time64_t tv_sec;
	int32_t tv_nsec;
};

// "linux_dirent64"
struct linux_dirent64
{
	__u64 d_ino;
	__s64 d_off;
	uint16_t d_reclen;
	uint8_t d_type;
	char d_name[0x0];
};

// "io_event"
struct io_event
{
	__u64 data;
	__u64 obj;
	__s64 res;
	__s64 res2;
};

// "spinlock"
struct spinlock
{
	struct raw_spinlock rlock;
};

// "clone_args"
struct clone_args
{
	__u64 flags;
	__u64 pidfd;
	__u64 child_tid;
	__u64 parent_tid;
	__u64 exit_signal;
	__u64 stack;
	__u64 stack_size;
	__u64 tls;
	__u64 set_tid;
	__u64 set_tid_size;
	__u64 cgroup;
};

// "fd_set"
typedef struct __kernel_fd_set fd_set;

// "itimerspec"
struct itimerspec
{
	struct timespec it_interval;
	struct timespec it_value;
};

// "sigevent_t"
struct sigevent_t
{
	union sigval_t sigev_value;
	int32_t sigev_signo;
	int32_t sigev_notify;
	union
	{
		int32_t _pad[0xa];
		int32_t _tid;
		struct
		{
			void (* _function)(union sigval_t);
			void* _attribute;
		} _sigev_thread;
	} _sigev_un;
};

// "io_uring_params"
struct io_uring_params
{
	__u32 sq_entries;
	__u32 cq_entries;
	__u32 flags;
	__u32 sq_thread_cpu;
	__u32 sq_thread_idle;
	__u32 features;
	__u32 wq_fd;
	__u32 resv[0x3];
	struct io_sqring_offsets sq_off;
	struct io_cqring_offsets cq_off;
};

// "statx"
struct statx
{
	__u32 stx_mask;
	__u32 stx_blksize;
	__u64 stx_attributes;
	__u32 stx_nlink;
	__u32 stx_uid;
	__u32 stx_gid;
	__u16 stx_mode;
	__u16 __spare0[0x1];
	__u64 stx_ino;
	__u64 stx_size;
	__u64 stx_blocks;
	__u64 stx_attributes_mask;
	struct statx_timestamp stx_atime;
	struct statx_timestamp stx_btime;
	struct statx_timestamp stx_ctime;
	struct statx_timestamp stx_mtime;
	__u32 stx_rdev_major;
	__u32 stx_rdev_minor;
	__u32 stx_dev_major;
	__u32 stx_dev_minor;
	__u64 stx_mnt_id;
	__u64 __spare2;
	__u64 __spare3[0xc];
};

// "__user_cap_header_struct"
struct __user_cap_header_struct
{
	__u32 version;
	int32_t pid;
};

// "statfs"
struct statfs
{
	__kernel_long_t f_type;
	__kernel_long_t f_bsize;
	__kernel_long_t f_blocks;
	__kernel_long_t f_bfree;
	__kernel_long_t f_bavail;
	__kernel_long_t f_files;
	__kernel_long_t f_ffree;
	struct __kernel_fsid_t f_fsid;
	__kernel_long_t f_namelen;
	__kernel_long_t f_frsize;
	__kernel_long_t f_flags;
	__kernel_long_t f_spare[0x4];
};

// "vm86_struct"
struct vm86_struct
{
	struct vm86_regs regs;
	uint32_t flags;
	uint32_t screen_bitmap;
	uint32_t cpu_type;
	struct revectored_struct int_revectored;
	struct revectored_struct int21_revectored;
};

// "mcontext_t"
struct mcontext_t
{
	gregset_t gregs;
	struct fpregset_t fpregs;
};

// "rlimit"
struct rlimit
{
	__kernel_ulong_t rlim_cur;
	__kernel_ulong_t rlim_max;
};

// "qspinlock"
struct qspinlock
{
	u8 reserved[0x2];
	u8 pending;
	u8 locked;
};

// "mq_attr"
struct mq_attr
{
	__kernel_long_t mq_flags;
	__kernel_long_t mq_maxmsg;
	__kernel_long_t mq_msgsize;
	__kernel_long_t mq_curmsgs;
	__kernel_long_t __reserved[0x4];
};

// "timeb"
struct timeb
{
	time_t time;
	uint16_t millitm;
	int16_t timezone;
	int16_t dstflag;
};

// "rusage"
struct rusage
{
	struct __kernel_old_timeval ru_utime;
	struct __kernel_old_timeval ru_stime;
	__kernel_long_t ru_maxrss;
	__kernel_long_t ru_ixrss;
	__kernel_long_t ru_idrss;
	__kernel_long_t ru_isrss;
	__kernel_long_t ru_minflt;
	__kernel_long_t ru_majflt;
	__kernel_long_t ru_nswap;
	__kernel_long_t ru_inblock;
	__kernel_long_t ru_oublock;
	__kernel_long_t ru_msgsnd;
	__kernel_long_t ru_msgrcv;
	__kernel_long_t ru_nsignals;
	__kernel_long_t ru_nvcsw;
	__kernel_long_t ru_nivcsw;
};

// "sigevent"
struct sigevent
{
	union sigval_t sigev_value;
	int32_t sigev_signo;
	int32_t sigev_notify;
	union
	{
		int32_t _pad[0xa];
		int32_t _tid;
		struct
		{
			void (* _function)(union sigval_t);
			void* _attribute;
		} _sigev_thread;
	} _sigev_un;
};

// "clock_t"
typedef __kernel_clock_t clock_t;

// "msghdr"
struct msghdr
{
	void* msg_name;
	int32_t msg_namelen;
	struct iov_iter msg_iter;
	void* msg_control_user;
	bool msg_control_is_user;
	__kernel_size_t msg_controllen;
	uint32_t msg_flags;
	struct kiocb* msg_iocb;
};

// "mmsghdr"
struct mmsghdr
{
	struct user_msghdr msg_hdr;
	uint32_t msg_len;
};


int32_t sys_restart_syscall() __syscall(0);
void sys_exit(int32_t status) __syscall(1) __noreturn;
pid_t sys_fork() __syscall(2);
int32_t sys_read(int32_t fd, void* buf, uint32_t count) __syscall(3);
int32_t sys_write(int32_t fd, void const* buf, uint32_t count) __syscall(4);
int32_t sys_open(char const* pathname, int32_t flags) __syscall(5);
int32_t sys_close(int32_t fd) __syscall(6);
pid_t sys_waitpid(pid_t pid, int32_t* wstatus, int32_t options) __syscall(7);
int32_t sys_creat(char const* pathname, mode_t mode) __syscall(8);
int32_t sys_link(char const* oldpath, char const* newpath) __syscall(9);
int32_t sys_unlink(char const* pathname) __syscall(10);
int32_t sys_execve(char const* pathname, char* const* argv, char* const* envp) __syscall(11);
int32_t sys_chdir(char const* path) __syscall(12);
time_t sys_time(time_t* tloc) __syscall(13);
int32_t sys_mknod(char const* pathname, mode_t mode, dev_t dev) __syscall(14);
int32_t sys_chmod(char const* pathname, mode_t mode) __syscall(15);
int32_t sys_lchown(char const* pathname, uid_t owner, gid_t group) __syscall(16);
int32_t sys_oldstat(char const* pathname, struct stat* statbuf) __syscall(18);
off_t sys_lseek(int32_t fd, off_t offset, int32_t whence) __syscall(19);
pid_t sys_getpid() __syscall(20);
int32_t sys_mount(char const* source, char const* target, char const* filesystemtype, uint32_t mountflags, void const* data) __syscall(21);
int32_t sys_umount(char const* target) __syscall(22);
int32_t sys_setuid(uid_t uid) __syscall(23);
uid_t sys_getuid() __syscall(24);
int32_t sys_stime(time_t const* t) __syscall(25);
int32_t sys_ptrace(enum __ptrace_request request, pid_t pid, void* addr, void* data) __syscall(26);
uint32_t sys_alarm(uint32_t seconds) __syscall(27);
int32_t sys_oldfstat(int32_t fd, struct stat* statbuf) __syscall(28);
int32_t sys_pause() __syscall(29);
int32_t sys_utime(char const* filename, struct utimbuf const* times) __syscall(30);
int32_t sys_access(char const* pathname, int32_t mode) __syscall(33);
int32_t sys_nice(int32_t inc) __syscall(34);
int32_t sys_ftime(struct timeb* tp) __syscall(35);
void sys_sync() __syscall(36);
int32_t sys_kill(pid_t pid, int32_t sig) __syscall(37);
int32_t sys_rename(char const* oldpath, char const* newpath) __syscall(38);
int32_t sys_mkdir(char const* pathname, mode_t mode) __syscall(39);
int32_t sys_rmdir(char const* pathname) __syscall(40);
int32_t sys_dup(int32_t oldfd) __syscall(41);
int32_t sys_pipe(int32_t pipefd[0x2]) __syscall(42);
clock_t sys_times(struct tms* buf) __syscall(43);
int32_t sys_brk(void* addr) __syscall(45);
int32_t sys_setgid(gid_t gid) __syscall(46);
gid_t sys_getgid() __syscall(47);
sighandler_t sys_signal(int32_t signum, sighandler_t handler) __syscall(48);
uid_t sys_geteuid() __syscall(49);
gid_t sys_getegid() __syscall(50);
int32_t sys_acct(char const* filename) __syscall(51);
int32_t sys_umount2(char const* target, int32_t flags) __syscall(52);
int32_t sys_ioctl(int32_t fd, uint32_t request, ...) __syscall(54);
int32_t sys_fcntl(int32_t fd, int32_t cmd, ...) __syscall(55);
int32_t sys_setpgid(pid_t pid, pid_t pgid) __syscall(57);
int32_t sys_ulimit(int32_t cmd, int32_t newlimit) __syscall(58);
int32_t sys_oldolduname(struct new_utsname* buf) __syscall(59);
mode_t sys_umask(mode_t mask) __syscall(60);
int32_t sys_chroot(char const* path) __syscall(61);
int32_t sys_ustat(dev_t dev, struct ustat* ubuf) __syscall(62);
int32_t sys_dup2(int32_t oldfd, int32_t newfd) __syscall(63);
pid_t sys_getppid() __syscall(64);
pid_t sys_getpgrp() __syscall(65);
pid_t sys_setsid() __syscall(66);
int32_t sys_sigaction(int32_t signum, struct sigaction const* act, struct sigaction* oldact) __syscall(67);
int32_t sys_sgetmask() __syscall(68);
int32_t sys_ssetmask(int32_t newmask) __syscall(69);
int32_t sys_setreuid(uid_t ruid, uid_t euid) __syscall(70);
int32_t sys_setregid(gid_t rgid, gid_t egid) __syscall(71);
int32_t sys_sigsuspend(struct kernel_sigset_t const* mask) __syscall(72);
int32_t sys_sigpending(struct kernel_sigset_t* set) __syscall(73);
int32_t sys_sethostname(char const* name, uint32_t len) __syscall(74);
int32_t sys_setrlimit(int32_t resource, struct rlimit const* rlim) __syscall(75);
int32_t sys_getrlimit(int32_t resource, struct rlimit* rlim) __syscall(76);
int32_t sys_getrusage(int32_t who, struct rusage* usage) __syscall(77);
int32_t sys_gettimeofday(struct timeval* tv, struct timezone* tz) __syscall(78);
int32_t sys_settimeofday(struct timeval const* tv, struct timezone const* tz) __syscall(79);
int32_t sys_getgroups(int32_t size, gid_t* list) __syscall(80);
int32_t sys_setgroups(uint32_t size, gid_t const* list) __syscall(81);
int32_t sys_select(int32_t nfds, fd_set* readfds, fd_set* writefds, fd_set* exceptfds, struct timeval* timeout) __syscall(82);
int32_t sys_symlink(char const* target, char const* linkpath) __syscall(83);
int32_t sys_oldlstat(char const* pathname, struct stat* statbuf) __syscall(84);
int32_t sys_readlink(char const* pathname, char* buf, uint32_t bufsiz) __syscall(85);
int32_t sys_uselib(char const* library) __syscall(86);
int32_t sys_swapon(char const* path, int32_t swapflags) __syscall(87);
int32_t sys_reboot(int32_t magic, int32_t magic2, int32_t cmd, void* arg) __syscall(88);
int32_t sys_readdir(uint32_t fd, struct old_linux_dirent* dirp, uint32_t count) __syscall(89);
void* sys_mmap(void* addr, uint32_t length, int32_t prot, int32_t flags, int32_t fd, off_t offset) __syscall(90);
int32_t sys_munmap(void* addr, uint32_t length) __syscall(91);
int32_t sys_truncate(char const* path, off_t length) __syscall(92);
int32_t sys_ftruncate(int32_t fd, off_t length) __syscall(93);
int32_t sys_fchmod(int32_t fd, mode_t mode) __syscall(94);
int32_t sys_fchown(int32_t fd, uid_t owner, gid_t group) __syscall(95);
int32_t sys_getpriority(int32_t which, id_t who) __syscall(96);
int32_t sys_setpriority(int32_t which, id_t who, int32_t prio) __syscall(97);
int32_t sys_profil(uint16_t* buf, uint32_t bufsiz, uint32_t offset, uint32_t scale) __syscall(98);
int32_t sys_statfs(char const* path, struct statfs* buf) __syscall(99);
int32_t sys_fstatfs(int32_t fd, struct statfs* buf) __syscall(100);
int32_t sys_ioperm(uint32_t from, uint32_t num, int32_t turn_on) __syscall(101);
int32_t sys_socketcall(int32_t call, uint32_t* args) __syscall(102);
int32_t sys_syslog(int32_t type, char* bufp, int32_t len) __syscall(103);
int32_t sys_setitimer(int32_t which, struct itimerval const* new_value, struct itimerval* old_value) __syscall(104);
int32_t sys_getitimer(int32_t which, struct itimerval* curr_value) __syscall(105);
int32_t sys_stat(char const* pathname, struct stat* statbuf) __syscall(106);
int32_t sys_lstat(char const* pathname, struct stat* statbuf) __syscall(107);
int32_t sys_fstat(int32_t fd, struct stat* statbuf) __syscall(108);
int32_t sys_olduname(struct new_utsname* buf) __syscall(109);
int32_t sys_iopl(int32_t level) __syscall(110);
int32_t sys_vhangup() __syscall(111);
int32_t sys_idle() __syscall(112);
int32_t sys_vm86old(struct vm86_struct* info) __syscall(113);
pid_t sys_wait4(pid_t pid, int32_t* wstatus, int32_t options, struct rusage* rusage) __syscall(114);
int32_t sys_swapoff(char const* path) __syscall(115);
int32_t sys_sysinfo(struct sysinfo* info) __syscall(116);
int32_t sys_ipc(uint32_t call, int32_t first, int32_t second, int32_t third, void* ptr, int32_t fifth) __syscall(117);
int32_t sys_fsync(int32_t fd) __syscall(118);
int32_t sys_clone(int32_t (* fn)(void*), void* stack, int32_t flags, void* arg, ...) __syscall(120);
int32_t sys_setdomainname(char const* name, uint32_t len) __syscall(121);
int32_t sys_uname(struct new_utsname* buf) __syscall(122);
int32_t sys_modify_ldt(int32_t func, void* ptr, uint32_t bytecount) __syscall(123);
int32_t sys_adjtimex(struct timex* buf) __syscall(124);
int32_t sys_mprotect(void* addr, uint32_t len, int32_t prot) __syscall(125);
int32_t sys_sigprocmask(int32_t how, struct kernel_sigset_t const* set, struct kernel_sigset_t* oldset) __syscall(126);
caddr_t sys_create_module(char const* name, uint32_t size) __syscall(127);
int32_t sys_init_module(void* module_image, uint32_t len, char const* param_values) __syscall(128);
int32_t sys_delete_module(char const* name, int32_t flags) __syscall(129);
int32_t sys_get_kernel_syms(struct kernel_sym* table) __syscall(130);
int32_t sys_quotactl(int32_t cmd, char const* special, int32_t id, caddr_t addr) __syscall(131);
pid_t sys_getpgid(pid_t pid) __syscall(132);
int32_t sys_fchdir(int32_t fd) __syscall(133);
int32_t sys_bdflush(int32_t func, int32_t* address) __syscall(134);
int32_t sys_sysfs(int32_t option, char const* fsname) __syscall(135);
int32_t sys_personality(uint32_t persona) __syscall(136);
int32_t sys_setfsuid(uid_t fsuid) __syscall(138);
int32_t sys_setfsgid(uid_t fsgid) __syscall(139);
int32_t sys__llseek(uint32_t fd, uint32_t offset_high, uint32_t offset_low, loff_t* result, uint32_t whence) __syscall(140);
int32_t sys_getdents(uint32_t fd, struct linux_dirent* dirp, uint32_t count) __syscall(141);
int32_t sys__newselect(int32_t nfds, fd_set* readfds, fd_set* writefds, fd_set* exceptfds, struct timeval* timeout) __syscall(142);
int32_t sys_flock(int32_t fd, int32_t operation) __syscall(143);
int32_t sys_msync(void* addr, uint32_t length, int32_t flags) __syscall(144);
int32_t sys_readv(int32_t fd, struct iovec const* iov, int32_t iovcnt) __syscall(145);
int32_t sys_writev(int32_t fd, struct iovec const* iov, int32_t iovcnt) __syscall(146);
pid_t sys_getsid(pid_t pid) __syscall(147);
int32_t sys_fdatasync(int32_t fd) __syscall(148);
int32_t sys__sysctl(struct __sysctl_args* args) __syscall(149);
int32_t sys_mlock(void const* addr, uint32_t len) __syscall(150);
int32_t sys_munlock(void const* addr, uint32_t len) __syscall(151);
int32_t sys_mlockall(int32_t flags) __syscall(152);
int32_t sys_munlockall() __syscall(153);
int32_t sys_sched_setparam(pid_t pid, struct sched_param const* param) __syscall(154);
int32_t sys_sched_getparam(pid_t pid, struct sched_param* param) __syscall(155);
int32_t sys_sched_setscheduler(pid_t pid, int32_t policy, struct sched_param const* param) __syscall(156);
int32_t sys_sched_getscheduler(pid_t pid) __syscall(157);
int32_t sys_sched_yield() __syscall(158);
int32_t sys_sched_get_priority_max(int32_t policy) __syscall(159);
int32_t sys_sched_get_priority_min(int32_t policy) __syscall(160);
int32_t sys_sched_rr_get_interval(pid_t pid, struct timespec* tp) __syscall(161);
int32_t sys_nanosleep(struct timespec const* req, struct timespec* rem) __syscall(162);
void* sys_mremap(void* old_address, uint32_t old_size, uint32_t new_size, int32_t flags, ...) __syscall(163);
int32_t sys_setresuid(uid_t ruid, uid_t euid, uid_t suid) __syscall(164);
int32_t sys_getresuid(uid_t* ruid, uid_t* euid, uid_t* suid) __syscall(165);
int32_t sys_vm86(uint32_t fn, struct vm86plus_struct* v86) __syscall(166);
int32_t sys_query_module(char const* name, int32_t which, void* buf, uint32_t bufsize, uint32_t* ret) __syscall(167);
int32_t sys_poll(struct pollfd* fds, nfds_t nfds, int32_t timeout) __syscall(168);
int32_t sys_nfsservctl(int32_t cmd, struct nfsctl_arg* argp, union nfsctl_res* resp) __syscall(169);
int32_t sys_setresgid(gid_t rgid, gid_t egid, gid_t sgid) __syscall(170);
int32_t sys_getresgid(gid_t* rgid, gid_t* egid, gid_t* sgid) __syscall(171);
int32_t sys_prctl(int32_t option, uint32_t arg2, uint32_t arg3, uint32_t arg4, uint32_t arg5) __syscall(172);
int32_t sigreturn(uint32_t __unused) __syscall(173);
int32_t sigaction(int32_t signum, struct sigaction const* act, struct sigaction* oldact) __syscall(174);
int32_t sys_rt_sigprocmask(int32_t how, struct kernel_sigset_t const* set, struct kernel_sigset_t* oldset, uint32_t sigsetsize) __syscall(175);
int32_t sigpending(struct kernel_sigset_t* set) __syscall(176);
int32_t sigtimedwait(struct kernel_sigset_t const* set, struct siginfo_t* info, struct timespec const* timeout) __syscall(177);
int32_t sys_rt_sigqueueinfo(pid_t tgid, int32_t sig, struct siginfo_t* info) __syscall(178);
int32_t sys_rt_sigsuspend(struct kernel_sigset_t const* mask) __syscall(179);
int32_t pread(int32_t fd, void* buf, uint32_t count, off_t offset) __syscall(180);
int32_t sys_pwrite64(int32_t fd, void const* buf, uint32_t count, off_t offset) __syscall(181);
int32_t sys_chown(char const* pathname, uid_t owner, gid_t group) __syscall(182);
char* sys_getcwd(char* buf, uint32_t size) __syscall(183);
int32_t sys_capget(cap_user_header_t hdrp, cap_user_data_t datap) __syscall(184);
int32_t sys_capset(cap_user_header_t hdrp, cap_user_data_t const datap) __syscall(185);
int32_t sys_sigaltstack(struct stack_t const* ss, struct stack_t* old_ss) __syscall(186);
int32_t sys_sendfile(int32_t out_fd, int32_t in_fd, off_t* offset, uint32_t count) __syscall(187);
int32_t sys_getpmsg(int32_t fildes, struct strbuf* ctlptr, struct strbuf* dataptr, int32_t* bandp, int32_t* flagsp) __syscall(188);
int32_t sys_putpmsg(int32_t fildes, struct strbuf const* ctlptr, struct strbuf const* dataptr, int32_t band, int32_t flags) __syscall(189);
pid_t sys_vfork() __syscall(190);
int32_t sys_ugetrlimit(int32_t resource, struct rlimit* rlim) __syscall(191);
void* sys_mmap2(void* addr, uint32_t length, int32_t prot, int32_t flags, int32_t fd, off_t pgoffset) __syscall(192);
int32_t sys_truncate64(char const* path, off_t length) __syscall(193);
int32_t sys_ftruncate64(int32_t fd, off_t length) __syscall(194);
int32_t sys_stat64(char const* pathname, struct stat* statbuf) __syscall(195);
int32_t sys_lstat64(char const* pathname, struct stat* statbuf) __syscall(196);
int32_t sys_fstat64(int32_t fd, struct stat* statbuf) __syscall(197);
int32_t sys_lchown32(char const* pathname, uid_t owner, gid_t group) __syscall(198);
uid_t sys_getuid32() __syscall(199);
gid_t sys_getgid32() __syscall(200);
uid_t sys_geteuid32() __syscall(201);
gid_t sys_getegid32() __syscall(202);
int32_t sys_setreuid32(uid_t ruid, uid_t euid) __syscall(203);
int32_t sys_setregid32(gid_t rgid, gid_t egid) __syscall(204);
int32_t sys_getgroups32(int32_t size, gid_t* list) __syscall(205);
int32_t sys_setgroups32(uint32_t size, gid_t const* list) __syscall(206);
int32_t sys_fchown32(int32_t fd, uid_t owner, gid_t group) __syscall(207);
int32_t sys_setresuid32(uid_t ruid, uid_t euid, uid_t suid) __syscall(208);
int32_t sys_getresuid32(uid_t* ruid, uid_t* euid, uid_t* suid) __syscall(209);
int32_t sys_setresgid32(gid_t rgid, gid_t egid, gid_t sgid) __syscall(210);
int32_t sys_getresgid32(gid_t* rgid, gid_t* egid, gid_t* sgid) __syscall(211);
int32_t sys_chown32(char const* pathname, uid_t owner, gid_t group) __syscall(212);
int32_t sys_setuid32(uid_t uid) __syscall(213);
int32_t sys_setgid32(gid_t gid) __syscall(214);
int32_t sys_setfsuid32(uid_t fsuid) __syscall(215);
int32_t sys_setfsgid32(uid_t fsgid) __syscall(216);
int32_t sys_pivot_root(char const* new_root, char const* put_old) __syscall(217);
int32_t sys_mincore(void* addr, uint32_t length, uint8_t* vec) __syscall(218);
int32_t sys_madvise(void* addr, uint32_t length, int32_t advice) __syscall(219);
int32_t sys_getdents64(uint32_t fd, struct linux_dirent64* dirp, uint32_t count) __syscall(220);
int32_t sys_fcntl64(int32_t fd, int32_t cmd, ...) __syscall(221);
pid_t sys_gettid() __syscall(224);
int32_t sys_readahead(int32_t fd, off64_t offset, uint32_t count) __syscall(225);
int32_t sys_setxattr(char const* path, char const* name, void const* value, uint32_t size, int32_t flags) __syscall(226);
int32_t sys_lsetxattr(char const* path, char const* name, void const* value, uint32_t size, int32_t flags) __syscall(227);
int32_t sys_fsetxattr(int32_t fd, char const* name, void const* value, uint32_t size, int32_t flags) __syscall(228);
int32_t sys_getxattr(char const* path, char const* name, void* value, uint32_t size) __syscall(229);
int32_t sys_lgetxattr(char const* path, char const* name, void* value, uint32_t size) __syscall(230);
int32_t sys_fgetxattr(int32_t fd, char const* name, void* value, uint32_t size) __syscall(231);
int32_t sys_listxattr(char const* path, char* list, uint32_t size) __syscall(232);
int32_t sys_llistxattr(char const* path, char* list, uint32_t size) __syscall(233);
int32_t sys_flistxattr(int32_t fd, char* list, uint32_t size) __syscall(234);
int32_t sys_removexattr(char const* path, char const* name) __syscall(235);
int32_t sys_lremovexattr(char const* path, char const* name) __syscall(236);
int32_t sys_fremovexattr(int32_t fd, char const* name) __syscall(237);
int32_t sys_tkill(int32_t tid, int32_t sig) __syscall(238);
int32_t sys_sendfile64(int32_t out_fd, int32_t in_fd, off_t* offset, uint32_t count) __syscall(239);
int32_t sys_futex(int32_t* uaddr, int32_t futex_op, int32_t val, struct timespec const* timeout, int32_t* uaddr2, int32_t val3) __syscall(240);
int32_t sys_sched_setaffinity(pid_t pid, uint32_t cpusetsize, struct cpu_set_t const* mask) __syscall(241);
int32_t sys_sched_getaffinity(pid_t pid, uint32_t cpusetsize, struct cpu_set_t* mask) __syscall(242);
int32_t sys_set_thread_area(struct user_desc* u_info) __syscall(243);
int32_t sys_get_thread_area(struct user_desc* u_info) __syscall(244);
int32_t sys_io_setup(uint32_t nr_events, io_context_t* ctx_idp) __syscall(245);
int32_t sys_io_destroy(io_context_t ctx_id) __syscall(246);
int32_t sys_io_getevents(io_context_t ctx_id, int32_t min_nr, int32_t nr, struct io_event* events, struct timespec* timeout) __syscall(247);
int32_t sys_io_submit(io_context_t ctx_id, int32_t nr, struct iocb** iocbpp) __syscall(248);
int32_t sys_io_cancel(io_context_t ctx_id, struct iocb* iocb, struct io_event* result) __syscall(249);
int32_t sys_arm_sys_fadvise64_64(int32_t fd, int32_t advice, loff_t offset, loff_t len) __syscall(250);
void sys_exit_group(int32_t status) __syscall(252) __noreturn;
int32_t sys_lookup_dcookie(u64 cookie, char* buffer, uint32_t len) __syscall(253);
int32_t sys_epoll_create(int32_t size) __syscall(254);
int32_t sys_epoll_ctl(int32_t epfd, int32_t op, int32_t fd, struct epoll_event* event) __syscall(255);
int32_t sys_epoll_wait(int32_t epfd, struct epoll_event* events, int32_t maxevents, int32_t timeout) __syscall(256);
int32_t sys_remap_file_pages(void* addr, uint32_t size, int32_t prot, uint32_t pgoff, int32_t flags) __syscall(257);
int32_t sys_set_tid_address(int32_t* tidptr) __syscall(258);
int32_t sys_timer_create(clockid_t clockid, struct sigevent* sevp, void** timerid) __syscall(259);
int32_t sys_timer_settime(void* timerid, int32_t flags, struct itimerspec const* new_value, struct itimerspec* old_value) __syscall(260);
int32_t sys_timer_gettime(void* timerid, struct itimerspec* curr_value) __syscall(261);
int32_t sys_timer_getoverrun(void* timerid) __syscall(262);
int32_t sys_timer_delete(void* timerid) __syscall(263);
int32_t sys_clock_settime(clockid_t clockid, struct timespec const* tp) __syscall(264);
int32_t sys_clock_gettime(clockid_t clockid, struct timespec* tp) __syscall(265);
int32_t sys_clock_getres(clockid_t clockid, struct timespec* res) __syscall(266);
int32_t sys_clock_nanosleep(clockid_t clockid, int32_t flags, struct timespec const* request, struct timespec* remain) __syscall(267);
int32_t sys_statfs64(char const* path, struct statfs* buf) __syscall(268);
int32_t sys_fstatfs64(int32_t fd, struct statfs* buf) __syscall(269);
int32_t sys_tgkill(int32_t tgid, int32_t tid, int32_t sig) __syscall(270);
int32_t sys_utimes(char const* filename, struct timeval const times[0x2]) __syscall(271);
int32_t arm_sys_fadvise64_64(int32_t fd, int32_t advice, loff_t offset, loff_t len) __syscall(272);
int32_t sys_mbind(void* addr, uint32_t len, int32_t mode, uint32_t const* nodemask, uint32_t maxnode, uint32_t flags) __syscall(274);
int32_t sys_get_mempolicy(int32_t* mode, uint32_t* nodemask, uint32_t maxnode, void* addr, uint32_t flags) __syscall(275);
int32_t sys_set_mempolicy(int32_t mode, uint32_t const* nodemask, uint32_t maxnode) __syscall(276);
mqd_t sys_mq_open(char const* name, int32_t oflag) __syscall(277);
int32_t sys_mq_unlink(char const* name) __syscall(278);
int32_t sys_mq_timedsend(mqd_t mqdes, char const* msg_ptr, uint32_t msg_len, uint32_t msg_prio, struct timespec const* abs_timeout) __syscall(279);
int32_t sys_mq_timedreceive(mqd_t mqdes, char* msg_ptr, uint32_t msg_len, uint32_t* msg_prio, struct timespec const* abs_timeout) __syscall(280);
int32_t sys_mq_notify(mqd_t mqdes, struct sigevent const* sevp) __syscall(281);
int32_t sys_mq_getsetattr(mqd_t mqdes, struct mq_attr* newattr, struct mq_attr* oldattr) __syscall(282);
int32_t sys_kexec_load(uint32_t entry, uint32_t nr_segments, struct kexec_segment* segments, uint32_t flags) __syscall(283);
int32_t sys_waitid(enum idtype_t idtype, id_t id, struct siginfo_t* infop, int32_t options) __syscall(284);
key_serial_t sys_add_key(char const* type, char const* description, void const* payload, uint32_t plen, key_serial_t keyring) __syscall(286);
key_serial_t sys_request_key(char const* type, char const* description, char const* callout_info, key_serial_t dest_keyring) __syscall(287);
int32_t sys_keyctl(int32_t operation, ...) __syscall(288);
int32_t sys_ioprio_set(int32_t which, int32_t who, int32_t ioprio) __syscall(289);
int32_t sys_ioprio_get(int32_t which, int32_t who) __syscall(290);
int32_t sys_inotify_init() __syscall(291);
int32_t sys_inotify_add_watch(int32_t fd, char const* pathname, uint32_t mask) __syscall(292);
int32_t sys_inotify_rm_watch(int32_t fd, int32_t wd) __syscall(293);
int32_t sys_migrate_pages(int32_t pid, uint32_t maxnode, uint32_t const* old_nodes, uint32_t const* new_nodes) __syscall(294);
int32_t sys_openat(int32_t dirfd, char const* pathname, int32_t flags) __syscall(295);
int32_t sys_mkdirat(int32_t dirfd, char const* pathname, mode_t mode) __syscall(296);
int32_t sys_mknodat(int32_t dirfd, char const* pathname, mode_t mode, dev_t dev) __syscall(297);
int32_t sys_fchownat(int32_t dirfd, char const* pathname, uid_t owner, gid_t group, int32_t flags) __syscall(298);
int32_t sys_futimesat(int32_t dirfd, char const* pathname, struct timeval const times[0x2]) __syscall(299);
int32_t sys_fstatat64(int32_t dirfd, char const* pathname, struct stat* statbuf, int32_t flags) __syscall(300);
int32_t sys_unlinkat(int32_t dirfd, char const* pathname, int32_t flags) __syscall(301);
int32_t sys_renameat(int32_t olddirfd, char const* oldpath, int32_t newdirfd, char const* newpath) __syscall(302);
int32_t sys_linkat(int32_t olddirfd, char const* oldpath, int32_t newdirfd, char const* newpath, int32_t flags) __syscall(303);
int32_t sys_symlinkat(char const* target, int32_t newdirfd, char const* linkpath) __syscall(304);
int32_t sys_readlinkat(int32_t dirfd, char const* pathname, char* buf, uint32_t bufsiz) __syscall(305);
int32_t sys_fchmodat(int32_t dirfd, char const* pathname, mode_t mode, int32_t flags) __syscall(306);
int32_t sys_faccessat(int32_t dirfd, char const* pathname, int32_t mode, int32_t flags) __syscall(307);
int32_t linux_sys_pselect6(l_int nfds, fd_set* readfd, fd_set* writefds, fd_set* exceptfds, struct l_timespec* tsp, l_uintptr_t* sig) __syscall(308);
int32_t sys_ppoll(struct pollfd* fds, nfds_t nfds, struct timespec const* tmo_p, struct kernel_sigset_t const* sigmask) __syscall(309);
int32_t sys_unshare(int32_t flags) __syscall(310);
int32_t sys_set_robust_list(struct robust_list_head* head, uint32_t len) __syscall(311);
int32_t sys_get_robust_list(int32_t pid, struct robust_list_head** head_ptr, uint32_t* len_ptr) __syscall(312);
int32_t sys_splice(int32_t fd_in, loff_t* off_in, int32_t fd_out, loff_t* off_out, uint32_t len, uint32_t flags) __syscall(313);
int32_t sys_sync_file_range(int32_t fd, off64_t offset, off64_t nbytes, uint32_t flags) __syscall(314);
int32_t sys_tee(int32_t fd_in, int32_t fd_out, uint32_t len, uint32_t flags) __syscall(315);
int32_t sys_vmsplice(int32_t fd, struct iovec const* iov, uint32_t nr_segs, uint32_t flags) __syscall(316);
int32_t sys_move_pages(int32_t pid, uint32_t count, void** pages, int32_t const* nodes, int32_t* status, int32_t flags) __syscall(317);
int32_t sys_getcpu(uint32_t* cpu, uint32_t* node, struct getcpu_cache* tcache) __syscall(318);
int32_t sys_epoll_pwait(int32_t epfd, struct epoll_event* events, int32_t maxevents, int32_t timeout, struct kernel_sigset_t const* sigmask) __syscall(319);
int32_t sys_utimensat(int32_t dirfd, char const* pathname, struct timespec const* times, int32_t flags) __syscall(320);
int32_t sys_signalfd(int32_t fd, struct kernel_sigset_t const* mask, int32_t flags) __syscall(321);
int32_t sys_timerfd_create(int32_t clockid, int32_t flags) __syscall(322);
int32_t sys_eventfd(uint32_t initval, int32_t flags) __syscall(323);
int32_t sys_fallocate(int32_t fd, int32_t mode, off_t offset, off_t len) __syscall(324);
int32_t sys_timerfd_settime(int32_t fd, int32_t flags, struct itimerspec const* new_value, struct itimerspec* old_value) __syscall(325);
int32_t sys_timerfd_gettime(int32_t fd, struct itimerspec* curr_value) __syscall(326);
int32_t signalfd(int32_t fd, struct kernel_sigset_t const* mask, int32_t flags) __syscall(327);
int32_t eventfd(uint32_t initval, int32_t flags) __syscall(328);
int32_t sys_epoll_create1(int32_t flags) __syscall(329);
int32_t sys_dup3(int32_t oldfd, int32_t newfd, int32_t flags) __syscall(330);
int32_t sys_pipe2(int32_t pipefd[0x2], int32_t flags) __syscall(331);
int32_t sys_inotify_init1(int32_t flags) __syscall(332);
int32_t sys_preadv(int32_t fd, struct iovec const* iov, int32_t iovcnt, off_t offset) __syscall(333);
int32_t sys_pwritev(int32_t fd, struct iovec const* iov, int32_t iovcnt, off_t offset) __syscall(334);
int32_t sys_rt_tgsigqueueinfo(pid_t tgid, pid_t tid, int32_t sig, struct siginfo_t* info) __syscall(335);
int32_t sys_perf_event_open(struct perf_event_attr* attr, pid_t pid, int32_t cpu, int32_t group_fd, uint32_t flags) __syscall(336);
int32_t sys_recvmmsg(int32_t sockfd, struct mmsghdr* msgvec, uint32_t vlen, int32_t flags, struct timespec* timeout) __syscall(337);
int32_t sys_fanotify_init(uint32_t flags, uint32_t event_f_flags) __syscall(338);
int32_t sys_fanotify_mark(int32_t fanotify_fd, uint32_t flags, uint64_t mask, int32_t dirfd, char const* pathname) __syscall(339);
int32_t sys_prlimit64(pid_t pid, int32_t resource, struct rlimit const* new_limit, struct rlimit* old_limit) __syscall(340);
int32_t sys_name_to_handle_at(int32_t dirfd, char const* pathname, struct file_handle* handle, int32_t* mount_id, int32_t flags) __syscall(341);
int32_t sys_open_by_handle_at(int32_t mount_fd, struct file_handle* handle, int32_t flags) __syscall(342);
int32_t sys_clock_adjtime(clockid_t clk_id, struct timex* buf) __syscall(343);
int32_t sys_syncfs(int32_t fd) __syscall(344);
int32_t sys_sendmmsg(int32_t sockfd, struct mmsghdr* msgvec, uint32_t vlen, int32_t flags) __syscall(345);
int32_t sys_setns(int32_t fd, int32_t nstype) __syscall(346);
int32_t sys_process_vm_readv(pid_t pid, struct iovec const* local_iov, uint32_t liovcnt, struct iovec const* remote_iov, uint32_t riovcnt, uint32_t flags) __syscall(347);
int32_t sys_process_vm_writev(pid_t pid, struct iovec const* local_iov, uint32_t liovcnt, struct iovec const* remote_iov, uint32_t riovcnt, uint32_t flags) __syscall(348);
int32_t sys_kcmp(pid_t pid1, pid_t pid2, int32_t type, uint32_t idx1, uint32_t idx2) __syscall(349);
int32_t sys_finit_module(int32_t fd, char const* param_values, int32_t flags) __syscall(350);
int32_t sys_sched_setattr(pid_t pid, struct sched_attr* attr, uint32_t flags) __syscall(351);
int32_t sys_sched_getattr(pid_t pid, struct sched_attr* attr, uint32_t size, uint32_t flags) __syscall(352);
int32_t sys_renameat2(int32_t olddirfd, char const* oldpath, int32_t newdirfd, char const* newpath, uint32_t flags) __syscall(353);
int32_t sys_seccomp(uint32_t operation, uint32_t flags, void* args) __syscall(354);
int32_t sys_getrandom(void* buf, uint32_t buflen, uint32_t flags) __syscall(355);
int32_t sys_memfd_create(char const* name, uint32_t flags) __syscall(356);
int32_t sys_bpf(int32_t cmd, union bpf_attr* attr, uint32_t size) __syscall(357);
int32_t sys_execveat(int32_t dirfd, char const* pathname, char* const* argv, char* const* envp, int32_t flags) __syscall(358);
int32_t sys_socket(int32_t domain, int32_t type, int32_t protocol) __syscall(359);
int32_t sys_socketpair(int32_t domain, int32_t type, int32_t protocol, int32_t sv[0x2]) __syscall(360);
int32_t sys_bind(int32_t sockfd, struct sockaddr const* addr, socklen_t addrlen) __syscall(361);
int32_t sys_connect(int32_t sockfd, struct sockaddr const* addr, socklen_t addrlen) __syscall(362);
int32_t sys_listen(int32_t sockfd, int32_t backlog) __syscall(363);
int32_t sys_accept4(int32_t sockfd, struct sockaddr* addr, socklen_t* addrlen, int32_t flags) __syscall(364);
int32_t sys_getsockopt(int32_t sockfd, int32_t level, int32_t optname, void* optval, socklen_t* optlen) __syscall(365);
int32_t sys_setsockopt(int32_t sockfd, int32_t level, int32_t optname, void const* optval, socklen_t optlen) __syscall(366);
int32_t sys_getsockname(int32_t sockfd, struct sockaddr* addr, socklen_t* addrlen) __syscall(367);
int32_t sys_getpeername(int32_t sockfd, struct sockaddr* addr, socklen_t* addrlen) __syscall(368);
int32_t sys_sendto(int32_t sockfd, void const* buf, uint32_t len, int32_t flags, struct sockaddr const* dest_addr, socklen_t addrlen) __syscall(369);
int32_t sys_sendmsg(int32_t sockfd, struct msghdr const* msg, int32_t flags) __syscall(370);
int32_t sys_recvfrom(int32_t sockfd, void* buf, uint32_t len, int32_t flags, struct sockaddr* src_addr, socklen_t* addrlen) __syscall(371);
int32_t sys_recvmsg(int32_t sockfd, struct msghdr* msg, int32_t flags) __syscall(372);
int32_t sys_shutdown(int32_t sockfd, int32_t how) __syscall(373);
int32_t sys_userfaultfd(int32_t flags) __syscall(374);
int32_t sys_membarrier(int32_t cmd, int32_t flags) __syscall(375);
int32_t sys_mlock2(void const* addr, uint32_t len, int32_t flags) __syscall(376);
int32_t sys_copy_file_range(int32_t fd_in, loff_t* off_in, int32_t fd_out, loff_t* off_out, uint32_t len, uint32_t flags) __syscall(377);
int32_t sys_preadv2(int32_t fd, struct iovec const* iov, int32_t iovcnt, off_t offset, int32_t flags) __syscall(378);
int32_t sys_pwritev2(int32_t fd, struct iovec const* iov, int32_t iovcnt, off_t offset, int32_t flags) __syscall(379);
int32_t sys_pkey_mprotect(void* addr, uint32_t len, int32_t prot, int32_t pkey) __syscall(380);
int32_t sys_pkey_alloc(uint32_t flags, uint32_t access_rights) __syscall(381);
int32_t sys_pkey_free(int32_t pkey) __syscall(382);
int32_t sys_statx(int32_t dirfd, char const* pathname, int32_t flags, uint32_t mask, struct statx* statxbuf) __syscall(383);
int32_t sys_arch_prctl(int32_t code, uint32_t addr) __syscall(384);
int32_t io_getevents(io_context_t ctx_id, int32_t min_nr, int32_t nr, struct io_event* events, struct timespec* timeout) __syscall(385);
int32_t sys_rseq(struct rseq* rseq, uint32_t rseq_len, int32_t flags, uint32_t sig) __syscall(386);
int32_t sys_semget(key_t key, int32_t nsems, int32_t semflg) __syscall(393);
int32_t sys_semctl(int32_t semid, int32_t semnum, int32_t cmd, ...) __syscall(394);
int32_t sys_shmget(key_t key, uint32_t size, int32_t shmflg) __syscall(395);
int32_t sys_shmctl(int32_t shmid, int32_t cmd, struct shmid_ds* buf) __syscall(396);
void* sys_shmat(int32_t shmid, void const* shmaddr, int32_t shmflg) __syscall(397);
int32_t sys_shmdt(void const* shmaddr) __syscall(398);
int32_t sys_msgget(key_t key, int32_t msgflg) __syscall(399);
int32_t sys_msgsnd(int32_t msqid, void const* msgp, uint32_t msgsz, int32_t msgflg) __syscall(400);
int32_t sys_msgrcv(int32_t msqid, void* msgp, uint32_t msgsz, int32_t msgtyp, int32_t msgflg) __syscall(401);
int32_t sys_msgctl(int32_t msqid, int32_t cmd, struct msqid_ds* buf) __syscall(402);
int32_t sys_clock_gettime64(clockid_t clockid, struct timespec* tp) __syscall(403);
int32_t sys_clock_settime64(clockid_t clockid, struct timespec const* tp) __syscall(404);
int32_t sys_clock_adjtime64(clockid_t clk_id, struct timex* buf) __syscall(405);
int32_t sys_clock_getres_time64(clockid_t __clock_id, struct __timespec64* __res) __syscall(406);
int32_t sys_clock_nanosleep_time64(clockid_t clock_id, int32_t flags, struct __timespec64 const* req, struct __timespec64* rem) __syscall(407);
int32_t sys_timer_gettime64(void* timerid, struct itimerspec* curr_value) __syscall(408);
int32_t sys_timer_settime64(void* timerid, int32_t flags, struct itimerspec const* new_value, struct itimerspec* old_value) __syscall(409);
int32_t sys_timerfd_gettime64(int32_t fd, struct itimerspec* curr_value) __syscall(410);
int32_t sys_timerfd_settime64(int32_t fd, int32_t flags, struct itimerspec const* new_value, struct itimerspec* old_value) __syscall(411);
int32_t sys_utimensat_time64(int32_t dirfd, char const* pathname, struct __timespec64 const* times, int32_t flags) __syscall(412);
int32_t sys_pselect6_time64(int32_t nfds, fd_set* readfds, fd_set* writefds, fd_set* exceptfds, struct __timespec64 const* timeout, struct kernel_sigset_t const* sigmask) __syscall(413);
int32_t sys_ppoll_time64(struct pollfd* fds, nfds_t nfds, struct __timespec64 const* tmo_p, struct kernel_sigset_t const* sigmask) __syscall(414);
int32_t sys_io_pgetevents_time64(io_context_t ctx_id, int32_t min_nr, int32_t nr, struct io_event* events, struct __timespec64* timeout) __syscall(416);
int32_t sys_recvmmsg_time64(int32_t sockfd, struct mmsghdr* msgvec, uint32_t vlen, int32_t flags, struct __timespec64* timeout) __syscall(417);
int32_t sys_mq_timedsend_time64(mqd_t mqdes, char const* msg_ptr, uint32_t msg_len, uint32_t msg_prio, struct __timespec64 const* abs_timeout) __syscall(418);
int32_t sys_mq_timedreceive_time64(mqd_t mqdes, char* msg_ptr, uint32_t msg_len, uint32_t* msg_prio, struct __timespec64 const* abs_timeout) __syscall(419);
int32_t sys_semtimedop_time64(int32_t semid, struct sembuf* sops, uint32_t nsops, struct __timespec64 const* timeout) __syscall(420);
int32_t sys_rt_sigtimedwait_time64(struct kernel_sigset_t const* set, struct siginfo_t* info, struct __timespec64 const* timeout) __syscall(421);
int32_t sys_futex_time64(int32_t* uaddr, int32_t futex_op, int32_t val, struct __timespec64 const* timeout, int32_t* uaddr2, int32_t val3) __syscall(422);
int32_t sys_sched_rr_get_interval_time64(pid_t pid, struct __timespec64* tp) __syscall(423);
int32_t sys_pidfd_send_signal(int32_t pidfd, int32_t sig, struct siginfo_t* info, uint32_t flags) __syscall(424);
int32_t sys_io_uring_setup(u32 entries, struct io_uring_params* p) __syscall(425);
int32_t sys_io_uring_enter(uint32_t fd, uint32_t to_submit, uint32_t min_complete, uint32_t flags, struct kernel_sigset_t* sig) __syscall(426);
int32_t sys_io_uring_register(uint32_t fd, uint32_t opcode, void* arg, uint32_t nr_args) __syscall(427);
int32_t sys_open_tree(uint32_t dfd, char const* pathname, uint32_t flags) __syscall(428);
int32_t sys_move_mount(int32_t from_dfd, char const* from_path, int32_t to_dfd, char const* to_path, uint32_t flags) __syscall(429);
int32_t sys_fsopen(char const* fsname, uint32_t flags) __syscall(430);
int32_t sys_fsconfig(int32_t fs_fd, uint32_t cmd, char const* key, void const* value, int32_t aux) __syscall(431);
int32_t sys_fsmount(int32_t fsfd, uint32_t flags, uint32_t attr_flags) __syscall(432);
int32_t sys_fspick(uint32_t dirfd, char const* path, uint32_t flags) __syscall(433);
int32_t sys_pidfd_open(pid_t pid, uint32_t flags) __syscall(434);
int32_t sys_clone3(struct clone_args* cl_args, uint32_t size) __syscall(435);
