"""\
Customized data types
"""

from log import logger


class ParserDict(dict):
    
    terminate = ('ENDMARKER', 'ENDQUEUE',)

    def __init__(self):
        self.ended = False
        self.header = ''

    def parse(self, line):
        # XXX account for the ENDMARKER, pop this onto a next dict
        # XXX list of dicts?
        if not line:
            return
        if line[0] == '#':
            self.header = line[1:]
            if self.header in self.terminate:
                self.ended = True
            return
        if line:
            self[self.header] = line


class ParserList(list):

    def __init__(self, filename):
        self.filename = filename

    def _getlines(self):
        f = open(self.filename)
        self.lines = f.readlines()
        f.close()

    def parse(self):
        self._getlines()
        header = ''

        current = ParserDict()
        for line in self.lines:
            line = line.strip('\r\n')
            current.parse(line)
            if current.ended:
                if current:
                    self.append(current)
                current = ParserDict()

        logger.info('Parsed %d entry(s) from "%s"', len(self), self.filename)
