import vim
from simplex import Tokenizer
from simplex import Token


class State():
    def __init__(self, token_stack):
       self.stack = token_stack
       print(self.__class__)

       if len(self.stack) > 0:
           print(self.stack[-1])

    def handle_token(self, token):
        self.stack.append(token)


class Init(State):
    def __init__(self, token_stack=[]):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'BRANCH_START':
            super().handle_token(token)
            return BranchStart(self.stack)
        elif token.kind == 'BRANCH_ALTERNATIVE':
            super().handle_token(token)
            return AlternativeBranchStart(self.stack)

        return self


class BranchStart(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'BRACE_OPEN':
            super().handle_token(token)
            return InsideBraces(self.stack)
        elif token.kind == 'SCOPE_START':
            super().handle_token(token)
            return InsideBranchScope(self.stack)

        return self


class InsideBranchScope(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'SCOPE_END':
            super().handle_token(token)
            return ScopeEnd(self.stack)
        elif token.kind == 'BRANCH_START' or token.kind == 'BRANCH_ALTERNATIVE':
            super().handle_token(token)
            return BranchStart(self.stack)

        return self


class ScopeEnd(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def unroll_stack(self, token, next_state):
        while len(self.stack) > 1 and self.stack[-1].kind != 'BRANCH_START' and self.stack[-1].kind != 'BRANCH_ALTERNATIVE':
            self.stack.pop()
        self.stack.pop() # removes the starting branch token
        super().handle_token(token)
        return next_state(self.stack)


    def handle_token(self, token):
        if token.kind == 'BRANCH_START':
            return self.unroll_stack(token, BranchStart)
        elif token.kind == 'BRANCH_ALTERNATIVE':
            return self.unroll_stack(token, AlternativeBranchStart)
        elif token.kind == 'SCOPE_END':
            return self.unroll_stack(token, ScopeEnd)

        return self


class AlternativeBranchStart(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'BRACE_OPEN':
            super().handle_token(token)
            return InsideBraces(self.stack)
        elif token.kind == 'SCOPE_START':
            super().handle_token(token)
            return InsideBranchScope(self.stack)
        elif token.kind == 'EXPRESSION_END':
            if len(self.stack) > 0 and self.stack[-1].kind == 'BRANCH_ALTERNATIVE':
                self.stack.pop()
                return Init(self.stack)

        return self


class InsideBraces(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'BRACE_OPEN':
            super().handle_token(token)
        elif token.kind == 'BRACE_CLOSE':
            if len(self.stack) > 0:
                self.stack.pop()
        elif token.kind == 'EXPRESSION_END':
            if len(self.stack) > 0 and self.stack[-1].kind != 'BRACE_OPEN':
                self.stack.pop()
                return Init(self.stack)
        elif token.kind == 'SCOPE_START':
            if len(self.stack) > 0 and self.stack[-1].kind != 'BRACE_OPEN':
                super().handle_token(token)
                return InsideBranchScope(self.stack)

        return self


class ExpressionEnd(State):
    def __init__(self, token_stack):
        super().__init__(token_stack)

    def handle_token(self, token):
        if token.kind == 'BRACE_CLOSE':
            super().handle_token(token)
            return InsideBranchScope(self.stack)

        return self


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
    tokenizer.add_token('BRACE_OPEN', r'\(', handler_generic)
    tokenizer.add_token('BRACE_CLOSE', r'\)', handler_generic)
    tokenizer.add_token('EXPRESSION_END', r';', handler_generic)
    tokenizer.add_token('MISMATCH', r'.', handler_skip)

    data = '\n'.join(vim.current.buffer[startline - 1 : endline - 1])
    estimate_stack(tokenizer.tokenize(data))

    vim.command("normal 'z")
    vim.command("lopen")


def estimate_stack(tokens):
    processor = Init([])

    for token in tokens:
        if not '#define' in vim.current.buffer[token.line - 1]:
            processor = processor.handle_token(token)

    vim.command('set errorformat=%f:%l:%m')

    # Clear location window from previous locations
    vim.command('lexpr []')

    filtered_stack = (token for token in processor.stack if token.kind != 'SCOPE_START')

    for depth, token in enumerate(filtered_stack):
        vim.command("ladd '{}:{}:{} {}'".format(
            vim.current.buffer.name,
            token.line,
            ('+' * depth),
            (vim.current.buffer[token.line - 1].strip().replace('|','\|'))))

