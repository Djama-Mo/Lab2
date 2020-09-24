from lexer import data_check
from parser import Parser
from syntax_tree import Tree
from errors import *
import sys
import copy
from robot import *
import re
import random


class Variable(object):
    def __init__(self, v_type, v_value, v_name=''):
        self.type = v_type
        self.name = v_name
        if v_value == 'true':
            self.value = True
        elif v_value == 'false':
            self.value = False
        else:
            self.value = v_value

    def __repr__(self):
        return f'{self.type} {self.name} = {self.value}'


class Arr_variable(object):
    def __init__(self, v_type, v_name, v_scope, v_array=None):
        self.type = v_type
        self.name = v_name
        self.scope = v_scope
        # if v_array is None:
        #     self.array = []
        #     nuls = 0
        #     for i in list(v_scope.values()):
        #         nuls += i
        #     for j in range(nuls):
        #         self.array.append(0)
        # else:
        self.array = v_array

    def __repr__(self):
        scopes = list(self.scope.values())
        # if len(self.scope) == 1:
        return f'{self.type} {self.name}{scopes} = {self.array}'
        # else:
        #     arr = f''
        #     for i in self.array:
        #         arr += f'{i}'
        #     return f'{self.type} {self.name}{scopes} = ({arr})'


class TypeConverter(object):
    def __init__(self):
        pass

    def converse(self, v_type, var):
        if v_type.value == var.type:
            return var
        elif v_type.value == 'logic':
            if var.type == 'digit':
                return self.digit_to_logic(var)
        elif v_type.value == 'digit':
            if var.type == 'logic':
                return self.logic_to_digit(var)
        elif v_type.find(var.type) != -1:
            return Variable(v_type, var.value)

    @staticmethod
    def digit_to_logic(var):
        if var.value == 0:
            return Variable('logic', False, var.name)
        else:
            return Variable('logic', True, var.name)

    @staticmethod
    def logic_to_digit(var):
        if var.value:
            return Variable('digit', 1, var.name)
        else:
            return Variable('digit', 0, var.name)


