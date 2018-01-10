import struct
import wallaroo
import pandas as pd

def application_setup(args):
    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]
    ab = wallaroo.ApplicationBuilder("Trending Hashtags")
    ab.new_pipeline("Tweets_new", wallaroo.TCPSourceConfig(in_host, in_port, Decoder() ))
    ab.to(HashtagFinder)
    ab.to_stateful(ComputeHashtags(), HashtagsStateBuilder(), "hashtags state")
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, Encoder()))
    return ab.build()


class Decoder(object):
    def header_length(self):
        return 5

    def payload_length(self, bs):
        return int(struct.unpack("!5s", bs)[0])

    def decode(self, bs):
        return bs.decode("utf-8")


class Encoder(object):
    def encode(self, data):
        # extract the hashtags from dataframe and convert them into array
        top_tags = [str(hashtag.encode("utf-8")) for hashtag in data]
        # extract the counts from dataframe and convert them into array
        tags_count = [data[hashtag] for hashtag in data]
        # transform the data to be as array of labels and array of counts
        request_data = {'label': str(top_tags), 'data': str(tags_count)}
        # return the data to TCP connection along with a special separator
        return str(request_data) + ';;\n'


class HashtagFinder(object):
    def name(self):
        return "HashtagFinder"

    def compute_multi(self, data):
        return [word.strip() for word in data.split() if word[0] == '#']


class HashtagCounts(object):

    def __init__(self):
        self.hashtags_df = pd.DataFrame(columns=['Hashtag','Counts'])
        # We want to be addressing by Hashtag most frequently
        self.hashtags_df = self.hashtags_df.set_index(['Hashtag'])
        # Counts is an int
        self.hashtags_df['Counts'] = self.hashtags_df['Counts'].astype('int')

    def update(self, hashtag_name, counts):
        # if the hashtag is already exists then add its counts to old counts
        # and if not exists, then add it in the dataframe with its current counts
        curr_count = 0
        if hashtag_name in self.hashtags_df.index:
            curr_count = self.hashtags_df.loc[hashtag_name]
        self.hashtags_df.loc[hashtag_name] = curr_count + counts

    def get_counts(self, n=10):
        # Return from the dataframe a dict of top n hashtags
        return self.hashtags_df.nlargest(n,'Counts').to_dict()['Counts']

    def get_count(self, c):
        # int is safe to return as is!
        return self.hashtags_df.loc[c]


class ComputeHashtags(object):
    def name(self):
        return "ComputeHashtags"

    def compute(self, data, state):
        # update the state object with the current data
        state.update(hashtag_name=data, counts=1)
        # returns the top 10 hashtags data from the state object
        return (state.get_counts(), True)


class HashtagsStateBuilder(object):
    def build(self):
        return HashtagCounts()
