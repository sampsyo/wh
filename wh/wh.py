from calyx.builder import Builder, while_with, par, const, if_with, invoke
from calyx import py_ast as ast
from . import wasm

WASM_SIZE = 256
WASM_IDX_WIDTH = (WASM_SIZE - 1).bit_length()


def build_chunker(prog, count):
    chunk_width = 8 * count

    # TODO Only create it once for each count...
    chunker = prog.component(f"chunker_{count}")
    chunker.output("chunk", chunk_width)

    # Input and output cells.
    chunk = chunker.reg("chunk_reg", chunk_width)
    mem = chunker.seq_mem_d1("mem", 8, WASM_SIZE, WASM_IDX_WIDTH, is_ref=True)
    idx = chunker.reg("idx", WASM_IDX_WIDTH, is_ref=True)

    # Wire result register to output.
    with chunker.continuous:
        chunker.this()["chunk"] = chunk.out

    # Initialize register to 0.
    chunker.control += [
        chunker.reg_store(chunk, 0, "init"),
    ]

    pad = chunker.cell("pad", ast.CompInst("std_pad", [8, chunk_width]))
    lsh = chunker.binary("lsh", chunk_width)
    or_ = chunker.binary("or", chunk_width)

    # Load each byte.
    incr = chunker.incr(idx, 1, False)
    read_wasm = chunker.mem_read_seq_d1(mem, idx.out)
    for i in range(count):
        # reg := reg | (zext(wasm) << (3-i)*8).
        with chunker.group(f"add_byte_{i}_to_chunk") as add_to_chunk:
            pad.in_ = mem.read_data
            lsh.left = pad.out
            lsh.right = const(chunk_width, (count - 1 - i) * 8)
            or_.left = chunk.out
            or_.right = lsh.out

            chunk.in_ = or_.out
            chunk.write_en = 1
            add_to_chunk.done = chunk.done

        chunker.control += [
            read_wasm,
            add_to_chunk,
            incr,
        ]

    return chunker


def build_main(prog):
    main = prog.component("main")

    # The input memories.
    wasm_mem = main.seq_mem_d1("wasm", 8, WASM_SIZE, WASM_IDX_WIDTH,
                               is_external=True)
    wasm_len = main.seq_mem_d1("wasm_len", WASM_IDX_WIDTH, 1, 1,
                               is_external=True)

    # Loop setup.
    wasm_idx = main.reg("wasm_idx", WASM_IDX_WIDTH)
    main.control += par(
        main.mem_read_seq_d1(wasm_len, 0),
        main.reg_store(wasm_idx, 0),
    )

    # Check the magic number.
    err = main.reg("err_reg", 1)
    magic_val = const(32, int.from_bytes(wasm.MAGIC))
    chunker_comp = build_chunker(prog, 4)  # A good place for modules...
    chunker = main.cell("chunker", chunker_comp)
    main.control += [
        main.reg_store(err, 0),
        invoke(chunker, ref_mem=wasm_mem, ref_idx=wasm_idx),
        # Wishing for Calyx `assert` here. Barring that, signal an error
        # with an actual output.
        if_with(main.neq_use(chunker.chunk, magic_val), [
            main.reg_store(err, 1, "error"),
        ]),
    ]

    # Main loop.
    # TODO: The condition should have an `and !err` in it for early
    # termination.
    main.control += while_with(
        main.le_use(wasm_idx.out, wasm_len.read_data),
        [
            main.incr(wasm_idx),
        ],
    )

    # Report errors.
    err_mem = main.seq_mem_d1("err", 1, 1, 1, is_external=True)
    main.control += [
        main.mem_store_seq_d1(err_mem, 0, err.out),
    ]

    return main


def build():
    prog = Builder()
    build_main(prog)
    return prog.program


if __name__ == '__main__':
    build().emit()
