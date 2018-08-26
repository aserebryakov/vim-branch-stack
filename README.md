vim-branch-stack
================

*vim-branch-stack* is a Vim plugin helping to find the branching path to current line of code.

Introduction
------------

`vim-branch-stack` plugin is intended to help working on legacy C/C++ code where
functions are long and have many nested branches (`if-else`, `switch-case`,
`try-catch`, `while`, `for`).

Installation
------------

#### Requirements

 * python3

#### Vim 8+

```
$ cd ~/.vim/pack/directory_name/start/
$ git clone --recurse-submodules https://github.com/aserebryakov/vim-branch-stack.git
```

#### Pathogen

```
$ cd ~/.vim/bundle
$ git clone --recurse-submodules https://github.com/aserebryakov/vim-branch-stack.git
```

#### NeoBundle

```
NeoBundle 'aserebryakov/vim-branch-stack'
```

Without plugin manager:

Clone or download this repository and copy its contents to your ~/.vim/
directory.


Usage
-----

The stack is shown in the location window after `BranchStack` command
execuiton while cursor is placed on the target line.

#### Example
##### main.cpp
```
int main ()
{
    const int meaning = 42;
    const int pi_floor = 3;
    
    if (meaning)
    {
        if (pi_floor == 4)
        {
            // Do the stuff
        }
        else
        {
            // Cursor is here
        }
    }
    
    return 0;
}
```

##### Location window

```
1 main.cpp |6| if (meaning)
2 main.cpp |12| + else
```


Limitations
-----------

The plugin has the following limitations:

  * Commented out code with `/* block comments */` brakes parsing
  * `goto` is not supported
  * `do-while` is not supported
  * Preprocessing is not supported


Contribution
------------

Source code and issues are hosted on GitHub:

```
https://github.com/aserebryakov/vim-branch-stack
```

License
-------

[MIT License](https://opensource.org/licenses/MIT)


Changelog
---------

#### 0.1.0

* Initial version


#### 0.1.1

* Fixed handling of single line comments

Credits
-------

* Alexander Serebryakov (author)  https://github.com/aserebryakov
