from calyx.builder import Builder, while_with, par

WASM_SIZE = 256


def idx_size(count):
    """Get the index size for a memory with `count` elements."""
    # The exception for 1-element memories is something of a wart
    # in Calyx: they should have zero-bit address ports, but Calyx
    # doesn't like that.
    return (count - 1).bit_length() if count > 1 else 1


def build():
    prog = Builder()
    main = prog.component("main")

    # The input memories.
    wasm_idx_width = idx_size(WASM_SIZE)
    wasm = main.seq_mem_d1("wasm", 8, WASM_SIZE, wasm_idx_width,
                           is_external=True)
    wasm_len = main.seq_mem_d1("wasm_len", wasm_idx_width, 1, 1,
                               is_external=True)

    # Loop setup.
    wasm_idx = main.reg("wasm_idx", wasm_idx_width)
    main.control += par(
        main.mem_read_seq_d1(wasm_len, 0),
        main.reg_store(wasm_idx, 0),
    )

    # Main loop.
    main.control += while_with(
        main.le_use(wasm_idx.out, wasm_len.read_data),
        [
            main.incr(wasm_idx),
        ],
    )

    return prog.program


if __name__ == '__main__':
    build().emit()
