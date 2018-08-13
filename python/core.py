import vim
from simplex import Tokenizer
from simplex import Token


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

    tokenizer.add_token('BRANCH_START', r'\bif\b|\bswitch\b', handler_generic)
    tokenizer.add_token('BRANCH_ALTERNATIVE', r'else if|\belse\b|\bcase\b|\bdefault\b', handler_generic)
    tokenizer.add_token('SCOPE_START', r'{', handler_generic)
    tokenizer.add_token('NEWLINE', r'\n', handler_newline)
    tokenizer.add_token('SCOPE_END', r'}', handler_generic)
    tokenizer.add_token('MISMATCH', r'.', handler_skip)

    data = '\n'.join(vim.current.buffer[startline - 1 : endline - 1])
    estimate_stack(tokenizer.tokenize(data))


# Branch Start -> Scope Start -> Branch Start
# Branch Start -> Scope Start -> Scope End -> Alternative Branch
#                                                     ^
#                                                     |
#                                         Decision to remove tokens is here
def estimate_stack(tokens):
    stack = []

    for token in tokens:
        if token.kind == 'BRANCH_START' or token.kind == 'SCOPE_START' or token.kind == 'BRANCH_ALTERNATIVE':
            stack.append(token)
        elif token.kind == 'SCOPE_END':
            stack.pop()
            while stack[-1].kind == 'BRANCH_START' or stack[-1].kind == 'BRANCH_ALTERNATIVE':
                stack.pop()

    vim.command('set errorformat=%f:%l:%m')
    vim.command('lexpr [' +
        ','.join(["'{}:{}:{}'".format(vim.current.buffer.name, token.line, vim.current.buffer[token.line - 1])
        for token in stack
        if token.kind != 'SCOPE_START']) +
        ']')

