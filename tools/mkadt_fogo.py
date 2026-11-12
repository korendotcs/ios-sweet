#!/usr/bin/env python3
"""Apple Device Tree for moto g 5G 2024 (fogo, SM4375 'blair').

Reuses mkadt.py's tree and swaps in fogo's addresses from its live FDT
(dt/live.dts). CPU layout matches sweet: MPIDR core<<8, 0-5 A55, 6-7 A78.
Usage: mkadt_fogo.py OUT.adt [--dump]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adt  # noqa: E402
import mkadt  # noqa: E402

# Upper DDR bank: System RAM 0x1_00000000.. up to the first fixed carve-out
# at 0x1_7ae00000 (/proc/iomem). ~1.9 GB for XNU.
mkadt.HIGH_PHYS_BASE = 0x100000000
mkadt.HIGH_MEM_SIZE = 0x7ae00000
mkadt.GICD, mkadt.GICD_SIZE = 0x0f200000, 0x10000
mkadt.GICR, mkadt.GICR_SIZE = 0x0f240000, 0x100000
# cont_splash_region 0x85200000 size 0xc00000; panel 720x1612 a8r8g8b8
mkadt.FB, mkadt.FB_SIZE = 0x85200000, 0xc00000
mkadt.FB_W, mkadt.FB_H, mkadt.FB_STRIDE = 720, 1612, 720 * 4
mkadt.UFS, mkadt.UFS_SIZE = 0x04804000, 0x3000
mkadt.SWEET_ECID = 0x464F474F00000001  # 'FOGO' + 1, synthetic

if __name__ == '__main__':
    root = mkadt.build(highmem=True)
    blob = adt.serialize(root)
    # self-check: the fogo addresses made it into the tree
    for v in (0x0f200000 - mkadt.SOC_BASE, 0x85200000, 0x04804000, 0x100000000):
        assert v.to_bytes(8, 'little') in blob, hex(v)
    open(sys.argv[1], 'wb').write(blob)
    if '--dump' in sys.argv:
        adt.dump(adt.parse(blob)[0])
    print(f'{sys.argv[1]}: {len(blob)} bytes', file=sys.stderr)
