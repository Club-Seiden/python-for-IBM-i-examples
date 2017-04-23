# Sample Bottle Application 
Python bottle example from the [IBM developerWorks wiki](https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Sample%20web%20application%20with%20Python)

# Installing requisites
 - Make sure you have installed 5733OPS Option 2, along with PTFs SI59051, SI60563, SI60564, and SI61963 (or subsequent PTFs)!
   See [here](https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs) for the latest PTF numbers.
 - ```pip3 install --no-index --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/bottle --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db --find-links /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/itoolkit -r requirements.txt```

# Starting the server 
python3 ./sample.py

Point your web browser to http://&lt;systemname&gt;:9000/sample

![screen shot](./screenshot.png?raw=true)
