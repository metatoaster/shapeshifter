from os.path import join
from shapeshifter.parser import Parser
p = Parser(join('data', 'derp.txt'))
p.parse()

from pprint import pprint as pp

pp(p)
