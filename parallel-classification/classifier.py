from collections import namedtuple
from StringIO import StringIO
import pandas as pd
import struct
import wallaroo
# The classifier, used as a black-box:
import fancy_ml_black_box

CHUNK_SIZE=100

def application_setup(args):
    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]

    ab = wallaroo.ApplicationBuilder("Parallel Classifier with Wallaroo")
    ab.new_pipeline("Classifier",
                    wallaroo.TCPSourceConfig(in_host, in_port, decode))
    ab.to_stateful(batch_rows, RowBuffer, "CSV rows + global header state")
    ab.to_parallel(classify)
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, encode))
    return ab.build()

@wallaroo.state_computation(name='Batch rows of csv, emit DataFrames')
def batch_rows(row, row_buffer):
    return (row_buffer.update_with(row), True)

@wallaroo.decoder(header_length=4, length_fmt=">I")
def decode(bs):
    if bs == "\x04":
        return EndOfInput()
    else:
        return bs

@wallaroo.computation(name="Classify")
def classify(batched_rows):
    df = build_dataframe(batched_rows)
    fancy_ml_black_box.classify_df(df)
    return df

@wallaroo.encoder
def encode(df):
    s = dataframe_to_csv(df)
    return struct.pack('>I',len(s)) + s

def build_dataframe(br):
    buf = StringIO(br.header + "\n" + ("\n".join(br.rows)))
    return pd.read_csv(buf, index_col=0, dtype=unicode, engine='python')

def dataframe_to_csv(df):
    buf = StringIO()
    df.to_csv(buf, header=False)
    s = buf.getvalue().strip()
    buf.close()
    return s

BatchedRows = namedtuple('BatchedRows', ['header', 'rows'])
EndOfInput = namedtuple('EndOfInput', [])

class RowBuffer():
    def __init__(self):
        self._header = None
        self._rows = []

    def update_with(self, row):
        if not self._header:
            return self._update_header(row)
        elif isinstance(row, EndOfInput):
            return self._flush()
        else:
            return self._add_row(row)

    def _update_header(self, header):
        self._header = header
        return None

    def _flush(self):
        out = list(self._rows)
        self._rows = []
        return BatchedRows(self._header, out)

    def _add_row(self, row):
        self._rows.append(row)
        if len(self._rows) == CHUNK_SIZE:
            return self._flush()
        else:
            return None
