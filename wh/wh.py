from calyx.builder import Builder, while_with, par, const
from calyx import py_ast as ast

WASM_SIZE = 256


def idx_size(count):
    """Get the index size for a memory with `count` elements."""
    # The exception for 1-element memories is something of a wart
    # in Calyx: they should have zero-bit address ports, but Calyx
    # doesn't like that.
    return (count - 1).bit_length() if count > 1 else 1


def build_load4(main, wasm, wasm_idx, reg):
    reg_width = main.infer_width(reg.out)

    # Initialize register to 0.
    ctrl = [
        main.reg_store(reg, 0, "init_chunk"),
    ]

    pad = main.cell("pad", ast.CompInst("std_pad", [8, reg_width]))
    lsh = main.binary("lsh", reg_width)
    or_ = main.binary("or", reg_width)

    # Load each byte.
    incr = main.incr(wasm_idx, 1, False, "wishing_for_gensym")
    read_wasm = main.mem_read_seq_d1(wasm, wasm_idx.out, "please_gensym")
    for i in range(4):
        # reg := reg | (zext(wasm) << (3-i)*8).
        with main.group(f"add_byte_{i}_to_chunk") as add_to_chunk:
            pad.in_ = wasm.read_data
            lsh.left = pad.out
            lsh.right = const(reg_width, (3 - i) * 8)
            or_.left = reg.out
            or_.right = lsh.out

            reg.in_ = or_.out
            reg.write_en = 1
            add_to_chunk.done = reg.done

        ctrl += [
            read_wasm,
            add_to_chunk,
            incr,
        ]

    return ctrl


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

    # Check the magic number.
    chunk = main.reg("chunk", 32)
    main.control += [
        build_load4(main, wasm, wasm_idx, chunk)
    ]

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
