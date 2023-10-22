.PHONY: interp debug sim dump

interp: wh.futil test/tiny.json
	fud exec $< --from calyx --to interpreter-out \
		-s verilog.data test/tiny.json \
		-s calyx.flags '-p compile-invoke' \
		| jq .main.err[0]

debug: wh.futil test/tiny.json
	fud exec $< --from calyx --to debugger \
		-s calyx.flags '-p compile-invoke' \
		-s verilog.data test/tiny.json

sim: wh.futil test/tiny.json
	fud exec $< --from calyx --to dat --through icarus-verilog \
		-s verilog.data test/tiny.json \
		| jq .memories.err[0]

dump:
	@python3 -m wh.wh

test/tiny.json: test/tiny.wat
	make -C test

wh.futil: wh/wh.py
	python3 -m wh.wh > $@
