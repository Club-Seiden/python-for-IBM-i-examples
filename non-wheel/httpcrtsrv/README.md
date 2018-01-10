# httpsrv 

Python script to create, delete, and rename HTTP Server Instances on the IBM i. 

# Installing requisites

I think this may require installing the toolkit. Is the toolkit already installed along
with Python on the IBM i?

# Usage examples:  

```commandline
$ python3 httpsrv.py --help                            # Display help
$ python3 httpsrv.py -c --conf=zendsvr6 --name=develop # Create an HTTP Server Instance. Configuration: PHP 5.6, Name: DEVELOP
$ python3 httpsrv.py -c --conf=zendphp7 --name=develop # Create an HTTP Server Instance. Configuration: PHP 7, Name: DEVELOP
$ python3 httpsrv.py -c --conf=apache --name=develop   # Create an HTTP Server Instance. Configuration: Apache, Name: DEVELOP
$ python3 httpsrv.py -d --name=develop                 # Delete HTTP Server Instance with name DEVELOP
$ python3 httpsrv.py -r --name=develop --newname=test  # Rename HTTP Server Instance DEVELOP to TEST
```
