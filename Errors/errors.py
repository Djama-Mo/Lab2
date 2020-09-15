import sys
from syntax_tree import Tree


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
                      'NotArrayError',
                      'UndeclaredVariableError',
                      'WrongParameterError',
                      'ArrayDeclarationError',
                      'ArrayToVariableError',
                      'UndeclaredFunctionError',
                      'CallPathfinderError']

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
            sys.stderr.write(f'Redeclaration of a variable "{self.node.children[1].children[0].value}" at line '
                             f'{self.node.children[1].children[0].lineno}\n')
        elif self.type == 6:
            sys.stderr.write(f"Can't converse types at line {self.node.lineno}\n")
        elif self.type == 7:
            sys.stderr.write(
                f'Trying to get index from not array variable "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 8:
            if node.type == 'variable' or node.type == 'arr variable':
                sys.stderr.write(f'Using undeclared variable "{self.node.value}" at line {self.node.lineno}\n')
            else:
                sys.stderr.write(
                    f'Using undeclared variable "{self.node.children[0].value}" at line {self.node.children[0].lineno}\n')
        elif self.type == 9:
            sys.stderr.write(f'Wrong parameters in function "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 10:
            if node.children[1].type == 'variable' or node.children[1].type == 'arr variable':
                sys.stderr.write(
                    f'Wrong declaration of array "{self.node.children[1].value}" at line {self.node.children[1].lineno}\n')
            else:
                sys.stderr.write(
                    f'Wrong declaration of array "{self.node.children[1].children[0].value}" at line {self.node.children[1].children[0].lineno}\n')
        elif self.type == 11:
            sys.stderr.write(f'Can\'t assign variable to array variable or vice versa at line {self.node.lineno}\n')
        elif self.type == 12:
            sys.stderr.write(f'Calling undeclared function "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 13:
            sys.stderr.write(f'Calling PATHFINDER function at line {self.node.lineno}\n')


class UnexpectedError(Exception):
    pass


class TypeError(Exception):
    pass


class ValueError(Exception):
    pass


class StartPointError(Exception):
    pass


class IndexError(Exception):
    pass


class RedeclarationError(Exception):
    pass


class ConverseError(Exception):
    pass


class NotArrayError(Exception):
    pass


class UndeclaredVariableError(Exception):
    pass


class WrongParameterError(Exception):
    pass


class ArrayDeclarationError(Exception):
    pass


class ArrayToVariableError(Exception):
    pass


class UndeclaredFunctionError(Exception):
    pass


class CallPathfinderError(Exception):
    pass
