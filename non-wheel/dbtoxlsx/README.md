Sample usage:
./dbtoxlsx -h 
```
usage: dbtoxlsx.py [-h] [-c C] [-l L] [-f [FNAMES [FNAMES ...]]] [-o O] [-b B] [-i I]

Implement SQL from IBM i command line and direct output to an Excel
spreadsheet.

optional arguments:
  -h, --help            show this help message and exit
  -c C, --c C           SQL command to execute. If left empty you must specify
                        a library and source file to execute the default
                        command: Select * from <library>.<file>
  -l L, --l L           Name of the library that contains the database source
                        file(s) that you wish to query
  -f [FNAMES [FNAMES ...]], --f [FNAMES [FNAMES ...]]
                        One or more database source files
  -o O, --o O           Name of the excel file to contain the output
  -b B, --b B           Turn on bold for column headings
  -i I, --i I           Turn on italic for column headings
```
