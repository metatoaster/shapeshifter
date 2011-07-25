class Parser(object):

    def __init__(self, filename):
        self.filename = filename
        self.structure = {}
        self._open()

    def _open(self):
        f = open(self.filename)
        self.lines = f.readlines()
        f.close()

    def parse(self):
        header = ''
        for line in self.lines:
            line = line.strip('\r\n')
            if not line:
                continue
            if line[0] == '#':
                header = line[1:]
                continue
            self.structure[header] = line

