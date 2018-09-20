from simplex import Token

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
