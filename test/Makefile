WAT := $(wildcard *.wat)
WASM := $(WAT:%.wat=%.wasm)

.PHONY: all clean

all: $(WASM)

clean:
	rm -rf $(WASM)

%.wasm: %.wat
	wat2wasm $^ -o $@
