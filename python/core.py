import vim
from simplex import Tokenizer, Token
from token_processor import estimate_stack
from tokenizer import initialize_tokenizer


def core_main():
    startline, endline = get_data_range()
    data = '\n'.join(vim.current.buffer[startline - 1 : endline - 1])

    tokenizer = initialize_tokenizer(startline)
    tokens = estimate_stack(tokenizer.tokenize(data))

    fill_location_window(tokens, endline)

    vim.command("normal 'z")
    vim.command("lopen")


def get_data_range():
    vim.command('normal mz')
    endline = int(vim.eval('line(".")'))
    vim.command('normal [[')
    startline = int(vim.eval('line(".")'))
    vim.command("normal 'z")
    return (startline, endline)


def fill_location_window(tokens, current_line):
    vim.command('set errorformat=%f:%l:%m')

    # Clear location window from previous locations
    vim.command('lexpr []')

    for depth, token in enumerate(tokens):
        add_location(token.line, depth)

    add_location(current_line, len(tokens))


def add_location(line_number, indent):
    vim.command("ladd '{}:{}:{} {}'".format(
        vim.current.buffer.name,
        line_number,
        ('+' * indent),
        prepare_line_of_code(vim.current.buffer[line_number - 1])))


def prepare_line_of_code(line):
    line = line.strip()
    line = line.replace('|', '\|') # Causes error in ladd command if not handles
    line = line.replace("'", '"') # Causes error in ladd command if not handles
    return line
