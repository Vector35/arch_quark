void quark_exec(void* buf, ...) __noreturn;

int64_t main(void* input) {
    quark_exec(input);
}