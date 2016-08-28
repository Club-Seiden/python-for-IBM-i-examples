#!/QOpenSys/usr/bin/python3
import argparse
import ibm_db   # To install on the IBM i execute
                # pip3 install /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db/ibm_db-*-cp34m-*.whl
                # Make sure you have installed 5733OPS PTF SI59051 and SI60563 or subsequent PTF's!
                # See https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs

import platform
import sys
from tabulate import tabulate # pip install tabulate --user


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Display netstat information.')
    parser.add_argument('--limit', type=int,
        help='Only show X rows')
    parser.add_argument('--offset', type=int,
        help='Skip first X rows')
    parser.add_argument('--port', type=int,
        help='Look for only local port')
    args = parser.parse_args()

db_name = '*LOCAL'
username = 'username'
password = 'password'

try:
  conn = ibm_db.connect(db_name, username, password, {})
except:
  print("no connection:", ibm_db.conn_errormsg())
if conn:
    sql = '''
SELECT
        REMOTE_ADDRESS, REMOTE_PORT, REMOTE_PORT_NAME,
        LOCAL_ADDRESS, LOCAL_PORT, LOCAL_PORT_NAME,
        CONNECTION_TYPE,
        TRIM(AUTHORIZATION_NAME) AS AUTHORIZATION_NAME, JOB_NAME, SLIC_TASK_NAME
    FROM QSYS2.NETSTAT_JOB_INFO
    {0} -- WHERE CLAUSE
    ORDER BY LOCAL_PORT, LOCAL_ADDRESS, REMOTE_PORT,  REMOTE_ADDRESS
'''
    sql = sql.format("WHERE LOCAL_PORT = ?") if  args.port is not None else sql.format('')
    params = (args.port,) if args.port is not None else None
    if args.limit is not None:
        sql += "\n    LIMIT {0}".format(args.limit)
    if args.offset is not None:
        sql += "\n    OFFSET {0}".format(args.offset)

    netstat_stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(netstat_stmt, params)
    row = ibm_db.fetch_assoc(netstat_stmt)
    if row:
        rows = [row]
        while row != False:
            rows.append(row)
            row = ibm_db.fetch_assoc(netstat_stmt)
        print(tabulate(rows, 'keys'))
    ibm_db.close(conn)
else:
  print ('connection failed')
