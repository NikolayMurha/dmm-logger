
class DataChain:
    def __init__(self, filters=None):
        self.filters = filters if filters is not None else []
        self.callbacks = []

    def add_filter(self, filter_func):
        self.filters.append(filter_func)

    def apply(self, data, *args):
        for filter in self.filters:
            data = filter.filter_list(data)
        if self.callbacks:
            for callback in self.callbacks:
                callback(data)
        return data

    def clear(self):
        self.filters.clear()
        self.callbacks.clear()

    def on_complete(self, callback):
        self.callbacks.append(callback)
