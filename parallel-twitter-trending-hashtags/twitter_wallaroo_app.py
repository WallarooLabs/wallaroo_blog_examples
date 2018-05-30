import string
import struct
import time
import wallaroo

# Maintain list of TOP_X size for trending hashtags
TOP_X = 10
# Look for values over a TRENDING_OVER minute period
TRENDING_OVER = 5


def application_setup(args):
    in_host, in_port = wallaroo.tcp_parse_input_addrs(args)[0]
    out_host, out_port = wallaroo.tcp_parse_output_addrs(args)[0]

    raw_hashtag_partitions = list(string.ascii_lowercase)
    raw_hashtag_partitions.append("!")

    ab = wallaroo.ApplicationBuilder("Trending Hashtags")
    ab.new_pipeline("Tweets", wallaroo.TCPSourceConfig(in_host, in_port,
                                                       decoder))
    ab.to_parallel(find_hashtags)
    ab.to_state_partition(count_hashtags, HashtagCounts, "raw hashtag counts",
                          extract_hashtag_key, raw_hashtag_partitions)
    ab.to_stateful(top_hashtags, TopTags, "top hashtags")
    ab.to_sink(wallaroo.TCPSinkConfig(out_host, out_port, encoder))
    return ab.build()


@wallaroo.computation_multi(name="find hashtags")
def find_hashtags(data):
    punctuation = " !\"$%&\'()*+,-./:;<=>?@[\\]^_`{|}~"

    hashtags = []

    for line in data.lower().split("\n"):
        for word in line.split(" "):
            clean_word = filter(lambda c: c not in punctuation, word)
            if len(clean_word) > 1 and clean_word[0] == "#":
                hashtag = clean_word.strip('#')
                if hashtag:
                    hashtags.append(hashtag)

    return hashtags


@wallaroo.state_computation(name="count hashtags")
def count_hashtags(hashtag, counts):
    """
    get the current top ten, if this changes
    after updating, we'll send an updated list
    to our top ten aggregator otherwise, skip
    """
    top_ten_if_changed = counts.increment(hashtag)
    return (top_ten_if_changed, True)


@wallaroo.state_computation(name="top tags")
def top_hashtags(tags_and_counts, top_tags):
    """
    receive a dictionary of tags and counts,
    add to our list of top tags and shrink to
    only ten, if our new top ten is different than
    our old, output the new list
    """
    top_ten_if_changed = top_tags.update(tags_and_counts)
    return (top_ten_if_changed, top_ten_if_changed != None)


class HashtagCounts(object):
    def __init__(self):
        self.__top_tags = {}
        self.__size = TRENDING_OVER
        self.__window = []
        for x in range(0, self.__size):
            self.__window.append((0, {}))

    def increment(self, hashtag):
        """
        Increment the count for `hashtag`
        """
        mse = self.__minutes_since_epoch()
        window_gap = int(mse % TRENDING_OVER)

        # have we rolled over?
        if self.__window[window_gap][0] < mse:
            self.__rollover(hashtag, window_gap, mse)
        else:
            self.__increment(hashtag, window_gap)

        # did our top ten change?
        new_top_tags = self.__calculate_top_tags()

        if new_top_tags != self.__top_tags:
            self.__top_tags = new_top_tags
            return self.__top_tags.copy()
        else:
            return None

    def __minutes_since_epoch(self):
        return int(time.time() / 60)

    def __increment(self, hashtag, gap):
        current_count = self.__window[gap][1].get(hashtag, 0)
        self.__window[gap][1][hashtag] = current_count + 1

    def __rollover(self, hashtag, gap, mse):
        self.__window[gap] = (mse, {hashtag: 1})

    def __calculate_top_tags(self):
        tags = {}
        for x in range(0, self.__size):
            subset = self.__window[x][1]
            for (key, value) in subset.items():
                tags[key] = tags.get(key, 0) + value

        return dict(sorted(tags.items(), key=lambda (k, v): v,
                           reverse=True)[:TOP_X])


class TopTags(object):
    def __init__(self):
        self.__top_tags = {}

    def update(self, hashtags_and_counts):
        self.__top_tags.update(hashtags_and_counts)
        new_top_tags = self.__calculate_top_tags()

        top_tags_changed = False

        if new_top_tags != self.__top_tags:
            top_tags_changed = True

        # trim to TOP_X
        self.__top_tags = new_top_tags

        if top_tags_changed:
            return self.__top_tags.copy()
        else:
            return None

    def __calculate_top_tags(self):
        return dict(sorted(self.__top_tags.items(), key=lambda (k, v): v,
                           reverse=True)[:TOP_X])


@wallaroo.decoder(header_length=4, length_fmt=">I")
def decoder(bs):
    return bs.decode("utf-8")


@wallaroo.partition
def extract_hashtag_key(data):
    if data[0] >= "a" and data[0] <= "z":
        return data[0]
    else:
        return "!"


@wallaroo.encoder
def encoder(data):
    top_first = sorted(data.items(), key=lambda (k, v): v, reverse=True)

    top_tags = []
    top_counts = []

    for (tag, count) in top_first:
        top_tags.append(str(tag.encode("utf-8")))
        top_counts.append(count)

    request_data = {'label': str(top_tags), 'data': str(top_counts)}
    # return the data to TCP connection along with a special separator
    return str(request_data) + ';;\n'
