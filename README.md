# Quark Architecture

This plugin adds support for the Quark architecture to Binary Ninja. It is intended to be used as an example for architecture plugins and has an extensive write-up on our blog:

## Contents

* [Target](https://binary.ninja/2026/02/20/quark-platform-part-1.html#target)
* [Setup](https://binary.ninja/2026/02/20/quark-platform-part-1.html#setup)
* [Part 1: Disassembly](https://binary.ninja/2026/02/20/quark-platform-part-1.html#disassembly)
    * [Decoding](https://binary.ninja/2026/02/20/quark-platform-part-1.html#decoding)
    * [Disassembly Text](https://binary.ninja/2026/02/20/quark-platform-part-1.html#disassembly-text)
    * [Control Flow](https://binary.ninja/2026/02/20/quark-platform-part-1.html#control-flow)
    * [Addendum](https://binary.ninja/2026/02/20/quark-platform-part-1.html#addendum)
    * [Patching](https://binary.ninja/2026/02/20/quark-platform-part-1.html#patching)
    * [Assembling](https://binary.ninja/2026/02/20/quark-platform-part-1.html#assembling)
* [Part 2: Lifting](https://binary.ninja/2026/02/26/quark-platform-part-2.html#lifting)
    * [Basics](https://binary.ninja/2026/02/26/quark-platform-part-2.html#basics)
    * [Loads and Stores](https://binary.ninja/2026/02/26/quark-platform-part-2.html#loads-and-stores)
    * [Calls](https://binary.ninja/2026/02/26/quark-platform-part-2.html#calls)
    * [Arithmetic](https://binary.ninja/2026/02/26/quark-platform-part-2.html#arithmetic)
    * [System Calls](https://binary.ninja/2026/02/26/quark-platform-part-2.html#system-calls)
    * [Intrinsics](https://binary.ninja/2026/02/26/quark-platform-part-2.html#intrinsics)
    * [Flags](https://binary.ninja/2026/02/26/quark-platform-part-2.html#flags)
    * [Conditionals](https://binary.ninja/2026/02/26/quark-platform-part-2.html#conditionals)
    * [Other](https://binary.ninja/2026/02/26/quark-platform-part-2.html#other)
* [Part 3: Platform Support](https://binary.ninja/2026/03/04/quark-platform-part-3.html#platform-support)
    * [Calling Convention](https://binary.ninja/2026/03/04/quark-platform-part-3.html#calling-convention)
    * [System Calls](https://binary.ninja/2026/03/04/quark-platform-part-3.html#system-calls-1)
    * [Platform Types](https://binary.ninja/2026/03/04/quark-platform-part-3.html#platform-types)
    * [Type Libraries](https://binary.ninja/2026/03/04/quark-platform-part-3.html#type-libraries)
    * [Function Signatures](https://binary.ninja/2026/03/04/quark-platform-part-3.html#function-signatures)
    * [Other](https://binary.ninja/2026/03/04/quark-platform-part-3.html#other)
* [Conclusion](https://binary.ninja/2026/03/04/quark-platform-part-3.html#conclusion)

## Repository Structure

* `__init__.py` - Architecture plugin code
* `signatures` - Standard library function signatures, including the files used to generate them
* `typelib` - Standard library and syscall Type Libraries, including the files used to generate them
* `types` - System Types sources
* `samples` - Sample binaries for testing

## License

MIT License. See LICENSE.txt.