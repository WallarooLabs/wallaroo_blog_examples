# Parallelizing a Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog post](http://example.com) for a quick run-down of this project.

## How to run this code

1. Make sure you have [Wallaroo](https://docs.wallaroolabs.com/book/getting-started/wallaroo-up.html) and `virtualenv` installed on your machine.

2. Run `make setup` to ensure that a sandboxed environment is present in `env`.

3. To run the 'old' pipeline, use this invocation:

```
 make run-old INPUT=input/1000.csv
```

4. To run the 'new' pipeline, use this one:

```
make run-new INPUT=input/1000.csv N_WORKERS=4
```

5. Play around with the size of the inputs, and number of workers, and see the
   effect on the run-time.  If you're feeling experimental, tweak the
   `CHUNK_SIZE` constant in `classifer.py` or the `CLASSIFIER_SLOWNESS`
   constant in `fancy_ml_black_box.py` and see how that effects the pipeline.
   Have fun!


## The components:

 - `classifier.py` : The Wallaroo application that parallelizes our classification
 - `env` : A local virtualenv environment (use `. env/bin/activate` to use it in your shell)
 - `fancy_ml_black_box.py` : Our fake (but expensive CPU-wise) classifier module
 - `generate_input_data.py` : A script to generate input CSV files
 - `input` : The generated input files live here
 - `log` : The Wallaroo workers put their logs here
 - `Makefile` : Encapsulates setting up and running the project
 - `old_pipeline.py` : The bottlenecking batch job we want to parallelize
 - `output` : The old and new applications drop their output here as `old_` and `new_` csv files
 - `README.md` : This readme
 - `requirements.txt` : Python requirements for setting up the virtual environment
 - `run_machida.sh` : A script that encapsulates starting the Wallaroo cluster, sending and receiving the data, and shutting it down at the end
 - `send.py` : The program used to send CSV input files to Wallaroo
