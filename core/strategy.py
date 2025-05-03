class Strategy:
    def init(self, symbol, data):
        pass

    def tick(self, symbol, data):
        pass

    def _init(self, data):
        for symbol, data in data.items():
            self.tick(symbol, data)

    def _tick(self, row_data):
        for symbol, data in row_data.items():
            self.tick(symbol, data)
