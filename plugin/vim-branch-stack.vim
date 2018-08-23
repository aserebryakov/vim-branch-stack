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


" Parses the code and shows the branching stack in location window
function! VimBranchStack()
  if !has('python3')
    echoerr 'Vim must be compiled with python3 support to use this plugin'
    return
  endif

python3 << EOF

import sys, os
import vim
script_folder = vim.eval('s:script_folder_path')

# TODO: Handle the adding the same path multiple times on pack-add
sys.path.insert(0, os.path.join(script_folder, '..', 'python'))
sys.path.insert(0, os.path.join(script_folder, '..', 'python', 'simplex'))

import core

core.core_main()

EOF
endfunction


"Plugin startup code
if !exists('g:vimbranchstack_plugin')
  let g:vimbranchstack_plugin = 1
  let s:script_folder_path = escape(expand('<sfile>:p:h'),'\')

  command! BranchStack silent call VimBranchStack()
endif

