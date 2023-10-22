"""Convert raw binary WebAssembly files to fud-friendly data JSON files.
"""
import json
import sys

MAX_BYTES = 256


def gen_dat():
    raw_bytes = list(sys.stdin.buffer.read())
    assert len(raw_bytes) <= MAX_BYTES

    memories = {
        "wasm": {
            "data": raw_bytes + [0] * (MAX_BYTES - len(raw_bytes)),
            "format": {
                "numeric_type": "bitnum",
                "is_signed": False,
                "width": 8,
            },
        }
    }

    json.dump(memories, sys.stdout, sort_keys=True)


if __name__ == "__main__":
    gen_dat()
