# "CPYTOIMPF" using Python 3 and ibm_db_dbi
This is a simple Python 3 example using the CSV support built in to Python 3 and the ibm_db_db2 package on IBM i to generate a CSV file from a DB2 records.

# Installing requisites
 - Make sure you have installed 5733OPS Option 2, along with PTFs SI59051, SI60563, SI60564, and SI61963 (or subsequent PTFs)!
   See [here](https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs) for the latest PTF numbers.
 - ```pip3 install --no-index --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db -r requirements.txt```

# Running the example
```python3 ./dbtocsv.py```

# More information

- Python [csv](https://docs.python.org/3/library/csv.html) module documentation
- [PEP 249](https://www.python.org/dev/peps/pep-0249/) - Python Database API v2
