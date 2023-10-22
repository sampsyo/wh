from . import wasm
import sys
from typing import Optional


class Read:
    def __init__(self, stream):
        self.stream = stream

    def read(self, count) -> bytes:
        res = self.stream.read(count)
        assert len(res) == count
        return res

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
            print(b)
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
        sec = read_section(read)
        if not sec:
            break


def read_section(read: Read) -> bool:
    id = read.maybe_byte()
    if id is None:
        return False
    size = read.u32()
    cont = read.read(size)
    assert len(cont) == size
    print(id, cont)
    return True


if __name__ == "__main__":
    read_module(Read(sys.stdin.buffer))
