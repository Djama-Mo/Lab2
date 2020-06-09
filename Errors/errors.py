import sys
from Lab2.Syntax_tree.syntax_tree import Tree


class Error_handler(object):
    def __init__(self):
        self.type = None
        self.node = None
        self.types = ['UnexpectedError',
                      'TypeError',
                      'ValueError',
                      'StartPointError',
                      'IndexError',
                      'RedeclarationError',
                      'ConverseError',
                      'NotArrayError']

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
        elif self.type == 3:
            sys.stderr.write(f'No PATHFINDER function in program\n')
        elif self.type == 4:
            sys.stderr.write(f'Index is wrong at line {self.node.lineno}\n')
        elif self.type == 5:
            sys.stderr.write(f'Redeclaration of a variable "{self.node.child[1].child[0].value}" at line '
                             f'{self.node.child[1].child[0].lineno}\n')
        elif self.type == 6:
            sys.stderr.write(f"Can't converse types at line {self.node.lineno}\n")
        elif self.type == 7:
            sys.stderr.write(
                f'Trying to get index from not array variable "{self.node.value}" at line {self.node.lineno}\n')


class UnexpectedError(object, Exception):
    pass


class TypeError(object, Exception):
    pass


class ValueError(object, Exception):
    pass


class StartPointError(object, Exception):
    pass


class IndexError(object, Exception):
    pass


class RedeclarationError(Exception):
    pass


class ConverseError(Exception):
    pass

class NotArrayError(Exception):
    pass
