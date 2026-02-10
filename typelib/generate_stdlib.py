from pathlib import Path

from binaryninja import TypeLibrary, Platform, TypeParser, Type, TypeParserResult

LIB_NAME = "stdlib"
HEADERS = [
	{
		"files": [
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/file.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/memory.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/net.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/process.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/shell.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/time.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/crc32.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/rc4.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/quark_vm.h",
		],
		"args": [
			"-I/Users/glennsmith/Documents/binaryninja/scc",
			"-include/Users/glennsmith/Documents/binaryninja/scc/runtime/vararg.h"
		]
	},
	{
		"files": [
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/string.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/linux/process.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/linux/x86/stat.h",
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/linux/x86/file.h",
		],
		"args": [
			"-I/Users/glennsmith/Documents/binaryninja/scc"
		]
	},
	{
		"files": [
			"/Users/glennsmith/Documents/binaryninja/scc/runtime/linux/net.h",
		],
		"args": [
			"-I/Users/glennsmith/Documents/binaryninja/scc",
			"-include/Users/glennsmith/Documents/binaryninja/scc/runtime/posix/net.h"
		],
	}
]

p = Platform["linux-quark"]

tl = TypeLibrary.new(p.arch, LIB_NAME)
tl.add_platform(p)

for group in HEADERS:
	for file in group["files"]:
		with open(file, "r") as f:
			source = f.read()
		parse, errors = TypeParser.default.parse_types_from_source(
			source,
			file,
			p,
			tl.type_container,
			group["args"]
		)

		if parse is None:
			print(f"Errors in {file}: {errors}")
		else:
			parse: TypeParserResult
			for ty in parse.types:
				if tl.get_named_type(ty.name) is not None:
					print(f"duplicate type {ty.name}")

				tl.add_named_type(ty.name, ty.type)

			for func in parse.functions:
				# print(f"{func.type.get_string_before_name()} {func.name}{func.type.get_string_after_name()}")
				tl.add_named_object(func.name, func.type)

	tl.write_to_file(str(Path(__file__).parent / f"{tl.name}.bntl"))

