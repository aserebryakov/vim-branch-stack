import vim
from simplex import Tokenizer, Token


class State():
    def __init__(self, token_stack, previous_state):
        self.previous_state = previous_state
        self.stack = token_stack
        print(self.__class__)

        if len(self.stack) > 0:
            print(self.stack[-1])

    def handle_token(self, token):
        self.stack.append(token)


class Init(State):
    def __init__(self, token_stack=[], previous_state=None):
        super().__init__(token_stack, previous_state)

    def handle_token(self, token):
        if token.kind == 'BRANCH_START':
            super().handle_token(token)
            return BranchStart(self.stack)
        elif token.kind == 'SCOPE_START':
            super().handle_token(token)
            return InsideBranchScope(self.stack)
        elif token.kind == 'COMMENT_BLOCK_START':
            super().handle_token(token)
            return InsideCommentBlock(self.stack, self)

        return self


class BranchStart(State):
    def __init__(self, token_stack, previous_state=None):
        super().__init__(token_stack, previous_state)

    def handle_token(self, token):
        if token.kind == 'BRACE_OPEN':
            super().handle_token(token)
            return InsideBraces(self.stack, self)
        elif token.kind == 'COMMENT_BLOCK_START':
            super().handle_token(token)
            return InsideCommentBlock(self.stack, self)
        elif token.kind == 'SCOPE_START':
            super().handle_token(token)
            return InsideBranchScope(self.stack)
        elif token.kind == 'EXPRESSION_END':
            if len(self.stack) > 0 and self.stack[-1].kind == 'BRANCH_START':
                self.stack.pop()
                return Init(self.stack).handle_token(self.stack[-1])

        return self


class InsideBranchScope(State):
    def __init__(self, token_stack, previous_state=None):
        super().__init__(token_stack, previous_state)

    def handle_token(self, token):
        if token.kind == 'SCOPE_END':
            super().handle_token(token)
            return ScopeEnd(self.stack)
        elif token.kind == 'BRANCH_START':
            super().handle_token(token)
            return BranchStart(self.stack)
        elif token.kind == 'COMMENT_BLOCK_START':
            super().handle_token(token)
            return InsideCommentBlock(self.stack, self)

        return self


class ScopeEnd(State):
    def __init__(self, token_stack, previous_state=None):
        super().__init__(token_stack, previous_state)

    def unroll_stack(self, token, next_state):
        while len(self.stack) > 1 and self.stack[-1].kind != 'BRANCH_START':
            self.stack.pop()
        self.stack.pop() # removes the starting branch token
        super().handle_token(token)
        return next_state(self.stack)

    def handle_token(self, token):
        if token.kind == 'BRANCH_START':
            return self.unroll_stack(token, BranchStart)
        elif token.kind == 'SCOPE_END':
            return self.unroll_stack(token, ScopeEnd)

        return self


class InsideBraces(State):
    def __init__(self, token_stack, previous_state):
        super().__init__(token_stack, previous_state)

    def handle_token(self, token):
        if token.kind == 'BRACE_OPEN':
            super().handle_token(token)
            return InsideBraces(self.stack, self)
        elif token.kind == 'BRACE_CLOSE':
            if len(self.stack) > 0:
                self.stack.pop()
            return self.previous_state
        elif token.kind == 'COMMENT_BLOCK_START':
            super().handle_token(token)
            return InsideCommentBlock(self.stack, self)

        return self


class InsideCommentBlock(State):
    def __init__(self, token_stack, previous_state):
        super().__init__(token_stack, previous_state)

    def unroll_comment_block(self):
        while len(self.stack) > 1 and self.stack[-1].kind != 'COMMENT_BLOCK_START':
            self.stack.pop()
        self.stack.pop() # removes the comment block start token

        # Continue unrolling until all comments will not be removed
        for e in self.stack:
            if e.kind == 'COMMENT_BLOCK_START':
                self.unroll_comment_block()

    def handle_token(self, token):
        if token.kind == 'COMMENT_BLOCK_END':
            self.unroll_comment_block()
            return self.previous_state

        return self


class ExpressionEnd(State):
    def __init__(self, token_stack, previous_state=None):
        super().__init__(token_stack, previous_state)

    def handle_token(self, token):
        if token.kind == 'BRACE_CLOSE':
            super().handle_token(token)
            return InsideBranchScope(self.stack)
        elif token.kind == 'COMMENT_BLOCK_START':
            super().handle_token(token)
            return InsideCommentBlock(self.stack, self)

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


def core_main():
    startline, endline = get_data_range()
    data = '\n'.join(vim.current.buffer[startline - 1 : endline - 1])

    tokenizer = initialize_tokenizer(startline)
    estimate_stack(tokenizer.tokenize(data))

    vim.command("normal 'z")
    vim.command("lopen")


def prepare_line_of_code(line):
    line = line.strip()
    line = line.replace('|', '\|') # Causes error in ladd command if not handles
    line = line.replace("'", '"') # Causes error in ladd command if not handles
    return line


def token_should_be_processed(token):
    line = vim.current.buffer[token.line - 1]
    comment_start = line.find('//')
    if (comment_start != -1 and
        token.column > comment_start and
        token.kind != 'COMMENT_BLOCK_START' and
        token.kind != 'COMMENT_BLOCK_END'):
        return False

    # define strings aren't part of the code but may contain tokens
    return (not '#define' in line)


def estimate_stack(tokens):
    processor = Init([])

    for token in tokens:
        if token_should_be_processed(token):
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
            prepare_line_of_code(vim.current.buffer[token.line - 1])))
