import vim
from state_machine import State, Init


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
    state = Init([])

    for token in tokens:
        if token_should_be_processed(token):
            state = state .handle_token(token)

    return [token for token in state.stack if token.kind != 'SCOPE_START']
