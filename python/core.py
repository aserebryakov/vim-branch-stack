import vim
from simplex import Tokenizer
from simplex import Token


# States
# INIT
# NOT_BRANCH_SCOPE
# BRANCH_START
# IN_BRANCH_SCOPE
# ALTERNATIVE_BRANCH
# IN_ALTERNATIVE_BRANCH_SCOPE
# SCOPE_END

class TokenProcessor:
    def __init__(self):
       self.stack = []
       self.state = 'INIT'

    def handle_token(self, token):
        print("append {} state {}".format(token, self.state))

        if token.kind == 'BRANCH_START':
            self.handle_branch_start()
        elif token.kind == 'BRANCH_ALTERNATIVE':
            self.handle_branch_alternative()
        elif token.kind == 'SCOPE_START':
            self.handle_scope_start()
        elif token.kind == 'SCOPE_END':
            self.handle_scope_end()

        self.stack.append(token)

    def handle_branch_start(self):
        previous_state = self.state
        self.state = 'BRANCH_START'

        if previous_state != 'SCOPE_END':
            return

        while len(self.stack) > 0 and self.stack[-1].kind != 'BRANCH_START':
            self.stack.pop()

        # Removes the BRANCH_START when scope is ended
        if len(self.stack) > 0:
            self.stack.pop()


    def handle_branch_alternative(self):
        previous_state = self.state
        self.state = 'ALTERNATIVE_BRANCH'

        if previous_state != 'SCOPE_END':
            return

        while len(self.stack) > 0 and self.stack[-1].kind != 'BRANCH_START' and self.stack[-1].kind != 'ALTERNATIVE_BRANCH':
            self.stack.pop()

    def handle_scope_start(self):
        if self.state == 'INIT':
            self.state = 'NOT_BRANCH_SCOPE'
        elif self.state == 'BRANCH_START':
            self.state = 'IN_BRANCH_SCOPE'
        elif self.state == 'ALTERNATIVE_BRANCH':
            self.state = 'IN_ALTERNATIVE_BRANCH_SCOPE'

    def handle_scope_end(self):
        self.state = 'SCOPE_END'


def handler_generic(match_object, kind, value, keywords, state):
    column = match_object.start() - state['line_start']
    return Token(kind, value, state['line_num'], column)


def handler_skip(match_object, kind, value, keywords, state):
    return None


def handler_newline(match_object, kind, value, keywords, state):
    state['line_start'] = match_object.end()
    state['line_num'] += 1


def get_data_range():
    vim.command('normal mz')
    endline = int(vim.eval('line(".")'))
    vim.command('normal [[')
    startline = int(vim.eval('line(".")'))
    vim.command("normal 'z")
    return (startline, endline)

def core_main():
    startline, endline = get_data_range()

    tokenizer = Tokenizer({
        'line_num' : startline,
        'line_start' : 0
    })

    tokenizer.add_token('BRANCH_START', r'\b(?<!#)if\b|\bswitch\b|\bfor\b|\bwhile\b', handler_generic)
    tokenizer.add_token('BRANCH_ALTERNATIVE', r'else if|\b(?<!#)else\b|\bcase\b|\bdefault\b', handler_generic)
    tokenizer.add_token('SCOPE_START', r'{', handler_generic)
    tokenizer.add_token('NEWLINE', r'\n', handler_newline)
    tokenizer.add_token('SCOPE_END', r'}', handler_generic)
    tokenizer.add_token('MISMATCH', r'.', handler_skip)

    data = '\n'.join(vim.current.buffer[startline - 1 : endline - 1])
    estimate_stack(tokenizer.tokenize(data))

    vim.command("normal 'z")
    vim.command("lopen")


def estimate_stack(tokens):
    processor = TokenProcessor()

    for token in tokens:
        processor.handle_token(token)

    print(processor.stack)

    vim.command('set errorformat=%f:%l:%m')

    # Clear location window from previous locations
    vim.command('lexpr []')

    filtered_stack = (token for token in processor.stack if token.kind != 'SCOPE_START')

    for depth, token in enumerate(filtered_stack):
        vim.command("ladd '{}:{}:{} {}'".format(
            vim.current.buffer.name, token.line, ('+' * depth), (vim.current.buffer[token.line - 1].strip())))

