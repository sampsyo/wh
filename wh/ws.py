from . import wasm
import sys
import os
from typing import Optional


class Read:
    def __init__(self, stream):
        self.stream = stream

    def read(self, count) -> bytes:
        res = self.stream.read(count)
        assert len(res) == count
        return res

    def skip(self, count) -> None:
        """Skip `count` bytes forward in the stream."""
        self.stream.seek(count, os.SEEK_CUR)

    def byte(self) -> int:
        """Read a single byte from the stream."""
        val = self.read(1)
        return val[0]

    def maybe_byte(self) -> Optional[int]:
        """Try to read a single byte from the stream, or detect EOF."""
        res = self.stream.read(1)
        if res:
            return res[0]
        else:
            return None

    def leb128(self, bits: int) -> int:
        """Read a LEB128-encoded unsigned integer of the given length."""
        out = 0
        shift = 0
        while True:
            b = self.byte()
            out |= (b & 0xEF) << shift
            shift += 7
            if not (b & 0x80):
                break
        return out

    def u32(self):
        return self.leb128(32)


def read_module(read: Read):
    magic = read.read(4)
    assert magic == wasm.MAGIC

    version = read.read(4)
    assert version == wasm.VERSION

    while True:
        hdr = read_section_header(read)
        if not hdr:
            break
        print(hdr)
        if hdr.id == wasm.SectionId.CODE:
            read_code_sec(read, hdr.size)
        else:
            # We just ignore all other sections for now.
            read.skip(hdr.size)


def read_section_header(read: Read) -> Optional[wasm.SectionHeader]:
    id = read.maybe_byte()
    if id is None:
        return None

    size = read.u32()
    return wasm.SectionHeader(
        wasm.SectionId(id),
        size,
    )


def read_code_sec(read: Read, size: int):
    func_count = read.u32()
    for _ in range(func_count):
        size = read.u32()
        print(size)

        # Locals.
        local_count = read.u32()
        print(local_count)
        for _ in range(local_count):
            local_num = read.u32()
            local_type = read.byte()
            print(local_num, local_type)

        # Body.
        while True:
            op = read_instr(read)
            if op == wasm.Opcode.END:
                break


def read_instr(read: Read) -> wasm.Opcode:
    opcode = read.byte()
    assert opcode in list(wasm.Opcode), f"unknown opcode 0x{opcode:x}"
    op = wasm.Opcode(opcode)

    match op:
        case wasm.Opcode.LOCAL_GET:
            idx = read.u32()
            print('local.get', idx)
        case wasm.Opcode.I32_ADD:
            print('add')
        case wasm.Opcode.END:
            print('end')
        case _:
            assert False, f"unhandled opcode {op.name}"

    return op


if __name__ == "__main__":
    read_module(Read(sys.stdin.buffer))
