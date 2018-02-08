import struct
import cPickle as pickle
import wallaroo


def application_setup(args):
    global pca
    global logistic
    with open('pca.model', 'r') as f:
        pca = pickle.load(f)
    with open('logistic.model', 'r') as f:
        logistic = pickle.load(f)

    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]

    ab = wallaroo.ApplicationBuilder("MNIST classification")
    ab.new_pipeline("MNIST",
                    wallaroo.TCPSourceConfig(in_host, in_port, decode))
    ab.to(pca_transform)
    ab.to(logistic_classify)
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, encode))
    return ab.build()


@wallaroo.decoder(header_length=4, length_fmt=">I")
def decode(bs):
    return pickle.loads(bs)


@wallaroo.computation(name="PCA")
def pca_transform(x):
    return pca.transform([x])


@wallaroo.computation(name="Logistic Regression")
def logistic_classify(x):
    return logistic.predict(x)


@wallaroo.encoder
def encode(data):
    s = str(data)
    return struct.pack('>I{}s'.format(len(s)), len(s), s)

