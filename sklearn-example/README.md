# Classifying Digits using scikit-learn

This is an example of an application that classifies streams of hand-written digits. This example is discussed in the [A scikit-learn pipeline in Wallaroo](https://blog.wallaroolabs.com/2018/02/a-scikit-learn-pipeline-in-wallaroo/) blog post. For details on how the application works, please refer to the blog post.

You will need a working [Wallaroo Python API](https://docs.wallaroolabs.com/book/python/intro.html).

## Training the models

Before running the application we will have to run a script to train the the scikit-learn models and serialize them for later use:

```bash
python train_models.py
```

## Running the application

In a shell, start up the Metrics UI if you don't already have it running:

```bash
docker start mui
```

In a shell, set up a listener:

```bash
nc -l 127.0.0.1 7002 > digits.out
```

In another shell, set up your environment variables if you haven't already done so. Assuming you installed Machida according to the tutorial instructions you would do:

```bash
export PYTHONPATH="$PYTHONPATH:.:$HOME/wallaroo-tutorial/wallaroo/machida"
export PATH="$PATH:$HOME/wallaroo-tutorial/wallaroo/machida/build"
```

Run `machida` with `--application-module digits`:

```bash
machida --application-module digits --in 127.0.0.1:8002 --out 127.0.0.1:7002 \
  --metrics 127.0.0.1:5001 --control 127.0.0.1:6000 --data 127.0.0.1:6001 \
  --name worker-name --cluster-initializer --ponythreads=1
```

In a third shell, send the MNIST data using the specialised sender:

```bash
python sender.py
```

## Reading the Output

The output is formatted as a 4-byte message length header containing the length of a string, followed by a string representing the output of the classification.

You can read it with the following code stub:

```python
import struct


with open('digits.out', 'rb') as f:
    while True:
        try:
            length = struct.unpack('>I', f.read(4))
            print f.read(length)
        except:
            break
```
