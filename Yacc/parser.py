import sys
import ply.yacc as yacc
from lexer import Lexer
from syntax_tree import Tree
from ply.lex import LexError


def main():
    with open('file.txt', 'r') as fh:
        data = fh.read()
        parser = Parser()
        tree = parser.parser.parse(data, debug=True)
        tree.print()


class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self, optimize=1, debug=False, write_tables=False)
        self.functions = dict()
        self.correct = True

    def parse(self, s):
        try:
            res = self.parser.parse(s)
            return res, self.functions, self.correct
        except LexError:
            sys.stderr.write(f'>>>>>Illegal token {s}\n')

    def p_program(self, p):
        """program : stat_list"""
        p[0] = Tree('program', children=p[1], lineno=p.lineno(1))

    def p_stat_group(self, p):
        """stat_group : L_FIGBRACKET NL stat_list R_FIGBRACKET NL
                    | statement"""
        if p[1] == '{':
            p[1] = Tree('border', value=p[1], lineno=p.lineno(1))
            p[4] = Tree('border', value=p[4], lineno=p.lineno(1))
            p[0] = Tree('group_stat', children=[p[1], p[3], p[4]], lineno=p.lineno(2) + 1)
        else:
            p[0] = p[1]

    def p_stat_list(self, p):
        """stat_list : stat_list statement
                    | statement
                    | NL"""
        if len(p) == 3:
            p[0] = Tree('statement list', p[2], children=[p[1], p[2]], lineno=p.lineno(1))
        else:
            if p[0] != '\n':
                p[0] = p[1]
            else:
                p[0] = Tree('NL', lineno=p.lineno(1))

    def p_statement(self, p):
        """statement : declaration ENDSTR NL
                    | assignment ENDSTR NL
                    | size ENDSTR NL
                    | to ENDSTR NL
                    | resize ENDSTR NL
                    | comp_br ENDSTR NL
                    | for
                    | check
                    | routing
                    | perform ENDSTR NL
                    | command ENDSTR NL
                    | ENDSTR NL"""
        if len(p) == 4 or len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Tree('EOS', lineno=p.lineno(1))

    def p_declaration(self, p):
        """declaration : type var_list EQQ expr"""
        if len(p) == 5:
            p[0] = Tree('declaration', children=[p[1], Tree('assign', children=[p[2], p[4]])], lineno=p.lineno(1))

    def p_var_list(self, p):
        """var_list : variable
                    | var_list COMMA var_list"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Tree('var_list', children=[p[1], p[3]], lineno=p.lineno(2))

    def p_assignment(self, p):
        """assignment : variable EQQ expr"""
        p[0] = Tree('assignment', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2))

    def p_ass_error(self, p):
        """assignment : variable EQQ error"""
        p[0] = Tree('error', value='Wrong assignment', children=p[1], lineno=p.lineno(2))
        sys.stderr.write(f'<<<<<Wrong assignment\n')

    def p_type(self, p):
        """type : DIGIT
                | LOGIC"""
        p[0] = Tree('type', value=p[1], children=[], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_digit(self, p):
        """digit : INT_DEC
                | INT_HEX
                | INT_OCT"""
        p[0] = Tree(f'digit', value=p[1], lineno=p.lineno(1))

    def p_bool(self, p):
        """logic : TRUE
                | FALSE"""
        p[0] = Tree('logic', value=p[1], lineno=p.lineno(1))

    def p_expr(self, p):
        """expr : variable
                | digit
                | logic
                | math_expr
                | perform
                | comp"""
        p[0] = p[1]

    def p_math_expr(self, p):
        """math_expr : expr PLUS expr
                    | expr MINUS expr
                    | expr MUL expr
                    | expr DIV expr
                    | expr AND expr
                    | DENY expr
                    | MOST expr"""
        if len(p) == 3:
            p[0] = Tree('unary_op', value=p[1], children=p[2], lineno=p.lineno(2))
        else:
            p[0] = Tree('binary_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2))

    def p_expr_br(self, p):
        """expr : L_SQBRACKET expr R_SQBRACKET"""
        p[1] = Tree('bracket', value=p[1], lineno=p.lineno(1))
        p[3] = Tree('bracket', value=p[3], lineno=p.lineno(3))
        p[0] = Tree('expression', children=[p[1], p[2], p[3]], lineno=p.lineno(1))

    def p_comp(self, p):
        """comp : EQ expr
                | LT expr
                | GT expr
                | LTE expr
                | GTE expr"""
        p[0] = Tree('comparison', value=p[1], children=p[2], lineno=p.lineno(1))

    def p_comp_br(self, p):
        """comp_br : EQ L_SQBRACKET R_SQBRACKET expr
                   | LT L_SQBRACKET R_SQBRACKET expr
                   | GT L_SQBRACKET R_SQBRACKET expr
                   | LTE L_SQBRACKET R_SQBRACKET expr
                   | GTE L_SQBRACKET R_SQBRACKET expr"""

        p[0] = Tree('comparison', value=p[1], children=p[4], lineno=p.lineno(1))

    def p_variable(self, p):
        """variable : VARIABLE
                    | arr_var"""
        if len(p) == 2:
            p[0] = Tree('variable', p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        # else:
        #     p[0] = Tree('indexing', p[1], children=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_arr_var(self, p):
        """arr_var : VARIABLE indexing
                   | arr_var COMMA arr_var"""
        if p[2] == ',':
            p[0] = Tree('array_comma', children=[p[1], p[3]], lineno=p.lineno(2))
        else:
            p[0] = Tree('array_lvl', value=p[1], children=p[2], lineno=p.lineno(2))

    def p_indexing(self, p):
        """indexing : L_SQBRACKET INT_DEC R_SQBRACKET
                    | L_SQBRACKET INT_DEC R_SQBRACKET indexing"""
        if len(p) == 4:
            p[0] = Tree('indexing', children=p[2], lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = Tree('indexing', children=[], lineno=p.lineno(1))

    def p_size(self, p):
        """size : SIZE LBRACKET VARIABLE RBRACKET
                | SIZE LBRACKET type RBRACKET"""
        p[0] = Tree('size', value=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_to(self, p):
        """to : TO type VARIABLE"""
        p[0] = Tree('type change', value=[p[3], p[2]], children=p[3], lineno=p.lineno(1))

    def p_resize(self, p):
        """resize : RESIZE VARIABLE L_SQBRACKET INT_DEC R_SQBRACKET"""
        p[0] = Tree('resize', value=[p[2], p[4]], children=p[2], lineno=p.lineno(1))

    def p_perform(self, p):
        """perform : PERFORM VARIABLE var_list"""
        p[0] = Tree('perform', value=p[2], children=p[3], lineno=p.lineno(1))

    def p_for(self, p):
        """for : FOR VARIABLE STOP VARIABLE STEP VARIABLE NL stat_group"""
        p[0] = Tree('for', children={'start': Tree('variable', p[2]),
                                     'step': Tree('variable', p[6]),
                                     'stop': Tree('variable', p[4]),
                                     'body': p[8]}, lineno=p.lineno(1))

    def p_check(self, p):
        """check : CHECK expr THEN NL stat_group
                | CHECK expr THEN NL stat_group OTHERWISE NL stat_group"""
        if len(p) == 6:
            p[0] = Tree('if_then', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1))
        else:
            p[0] = Tree('if_then', children={'condition': p[2], 'body_1': p[5], 'body_2': p[8]}, lineno=p.lineno(1))

    def p_check_error(self, p):
        """check : CHECK expr error"""
        p[0] = Tree('error', value='Wrong if declaration', lineno=p.lineno(1))

    def p_routing(self, p):
        """routing : type ROUTING VARIABLE var_list NL stat_group RETURN expr ENDSTR NL"""
        if p[3] in self.functions.keys():
            p[0] = Tree('error', value='Function declared earlier', lineno=p.lineno(1))
            sys.stderr.write(f'<<<<<Redeclared function\n')
        else:
            p[0] = Tree('function', value=str(p[3]), children={'parameters': p[4],
                                                               'body': p[6],
                                                               'return': p[8]}, lineno=p.lineno(1))
            self.functions[p[3]] = p[0]

    def p_routing_error(self, p):
        """routing : ROUTING error"""
        p[0] = Tree('error', value='Wrong function declaration', children=p[1], lineno=p.lineno(1))
        sys.stderr.write(f'<<<<<Wrong function declaration\n')

    def p_command(self, p):
        """command : MOVE expr
                    | ROTATE expr
                    | SURROUNDINGS VARIABLE"""
        p[0] = Tree('command', value=p[1], children=p[2], lineno=p.lineno(1))

    def p_error(self, p):
        try:
            sys.stderr.write(f'Syntax error at {p.lineno} line\n')
        except Exception:
            sys.stderr.write(f'Syntax error in input!')
        self.correct = False


if __name__ == '__main__':
    main()
