.PHONY: run-new run-old setup

INPUT_FILES := input/1000.csv input/100000.csv input/1000000.csv input/10000000.csv

setup: env $(INPUT_FILES) log output

env:
	virtualenv env
	(. env/bin/activate && pip install -r requirements.txt)

input/%.csv: input
	(. env/bin/activate && \
	  ./generate_input_data.py $(basename $(notdir $@)) > $@)

input:
	mkdir -p input

log:
	mkdir -p log

output:
	mkdir -p output

run-new: input log output
	@-killall -9 machida 2>/dev/null
	INPUT=$(INPUT) OUTPUT="output/new_$(notdir $(INPUT))" \
	  N_WORKERS=$(N_WORKERS) ./run_machida.sh

run-old: input output
	./old_pipeline.py $(INPUT) "output/old_$(notdir $(INPUT))"
