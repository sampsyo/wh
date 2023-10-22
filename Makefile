.PHONY: interp debug sim

interp: wh.futil test/tiny.json
	fud exec $< --from calyx --to interpreter-out \
		-s verilog.data test/tiny.json

debug: wh.futil test/tiny.json
	fud exec $< --from calyx --to debugger \
		-s verilog.data test/tiny.json

sim: wh.futil test/tiny.json
	fud exec $< --from calyx --to dat --through icarus-verilog \
		-s verilog.data test/tiny.json

test/tiny.json: test/tiny.wat
	make -C test

wh.futil: wh/wh.py
	python3 -m wh.wh > $@
