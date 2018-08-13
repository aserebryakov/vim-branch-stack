import vim
from simplex import Tokenizer
from simplex import Token

data = '''
if (true) {
  ifif
}
else
{
}

if (true)
  do
else if
{
    do something else
}

switch (test) {
  case 0:
  {
  }
  case 1:
  {
  }
  case 3:
  case 4:

}
'''

def handler_generic(match_object, kind, value, keywords, state):
    column = match_object.start() - state['line_start']
    return Token(kind, value, state['line_num'], column)


def handler_skip(match_object, kind, value, keywords, state):
    return None


def handler_newline(match_object, kind, value, keywords, state):
    state['line_start'] = match_object.end()
    state['line_num'] += 1


def core_main():
    tokenizer = Tokenizer({
        'line_num' : 1,
        'line_start' : 0
    })

    tokenizer.add_token('BRANCH_START', r'\bif\b|\bswitch\b', handler_generic)
    tokenizer.add_token('BRANCH_ALTERNATIVE', r'else if|\belse\b|\bcase\b|\bdefault\b', handler_generic)
    tokenizer.add_token('SCOPE_START', r'{', handler_generic)
    tokenizer.add_token('NEWLINE', r'\n', handler_newline)
    tokenizer.add_token('SCOPE_END', r'}', handler_generic)
    tokenizer.add_token('MISMATCH', r'.', handler_skip)

    estimate_stack(tokenizer.tokenize(data))


def estimate_stack(tokens):
    stack = []

    for token in tokens:
        if token.kind == 'BRANCH_START' or token.kind == 'SCOPE_START' or token.kind == 'BRANCH_ALTERNATIVE':
            stack.append(token)
        elif token.kind == 'SCOPE_END':
            stack.pop()

    vim.command('set errorformat=%f:%l')
    vim.command('lexpr [' + ','.join(["'{}:{}'".format(vim.current.buffer.name, str(token.line)) for token in stack]) + ']')