class Interpreter(object):
    def __init__(self, program=None, robot = None):
        self.parser = Parser()
        self.error = Error_handler()
        self.converse = TypeConverter()
        self.scope = 0
        self.symbol_table = [dict()]
        self.tree = None
        self.err_types = {
                        'UnexpectedError': 0,
                        'TypeError': 1,
                        'ValueError': 2,
                        'StartPointError': 3,
                        'IndexError': 4,
                        'RedeclarationError': 5,
                        'ConverseError': 6,
                        'NotArrayError': 7,
                        'UndeclaredVariableError': 8,
                        'WrongParameterError': 9,
                        'ArrayDeclarationError': 10,
                        'ArrayToVariableError': 11,
                        'UndeclaredFunctionError': 12,
                        'CallPathfinderError': 13}
        self.funcs = None
        self.correct = None
        self.program = program
        self.robot = robot
        self.steps = 0
        self.exit = False

    def interpreter(self):
        self.tree, self.funcs, self.correct = self.parser.parse(self.program)
        if self.correct:
            if 'pathfinder' not in self.funcs.keys():
                self.error.call(self.err_types['StartPointError'])
                return
            try:
                self.interpreter_node(self.funcs['pathfinder'].children['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RecursionError: function calls itself too many times\n')
                sys.stderr.write("========= Program has finished with fatal error =========\n")
                return False
        else:
            sys.stderr.write(f'Incorrect input file\n')

    def interpreter_node(self, node):
        if node is None:
            return
        elif node.type == 'NL':
            pass
        elif node.type == 'EOS':
            pass
        elif node.type == 'error':
            self.error.call(self.err_types['UnexpectedError'], node)
        elif node.type == 'program':
            self.interpreter_node(node.children)
        elif node.type == 'group_stat':
            self.interpreter_node(node.children[1])
        elif node.type == 'statement list':
            self.interpreter_node(node.children[0])
            self.interpreter_node(node.children[1])
        elif node.type == 'declaration':
            decl_type = node.children[0]
            decl_child = node.children[1]
            try:
                if decl_child.type == 'var_list':
                    while decl_child.type == 'var_list':
                        self.declaration(decl_type, decl_child.children[0])
                        if decl_child.children[1].type != 'var_list':
                            self.declaration(decl_type, decl_child.children[1])
                        decl_child = decl_child.children[1]
                else:
                    self.declaration(decl_type, decl_child)
            except RedeclarationError:
                self.error.call(self.err_types['RedeclarationError'], node)
            except TypeError:
                self.error.call(self.err_types['TypeError'], node)
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except ArrayDeclarationError:
                self.error.call(self.err_types['ArrayDeclarationError'], node)
            except WrongParameterError:
                self.error.call(self.err_types['WrongParameterError'], node)
            except NameError:
                self.error.call(self.err_types['NameError'], node)
        elif node.type == 'assignment':
            try:
                self.assign_variable(node)
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
            except TypeError:
                self.error.call(self.err_types['TypeError'], node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except UndeclaredVariableError:
                self.error.call(self.err_types['UndeclaredVariableError'], node)
            except NotArrayError:
                self.error.call(self.err_types['NotArrayError'], node)
            except WrongParameterError:
                self.error.call(self.err_types['WrongParameterError'], node)
            except NameError:
                self.error.call(self.err_types['NameError'], node)
            except ArrayToVariableError:
                self.error.call(self.err_types['ArrayToVariableError'], node)
        elif node.type == 'var_list':
            for var in node.children:
                self.interpreter_node(var)
        elif node.type == 'variable':
            try:
                return self._variable(node)
            except UndeclaredVariableError:
                self.error.call(self.err_types['UndeclaredVariableError'], node)
            except NameError:
                self.error.call(self.err_types['NameError'], node)
        elif node.type == 'array variable':
            try:
                var_name = self.symbol_table[self.scope][node.value]
                if node.children.type == 'indexing':
                    index = self.symbol_table[self.scope][node.children.children]
                    result = Variable(var_name.type, var_name.array[index.value - 1])
                    return result
                else:
                    return None
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
            except UndeclaredVariableError:
                self.error.call(self.err_types['UndeclaredVariableError'], node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except NotArrayError:
                self.error.call(self.err_types['NotArrayError'], node)
        elif node.type == 'digit':
            return Variable('digit', node.value)
        elif node.type == 'logic':
            return Variable('logic', node.value)
        elif node.type == 'EOS' or node.type == 'bracket':
            return node.value
        elif node.type == 'size':
            try:
                return Variable('digit', self._size(node))
            except WrongParameterError:
                self.error.call(self.err_types['WrongParameterError'], node)
        elif node.type == 'type change':
            try:
                name = self.get_name(node.children)
                if name is None:
                    raise UndeclaredVariableError
                var = self.symbol_table[self.scope][name]
                self.symbol_table[self.scope][name] = self.converse.converse(node.value[1], var)
            except TypeError:
                self.error.call(self.err_types['TypeError'], node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
        elif node.type == 'resize':
            try:
                self._resize(node)
            except WrongParameterError:
                self.error.call(self.err_types['WrongParameterError'], node)
            except NotArrayError:
                self.error.call(self.err_types['NotArrayError'], node)
        elif node.type == 'calculation':
            try:
                return self._calculation(node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
        elif node.type == 'expression':
            return self.interpreter_node(node.children[1])
        elif node.type == 'if_then':
            try:
                self.func_check_then(node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
        elif node.type == 'if_th_el':
            try:
                self.func_check_th_oth(node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
        elif node.type == 'comparison':
            try:
                return self._comparison(node)
            except UnexpectedError:
                self.error.call(self.err_types['UnexpectedError'], node)
        elif node.type == 'for':
            try:
                self.op_for(node)
            except ConverseError:
                self.error.call(self.err_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.err_types['IndexError'], node)
        elif node.type == 'perform':
            try:
                return self.call_function(node)
            except RecursionError:
                raise RecursionError from None
            except UndeclaredFunctionError:
                self.error.call(self.err_types['UndeclaredFunctionError'], node)
            except CallPathfinderError:
                self.error.call(self.err_types['CallPathfinderError'], node)
            except WrongParameterError:
                self.error.call(self.err_types['WrongParameterError'], node)

        elif node.type == 'command':
            if self.robot is None:
                self.error.call(self.err_types['RobotError'], node)
                self.correct = False
                return 0
            else:
                if self.robot.exit():
                    self.exit = True
                    return Variable('logic', 'true')
                self.steps += 1
                if node.value == 'surroundings':
                    name = self.get_name(node.children)
                    if name is None:
                        raise UndeclaredVariableError
                    var = self.symbol_table[self.scope][name]
                    print(self.robot.surroundings(var))
                if node.value == 'move':
                    name = self.get_name(node.children)
                    if name is None:
                        raise UndeclaredVariableError
                    var = self.symbol_table[self.scope][name]
                    if self.robot.move(var.value) == True:
                        print('I MOVED ))')
                if node.value == 'rotate':
                    name = self.get_name(node.children)
                    if name is None:
                        raise UndeclaredVariableError
                    var = self.symbol_table[self.scope][name]
                    self.robot.rotate(var.value)
                self.robot.show()
                return True

        else:
            print('Not all nodes checked')

    def get_name(self, name):  # Done
        res = None
        length = len(name)
        for var in sorted(self.symbol_table[self.scope].keys()):
            if var[:length] == name:
                res = var
                if len(var) == len(name):
                    return res
        return res

    def _calculation(self, node):  # Done
        if isinstance(node.children, list):
            first_term = copy.deepcopy(self.interpreter_node(node.children[0]))
            second_term = copy.deepcopy(self.interpreter_node(node.children[1]))
            if isinstance(first_term, Arr_variable) or isinstance(second_term, Arr_variable):
                raise ConverseError
            if node.value == '+':
                return self._add(first_term, second_term)
            elif node.value == '-':
                return self._sub(first_term, second_term)
            elif node.value == '&&':
                return self._and(first_term, second_term)
        elif isinstance(node.children, Tree):
            first_term = copy.deepcopy(self.interpreter_node(node.children))
            if isinstance(first_term, Arr_variable):
                if node.value == 'most':
                    return self._most(first_term)
                else:
                    raise ConverseError
            if node.value == '!':
                return self._not(first_term)

    def _comparison(self, node):  # Done
        result = self.interpreter_node(node.children)
        if isinstance(result, Arr_variable):
            arr = []
            for i in result.array:
                _node = copy.deepcopy(node)
                _node.children = Variable(result.type, i)
                tmp = self._comparison(_node)
                arr.append(tmp.value)
            arr = Arr_variable('logic', 'tmp_result', result.scope, arr)
            return arr
        elif node.value == 'lt':
            return self._first_less(result)
        elif node.value == 'gt':
            return self._first_greater(result)
        elif node.value == 'lte':
            return self._first_less_eq(result)
        elif node.value == 'gte':
            return self._first_greater_eq(result)
        elif node.value == 'eq':
            return self._eq_comp(result)

    def _add(self, first, second):  # Done
        if first.type == 'logic':
            if second.type == 'digit':
                self.converse.digit_to_logic(second)
        if first.type == 'digit':
            if second.type == 'logic':
                self.converse.logic_to_digit(second)
        return Variable('digit', first.value + second.value)

    def _sub(self, first, second):  # Done
        if first.type == 'logic':
            if second.type == 'digit':
                second = self.converse.digit_to_logic(second)
        if first.type == 'digit':
            if second.type == 'logic':
                second = self.converse.logic_to_digit(second)
        return Variable('digit', first.value - second.value)

    def _first_less(self, first):  # Done
        if first.type == 'logic':
            first = self.converse.logic_to_digit(first)
        if first.value < 0:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _first_greater(self, first):  # Done
        if first.type == 'logic':
            first = self.converse.logic_to_digit(first)
        if first.value > 0:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _first_less_eq(self, first):  # Done
        if first.type == 'logic':
            first = self.converse.logic_to_digit(first)
        if first.value <= 0:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _first_greater_eq(self, first):  # Done
        if first.type == 'logic':
            first = self.converse.logic_to_digit(first)
        elif first.value >= 0:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _eq_comp(self, first):  # Done
        if first.type == 'logic':
            first = self.converse.logic_to_digit(first)
        if first.value == 0:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _and(self, first, second):
        if first.type != 'logic':
            first = self.converse.digit_to_logic(first)
        if second.type != 'logic':
            second = self.converse.digit_to_logic(second)
        if first.value == True and second.value == True:
            return Variable('logic', 'true')
        elif first.value == True and second.value == False:
            return Variable('logic', 'false')
        elif first.value == False and second.value == True:
            return Variable('logic', 'false')
        elif first.value == False and second.value == False:
            return Variable('logic', 'false')

    def _not(self, first):
        if first.type != 'logic':
            first = self.converse.digit_to_logic(first)
        if first.value:
            return Variable('logic', 'false', first.name)
        elif first.value == False:
            return Variable('logic', 'true', first.name)

    def _most(self, arr):
        length = arr.scope[1]
        count = 0
        for el in arr.array:
            if el:
                count += 1
        if count > length / 2:
            return Variable('logic', 'true')
        else:
            return Variable('logic', 'false')

    def _resize(self, node):
        try:
            if node.value == 0:
                raise NotArrayError
            name = self.get_name(node.children)
            if name is None:
                raise UndeclaredVariableError
            var = self.symbol_table[self.scope][name]
            if isinstance(var, Variable):
                raise NotArrayError
            if var.scope[1] < node.value:
                i = 0
                while i != node.value - var.scope[1]:
                    var.array.append(0)
                    i += 1
            elif var.scope[1] > node.value:
                sz = var.scope[1] - node.value
                while sz != 0:
                    var.array.pop()
                    sz -= 1
            else:
                raise WrongParameterError
            var.scope[1] = node.value
            return var
        except WrongParameterError:
            return

    def _variable(self, node):  # Done
        var = self.get_name(node.value)
        if var is None:
            raise UndeclaredVariableError
        else:
            return self.symbol_table[self.scope][var]

    def _arr_variable(self, node):
        name = self.get_name(node.value)
        if name is None:
            raise UndeclaredVariableError
        var = self.symbol_table[self.scope][name]
        if isinstance(var, Variable):
            raise NotArrayError
        i = self.get_el_index(node, var)
        type_var = var.type
        new_var = Variable(type_var, self.symbol_table[self.scope][name].array[i])
        return new_var

    def get_el_index(self, node, var):  # Done
        ind = []
        if isinstance(node.children.children, Tree):
            ind = self.get_var_indexes(node, ind)
        else:
            if type(node.children.children) == str:
                index = self.symbol_table[self.scope][node.children.children]
                if isinstance(index, Variable):
                    if index.type == 'digit':
                        ind.append(index.value)
                else:
                    raise IndexError
        if isinstance(var, Variable):
            raise NotArrayError
        if len(ind) == 1:
            return ind[0]
        else:
            return ind

    def get_var_indexes(self, node, ind):  # Done
        if isinstance(node.children, list) and len(node.children) > 0:
            index = self.interpreter_node(node.children[0])
            if isinstance(index, Arr_variable):
                raise IndexError
            if index.value <= 0 and node.type != 'matr':
                raise IndexError
            ind.append(index.value)
            ind = self.get_var_indexes(node.children[1], ind)
        elif node.type != 'indexing' and node.type != 'array variable':
            index = self.interpreter_node(node)
            if isinstance(index, Arr_variable):
                raise IndexError
            if index.value <= 0 and len(ind) == 0:
                raise IndexError
            ind.append(index.value)
        else:
            ind = self.get_var_indexes(node.children, ind)
        return ind

    def _size(self, node):
        try:
            var = self.symbol_table[self.scope][node.children]
            if isinstance(var, Arr_variable):
                raise WrongParameterError
            if isinstance(var, Variable):
                tip = var.type
                return self.size_type(tip)
        except Exception:
            if node.children.type == 'type':
                tip = node.children.value
                return self.size_type(tip)
            else:
                raise WrongParameterError

    def size_type(self, type):
        if type == 'digit':
            return 8
        else:
            return 1

    def _arr_scope(self, node, i):
        if node.type == 'type':
            return i
        else:
            return self._arr_scope(node.children, i + 1)

    def _index_scope(self, node, i):
        if isinstance(node, list):
            return self._index_scope(node[1], i + 1)
        else:
            return i

    def _arr_type(self, node):
        if node.type == 'type':
            return node.value
        else:
            return self._arr_type(node.children)

    def get_arr_values(self, val, type, size):
        arr = []
        i = 0
        value = self.interpreter_node(val)
        if value.type != type:
            raise TypeError
        if isinstance(size, int):
            while i != size:
                arr.append(value.value)
                i += 1
        elif isinstance(size, list):
            for i in size:
                arr.append(self.get_arr_values(val, type, i))
        return arr

    def assign_variable(self, node):
        var = node.children[0]
        if var.type == 'variable':
            name = self.get_name(var.value)
            if name is None:
                raise UndeclaredVariableError
            expr = self.interpreter_node(node.children[1])
            variab = self.symbol_table[self.scope][name]
            if expr is None:
                return
            if expr.type != variab.type:
                raise TypeError
            if self.robot is None:
                if isinstance(variab, Arr_variable) and isinstance(expr, Arr_variable):
                    if variab.scope != expr.scope:
                        raise IndexError
                    self.symbol_table[self.scope][name].array = expr.array
                elif isinstance(variab, Variable) and isinstance(expr, Variable):
                    self.symbol_table[self.scope][name].value = expr.value
                else:
                    raise ArrayToVariableError
            else:
                if isinstance(variab, Arr_variable):
                    self.symbol_table[self.scope][name].array = expr.array
                else:
                    self.symbol_table[self.scope][name].value = expr.value
        elif var.type == 'array variable':
            name = self.get_name(var.value)
            if name is None:
                self.error.call(self.err_types['UndeclaredVariableError'], node)
                raise UndeclaredVariableError
            expr = self.interpreter_node(node.children[1])
            if expr is not None:
                var_class = self.symbol_table[self.scope][name]
                if expr.type != var_class.type:
                    raise TypeError
                ind = self.get_el_index(var, var_class)
                if isinstance(ind, list):
                    j = 0
                    for i in ind:
                        if i == 0:
                            j += 1
                            continue
                        if i > var_class.scope[i]:
                            raise IndexError
                        self.symbol_table[self.scope][var_class.name].array[j][i - 1] = expr.value
                        j += 1
                else:
                    if ind > var_class.scope[1]:
                        raise IndexError
                    self.symbol_table[self.scope][var_class.name].array[ind - 1] = expr.value

    def func_check_then(self, node):  # Done
        condition = self.interpreter_node(node.children['condition'])
        if condition.value:
            self.interpreter_node(node.children['body'])

    def func_check_th_oth(self, node):  # Done
        condition = self.interpreter_node(node.children['condition'])
        if condition.value:
            self.interpreter_node(node.children['body_1'])
        else:
            self.interpreter_node(node.children['body_2'])

    def op_for(self, node):  # Done
        variable = node.children['start'].value
        flag = False
        if variable not in self.symbol_table[self.scope].keys():
            flag = True
        from_ = self.interpreter_node(node.children['start'])
        to_ = self.interpreter_node(node.children['stop'])
        step_ = self.interpreter_node(node.children['step'])
        try:
            self.symbol_table[self.scope][variable] = Variable('digit', from_.value, from_.name)
            while self.symbol_table[self.scope][variable].value != to_.value:
                self.interpreter_node(node.children['body'])
                self.symbol_table[self.scope][variable].value += step_.value
            if flag:
                del self.symbol_table[self.scope][variable]
        except ConverseError:
            raise ConverseError
        except TypeError:
            raise TypeError
        except ValueError:
            raise ValueError
        except IndexError:
            raise IndexError
        except UndeclaredVariableError:
            raise UndeclaredVariableError

    def declaration(self, type, node):
        try:
            _type = node.children[0].type
        except Exception:
            _type = ''
        if _type == 'var_list':
            for child in node.children[0].children:
                self.declaration(node.children[1], child)
            return
        if _type == 'array variable':
            arr_scope = self._arr_scope(type, 1)  # counting vector of
            arr_type = self._arr_type(type)
            if _type == 'array variable':
                var_ch = node.children[0]
                expr_ch = node.children[1]
                arr_name = var_ch.value
                if arr_name in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if var_ch.type == 'array variable':
                    arr_indexes = {}
                    for i in range(arr_scope):
                        arr_indexes[i + 1] = -1
                    if var_ch.children.children.type == 'digit':
                        arr_size = var_ch.children.children.value
                    elif var_ch.children.children.type == 'matr':
                        arr_size = self.matr_size(var_ch.children.children)
                        arr_scope = len(arr_size)
                        # arr_size = []
                        # for sz in var_ch.children.children.children:
                        #     if sz.type == 'digit':
                        #         arr_size.append(sz.value)
                        #     elif sz.type == 'matr':
                    else:
                        raise ArrayDeclarationError
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_size)
                    if isinstance(arr_size, int) and len(arr_values) != arr_size:
                        raise ArrayDeclarationError
                    for i in range(arr_scope):
                        if isinstance(arr_size, int):
                            arr_indexes[i + 1] = arr_size
                        elif isinstance(arr_size, list):
                            arr_indexes[i + 1] = arr_size[i]
                    var = Arr_variable(arr_type, arr_name, arr_indexes, arr_values)
                    if var is not None:
                        self.symbol_table[self.scope][arr_name] = var

        else:
            if node.type == 'variable':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                else:
                    if type.type == 'variable':
                        type = self.symbol_table[self.scope][type.value]
                    self.symbol_table[self.scope][node.value] = Variable(type.type, type.value, node.value)
            elif node.type == 'digit':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                else:
                    self.symbol_table[self.scope][node.value] = Variable(type.value, node.value)
            elif node.type == 'arr variable':
                raise RedeclarationError
            elif node.type == 'assignment array':
                raise ArrayDeclarationError
            else:  # if node.type == 'assignment'
                var = node.children[0].value
                if var in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if node.children[0].type != 'array variable':
                    expr = self.interpreter_node(node.children[1])
                    if expr is not None:
                        expr = self.converse.converse(type, expr)
                        self.symbol_table[self.scope][var] = Variable(type.value, expr.value, var)
                else:
                    raise RedeclarationError

    def matr_size(self, node):
        arr_size = []
        for sz in node.children:
            if sz.type == 'digit':
                arr_size.append(sz.value)
            elif sz.type == 'matr':
                arr_size += self.matr_size(sz)
            else:
                raise ArrayDeclarationError
        return arr_size

    def set_param(self, input, func):
        if isinstance(input, Arr_variable) and (func.type == 'array variable' or func.type == 'variable'):
            func = Arr_variable(input.type, func.value, input.scope, input.array)
            return func
        elif isinstance(input, Variable) and func.type == 'variable':
            func = Variable(input.type, input.value, func.value)
            return func
        else:
            raise WrongParameterError

    def call_function(self, node):
        name = node.value
        if self.scope > 100:
            self.scope = -1
            raise RecursionError
        if name not in self.funcs.keys():
            raise UndeclaredFunctionError
        if name == 'pathfinder':
            raise CallPathfinderError
        param = node.children
        input_param = []
        change_value = []
        try:
            while param is not None:
                if param.type == 'var_list':
                    for par in param.children:
                        input_param.append(self.interpreter_node(par))
                else:
                    input_param.append(self.interpreter_node(param))
                break
            for i in range(len(change_value)):
                change_value[i] = -change_value[i] - 1
        except NotArrayError:
            self.error.call(self.err_types['NotArrayError'], node)
        except IndexError:
            self.error.call(self.err_types['IndexError'], node)
        self.scope += 1
        self.symbol_table.append(dict())
        func_param = []
        node_param = self.funcs[name].children['parameters']
        if node_param.type == 'var_list':
            for par in node_param.children:
                func_param.append(par)
        else:
            func_param.append(node_param)
        if len(func_param) != len(input_param):
            raise WrongParameterError
        for i in range(len(input_param)):
            func_param[i] = self.set_param(input_param[i], func_param[i])
        for par in func_param:
            self.symbol_table[self.scope][par.name] = par
        self.interpreter_node(self.funcs[name].children['body'])
        result = copy.deepcopy(self.interpreter_node(self.funcs[name].children['return']))
        self.symbol_table.pop()
        self.scope -= 1

        return result


def create_robot(descriptor):
    with open(descriptor) as file:
        text = file.read()
    text = text.split('\n')
    robot_info = text.pop(0).split(' ')
    map_size = text.pop(0).split(' ')
    x = int(robot_info[0])
    y = int(robot_info[1])
    mapp = [0] * int(map_size[0])
    # text = list(reversed(text))
    # text.pop(0)
    for i in range(int(map_size[0])):
        mapp[i] = [0]*int(map_size[1])
    for i in range(int(map_size[0])):
        for j in range(int(map_size[1])):
            mapp[i][j] = Cell("EMPTY")
    pos = 0
    while len(text) > 1:
        line = list(text.pop(0))
        line = [Cell(cells[i]) for i in line]
        mapp[pos] = line
        pos += 1
    return Robot(x, y, mapp)


if __name__ == '__main__':
    prog_names = ['factorial.txt', 'quicksort.txt', 'factorial_recursion.txt', 'chprog.txt', 'erorrs.txt']
    algorithm = 'alg.txt'
    maps = 'map_simple.txt'
    n = 0
    while 3 > n > -1:
        print('\n==========\n1 - Algorithm \n2 - Robot \n3 - Exit\n==========\n')
        n = int(input())
        if n == 1:
            print('1 - Factorial\n2 - Quicksort\n3 - Recursion Factorial\n4 - Check\n5 - Errors')
            num = int(input())
            if num < 1 or num > 5:
                print('Wrong number\n')
            else:
                f = open(prog_names[num-1])
                prog = f.read()
                # lines_count = len(re.findall(r"[\n']+?", prog))
                # redline = int(lines_count / 7)
                # psix = random.randint(0, redline)
                # check = re.findall(r'please', prog)
                # if len(check) >= psix:
                #     a = True
                i = Interpreter(program=prog)
                res = i.interpreter()
                if res:
                    print('Symbol table:')
                    for symbol_table in i.symbol_table:
                        for k, v in symbol_table.items():
                            print(v)
                else:
                    print('Something wrong')
                f.close()
        elif n == 2:
            print('1 - Empty map \n2 - Simple map \n3 - Big map \n4 - No exit')
            m = int(input())
            if m < 1 or m > 4:
                print('Wrong number\n')
            else:
                robot = create_robot(maps)
                f = open(algorithm)
                prog = f.read().lower()
                f.close()
                i = Interpreter(program=prog, robot=robot)
                i.robot.show()
                res = i.interpreter()
                if res:
                    print('Symbol table:')
                    for symbol_table in i.symbol_table:
                        for k, v in symbol_table.items():
                            print(v)
                else:
                    print('Something wrong')
                if i.exit:
                    print(f'Robot found exit in {i.steps} steps\n')
                else:
                    print('Robot can\'t find exit\n')
                i.robot.show()
            print(i.robot)
        elif n == 0:
            prog = data_check
            i = Interpreter(program=prog)
            res = i.interpreter()
            if res:
                print('Symbol table:')
                for symbol_table in i.symbol_table:
                    for k, v in symbol_table.items():
                        print(v)
            else:
                print('Something wrong')
        else:
            print('Ok, exit')

