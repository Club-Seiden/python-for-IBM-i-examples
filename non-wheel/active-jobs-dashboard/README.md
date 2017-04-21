# Active Jobs Dashboard
Python script for IBM i that shows active jobs and allows sorting
using the DB2 qsys2.active_job_info() service.  

# Installing requisites
 - Make sure you have installed 5733OPS Option 2, along with PTF's SI59051, SI60563, and SI61963 (or subsequent PTF's)!
   See https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs
 - ```pip3 install --no-index --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/bottle --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db -r requirements.txt```

# Starting the server 
python3 ./server.py

Point your web browser to http://&lt;systemname&gt;:3333

![screen shot](https://raw.githubusercontent.com/Club-Seiden/python-for-IBM-i-examples/master/non-wheel/active-jobs-dashboard/screenshot.jpg)
