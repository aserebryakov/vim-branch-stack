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

    for token in tokenizer.tokenize(data):
        print(token)

