import struct, os

f = open("recovery.img", "rb")
d = f.read()

u32 = lambda o: struct.unpack_from("<I", d, o)[0]
page = u32(36)
version = u32(40)

kernel_size = u32(8)
ramdisk_size = u32(16)
second_size = u32(24)

align = lambda x: (x + page - 1) // page * page

ko = page
ro = align(ko + kernel_size)
so = align(ro + ramdisk_size)

print("Header version:", version)
print("Page size:", page)
print("Kernel:", kernel_size, "offset:", hex(ko))
print("Ramdisk:", ramdisk_size, "offset:", hex(ro))
print("Second:", second_size, "offset:", hex(so))

os.makedirs("unpacked", exist_ok=True)

for name, off, size in [
    ("kernel", ko, kernel_size),
    ("ramdisk", ro, ramdisk_size),
]:
    if size:
        open("unpacked/" + name + ".img", "wb").write(d[off:off+size])

if version >= 1:
    recovery_dtbo_size = u32(1632)
    recovery_dtbo_offset = struct.unpack_from("<Q", d, 1636)[0]
    print("Recovery DTBO:", recovery_dtbo_size, hex(recovery_dtbo_offset))
    if recovery_dtbo_size:
        open("unpacked/recovery_dtbo.img", "wb").write(
            d[recovery_dtbo_offset:recovery_dtbo_offset+recovery_dtbo_size])

if version >= 2:
    dtb_size = u32(1648)
    print("DTB size:", dtb_size)
    if dtb_size:
        dtb_offset = align(recovery_dtbo_offset + recovery_dtbo_size)
        open("unpacked/dtb.img", "wb").write(d[dtb_offset:dtb_offset+dtb_size])

print("Extraction completed.")
