class Parser(dict):

    def __init__(self, filename):
        self.filename = filename

    def _getlines(self):
        f = open(self.filename)
        self.lines = f.readlines()
        f.close()

    def parse(self):
        self._getlines()
        header = ''
        for line in self.lines:
            line = line.strip('\r\n')
            if not line:
                continue
            if line[0] == '#':
                header = line[1:]
                continue
            self[header] = line
