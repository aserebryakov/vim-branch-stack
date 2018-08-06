" MIT License
"
" Copyright (c) 2018 Alexander Serebryakov (alex.serebr@gmail.com)
"
" Permission is hereby granted, free of charge, to any person obtaining a copy
" of this software and associated documentation files (the "Software"), to
" deal in the Software without restriction, including without limitation the
" rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
" sell copies of the Software, and to permit persons to whom the Software is
" furnished to do so, subject to the following conditions:
"
" The above copyright notice and this permission notice shall be included in
" all copies or substantial portions of the Software.
"
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
" FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
" IN THE SOFTWARE.


" TODO: Document
function! VimBranchStackFind()
  let s:script_folder_path = escape(expand('<sfile>:p:h'),'\')  

python3 << EOF
import sys, os
import vim
script_folder = vim.eval('s:script_folder_path')

# TODO: Handle the adding the same path multiple times on pack-add
sys.path.insert(0, os.path.join(script_folder, 'python', 'simplex'))
from simplex import Tokenizer

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


tokenizer = Tokenizer({
    'line_num' : 1,
    'line_start' : 0
})

tokenizer.add_token('BRANCH_START', r'\bif\b|\bswitch\b', handler_generic) # Integer or decimal number
tokenizer.add_token('BRANCH_ALTERNATIVE', r'else if|\belse\b|\bcase\b|\bdefault\b', handler_generic) # Integer or decimal number
tokenizer.add_token('SCOPE_START', r'{', handler_generic) # Assignment operator
tokenizer.add_token('NEWLINE', r'\n', handler_newline) # Assignment operator
tokenizer.add_token('SCOPE_END', r'}', handler_generic) # Assignment operator
tokenizer.add_token('MISMATCH', r'.', handler_skip) # Any other character

for token in tokenizer.tokenize(data):
    print(token)

EOF
endfunction


"Plugin startup code
if !exists('g:vimbranchstack_plugin')
  let g:vimbranchstack_plugin = 1
 
  command! BranchStack silent call VimBranchStackFind()
endif

