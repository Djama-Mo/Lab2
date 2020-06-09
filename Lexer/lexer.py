import ply.lex as lex


def main():
    print("Hi, nig'")
    with open('example.txt', 'r') as fh:
        data = fh.read()
    lexer = Lexer()
    lexer.input(data)
    while True:
        token = lexer.token()
        if not token:
            break
        print(token)
    print('Thank u, bye')


reserved = {
    'true': 'TRUE',
    'false': 'FALSE',
    'for': 'FOR',
    'stop': 'STOP',
    'step': 'STEP',
    'check': 'CHECK',
    'then': 'THEN',
    'otherwise': 'OTHERWISE',
    'move': 'MOVE',
    'rotate': 'ROTATE',
    'surroundings': 'SURROUNDINGS',
    'return': 'RETURN',
    'perform': 'PERFORM',
    'routing': 'ROUTING',
    'most': 'MOST',
    'digit': 'DIGIT',
    'logic': 'LOGIC',
    'size': 'SIZE',
    'resize': 'RESIZE',
    'to': 'TO',
}


class Lexer(object):

    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['INT_DEC', 'INT_OCT', 'INT_HEX', 'PLUS',
              'MINUS', 'DIV', 'MUL', 'EQ', 'LT', 'GT', 'LTE', 'GTE',
              'VARIABLE', 'COMMA', 'AND', 'DENY', 'LBRACKET', 'RBRACKET',
              'L_FIGBRACKET', 'R_FIGBRACKET', 'NL', 'ENDSTR', 'L_SQBRACKET',
              'R_SQBRACKET'] + list(reserved.values())

    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_DIV = r'\/'
    t_MUL = r'\*'
    t_EQ = r'\='
    t_LT = r'\<'
    t_GT = r'\>'
    t_LTE = r'\<\='
    t_GTE = r'\>\='
    t_COMMA = r'\,'
    t_AND = r'&&'
    t_DENY = r'\!'
    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'
    t_L_FIGBRACKET = r'\{'
    t_R_FIGBRACKET = r'\}'
    t_L_SQBRACKET = r'\['
    t_R_SQBRACKET = r'\]'
    t_ENDSTR = r'\;'

    def t_VARIABLE(self, t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VARIABLE')
        return t

    def t_INT_OCT(self, t):
        r'[0][0-7]+'
        t.value = int(t.value, 8)
        return t

    def t_INT_HEX(self, t):
        r'([0][x][A-F][0-9A-F]*)|([0-9]([A-F]+[0-9]*)*)'# 0xA1 1A
        t.value = int(t.value, 16)
        return t

    def t_INT_DEC(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    t_ignore = ' \t'

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        print("<<<<<Illegal character '%s' " % t.value[0])
        t.lexer.skip(1)
        return t

    def token(self):
        return self.lexer.token()

    def input(self, value):
        return self.lexer.input(value)


if __name__ == '__main__':
    main()
