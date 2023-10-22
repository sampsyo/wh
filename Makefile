.PHONY: tiny
tiny: wh.futil
	make -C test
	fud exec --from calyx --to dat --through icarus-verilog \
		-s verilog.data test/tiny.json \
		$<

wh.futil: wh/wh.py
	python3 -m wh.wh > $@
