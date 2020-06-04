import sys
from Lab2.Syntax_tree.syntax_tree import Tree


class Error_handler(object):
    def __init__(self):
        self.type = None
        self.node = None
        self.types = ['UnexpectedError',
                      'TypeError',
                      'ValueError']

    def call(self, err_type, node: Tree = None):
        self.type = err_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(err_type)]}: ')
        if self.type == 0:
            sys.stderr.write(f'Incorrect syntax at {self.node.children[0].lineno} line \n')
            return
        elif self.type == 1:
            sys.stderr.write(f'Incompatible types at line {self.node.lineno}\n')
        elif self.type == 2:
            sys.stderr.write(f'Bad value for a variable {self.node.value} at line {self.node.lineno}\n')


class UnexpectedError(object, Exception):
    pass


class TypeError(object, Exception):
    pass


class ValueError(object, Exception):
    pass
