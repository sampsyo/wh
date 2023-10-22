WAT := $(wildcard *.wat)
WASM := $(WAT:%.wat=%.wasm)
JSON := $(WAT:%.wat=%.json)

.PHONY: all clean

all: $(WASM) $(JSON)

clean:
	rm -rf $(WASM) $(JSON)

%.wasm: %.wat
	wat2wasm $^ -o $@

%.json: %.wasm
	python3 gen_dat.py < $^ > $@
