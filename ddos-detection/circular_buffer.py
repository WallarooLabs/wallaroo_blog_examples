class CircularBuffer(object):
    def __init__(self, size):
        self.index = 0
        self.size = size
        self._data = []

    def append(self, value):
        if len(self._data) == self.size:
            self._data[self.index] = value
        else:
            self._data.append(value)
        self.index = (self.index + 1) % self.size

    def __getitem__(self, key):
        if key >= self.size or key < -self.size:
            raise IndexError('CircularBuffer index out of range')
        if len(self._data) == self.size:
            return(self._data[(key + self.index) % self.size])
        else:
            return(self._data[key])

    def __repr__(self):
        return self.get().__repr__()

    def __len__(self):
        return len(self._data)

    def get(self):
        return self._data[self.index:] + self._data[:self.index]
