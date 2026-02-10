from pathlib import Path

from binaryninja import Platform, TypeLibrary, Architecture

tl = TypeLibrary.new(Architecture["Quark"], "SYSCALLS")
xtl = TypeLibrary.from_guid(Architecture["x86"], "48c0260e-d895-4cf4-a929-cc50a63593c9")

tl.add_platform(Platform["linux-quark"])

for name, ty in xtl.named_types.items():
	tl.add_named_type(name, ty)

for name, ty in xtl.named_objects.items():
	tl.add_named_object(name, ty)

tl.write_to_file(str(Path(__file__).parent / f"syscalls_linux_x86.bntl"))
