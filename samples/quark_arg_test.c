void no_args() {
    puts("no args");
}
void one_arg(const char* arg) {
    puts("arg:");
    puts(arg);
}
void two_args(const char* arg1, const char* arg2) {
    puts("args:");
    puts(arg1);
    puts(arg2);
}
void three_args(
    const char* arg1,
    const char* arg2,
    const char* arg3
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
}
void four_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
}
void five_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
}
void six_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5,
    const char* arg6
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
    puts(arg6);
}
void seven_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5,
    const char* arg6,
    const char* arg7
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
    puts(arg6);
    puts(arg7);
}
void eight_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5,
    const char* arg6,
    const char* arg7,
    const char* arg8
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
    puts(arg6);
    puts(arg7);
    puts(arg8);
}
void nine_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5,
    const char* arg6,
    const char* arg7,
    const char* arg8,
    const char* arg9
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
    puts(arg6);
    puts(arg7);
    puts(arg8);
    puts(arg9);
}
void ten_args(
    const char* arg1,
    const char* arg2,
    const char* arg3,
    const char* arg4,
    const char* arg5,
    const char* arg6,
    const char* arg7,
    const char* arg8,
    const char* arg9,
    const char* arg10
) {
    puts("args:");
    puts(arg1);
    puts(arg2);
    puts(arg3);
    puts(arg4);
    puts(arg5);
    puts(arg6);
    puts(arg7);
    puts(arg8);
    puts(arg9);
    puts(arg10);
}

int64_t main() {
    no_args();
    one_arg("1");
    two_args("1", "2");
    three_args("1", "2", "3");
    four_args("1", "2", "3", "4");
    five_args("1", "2", "3", "4", "5");
    six_args("1", "2", "3", "4", "5", "6");
    seven_args("1", "2", "3", "4", "5", "6", "7");
    eight_args("1", "2", "3", "4", "5", "6", "7", "8");
    nine_args("1", "2", "3", "4", "5", "6", "7", "8", "9");
    ten_args("1", "2", "3", "4", "5", "6", "7", "8", "9", "10");
}