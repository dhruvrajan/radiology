class Indexer(object):
    def __init__(self):
        self.objs_to_ints = {}
        self.ints_to_objs = {}

    def __repr__(self):
        return "Indexer(" + str([str(self.get_object(i)) for i in range(0, len(self))]) + ")"

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.objs_to_ints)

    def get_object(self, index):
        if (index not in self.ints_to_objs):
            return None
        else:
            return self.ints_to_objs[index]

    def contains(self, object):
        return self.index_of(object) != -1

    # Returns -1 if the object isn't present, index otherwise
    def index_of(self, object):
        if (object not in self.objs_to_ints):
            return -1
        else:
            return self.objs_to_ints[object]

    # Adds the object to the index if it isn't present, always returns a nonnegative index
    def get_index(self, object, add=True):
        if not add:
            return self.index_of(object)
        if (object not in self.objs_to_ints):
            new_idx = len(self.objs_to_ints)
            self.objs_to_ints[object] = new_idx
            self.ints_to_objs[new_idx] = object
        return self.objs_to_ints[object]

    def objects(self):
        for i in range(len(self.ints_to_objs)):
            yield self.ints_to_objs[i]


def indexer_from_values(values, in_order=False):
    indexer = Indexer()
    for value in values:
        indexer.get_index(value)

    if in_order:
        for i in range(len(values)):
            assert indexer.index_of(values[i]) == i

    return indexer
