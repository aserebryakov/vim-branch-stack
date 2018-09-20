from simplex import Tokenizer, Token


def handler_generic(match_object, kind, value, keywords, state):
    column = match_object.start() - state['line_start']
    return Token(kind, value, state['line_num'], column)


def handler_skip(match_object, kind, value, keywords, state):
    return None


def handler_newline(match_object, kind, value, keywords, state):
    state['line_start'] = match_object.end()
    state['line_num'] += 1


def initialize_tokenizer(startline):
    tokenizer = Tokenizer({
        'line_num' : startline,
        'line_start' : 0
    })

    tokenizer.add_token('BRANCH_START', r'\b(?<!#)if\b|\bswitch\b|\bfor\b|'
                                        r'\bwhile\b|\btry\b|else if|\b(?<!#)else\b|'
                                        r'\bcase\b|\bdefault\b|\bcatch\b', handler_generic)
    tokenizer.add_token('SCOPE_START', r'{', handler_generic)
    tokenizer.add_token('NEWLINE', r'\n', handler_newline)
    tokenizer.add_token('SCOPE_END', r'}', handler_generic)
    tokenizer.add_token('BRACE_OPEN', r'\(', handler_generic)
    tokenizer.add_token('BRACE_CLOSE', r'\)', handler_generic)
    tokenizer.add_token('COMMENT_BLOCK_START', r'/\*', handler_generic)
    tokenizer.add_token('COMMENT_BLOCK_END', r'\*/', handler_generic)
    tokenizer.add_token('EXPRESSION_END', r';', handler_generic)
    tokenizer.add_token('MISMATCH', r'.', handler_skip)

    return tokenizer
