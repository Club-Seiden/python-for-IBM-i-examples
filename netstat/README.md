# netstat  
Python script for IBM i that provides NETSTAT information  
using DB2 QSYS2.NETSTAT_JOB_INFO service.  

# Installing requisites
 - Make sure you have installed 5733OPS Option 2, along with PTF's SI59051, SI60563, and SI61963 (or subsequent PTF's)!
   See https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs
 - ```pip3 install /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db/ibm_db-*-cp34m-*.whl```
 - ```pip3 install tabulate --user```

# Usage examples:  
python3 netstat.py -h                     # show help  
python3 netstat.py                        # show all network services  
python3 netstat.py --limit 5 --offset 10  # show a subset based on limit 5 (how many) and offset 10 (what row to start with)  
python3 netstat.py --port 21              # show what's on smtp  
python3 netstat.py --port 80              # get info for port 80 (standard web port)  
