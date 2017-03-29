Sample usage:
./dbtoxlsx -h 
```
usage: dbtoxlsx.py [-h] [-c C] [-l L] [-f [FNAMES [FNAMES ...]]] [-o O] [-b B] [-i I]

Example: python3 dbtoxlsx.py -c "select * From QSYS2.USER_INFO WHERE STATUS = '*ENABLED'" -o /home/test.xlsx 

Implement SQL from IBM i command line and direct output to an Excel
spreadsheet.

Requires the latest ibm_db PTF: 
https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs
And xlsxwriter via command from SSH or qp2term:
pip3 install xlsxwriter

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
